from typing import Annotated, Optional

from fastapi import APIRouter
from typing_extensions import Doc

from src.modules.ticket.schemas import (
    CreateTicketMessageSchema,
    EditTicketMessageSchema,
)
from src.utils.response import CustomResponseSchema

from ..services.converstaion import ticket_conversation_service

router = APIRouter(prefix="/conversation")


@router.post(
    "/", summary="Send ticket concern messages", response_model=CustomResponseSchema
)
async def save_message(payload: CreateTicketMessageSchema):
    """
    Save and sends email to the customer
    """
    return await ticket_conversation_service.send_message(payload)


@router.get(
    "/{ticket_id:int}",
    summary="Fetch ticket messages of the particualr converstation id",
    response_model=CustomResponseSchema,
)
async def list_ticket_messages(
    ticket_id: int,
    limit: Annotated[int, Doc("Maximum number of data to send")],
    before: Annotated[
        Optional[int], Doc("Lists the messages before the provided message id")
    ] = None,
):
    return await ticket_conversation_service.list_messages(
        ticket_id=ticket_id, limit=limit, before=before
    )


@router.patch(
    "/{message_id:int}",
    summary="Edit message_id content",
    response_model=CustomResponseSchema,
)
async def edit_ticket_messages(message_id: int, payload: EditTicketMessageSchema):
    return await ticket_conversation_service.edit_message(
        message_id=message_id, payload=payload
    )
