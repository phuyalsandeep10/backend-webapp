from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.ticket.crud import ticket_crud as tc
from src.modules.ticket.schemas import CreateTicketSchema
from src.utils.response import CustomResponse as cr


class TicketServices:

    async def create_ticket(self, db: AsyncSession, data: CreateTicketSchema):
        try:
            ticket = await tc.create(db, data)
            if ticket is None:
                return cr.error(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="Error while creating a ticket",
                )

            return cr.success(
                status_code=status.HTTP_201_CREATED,
                message="Successfully created a ticket",
            )
        except Exception as e:
            print(e)
            return cr.error(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Error while creating a ticket",
            )
