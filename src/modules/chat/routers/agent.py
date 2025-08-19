from fastapi import APIRouter,status,Depends, HTTPException
from src.common.dependencies import get_current_user
from src.utils.response import CustomResponse as cr
from src.models import Conversation, Customer, Message, MessageAttachment
from src.common.context import UserContext, TenantContext
from ..schema import ConversationSchema,CustomerSchema
from sqlalchemy.orm import selectinload

router = APIRouter()


@router.get("/conversations")
async def get_conversations():
    organizationId = TenantContext.get()
   
    conversations = await Conversation.filter({"organization_id": organizationId},
    related_items=[selectinload(Conversation.customer)])
    records = [
                c.to_json(
                    schema=ConversationSchema,
                    include_relationships=True,
                    related_schemas={"customer": CustomerSchema},
                )
                for c in conversations
            ]





    print(f"Fetched conversations: {conversations}")


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