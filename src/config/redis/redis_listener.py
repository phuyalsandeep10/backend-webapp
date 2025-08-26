import redis.asyncio as redis

# from src.config.broadcast import broadcast  # Replaced with direct Redis pub/sub
from src.config.settings import settings
from src.websocket.subscribers.chat_subscriber import chat_subscriber
import json
from src.websocket.channel_names import is_chat_channel

# Redis keys (imported from chat_handler)
REDIS_ROOM_KEY = "chat:room:"  # chat:room:{conversation_id} -> set of sids
REDIS_SID_KEY = "chat:sid:"  # chat:sid:{sid} -> conversation_id


async def start_listener():
    r = redis.Redis()
    pubsub = r.pubsub()
    await pubsub.subscribe("sla_channel")

    async for msg in pubsub.listen():
        print(f"Received SLA message: {msg['data']}")
        # TODO: Implement SLA message handling


redis_client = None


async def get_redis() -> redis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=False)
    return redis_client


async def redis_listener(sio):
    print("subscriber listen")

    redis = await get_redis()
    # Don't clear Redis data on startup - this was causing issues
    # await redis.flushall()
    # await redis.flushdb()
    pattern = "ws:*"

    # Get all matching keys
    keys = await redis.keys(pattern)
    print(f"keys {keys}")
    pubsub = redis.pubsub()
    # Subscribe to chat channels only to avoid noise
    await pubsub.psubscribe("chat-*")  # Only chat channels

    # await pubsub.subscribe("notifications", "chat:room1")

    async for message in pubsub.listen():
        print(f"Received message type: {message['type']} on channel: {message['channel']}")

        if message["type"] != "pmessage":
            print(f"Received on {message['channel']}: {message['data']}")
        channel = message["channel"]
        

        if isinstance(channel, bytes):
            try:
                channel = channel.decode("utf-8")
            except UnicodeDecodeError:
                print(f"⚠ Non-UTF8 channel name: {channel!r}")
                continue
        elif not isinstance(channel, str):
            print(f"⚠ Unexpected channel type: {type(channel)}")
            continue

        if channel == "/0.celeryev/worker.heartbeat" or channel == "socketio":
            continue

        data = message.get("data")
        if data is None:
            print("⚠ No data in message")
            continue


        try:
            if isinstance(data, (dict, list)):
                payload = data
            elif isinstance(data, (int, float)):
                payload = {"value": data}
            elif isinstance(data, str):
                try:
                    payload = json.loads(data)
                except json.JSONDecodeError:
                    payload = {"raw": data}
            else:
                try:
                    payload = {"raw": json.loads(data.decode("utf-8"))}
                except (json.JSONDecodeError, AttributeError):
                    payload = {"raw": str(data)}

        except Exception as e:
            print(f"Error parsing payload: {e}")
            payload = {"raw": str(data)}
            
        if payload.get("raw"):
            payload = payload.get("raw")

        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError:
                payload = {"raw": payload}

        if is_chat_channel(channel):
            try:
                print(f"🔔 Processing chat channel: {channel}")
                await chat_subscriber(sio, channel=channel, payload=payload)
            except Exception as e:
                print(f"❌ Error processing chat channel {channel}: {e}")
                import traceback
                traceback.print_exc()
            continue
