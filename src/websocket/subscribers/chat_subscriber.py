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
        
        # print(f"emit to payload {self.payload}")

        return await self.sio.emit(
            event=self.event,
            room=room,
            data=self.payload,
            namespace=namespace,
            skip_sid=sid,
        )

    async def agent_notification(self):
        room_name = ChatUtils.user_notification_group(
            org_id=self.payload.get("organization_id")
        )
        await self.emit(room_name, namespace=self.agent_namespace)

    async def customer_notification(self):
        room_name = ChatUtils.customer_notification_group(
            org_id=self.payload.get("organization_id")
        )
        await self.emit(room_name)

    async def agent_message_broadcast(self):
        
        room_name = ChatUtils.conversation_group(
            conversation_id=self.payload.get("conversation_id")
        )

        await self.emit(
            room_name, namespace=self.agent_namespace, sid=self.payload.get("sid")
        )

    async def customer_message_broadcast(self):
        room_name = ChatUtils.conversation_group(
            conversation_id=self.payload.get("conversation_id")
        )
        await self.emit(room_name, namespace=self.customer_namespace)

    async def broadcast_conversation(self):
        is_customer = self.payload.get("is_customer")
        if is_customer:
            return await self.agent_message_broadcast()

        await self.customer_message_broadcast()
        await self.agent_message_broadcast()
    
    async def agent_join_conversation(self):
        await self.agent_message_broadcast()

    async def message(self):
        await self.broadcast_conversation()

    async def typing(self):
        await self.broadcast_conversation()

    async def stop_typing(self):
        await self.broadcast_conversation()

    async def message_seen(self):
        room_name = ChatUtils.conversation_group(
            conversation_id=self.payload.get("conversation_id")
        )
        if self.payload.get("is_customer"):
            await self.emit(room=room_name, namespace=self.customer_namespace,sid=self.payload.get("sid"))
        else:
            await self.emit(room=room_name, namespace=self.agent_namespace,sid=self.payload.get("sid"))
        


async def chat_subscriber(sio: socketio.AsyncServer, channel: str, payload: dict):
    # print(f"chat subscriber payload {payload} and type {type(payload)}")
    subscriber = ChatSubscriber(sio, payload=payload)
    # handle chat events
    if channel == AGENT_NOTIFICATION_CHANNEL:
        await subscriber.agent_notification()

    elif channel == AGENT_JOIN_CONVERSATION_CHANNEL:
        await subscriber.agent_join_conversation()

    elif channel == MESSAGE_CHANNEL:
        await subscriber.message()

    elif channel == TYPING_CHANNEL:
        await subscriber.typing()

    elif channel == TYPING_STOP_CHANNEL:
        await subscriber.stop_typing()

    elif channel == MESSAGE_SEEN_CHANNEL:
        await subscriber.message_seen()
