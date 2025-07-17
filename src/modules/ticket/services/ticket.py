from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.common.dependencies import get_user_by_token
from src.modules.ticket.models.ticket import Ticket
from src.modules.ticket.schemas import CreateTicketSchema
from src.utils.response import CustomResponse as cr


class TicketServices:

    async def create_ticket(self, payload: CreateTicketSchema, authorization: str):
        try:
            token = authorization.split(" ")[1]
            if authorization.split(" ")[0] != "Bearer":
                raise IndexError()
            user = await get_user_by_token(token)

            if not user:
                raise HTTPException(status_code=403, detail="Authorization denied")

            user_id = user.id
            data = dict(payload)
            data["issued_by"] = user_id

            ticket = await Ticket.create(**dict(data))
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

    async def list_tickets(self):
        try:
            all_tickets = await Ticket.get_all(
                [selectinload(Ticket.sla), selectinload(Ticket.contacts)]
            )
            tickets = [ticket.to_dict() for ticket in all_tickets]
            return cr.success(
                status_code=status.HTTP_200_OK,
                message="Successfully listed all tickets",
                data=tickets,
            )
        except Exception as e:
            print(e)
            return cr.error(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Error while listing  tickets",
            )


ticket_services = TicketServices()
