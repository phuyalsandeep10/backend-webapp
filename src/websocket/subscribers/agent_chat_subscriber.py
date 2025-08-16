from src.websocket.chat_utils import ChatUtils
from ..chat_namespace_constants import AGENT_CHAT_NAMESPACE
import socketio
from .chat_subscriber import ChatSubscriber
from ..channel_names import (
    AGENT_MESSAGE_CHANNEL,
    AGENT_NOTIFICATION_CHANNEL,
    AGENT_TYPING_CHANNEL,
    AGENT_TYPING_STOP_CHANNEL,
    AGENT_MESSAGE_SEEN_CHANNEL,
)


class AgentChatSubscriber(ChatSubscriber):
    namespace = AGENT_CHAT_NAMESPACE


    def __init__(self,sio:socketio.AsyncServer,payload:dict):
        super().__init__(sio,payload=payload,namespace=self.namespace)
     

    
    async def user_notification(self):
        room_name = ChatUtils.user_notification_group(org_id=self.payload.get("organization_id"))
        await self.emit(room_name)
    
    async def user_message(self):
        room_name = ChatUtils.conversation_group(self.payload.get("conversation_id"))
        await self.emit(room_name)
    
    async def user_typing(self):
        room_name = ChatUtils.conversation_group(self.payload.get("conversation_id"))
        await self.emit(room_name)
    
    async def user_typing_stop(self):
        room_name = ChatUtils.conversation_group(self.payload.get("conversation_id"))
        await self.emit(room_name)
    
    async def user_message_seen(self):
        room_name = ChatUtils.conversation_group(self.payload.get("conversation_id"))
        await self.emit(room_name)
 


async def agent_chat_subscriber(sio:socketio.AsyncServer,channel:str,payload:dict):

    subscriber = AgentChatSubscriber(sio,payload)
    # handle chat events
    if channel == AGENT_NOTIFICATION_CHANNEL:
        await subscriber.user_notification()
    
    elif channel == AGENT_MESSAGE_CHANNEL:
        await subscriber.user_message()
    
    elif channel == AGENT_TYPING_CHANNEL:
        await subscriber.user_typing()
    
    elif channel == AGENT_TYPING_STOP_CHANNEL:
        await subscriber.user_typing_stop()
    
    elif channel == AGENT_MESSAGE_SEEN_CHANNEL:
        await subscriber.user_message_seen()
    
    
    
            
            

