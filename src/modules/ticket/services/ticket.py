from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload

from src.common.dependencies import get_user_by_token
from src.modules.auth.models import User
from src.modules.ticket.models.contact import Contact
from src.modules.ticket.models.sla import SLA
from src.modules.ticket.models.ticket import Ticket
from src.modules.ticket.schemas import CreateTicketSchema, FullCreateTicketSchema
from src.utils.response import CustomResponse as cr


class TicketServices:

    async def create_ticket(self, payload: CreateTicketSchema, user: User):
        try:
            user_id = user.id
            data = dict(payload)
            data["issued_by"] = user_id
            data["organization_id"] = user.attributes.get("organization_id")
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

            # assignes

            users = []
            for assigne_id in data["assignees"]:
                usr = await User.find_one(where={"id": assigne_id})
                users.append(usr)

            data["assignees"] = users

            ticket_data = {
                "title": data["title"],
                "description": data["description"],
                "priority": data["priority"],
                "status": data["status"],
                "sla_id": data["sla_id"],
                "contact_id": data["contact_id"],
                "issued_by": data["issued_by"],
                "assignees": data["assignees"],
            }

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
