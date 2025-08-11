import logging
import secrets
from datetime import datetime

from fastapi import HTTPException, status
from kombu import message
from sqlalchemy.orm import selectinload
from starlette.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

from src.common.dependencies import get_user_by_token
from src.config.settings import settings
from src.factory.notification import NotificationFactory
from src.modules.auth.models import User
from src.modules.team.models import Team
from src.modules.ticket.models import TicketPriority
from src.modules.ticket.models.contact import Contact
from src.modules.ticket.models.sla import TicketSLA
from src.modules.ticket.models.status import TicketStatus
from src.modules.ticket.models.ticket import Ticket, TicketAttachment
from src.modules.ticket.schemas import (
    CreateTicketSchema,
    EditTicketSchema,
    TicketByStatusSchema,
    TicketOut,
)
from src.modules.ticket.services.status import ticket_status_service
from src.utils.exceptions.ticket import (
    TicketNotFound,
    TicketSLANotFound,
    TicketStatusNotFound,
)
from src.utils.get_templates import get_templates
from src.utils.response import CustomResponse as cr
from src.utils.validations import TenantEntityValidator

logger = logging.getLogger(__name__)


class TicketServices:

    async def create_ticket(self, payload: CreateTicketSchema, user):
        """
        Create ticket for the organization
        """
        try:
            # for getting the default ticket status set by the organization
            sts = await self.get_default_ticket_status()
            sla = await self.get_default_ticket_sla(priority_id=payload.priority_id)

            if not sts:
                raise TicketStatusNotFound(detail="Default ticket status not found")

            if not sla:
                raise TicketSLANotFound(detail="Ticket SLA not found for this priority")

            data = payload.model_dump(exclude_none=True)

            data["status_id"] = sts.id
            data["sla_id"] = sla.id
            if "assignees" in data:
                data["assignees"] = await self.get_assigned_members_by_id(
                    data["assignees"]
                )

            await self.validate_foreign_restrictions(data)

            # generating the confirmation token using secrets
            data["confirmation_token"] = await self.generate_secret_tokens()

            attachments = data.pop("attachments", None)

            # creating the ticket
            ticket = await Ticket.create(**data)
            logger.info("The tick rajib", ticket, data)

            if attachments:
                for attachment in attachments:
                    await TicketAttachment.create(
                        ticket_id=ticket.id, attachment=attachment
                    )

            # sending the confirmation email
            await self.send_confirmation_email(ticket)

            return cr.success(
                status_code=status.HTTP_201_CREATED,
                message="Successfully created a ticket",
            )
        except Exception as e:
            logger.exception(e)
            return cr.error(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Error while creating a ticket",
                data=str(e),
            )

    async def list_tickets(self, user):
        """
        List all the tickets of the user organization
        """
        try:
            all_tickets = await Ticket.filter(
                related_items=[
                    selectinload(Ticket.sla),
                    selectinload(Ticket.assignees),
                    selectinload(Ticket.priority),
                    selectinload(Ticket.status),
                    selectinload(Ticket.customer),
                    selectinload(Ticket.created_by),
                    selectinload(Ticket.department),
                    selectinload(Ticket.attachments),
                ],
            )
            print("The all tickets", all_tickets)
            tickets = [ticket.to_dict() for ticket in all_tickets]
            return cr.success(
                status_code=status.HTTP_200_OK,
                message="Successfully listed all tickets",
                data=tickets,
            )
        except Exception as e:
            logger.exception(e)
            return cr.error(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Error while listing  tickets",
            )

    async def get_ticket(self, ticket_id: int, user):
        """
        List the particular ticket of the organization by id
        """
        try:
            organization_id = user.attributes.get("organization_id")
            ticket = await Ticket.find_one(
                where={"id": ticket_id, "organization_id": organization_id},
                options=[
                    selectinload(Ticket.sla),
                    selectinload(Ticket.assignees),
                    selectinload(Ticket.priority),
                    selectinload(Ticket.status),
                    selectinload(Ticket.customer),
                    selectinload(Ticket.created_by),
                    selectinload(Ticket.department),
                    selectinload(Ticket.attachments),
                ],
            )
            if ticket is None:
                return cr.error(message="Not found")
            return cr.success(
                status_code=status.HTTP_200_OK,
                message="Successfully listed the ticket",
                data=ticket.to_dict() if ticket else [],
            )
        except Exception as e:
            logger.exception(e)
            return cr.error(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Error while listing ticket",
            )

    async def delete_ticket(self, ticket_id: int, user):
        try:
            await Ticket.soft_delete(
                where={
                    "id": ticket_id,
                }
            )
            return cr.success(
                status_code=status.HTTP_200_OK,
                message="Successfully deleted the ticket",
            )
        except Exception as e:
            logger.exception(e)
            return cr.error(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Error while deleting the tickets",
            )

    async def confirm_ticket(self, ticket_id: int, token: str):
        try:
            ticket = await Ticket.find_one(
                where={"id": ticket_id, "confirmation_token": token}
            )
            if ticket is None:
                raise TicketNotFound("Invalid credentials")
            # to find which is the open status category status defined the organization it could be in-progress, or open,ongoing
            open_status_category = (
                await ticket_status_service.get_status_category_by_name("open")
            )
            await Ticket.update(
                id=ticket.id,
                status_id=open_status_category.id,
                opened_at=datetime.utcnow(),
            )
            return cr.success(
                message="Your ticket has been activated.", data={"id": ticket.id}
            )

        except Exception as e:
            logger.exception(e)
            return cr.error(message="Invalid confirmation token")

    async def list_tickets_by_status(self, payload: TicketByStatusSchema):
        """
        List the tickets on the basis of status id
        """
        try:
            # validator so that it doesn't fetch other organization status tickets
            tenant = TenantEntityValidator()
            await tenant.validate(TicketStatus, payload.status_id)

            tickets = await Ticket.filter(
                where={"status_id": payload.status_id},
                related_items=[
                    selectinload(Ticket.sla),
                    selectinload(Ticket.assignees),
                    selectinload(Ticket.priority),
                    selectinload(Ticket.status),
                    selectinload(Ticket.customer),
                    selectinload(Ticket.created_by),
                    selectinload(Ticket.department),
                    selectinload(Ticket.attachments),
                ],
            )

            if not tickets:
                return cr.success(
                    message="Successfully fetched tickets by the status", data=[]
                )

            return cr.success(
                message="Successfully fetched tickets by the status",
                data=[ticket.to_dict() for ticket in tickets],
            )

        except Exception as e:
            return cr.error(
                message="Error while listing the tickets by status", data=str(e)
            )

    async def edit_ticket(self, ticket_id: int, payload: EditTicketSchema, user):
        """
        Edit ticket on the basis of the id
        """
        try:
            ticket = await Ticket.find_one(
                where={
                    "id": ticket_id,
                },
                related_items=[
                    selectinload(Ticket.sla),
                    selectinload(Ticket.assignees),
                    selectinload(Ticket.priority),
                    selectinload(Ticket.status),
                    selectinload(Ticket.customer),
                    selectinload(Ticket.created_by),
                    selectinload(Ticket.department),
                    selectinload(Ticket.attachments),
                ],
            )
            if ticket is None:
                raise TicketNotFound()

            # checking if the foreignkeys don't belong to the other organization
            tenant = TenantEntityValidator()
            data = dict(payload.model_dump(exclude_none=True))

            if "priority_id" in data:
                await tenant.validate(
                    TicketPriority, data["priority_id"], check_default=True
                )
            if "status_id" in data:
                await tenant.validate(
                    TicketStatus, data["status_id"], check_default=True
                )
            if "sla_id" in data:
                await tenant.validate(TicketSLA, data["sla_id"], check_default=True)
            if "department_id" in data:
                await tenant.validate(Team, data["department_id"])

            await Ticket.update(ticket.id, **data)

            return cr.success(
                message="Successfully updated the ticket", data=ticket.to_dict()
            )

        except Exception as e:
            logger.exception(e)
            return cr.error(message="Error while editing the ticket", data=str(e))

    async def get_default_ticket_status(self):
        """
        Returns the default tiket status set by the organization else move to default ticket status
        """
        sts = await TicketStatus.find_one(
            where={
                "is_default": True,
            }
        )
        if not sts:
            raise TicketStatusNotFound(detail="Default status has not been set")

        return sts

    async def get_default_ticket_sla(self, priority_id: int):
        """
        Returns the default tiket status set by the organization else move to default ticket status
        """
        sla = await TicketPriority.find_one(where={"id": priority_id})
        if not sla:
            raise TicketSLANotFound(
                detail="SLA with this priority has not been defined"
            )

        return sla

    async def get_assigned_members_by_id(self, user_ids: list[int]):
        """
        Returns the list of users by users id
        """
        users = []
        for assigne_id in user_ids:
            usr = await User.find_one(where={"id": assigne_id})
            users.append(usr)
        return users

    async def validate_foreign_restrictions(self, data):
        """
        Validates foreign restriction to secure data leaks
        """
        # validating the data
        tenant = TenantEntityValidator()

        await tenant.validate(TicketPriority, data["priority_id"], check_default=True)
        await tenant.validate(TicketStatus, data["status_id"], check_default=True)
        await tenant.validate(TicketSLA, data["sla_id"], check_default=True)
        await tenant.validate(Team, data["department_id"])

    async def generate_secret_tokens(self):
        """
        Returns the 32 character secret token
        """
        return secrets.token_hex(32)

    async def send_confirmation_email(self, ticket: Ticket):
        """
        Sends email for the confirmation
        """
        tick = await Ticket.find_one(
            where={"id": ticket.id},
            related_items=[selectinload(Ticket.customer)],
        )
        if not tick:
            raise TicketNotFound()

        receiver = tick.customer.email if tick.customer_id else tick.customer_email
        name = tick.customer.name if tick.customer_id else tick.customer_name
        html_content = {"name": name, "ticket": tick, "settings": settings}
        template = await get_templates(
            name="ticket/ticket-confirmation-email.html", content=html_content
        )

        email = NotificationFactory.create("email")
        email.send(
            subject="Ticket confirmation", recipients=[receiver], body_html=template
        )

    async def get_confirmation_content(self, ticket: Ticket):
        """
        Returns the simple confirmation html
        """
        content = f"""

        <p>Hello {name}</p>,

        <p>Your ticket (ID: {ticket.id}) has been successfully created. Please confirm your ticket </p>
        <div><h1>Please verify the ticket confirmation</h1><a href='{settings.FRONTEND_URL}/ticket-confirm/{ticket.id}/{ticket.confirmation_token}'>Verify ticket</a></div>


        Thank you for contacting us!

        Best regards,  
        Support Team
        """

        return content


ticket_services = TicketServices()
