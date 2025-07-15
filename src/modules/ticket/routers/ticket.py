from fastapi import APIRouter

from src.modules.ticket.schemas import CreateTicketSchema
from src.modules.ticket.services.ticket import ticket_services

router = APIRouter()


@router.post("/", summary="Creates new ticket")
async def register_ticket(payload: CreateTicketSchema):
    return await ticket_services.create_ticket(payload)
