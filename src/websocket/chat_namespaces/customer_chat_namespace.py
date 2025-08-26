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
        organization_id = auth.get("organization_id")

        if not customer_id or not organization_id:
            print(
                f"❌ Missing customer connection data: customer_id={customer_id}"
            )
            return False
        redis = await self.get_redis()

        await redis.set(f"customer_id:{customer_id}",sid)
 
        

        # notify users in the same workspace that a customer has connected
        await self._notify_to_users(organization_id)

        # notify users with a specific customer landing event

        print("✅ Published customer_land event to ")

        return True

