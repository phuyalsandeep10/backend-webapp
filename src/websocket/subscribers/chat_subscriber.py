import socketio
from ..chat_namespace_constants import AGENT_CHAT_NAMESPACE, CUSTOMER_CHAT_NAMESPACE
from ..chat_utils import ChatUtils
from ..channel_names import (
    AGENT_NOTIFICATION_CHANNEL,
    MESSAGE_CHANNEL,
    TYPING_CHANNEL,
    TYPING_STOP_CHANNEL,
    MESSAGE_SEEN_CHANNEL,
    AGENT_JOIN_CONVERSATION_CHANNEL
)



class ChatSubscriber:
    agent_namespace = AGENT_CHAT_NAMESPACE
    customer_namespace = CUSTOMER_CHAT_NAMESPACE
    

    def __init__(
        self, sio: socketio.AsyncServer, namespace: str = None, payload: dict = {}
    ):
        # print(f"chat subscriber payload {payload} and type {type(payload)}")
        self.sio = sio
        self.payload = payload
        self.event = payload.get("event")
        self.namespace = namespace

    async def emit(self, room: str, namespace: str = None, sid: str = None):
        namespace = namespace if namespace else self.namespace
        print(f"emit to room {room} ")
        print(f"emit to namespace {namespace}")
        print(f"emit to event {self.event}")
        print(f"skip to sid {sid}")
        
        # print(f"emit to payload {self.payload}")
        
        try:
            result = await self.sio.emit(
                event=self.event,
                room=room,
                data=self.payload,
                namespace=namespace,
                skip_sid=sid,
            )
            print(f"✅ Emitted event '{self.event}' to room '{room}' in namespace '{namespace}'")
            return result
        except Exception as e:
            print(f"❌ Emit failed: {e}")
            return None

    async def agent_notification(self):
        print("📢 Agent notification broadcast")
        room_name = ChatUtils.user_notification_group(
            org_id=self.payload.get("organization_id")
        )
        await self.emit(room_name, namespace=self.agent_namespace)

    async def customer_notification(self):
        print("📢 Customer notification broadcast")
        room_name = ChatUtils.customer_notification_group(
            org_id=self.payload.get("organization_id")
        )
        await self.emit(room_name, namespace=self.customer_namespace)

    async def agent_message_broadcast(self):
        print("agent message broadcast")
        room_name = ChatUtils.conversation_group(
            conversation_id=self.payload.get("conversation_id")
        )

        await self.emit(
            room_name, namespace=self.agent_namespace, sid=self.payload.get("sid")
        )

    async def customer_message_broadcast(self):
        print("customer message broadcast")
        room_name = ChatUtils.conversation_group(
            conversation_id=self.payload.get("conversation_id")
        )
        sids = self.sio.manager.rooms.get(self.customer_namespace, {}).get(room_name, set())
        print(f"sids in room {room_name}: {sids}")
        
        # Skip the sender if sid is provided
        skip_sid = self.payload.get("sid")
        await self.emit(room_name, namespace=self.customer_namespace, sid=skip_sid)

    async def broadcast_conversation(self):
        is_customer = self.payload.get("is_customer")
        print(f"Broadcasting conversation - is_customer: {is_customer}")
        
        if is_customer:
            print("Customer message - broadcasting to agents only")
            return await self.agent_message_broadcast()

        print("Agent message - broadcasting to both customers and agents")
        await self.customer_message_broadcast()
        await self.agent_message_broadcast()
    
    async def agent_join_conversation(self):
        print("👥 Agent join conversation broadcast")
        await self.agent_message_broadcast()

    async def message(self):
        print(f"📨 Processing message event: {self.event}")
        print(f"📨 Message payload: {self.payload}")
        await self.broadcast_conversation()

    async def typing(self):
        print("⌨️ Processing typing event")
        await self.broadcast_conversation()

    async def stop_typing(self):
        print("⏹️ Processing stop typing event")
        await self.broadcast_conversation()

    async def message_seen(self):
        room_name = ChatUtils.conversation_group(
            conversation_id=self.payload.get("conversation_id")
        )
        if self.payload.get("is_customer"):
            await self.emit(room_name, namespace=self.customer_namespace, sid=self.payload.get("sid"))
        else:
            await self.emit(room_name, namespace=self.agent_namespace, sid=self.payload.get("sid"))
        


async def chat_subscriber(sio: socketio.AsyncServer, channel: str, payload: dict):
    print(f"🔔 Chat subscriber called for channel: {channel}")
    print(f"🔔 Payload: {payload}")
    
    subscriber = ChatSubscriber(sio, payload=payload)
    
    # handle chat events
    if channel == AGENT_NOTIFICATION_CHANNEL:
        print("📢 Processing agent notification")
        await subscriber.agent_notification()

    elif channel == AGENT_JOIN_CONVERSATION_CHANNEL:
        print("👥 Processing agent join conversation")
        await subscriber.agent_join_conversation()

    elif channel == MESSAGE_CHANNEL:
        print("💬 Processing message")
        await subscriber.message()

    elif channel == TYPING_CHANNEL:
        print("⌨️ Processing typing")
        await subscriber.typing()

    elif channel == TYPING_STOP_CHANNEL:
        print("⏹️ Processing stop typing")
        await subscriber.stop_typing()

    elif channel == MESSAGE_SEEN_CHANNEL:
        print("👁️ Processing message seen")
        await subscriber.message_seen()
    
    else:
        print(f"⚠️ Unknown channel: {channel}")
