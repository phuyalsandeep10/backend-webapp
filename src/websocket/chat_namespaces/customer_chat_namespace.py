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
from .base_chat_namespace import BaseChatNamespace


REDIS_URL = settings.REDIS_URL


# Redis keys
REDIS_ROOM_KEY = "chat:room:"  # chat:room:{conversation_id} -> set of sids
REDIS_SID_KEY = "chat:sid:"  # chat:sid:{sid} -> conversation_id


# Redis helper


class CustomerChatNamespace(BaseChatNamespace):
    

    def __init__(self):
        super().__init__("/chat")

 

    async def _notify_to_users(self, org_id: int):
        print(f"notify users in the same workspace that a customer has connected")
        await self.redis_publish(
            channel=f"ws:{org_id}:user_notification",
            message=json.dumps(
                {
                    "event": self.customer_land,
                    "mode": "online",
                    "organization_id": org_id,
                }
            ),
        )



   


    async def on_connect(self, sid, environ, auth:dict):
        print(f"🔌Customer Socket connection attempt: {sid}")
        # print(f"🔑 Auth data: {auth}")

        if not auth:
            print("No auth data provided")
            return False

        # Handle customer connection (without token)
        customer_id = auth.get("customer_id")
        conversation_id = auth.get("conversation_id")
        organization_id = auth.get("organization_id")



        if not conversation_id or not customer_id or not organization_id:
            print(
                f"❌ Missing customer connection data: customer_id={customer_id}, conversation_id={conversation_id}"
            )
            return False
        
        await self.join_conversation(conversation_id, sid)
    

        # notify users in the same workspace that a customer has connected
        await self._notify_to_users(organization_id)

        # notify users with a specific customer landing event
        channel = f"ws:{organization_id}:user_notification"

        print(f"✅ Published customer_land event to {channel}")

        return True

   

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

            sids = await self.get_redis().smembers(f"ws:user_conversation_sids:{conversation_id}")
            print(f"sids {sids}")
            if sids:
                event = self.receive_message
                channel_name = user_conversation_group(conversationId=conversation_id)

            print(f"event {event} and channel {channel_name}")

            await self.redis_publish(
                channel=channel_name,
                message={
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
                
            )
        except Exception as e:
            print(f"Error publishing message to Redis: {e}")

        # await save_message_db(
        #     conversation_id=int(conversation_id), data=data, user_id=data.get("user_id")
        # )

    
    
