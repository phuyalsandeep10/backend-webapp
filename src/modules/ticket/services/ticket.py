from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.common.dependencies import get_user_by_token
from src.modules.ticket.models.contact import Contact
from src.modules.ticket.models.sla import SLA
from src.modules.ticket.models.ticket import Ticket
from src.modules.ticket.schemas import CreateTicketSchema, FullCreateTicketSchema
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

    async def create_full_ticket(
        self, payload: FullCreateTicketSchema, authorization: str
    ):

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

            # now checking if sla_id exists or not
            if data["sla_id"] is None:
                # we need to register sla first
                sla = await SLA.create(**dict(data["sla"]))
                data["sla_id"] = sla.id

            if data["contact_id"] is None:
                # we need to register contact first
                contact = await Contact.create(**dict(data["contact"]))
                data["contact_id"] = contact.id

            ticket_data = {
                "title": data["title"],
                "description": data["description"],
                "priority": data["priority"],
                "status": data["status"],
                "sla_id": data["sla_id"],
                "contact_id": data["contact_id"],
                "issued_by": data["issued_by"],
            }

            print("The ticket", ticket_data)
            ticket = await Ticket.create(**ticket_data)
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


ticket_services = TicketServices()
