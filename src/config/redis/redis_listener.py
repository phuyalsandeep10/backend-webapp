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
        await broadcast(msg["data"])


redis_client = None


async def get_redis() -> redis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=False)
    return redis_client


async def redis_listener(sio):
    print(f"subscriber listen")
    
    redis = await get_redis()
    await redis.flushall()
    await redis.flushdb()
    pattern = "ws:*"

# Get all matching keys
    keys = await redis.keys(pattern)
    print(f"keys {keys}")
    pubsub = redis.pubsub()
    # Subscribe to ALL channels
    await pubsub.psubscribe("*")  # Wildcard for all channels

    # await pubsub.subscribe("notifications", "chat:room1")

    async for message in pubsub.listen():
        # print(f"Received on {message['channel']}: {message['data']} and message type {message['type']}")

        if message["type"] != "pmessage":
            print(f"Received on {message['channel']}: {message['data']}")
        channel = message["channel"]

        if isinstance(channel, bytes):
            try:
                channel = channel.decode("utf-8")
            except UnicodeDecodeError:
                print(f"⚠ Non-UTF8 channel name: {channel!r}")
                continue

        if channel == "/0.celeryev/worker.heartbeat" or channel == "socketio":
            continue

        # print(f"channel name {channel}")
        data = message["data"]

        try:
            if isinstance(data, (dict, list)):
                payload = data
            elif isinstance(data, (int, float)):
                payload = {"value": data}
            elif isinstance(data, str):
                payload = json.loads(data)

            else:
                payload = {"raw": json.loads(data.decode("utf-8"))}

        except json.JSONDecodeError:
            print("json decorder error")
            # print(f"type of data {data}")
            payload = {"raw": data}
        if payload.get("raw"):
            payload = payload.get("raw")
        
        if isinstance(payload, str):
            payload = json.loads(payload)
        # print(f"redis listener payload {payload} and type {type(payload)}")

     

        if is_chat_channel(channel):
            await chat_subscriber(sio,channel=channel,payload=payload)
            continue

        # print(f" Received from Redis | Channel: {channel} | Data: {payload}")

        # Example: route message to all clients in that conversation

        # if channel.startswith("customer-message"):
        #     conversation_id = payload.get("conversation_id")
        #     event = payload.get("event", "message")
        #     room_name = user_conversation_group(conversation_id)
        #     print(f"sending message to agent with conversation {conversation_id}")
        #     await sio.emit(
        #         event,
        #         payload,
        #         room=room_name,
        #         namespace="/agent-chat",
        #     )

        # if channel == "user-message-notification":
        #     print("--user message notification--")
        #     org_id = payload.get("organization_id")
        #     event = payload.get("event")
        #     room_name = user_notification_group(org_id)
        #     await sio.emit(event, payload, room=room_name, namespace="/agent-chat")

        # if channel.startswith("user-message"):
        #     conversation_id = payload.get("conversation_id")
        #     # conversation_id = channel.replace("conversation-", "")
        #     event = payload.get("event", "message")
        #     room_name = conversation_group(conversation_id)
        #     print(f"sending message to agent with conversation {conversation_id}")
        #     await sio.emit(
        #         event,
        #         payload,
        #         room=room_name,
        #         namespace="/chat",
        #     )

        # if channel.startswith("conversation-"):
        #     conversation_id = channel.replace("conversation-", "")
        #     event = payload.get("event", "message")
        #     room_name = conversation_group(conversation_id)

        #     # if not is_room_empty(sio, namespace, room_name) or payload.get("event") == "typing":
        #     print(f"conversation emit to room {room_name}")
        #     await sio.emit(
        #         event,
        #         payload,
        #         room=room_name,
        #         namespace="/chat",
        #     )

 
        # # Example: handle org-level notifications
        # elif ":user_notification" in channel:
        #     print("user notification subscribe")

        #     org_id = payload.get("organization_id")
        #     event = payload.get("event", "notification")

        #     room = user_notification_group(org_id)
        #     print(f"room {room}")
        #     print(f"event {event}")

        #     await sio.emit(
        #         event,
        #         payload,
        #         room=room,
        #         namespace="/agent-chat",
        #     )

        # elif ":customer_notification" in channel:
        #     print("Customer notification subscribe ")
        #     event = payload.get("event", "notification")
        #     org_id = payload.get("organization_id")
        #     room = customer_notification_group(org_id)
            # await sio.emit(event, payload, room=room, namespace="/chat")


def is_room_empty(sio, namespace, room_name):
    room_dict = sio.manager.rooms.get(namespace, {})
    # Get the room members set/dict
    members = room_dict.get(room_name)
    return not members
