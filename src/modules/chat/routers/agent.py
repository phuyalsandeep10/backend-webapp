from fastapi import APIRouter,status,Depends, HTTPException
from src.common.dependencies import get_current_user
from src.utils.response import CustomResponse as cr
from src.models import Conversation, Customer, Message, MessageAttachment
from src.common.context import UserContext, TenantContext
from ..schema import ConversationSchema,CustomerSchema, MessageSchema

from sqlalchemy.orm import selectinload
from ..models.conversation import get_conversation_list

from src.config.redis.redis_listener import get_redis
import json

router = APIRouter()


@router.get("/conversations")
async def get_conversations():
    organizationId = TenantContext.get()

    records = await get_conversation_list(organizationId)

    return cr.success(data=records)

@router.get("/conversations/{conversation_id}")
async def conversation_detail(conversation_id: int):
    organizationId = TenantContext.get()

    record = await Conversation.find_one({
        "id": conversation_id,
        "organization_id": organizationId
    })

    if not record:
        return cr.error(message='Conversation Not found')

    customer = await Customer.get(record.customer_id)

    return cr.success(data={"conversation": record.to_json(), "customer": customer.to_json()})

@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: int):
    organizationId = TenantContext.get()

    record = await Conversation.find_one({
        "id": conversation_id,
        "organization_id": organizationId
    })

    if not record:
        return cr.error(message='Conversation Not found')

    messages = await Message.filter({"conversation_id": conversation_id})

    
    return cr.success(data={"messages": [msg.to_json() for msg in messages]})

@router.post('/conversations/{conversation_id}/messages')
async def create_conversation_message(conversation_id: int, message: MessageSchema):
    organizationId = TenantContext.get()

    record = await Conversation.find_one({
        "id": conversation_id,
        "organization_id": organizationId
    })


    if not record:
        return cr.error(message='Conversation Not found')
    data = json.dumps({**message.dict(),"event":"receive-message"})

    new_message = await Message.create(**message.dict(), conversation_id=conversation_id)
    await redis_publish(channel=MESSAGE_CHANNEL, message=data)

    return cr.success(data=new_message.to_json())