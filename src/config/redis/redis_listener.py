import redis.asyncio as redis
# from src.config.broadcast import broadcast  # Replaced with direct Redis pub/sub
from src.config.settings import settings
import socketio
import json

# Redis keys (imported from chat_handler)
REDIS_ROOM_KEY = "chat:room:"  # chat:room:{conversation_id} -> set of sids
REDIS_SID_KEY = "chat:sid:"  # chat:sid:{sid} -> conversation_id


async def start_listener():
    r = redis.Redis()
    pubsub = r.pubsub()
    await pubsub.subscribe("sla_channel")

    async for msg in pubsub.listen():
        await broadcast(msg["data"])


redis_client = None


async def get_redis() -> redis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(
            settings.REDIS_URL, decode_responses=True
        )
    return redis_client


async def redis_listener(sio: socketio.AsyncServer):
    print("🚀 Redis listener task started")
    while True:
    
        redis_client = None
        pubsub = None
        
        try:
            print("🔌 Connecting to Redis for pub/sub...")
            # Create a persistent Redis connection for pub/sub
            redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            print("✅ Redis client created")
            
            pubsub = redis_client.pubsub()
            print("✅ Pubsub object created")
            
            # Subscribe to all channels with pattern matching
            await pubsub.psubscribe("*")
            print("✅ Successfully subscribed to Redis pub/sub pattern '*'")
            
            # Verify subscription worked with a simple test
            import asyncio
            await asyncio.sleep(0.2)  # Give subscription time to register
            print("🔍 Subscription should now be active...")
            
            # Test the pub/sub connection by publishing a test message
            # test_client = await redis.from_url(settings.REDIS_URL, decode_responses=True)
            # try:
            #     result = await test_client.publish("startup_test", '{"event": "startup_test"}')
            #     print(f"🧪 Published startup test, {result} subscribers received it")
            #     if result == 0:
            #         print("⚠️ WARNING: No subscribers detected - subscription may have failed")
            # except Exception as e:
            #     print(f"❌ Test publish failed: {e}")
            # finally:
            #     await test_client.aclose()
            
            async for message in pubsub.listen():
                print(f"message: {message}")
                if message['type'] == 'pmessage':
                    print("📨 Got message from Redis pub/sub")
                    try:
                        channel = message['channel'].decode() if isinstance(message['channel'], bytes) else message['channel']
                        data = message['data'].decode() if isinstance(message['data'], bytes) else message['data']
                        
                        print(f"📨 Got message: {data} from channel: {channel}")
                        
                        # Attempt to parse JSON payloads only
                        try:
                            payload = json.loads(data)
                        except Exception:
                            continue

                        event_type = payload.get("event")
                        
                        # Process the message based on channel type
                        message_processed = False
                    except Exception as e:
                        print(f"❌ Exception in redis_listener: {e}")
                        continue

                    # 1) Conversation room fanout (messages, typing, seen, etc.) using channel name
                    if channel.startswith("conversation-"):
                        conversation_id = channel.split("conversation-", 1)[1]
                        # Reuse the existing redis_client instead of creating a new one
                        sids = await redis_client.smembers(f"{REDIS_ROOM_KEY}{conversation_id}")
                        sender_sid = payload.get("sid")
                        for target_sid in sids:
                            if sender_sid and target_sid == sender_sid:
                                continue
                            await sio.emit(
                                event_type, payload, room=target_sid, namespace="/chat"
                            )
                        message_processed = True

                    # 2) Workspace-scoped online notifications
                    # Channels: ws:{org_id}:customer_sids and ws:{org_id}:user_sids
                    if channel.startswith("ws:"):
                        parts = channel.split(":")
                        # Expecting ["ws", "{org_id}", "{group}"]
                        if len(parts) >= 3:
                            org_id = parts[1]
                            group = parts[2]

                            # Notify all customer sockets in the org (iterate all conversation sets)
                            if group == "customer_sids":
                                cursor = "0"
                                pattern = f"ws:{org_id}:conversation_sids:*"
                                # Reuse the existing redis_client instead of creating a new one
                                while True:
                                    cursor, keys = await redis_client.scan(
                                        cursor=cursor, match=pattern, count=100
                                    )
                                    for key in keys:
                                        sids = await redis_client.smembers(key)
                                        for target_sid in sids:
                                            await sio.emit(
                                                event_type,
                                                payload,
                                                room=target_sid,
                                                namespace="/chat",
                                            )
                                    if cursor == "0":
                                        break
                                message_processed = True

                            # Notify all user sockets in the org (iterate all user_sids per user)
                            if group == "user_sids":
                                cursor = "0"
                                pattern = f"ws:{org_id}:user_sids:*"
                                # Reuse the existing redis_client instead of creating a new one
                                while True:
                                    cursor, keys = await redis_client.scan(
                                        cursor=cursor, match=pattern, count=100
                                    )
                                    for key in keys:
                                        sids = await redis_client.smembers(key)
                                        for target_sid in sids:
                                            await sio.emit(
                                                event_type,
                                                payload,
                                                room=target_sid,
                                                namespace="/chat",
                                            )
                                    if cursor == "0":
                                        break
                                message_processed = True

                    # 3) Handle direct user notifications (like customer_land events)
                    if channel.startswith("ws:") and channel.endswith(":user_notification"):
                        parts = channel.split(":")
                        if len(parts) >= 2:
                            org_id = parts[1]
                            print(f"🎯 Processing user_notification for org {org_id}")
                            # Find all user sids in this organization
                            cursor = "0"
                            pattern = f"ws:{org_id}:user_sids:*"
                            user_count = 0
                            # Reuse the existing redis_client instead of creating a new one
                            while True:
                                cursor, keys = await redis_client.scan(
                                    cursor=cursor, match=pattern, count=100
                                )
                                for key in keys:
                                    sids = await redis_client.smembers(key)
                                    for target_sid in sids:
                                        await sio.emit(
                                            event_type,
                                            payload,
                                            room=target_sid,
                                            namespace="/chat",
                                        )
                                        user_count += 1
                                if cursor == "0":
                                    break
                            print(f"📤 Sent {event_type} to {user_count} users in org {org_id}")
                            message_processed = True
                    
                    if not message_processed:
                        print(f"⚠️  Unhandled channel: {channel}")
                        
        except Exception as e:
            print(f"❌ Redis listener failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print('finally unsubscribe')
            # Clean up connections
            if pubsub:
                try:
                    await pubsub.unsubscribe()
                    await pubsub.aclose()
                    print("🧹 Pub/sub connection closed")
                except Exception as e:
                    print(f"⚠️ Error closing pub/sub: {e}")
            
            if redis_client:
                try:
                    await redis_client.aclose()
                    print("🧹 Redis client connection closed")
                except Exception as e:
                    print(f"⚠️ Error closing Redis client: {e}")


                #     if conversation_id:
                #         sids = await redis.smembers(f"{REDIS_ROOM_KEY}{conversation_id}")
                #         for target_sid in sids:
                #             if target_sid != sid:
                #                 await sio.emit(
                #                     event_type,
                #                     payload,
                #                     room=target_sid,
                #                     namespace=chat_namespace,
                #                 )

