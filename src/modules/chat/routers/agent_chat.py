from fastapi import APIRouter
from src.utils.response import CustomResponse as cr
from src.models import Conversation, Customer, Message
from src.common.context import UserContext, TenantContext
from ..schema import MessageSchema, EditMessageSchema

from ..services.message_service import MessageService
from ..models.conversation import get_conversation_list


router = APIRouter()


@router.get("/conversations")
async def get_conversations():
    organizationId = TenantContext.get()

    records = await get_conversation_list(organizationId)

    return cr.success(data=records)


@router.get("/conversations/{conversation_id}")
async def conversation_detail(conversation_id: int):
    organizationId = TenantContext.get()

    record = await Conversation.find_one(
        {"id": conversation_id, "organization_id": organizationId}
    )

    if not record:
        return cr.error(message="Conversation Not found")

    customer = await Customer.get(record.customer_id)

    return cr.success(
        data={"conversation": record.to_json(), "customer": customer.to_json()}
    )


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: int):
    organizationId = TenantContext.get()

    record = await Conversation.find_one(
        {"id": conversation_id, "organization_id": organizationId}
    )

    if not record:
        return cr.error(message="Conversation Not found")

    messages = await Message.filter({"conversation_id": conversation_id})

    return cr.success(data={"messages": [msg.to_json() for msg in messages]})


@router.post("/conversations/{conversation_id}/messages")
async def create_conversation_message(conversation_id: int, payload: MessageSchema):
    organizationId = TenantContext.get()
    userId = UserContext.get()

    del payload.customer_id

    service = MessageService(organizationId, payload, userId)
    record = await service.create(conversation_id)

    return cr.success(data=record.to_json())


# edit the message
@router.put("/messages/{message_id}")
async def edit_message(message_id: int, payload: EditMessageSchema):
    organizationId = TenantContext.get()
    print(f"organizationId {organizationId}")

    userId = UserContext.get()

    service = MessageService(organizationId, payload, userId)
    record = await service.edit(message_id)

    return cr.success(data=record.to_json())


# resolved conversations
@router.put("/conversations/{conversation_id}/resolved")
async def resolved_conversation(conversation_id: int):
    organizationId = TenantContext.get()

    # Find the conversation
    record = await Conversation.find_one(
        {"id": conversation_id, "organization_id": organizationId}
    )

    if not record:
        return cr.error(message="Failed to resolve conversation")

    # update the conversation
    record = await Conversation.update(conversation_id, is_resolved=True)

    return cr.success(data=record.to_json())
