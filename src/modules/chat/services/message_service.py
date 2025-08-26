from src.services.redis_service import RedisService
from src.models import Conversation, Message, MessageAttachment
from src.utils.response import CustomResponse as cr
from src.websocket.channel_names import MESSAGE_CHANNEL
from ..schema import MessageSchema
from typing import Optional
from sqlalchemy.orm import selectinload
from src.services.redis_service import RedisService
from src.websocket.chat_utils import ChatUtils


class MessageService:
    def __init__(
        self, organization_id, payload: Optional[MessageSchema] = None, user_id: Optional[int] = None
    ):
        self.organization_id = organization_id
        self.payload = payload
        self.user_id = user_id
        


    async def get_user_sid(self, userId: int):
        if not userId:
            return None
            
        redis = await RedisService.get_redis()
        result = await redis.get(ChatUtils._user_add_sid(userId))
        if not result:
            return None
        return result.decode('utf-8')

    def make_msg_payload(self,record): 
        payload = record.to_json()
        
        if record.user:
            payload["user"] = {
                "id": record.user.id,
                "name": record.user.name,
                "email": record.user.email,
                "image": record.user.image
            }
        if record.reply_to:
            payload["reply_to"] = {
                "id": record.reply_to.id,
                "content": record.reply_to.content,
                "user_id": record.reply_to.user_id,
            }
        
        
        return payload
    

    

    async def get_message_payload(self, messageId:int):

        record = await Message.find_one({
            "id": messageId,
        }, options=[selectinload(Message.reply_to), selectinload(Message.user)])
        
        # Only get user SID if user_id is present (agent messages)
        userSid = None
        if self.user_id:
            userSid = await self.get_user_sid(self.user_id)
        
        print(f"user sid {userSid}")

        payload = self.make_msg_payload(record)
        print(f"payload {payload}")
        payload["sid"] = userSid
        payload["event"] = "receive-message"
        
        return payload

    
    async def create(self, conversation_id: int):
        record = await Conversation.find_one(
            {"id": conversation_id, "organization_id": self.organization_id}
        )

        if not record:
            return cr.error(message="Conversation Not found")
        
        
        data = {
            **self.payload.dict(),
            "user_id": self.user_id,
            "conversation_id": conversation_id,
        }
        
        new_message = await Message.create(**data)

        for file in self.payload.attachments:
            await MessageAttachment.create(message_id=new_message.id, **file.dict())
        

        payload = await self.get_message_payload(new_message.id)
        payload['customer_id'] = record.customer_id
        payload['organization_id'] = self.organization_id
        
        # Set is_customer flag based on whether user_id is present
        # If user_id is None, it's a customer message
        payload['is_customer'] = self.user_id is None


        await RedisService.redis_publish(
            channel=MESSAGE_CHANNEL, message=payload
        )
        

        return payload

    # edit message service
    async def edit(self, message_id: int):
        record = await Message.find_one({"id": message_id})

        if not record:
            return cr.error(message="Message Not found")

        updated_data = {**self.payload.dict()}
        await Message.update(message_id, **updated_data)

        payload = await self.get_message_payload(message_id)
        
        # Set is_customer flag based on whether user_id is present
        payload['is_customer'] = self.user_id is None

        await RedisService.redis_publish(
            channel=MESSAGE_CHANNEL, message={"event": "edit-message", **payload}
        )



        return record
    

    async def get_messages(self,conversationId:int):
   
        messages = await Message.filter(where={"conversation_id": conversationId},options=[selectinload(Message.reply_to), selectinload(Message.user)])
        records = []
        for msg in messages:
            payload = self.make_msg_payload(msg)
            records.append(payload)
        
        return records
