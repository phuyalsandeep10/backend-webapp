from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.ticket.models.ticket import Ticket
from src.modules.ticket.schemas import CreateTicketSchema


async def create(db: AsyncSession, data: CreateTicketSchema) -> Ticket | None:

    try:
        ticket = Ticket(**dict(data))
        db.add(ticket)
        await db.commit()
        await db.refresh(ticket)
        return ticket
    except SQLAlchemyError as e:
        print(e)
        return None
