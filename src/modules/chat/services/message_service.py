from src.services.redis_service import RedisService
from src.models import Conversation, Message, MessageAttachment
from src.utils.response import CustomResponse as cr
from src.websocket.channel_names import MESSAGE_CHANNEL
from ..schema import MessageSchema
from typing import Optional
from sqlalchemy.orm import selectinload


class MessageService:
    def __init__(
        self, organization_id, payload: Optional[MessageSchema] = None, user_id: Optional[int] = None
    ):
        self.organization_id = organization_id
        self.payload = payload
        self.user_id = user_id

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

        await RedisService.redis_publish(
            channel=MESSAGE_CHANNEL, message={"event": "receive-message", **data}
        )

        return new_message

    # edit message service
    async def edit(self, message_id: int):
        record = await Message.find_one({"id": message_id})

        if not record:
            return cr.error(message="Message Not found")

        updated_data = {**self.payload.dict()}
        await Message.update(message_id, **updated_data)

        await RedisService.redis_publish(
            channel=MESSAGE_CHANNEL, message={"event": "edit-message", **updated_data}
        )

        return record
    
    async def get_messages(self,conversationId:int):
   
        messages = await Message.filter(where={"conversation_id": conversationId},options=[selectinload(Message.reply_to)])
        records = []
       
        for msg in messages:
            data = msg.to_json()
            reply_to = {}
            if msg.reply_to:
                reply_to = {
                    "id": msg.reply_to.id,
                    "content": msg.reply_to.content,
                    "user_id": msg.reply_to.user_id,
                }
            records.append({**data, "reply_to": reply_to})
        return records
