from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.deps import get_db
from src.modules.ticket.schemas import CreateTicketSchema
from src.modules.ticket.services.ticket import ticket_services

router = APIRouter()


@router.post("/", summary="Creates new ticket")
async def register_ticket(
    payload: CreateTicketSchema, db: AsyncSession = Depends(get_db)
):
    return await ticket_services.create_ticket(db, payload)
