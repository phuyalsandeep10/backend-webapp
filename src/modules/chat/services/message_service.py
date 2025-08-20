
from src.services.redis_service import RedisService
from src.models import Conversation, Message
from src.utils.response import CustomResponse as cr
from src.websocket.channel_names import MESSAGE_CHANNEL
from ..schema import MessageSchema
from typing import Optional

class MessageService:
    def __init__(self,organization_id,payload:MessageSchema,user_id:Optional[int]=None):
        self.organization_id = organization_id
        self.payload = payload
        self.user_id = user_id
    

    async def create_conversation_message(self,conversation_id: int):
        record = await Conversation.find_one({
            "id": conversation_id,
            "organization_id": self.organization_id
        })
        
        if not record:
            return cr.error(message='Conversation Not found')
        data = {**self.payload.dict(),"user_id":self.user_id,"conversation_id":conversation_id}

        new_message = await Message.create(**data)
        await RedisService.redis_publish(channel=MESSAGE_CHANNEL, message={"event":"receive-message",**data})

        return cr.success(data=new_message.to_json())