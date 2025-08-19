from fastapi import APIRouter

from src.modules.ticket.schemas import CreateTicketMessageSchema
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
