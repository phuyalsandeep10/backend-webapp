from fastapi import APIRouter, status, Depends, HTTPException
from src.common.dependencies import get_current_user
from src.models import Conversation, Customer, Message


router = APIRouter()


@router.get("")
async def get_conversations(user=Depends(get_current_user)):
    organizationId = user.attributes.get("organization_id")
    return await Conversation.filter(where={"organization_id": organizationId})


@router.get("/{conversation_id}")
async def conversation_detail(conversation_id: int, user=Depends(get_current_user)):
    organizationId = user.attributes.get("organization_id")
    record = await Conversation.get(conversation_id)

    if not record or record.organization_id != organizationId:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation Not found"
        )

    customer = await Customer.get(record.customer_id)
    

    return {"conversation": record, "customer": customer}


@router.get("/{conversation_id}/customer_messages")
async def customer_messages(conversation_id: int, limit: int = 20):
    messages = await Message.filter(
        where={"conversation_id": conversation_id}, limit=limit
    )
    return {"messages": messages}


@router.get("/{conversation_id}/messages")
async def user_messages(
    conversation_id: int, limit: int = 20, user=Depends(get_current_user)
):
    messages = await Message.filter(
        where={"conversation_id": conversation_id}, limit=limit
    )

    return {"messages": messages}
