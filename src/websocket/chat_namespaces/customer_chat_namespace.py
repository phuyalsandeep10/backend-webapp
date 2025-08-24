import json



from .base_chat_namespace import BaseChatNamespace
from ..chat_namespace_constants import CUSTOMER_CHAT_NAMESPACE
from ..channel_names import AGENT_NOTIFICATION_CHANNEL



class CustomerChatNamespace(BaseChatNamespace):
    namespace = CUSTOMER_CHAT_NAMESPACE

    def __init__(self):
        super().__init__(self.namespace, is_customer=True)

    async def _notify_to_users(self, org_id: int):
        print("notify users in the same workspace that a customer has connected")
        await self.redis_publish(
            channel=AGENT_NOTIFICATION_CHANNEL,
            message=json.dumps(
                {
                    "event": self.customer_land,
                    "mode": "online",
                    "organization_id": org_id,
                }
            ),
        )

    
       

    async def on_connect(self, sid, environ, auth: dict):
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

        await self.join_group(conversation_id, sid)

        # notify users in the same workspace that a customer has connected
        await self._notify_to_users(organization_id)

        # notify users with a specific customer landing event

        print("✅ Published customer_land event to ")

        return True

    # async def on_message(self, sid, data: dict):
    #     print(f"on message {data} and sid {sid} and organization")

    #     conversation_id = await self._get_conversation_id_from_sid(sid)
    #     print(f"conversation_id {conversation_id}")
    #     organization_id = data.get("organization_id")

    #     if not conversation_id:
    #         print(f"❌ Missing conversation_id: {conversation_id}")
    #         return

    #     try:
    #         # channel_name = user_notification_group(organization_id)

    #         channel_name = AGENT_NOTIFICATION_CHANNEL
    #         event = self.message_notification
    #         # Get all sids for the conversation
    #         sids = await self.get_conversation_sids(conversationId=conversation_id)

    #         print(f"sids {sids}")
    #         if len(sids) > 1:
    #             event = self.receive_message
    #             channel_name = MESSAGE_CHANNEL
    #         payload = {
    #             "event": event,
    #             "sid": sid,
    #             "message": data.get("message"),
    #             "message_id": data.get("message_id"),
    #             "status": data.get("status", "SENT"),  # delivered, SENT and seen
    #             "user_id": data.get("user_id"),
    #             "files": data.get("files", []),
    #             "organization_id": organization_id,
    #             "mode": "message",
    #             "conversation_id": conversation_id,
    #             "is_customer": True,
    #             "customer_id": data.get("customer_id"),
    #         }

    #         await self.redis_publish(channel=channel_name, message=payload)
    #         await self.save_message_db(conversation_id, payload)

    #         return True
    #     except Exception as e:
    #         print(f"Error publishing message to Redis: {e}")
    #         return False

    #     # await save_message_db(
    #     #     conversation_id=int(conversation_id), data=data, user_id=data.get("user_id")
    #     # )
