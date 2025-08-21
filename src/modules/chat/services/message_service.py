from src.services.redis_service import RedisService
from src.models import Conversation, Message, MessageAttachment
from src.utils.response import CustomResponse as cr
from src.websocket.channel_names import MESSAGE_CHANNEL
from ..schema import MessageSchema
from typing import Optional


class MessageService:
    def __init__(
        self, organization_id, payload: MessageSchema, user_id: Optional[int] = None
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

        for file in self.payload.files:
            await MessageAttachment.create(message_id=new_message.id, **file.dict())

        await RedisService.redis_publish(
            channel=MESSAGE_CHANNEL, message={"event": "receive-mesjsage", **data}
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
