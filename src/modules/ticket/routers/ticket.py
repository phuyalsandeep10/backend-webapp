from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.deps import get_db
from src.modules.ticket.schemas import CreateTicketSchema
from src.modules.ticket.services.ticket import TicketServices

router = APIRouter()


@router.post("/")
async def register_ticket(
    payload: CreateTicketSchema, db: AsyncSession = Depends(get_db)
):
    ticket_service = TicketServices()
    return await ticket_service.create_ticket(db, payload)
