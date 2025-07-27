from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload

from src.common.dependencies import get_user_by_token
from src.modules.auth.models import User
from src.modules.ticket.models.contact import Contact
from src.modules.ticket.models.sla import TicketSLA
from src.modules.ticket.models.status import TicketStatus
from src.modules.ticket.models.ticket import Ticket
from src.modules.ticket.schemas import CreateTicketSchema, FullCreateTicketSchema
from src.utils.response import CustomResponse as cr


class TicketServices:

    async def create_ticket(self, payload: CreateTicketSchema, user):
        try:
            user_id = user.id
            data = dict(payload)
            data["created_by_id"] = user_id
            data["organization_id"] = user.attributes.get("organization_id")
            sts = await TicketStatus.find_one(
                where={
                    "is_default": True,
                    "organization_id": data["organization_id"],
                }
            )
            if not sts:
                raise HTTPException(
                    status_code=500, detail="Ticket default status has not been set yet"
                )
            data["status_id"] = sts.id
            if data["assignees"] is not None:
                print("First")
                users = []
                for assigne_id in data["assignees"]:
                    usr = await User.find_one(where={"id": assigne_id})
                    users.append(usr)

                data["assignees"] = users

            del data["assignees"]  # not assing None to the db
            await Ticket.create(**dict(data))

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

    async def list_tickets(self, user: User):
        try:

            all_tickets = await Ticket.filter(
                where={"organization_id": user.attributes.get("organization_id")},
                related_items=[
                    selectinload(Ticket.sla),
                    selectinload(Ticket.assignees),
                    selectinload(Ticket.priority),
                    selectinload(Ticket.status),
                    selectinload(Ticket.customer),
                    selectinload(Ticket.issued),
                    selectinload(Ticket.department),
                ],
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

    async def get_ticket(self, ticket_id: int):
        try:
            ticket = await Ticket.find_one(
                where={"id": ticket_id},
                options=[
                    selectinload(Ticket.sla),
                    selectinload(Ticket.contacts),
                    selectinload(Ticket.assignees),
                ],
            )
            return cr.success(
                status_code=status.HTTP_200_OK,
                message="Successfully listed the ticket",
                data=ticket.to_dict(),
            )
        except Exception as e:
            print(e)
            return cr.error(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Error while listing ticket",
            )

    async def delete_ticket(self, ticket_id: int):
        try:
            await Ticket.delete(id=ticket_id)
            return cr.success(
                status_code=status.HTTP_200_OK,
                message="Successfully deleted the ticket",
            )
        except Exception as e:
            print(e)
            return cr.error(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Error while deleting the tickets",
            )


ticket_services = TicketServices()
