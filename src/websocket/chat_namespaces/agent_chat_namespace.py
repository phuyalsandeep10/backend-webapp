import json

import socketio

from src.models import Message, MessageAttachment, Conversation
from src.common.dependencies import get_user_by_token

# from src.config.broadcast import broadcast  # Replaced with direct Redis pub/sub

from src.config.settings import settings
from ..chat_utils import (
    get_room_channel,
    user_notification_group,
    conversation_group,
    user_conversation_group,
)
from src.config.redis.redis_listener import get_redis
from ..chat_redis import redis_publish
from .base_chat_namespace import BaseChatNamespace
from .chat_namespace_constants import AGENT_CHAT_NAMESPACE

REDIS_URL = settings.REDIS_URL

chat_namespace = "/chat"

# Redis keys



# Redis helper


class AgentChatNamespace(BaseChatNamespace):

    namespace = AGENT_CHAT_NAMESPACE
    
    def __init__(self):
        super().__init__(self.namespace)
    
    async def _notify_to_customers(self, org_id: int):
        await self.redis_publish(
            channel=f"ws:{org_id}:customer_notification",
            message={"event": self.chat_online, "mode": "online", "organization_id": org_id}
        )

    async def _join_org_user_group(self, org_id: int, sid: int):
        await self.enter_room(sid=sid, room=user_notification_group(org_id))


    async def on_connect(self, sid, environ, auth):
        print(f"🔌Agent Socket connection attempt: {sid}")
        if not auth:
            print("No auth data provided")
            return False

        token = auth.get("token")

        user = await get_user_by_token(token)

        if not user:
            print("Invalid token provided")
            return False

        organization_id = user.attributes.get("organization_id")

        if not organization_id:
            print("User has no organization_id")
            return False

        await self._join_org_user_group(organization_id, sid)
        await self._notify_to_customers(organization_id)


        print(f"User {user.id} connected with sid {sid} in workspace {organization_id}")
        return True

    async def on_join_conversation(self, sid, data:dict):
        print(f"agent join conversation with {sid} and data {data}")
        conversation_id = data.get("conversation_id")
        if not conversation_id:
            return False
        await self.join_conversation(conversation_id, sid)

    async def on_leave_conversation(self, sid, data:dict):
        conversation_id = data.get("conversation_id")
        if not conversation_id:
            return False
        await self.leave_conversation(conversation_id, sid)

    async def on_message(self, sid, data:dict):
        print(f"on message {data} and sid {sid}")

        conversation_id = data.get("conversation_id")
        organization_id = data.get("organization_id")

        if not conversation_id:
            return False

        try:
            channel_name = get_room_channel(conversation_id)
            if not data.get("user_id"):
                redis = await self.get_redis()
                sids = await redis.smembers(
                    f"ws:{organization_id}:conversation_sids:{conversation_id}"
                )
                print("SIDs in this conversation:", [sid.decode() for sid in sids])

                if not sids:
                    channel_name = user_notification_group(organization_id)
                else:
                    channel_name = conversation_group(conversation_id)
            print(f"message channel {channel_name}")
            await self.redis_publish(
                channel=channel_name,
                message=json.dumps(
                    {
                        "event": self.receive_message,
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
                    }
                ),
            )
        except Exception as e:
            print(f"Error publishing message to Redis: {e}")

    

