import json

import socketio
from socketio.simple_client import Event


from src.common.dependencies import get_user_by_token

# from src.config.broadcast import broadcast  # Replaced with direct Redis pub/sub

from src.config.settings import settings
from src.websocket.chat_namespaces.agent_chat_namespace import chat_namespace
from ..chat_utils import (
    get_room_channel,
    user_notification_group,
    customer_notification_group,
    conversation_group,
    user_conversation_group,
)
from ..chat_redis import redis_publish
from src.config.redis.redis_listener import get_redis


REDIS_URL = settings.REDIS_URL


# Redis keys
REDIS_ROOM_KEY = "chat:room:"  # chat:room:{conversation_id} -> set of sids
REDIS_SID_KEY = "chat:sid:"  # chat:sid:{sid} -> conversation_id


# Redis helper


class CustomerChatNamespace(socketio.AsyncNamespace):
    receive_message = "receive-message"
    receive_typing = "typing"
    stop_typing = "stop-typing"
    message_seen = "message_seen"
    chat_online = "chat_online"
    customer_land = "customer_land"
    message_notification = "message-notification"

    def __init__(self):
        super().__init__("/chat")
        self.rooms = {}

    async def _notify_to_customers(self, org_id: int):
        await redis_publish(
            channel=f"ws:{org_id}:customer_notification",
            message=json.dumps(
                {"event": self.chat_online, "mode": "online", "organization_id": org_id}
            ),
        )

    async def _notify_to_users(self, org_id: int):
        print(f"notify users in the same workspace that a customer has connected")
        await redis_publish(
            channel=f"ws:{org_id}:user_notification",
            message=json.dumps(
                {
                    "event": self.customer_land,
                    "mode": "online",
                    "organization_id": org_id,
                }
            ),
        )

    async def _join_org_user_group(self, org_id: int, sid: int):
        print(f"join room name {user_notification_group(org_id)} and sid {sid}")
        await self.enter_room(sid=sid, room=user_notification_group(org_id))

    async def _join_org_customer_group(self, org_id: int, sid: int):
        self.enter_room(sid=sid, room=customer_notification_group(org_id))

    async def _join_conversation(self, conversation_id: int, sid: int):
        redis = await get_redis()
        await redis.sadd(f"ws:conversation_sids:{conversation_id}", sid)
        await redis.set(f"ws:sid_conversation:{sid}", conversation_id)
        self.enter_room(sid=sid, room=conversation_group(conversation_id))

    async def _leave_conversation(self, conversation_id: int, sid: int):
        self.leave_room(sid=sid, room=conversation_group(conversation_id))
        # await redis.srem(f'ws:conversation_sids:{conversation_id}', sid)
        # await redis.delete(f"ws:sid_conversation:{sid}")

    async def _leave_user_group(self, org_id: int, sid: int):
        self.leave_room(sid=sid, room=user_notification_group(org_id))

    async def _leave_customer_group(self, org_id: int, sid: int):
        self.leave_room(sid=sid, room=customer_notification_group(org_id))

    async def on_connect(self, sid, environ, auth):
        print(f"🔌Customer Socket connection attempt: {sid}")
        # print(f"🔑 Auth data: {auth}")

        if not auth:
            print("No auth data provided")
            return False

        redis = await get_redis()

        # Handle customer connection (without token)
        customer_id = auth.get("customer_id")
        conversation_id = auth.get("conversation_id")
        organization_id = auth.get("organization_id")

        if not conversation_id or not customer_id:
            print(
                f"❌ Missing customer connection data: customer_id={customer_id}, conversation_id={conversation_id}"
            )
            return False

        # For customer connections, we'll use organization_id = 1 as default if not provided
        if not organization_id:
            organization_id = 1
            print(f"Using default organization_id: {organization_id}")

        await redis.sadd(
            f"ws:{organization_id}:conversation_sids:{conversation_id}", sid
        )

        await redis.set(f"ws:{organization_id}:sid_conversation:{sid}", conversation_id)

        # Maintain conversation membership for cross-instance message fanout
        await redis.sadd(f"{REDIS_ROOM_KEY}{conversation_id}", sid)
        await redis.set(f"{REDIS_SID_KEY}{sid}", conversation_id)

        # notify users in the same workspace that a customer has connected
        await self._notify_to_users(organization_id)
        await self._join_org_customer_group(organization_id, sid)

        # notify users with a specific customer landing event
        channel = f"ws:{organization_id}:user_notification"

        print(f"✅ Published customer_land event to {channel}")

        return True

    async def on_join_conversation(self, sid, data):
        conversation_id = data.get("conversation_id")
        if not conversation_id:
            return
        await self._join_conversation(conversation_id, sid)

    async def on_leave_conversation(self, sid, data):
        conversation_id = data.get("conversation_id")
        if not conversation_id:
            return False
        await self._leave_conversation(conversation_id, sid)

    async def on_message(self, sid, data):
        print(f"on message {data} and sid {sid} and organization")

        conversation_id = data.get("conversation_id")
        organization_id = data.get("organization_id")

        if not conversation_id:
            return

        try:

            # channel_name = user_notification_group(organization_id)
            channel_name = f"user-message-notification"
            event = self.message_notification

            redis = await get_redis()
            sids = await redis.smembers(f"ws:user_conversation_sids:{conversation_id}")
            print(f"sids {sids}")
            if sids:
                event = self.receive_message
                channel_name = user_conversation_group(conversationId=conversation_id)

            print(f"event {event} and channel {channel_name}")

            await redis_publish(
                channel=channel_name,
                message=json.dumps(
                    {
                        "event": event,
                        "sid": sid,
                        "message": data.get("message"),
                        "uuid": data.get("uuid"),
                        "status": data.get(
                            "status", "SENT"
                        ),  # delivered, SENT and seen
                        "user_id": data.get("user_id"),
                        "files": data.get("files", []),
                        "organization_id": organization_id,
                        "mode": "message",
                        "conversation_id": conversation_id,
                    }
                ),
            )
        except Exception as e:
            print(f"Error publishing message to Redis: {e}")

        # await save_message_db(
        #     conversation_id=int(conversation_id), data=data, user_id=data.get("user_id")
        # )

    async def on_message_seen(self, sid, data):
        redis = await get_redis()
        conversation_id = await redis.get(f"{REDIS_SID_KEY}{sid}")
        if not conversation_id:
            return False

        await redis_publish(
            channel=get_room_channel(conversation_id),
            message=json.dumps(
                {"event": self.message_seen, "sid": sid, "uuid": data.get("uuid")}
            ),
        )

    async def on_typing(self, sid, data):
        redis = await get_redis()
        conversation_id = data.get("conversation_id")
        if not conversation_id:
            return

        await redis_publish(
            channel=get_room_channel(conversation_id),
            message=json.dumps(
                {
                    "event": self.receive_typing,
                    "sid": sid,
                    "message": data.get("message", ""),
                    "mode": data.get("mode", "typing"),
                    "organization_id": data.get("organization_id"),
                }
            ),
        )

    async def on_stop_typing(self, sid, data):
        print(f"on stop typing  sid {sid} and {data}")
        conversation_id = data.get("conversation_id")
        if not conversation_id:
            return

        await redis_publish(
            channel=get_room_channel(conversation_id),
            message=json.dumps(
                {"event": self.stop_typing, "sid": sid, "mode": "stop-typing"}
            ),
        )

    async def on_disconnect(self, sid, auth):
        customer_id = auth.get("customer_id")
        conversation_id = auth.get("conversation_id")
        organization_id = auth.get("organization_id")
        user_id = auth.get("user_id")
        redis = await get_redis()
        if customer_id:
            await redis.srem(
                f"ws:{organization_id}:conversation_sids:{conversation_id}", sid
            )
            await redis.delete(f"ws:{organization_id}:sid_conversation:{sid}")
            await self._leave_customer_group(organization_id, sid)
        if user_id:
            await redis.srem(f"ws:{organization_id}:user_sids:{user_id}", sid)
            await redis.delete(f"ws:{organization_id}:sid_user:{sid}")
            await self._leave_user_group(organization_id, sid)

        redis = await get_redis()
        conversation_id = await redis.get(f"{REDIS_SID_KEY}{sid}")
        if conversation_id:
            await redis.srem(f"{REDIS_ROOM_KEY}{conversation_id}", sid)
            await redis.delete(f"{REDIS_SID_KEY}{sid}")
            print(f"❌ Disconnected {sid} from conversation {conversation_id}")
