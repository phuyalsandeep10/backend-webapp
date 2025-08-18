import json

from src.common.dependencies import get_user_by_token

from src.websocket.channel_names import AGENT_NOTIFICATION_CHANNEL, CUSTOMER_NOTIFICATION_CHANNEL, MESSAGE_CHANNEL
from ..chat_utils import (
    ChatUtils
)
from .base_chat_namespace import BaseChatNamespace
from ..chat_namespace_constants import AGENT_CHAT_NAMESPACE





# Redis keys



# Redis helper


class AgentChatNamespace(BaseChatNamespace):

    namespace = AGENT_CHAT_NAMESPACE
    
    def __init__(self):
        super().__init__(self.namespace)
    
    async def _notify_to_customers(self, org_id: int):
        await self.redis_publish(
            channel=CUSTOMER_NOTIFICATION_CHANNEL,
            message={"event": self.chat_online, "mode": "online", "organization_id": org_id}
        )

    async def _join_org_user_group(self, org_id: int, sid: int):
        await self.enter_room(sid=sid, room=ChatUtils.user_notification_group(org_id))


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


        print(f"\n User {user.id} connected with sid {sid} in workspace {organization_id}")
        return True

    async def on_join_conversation(self, sid, data:dict):
        print(f"agent join conversation with {sid} and data {data}")
        conversation_id = data.get("conversation_id")
        print(f"conversation_id {conversation_id}")
        if not conversation_id:
            return False
        await self.join_conversation(conversation_id, sid)
        return True

    async def on_leave_conversation(self, sid, data:dict):
        conversation_id = data.get("conversation_id")
        if not conversation_id:
            return False
        await self.leave_conversation(conversation_id, sid)
        return True

    async def on_message(self, sid, data:dict):
        print(f"on message {data} and sid {sid}")

        conversation_id = data.get("conversation_id")
        organization_id = data.get("organization_id")

        if not conversation_id:
            return False
        try:
            channel_name = MESSAGE_CHANNEL
            payload = {
                        "event": self.receive_message,
                        "sid": sid,
                        "message": data.get("message"),
                        "message_id": data.get("message_id"),
                        "status": data.get(
                            "status", "SENT"
                        ),  # delivered, SENT and seen
                        "user_id": data.get("user_id"),
                        "files": data.get("files", []),
                        "organization_id": organization_id,
                        "mode": "message",
                        "conversation_id": conversation_id,
                        "is_customer": False,
                        "sid": sid,
                    }
            await self.redis_publish(
                channel=channel_name,
                message=payload
            )
            await self.save_message_db(conversation_id, payload)
            return True
        except Exception as e:
            print(f"Error publishing message to Redis: {e}")
            return False

    

