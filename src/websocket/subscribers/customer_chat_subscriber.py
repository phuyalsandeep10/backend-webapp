from .chat_subscriber import ChatSubscriber
from ..chat_namespace_constants import AGENT_CHAT_NAMESPACE
from ..chat_utils import ChatUtils
import socketio
from ..channel_names import (
    CUSTOMER_MESSAGE_CHANNEL,
    CUSTOMER_NOTIFICATION_CHANNEL,
    CUSTOMER_TYPING_CHANNEL,
    CUSTOMER_TYPING_STOP_CHANNEL,
    CUSTOMER_MESSAGE_SEEN_CHANNEL,
)

class CustomerChatSubscriber(ChatSubscriber):
    

    def __init__(self,sio:socketio.AsyncServer,payload:dict):
        super().__init__(sio,payload=payload,namespace=self.agent_namespace)
        
    async def agent_notification(self):
        room_name = ChatUtils.user_notification_group(org_id=self.payload.get("organization_id"))
        await self.emit(room_name)
    
    async def customer_message(self):
        room_name = ChatUtils.conversation_group(conversation_id=self.payload.get("conversation_id"))
        await self.emit(room_name)
    
    async def customer_typing(self):
        room_name = ChatUtils.conversation_group(conversation_id=self.payload.get("conversation_id"))
        await self.emit(room_name)
    
    async def customer_typing_stop(self):
        room_name = ChatUtils.conversation_group(conversation_id=self.payload.get("conversation_id"))
        await self.emit(room_name)
    
    async def customer_message_seen(self):
        room_name = ChatUtils.conversation_group(conversation_id=self.payload.get("conversation_id"))
        await self.emit(room_name)
    

async def customer_chat_subscriber(sio:socketio.AsyncServer,channel:str,payload:dict):
    print(f"customer chat subscriber payload {payload} and type {type(payload)}")
    subscriber = CustomerChatSubscriber(sio,payload=payload)
    # handle chat events
    if channel == CUSTOMER_NOTIFICATION_CHANNEL:
        await subscriber.agent_notification()
    
    elif channel == CUSTOMER_MESSAGE_CHANNEL:
        await subscriber.customer_message()
    
    elif channel == CUSTOMER_TYPING_CHANNEL:
        await subscriber.customer_typing()
    
    elif channel == CUSTOMER_TYPING_STOP_CHANNEL:
        await subscriber.customer_typing_stop()
    
    elif channel == CUSTOMER_MESSAGE_SEEN_CHANNEL:
        await subscriber.customer_message_seen()
    