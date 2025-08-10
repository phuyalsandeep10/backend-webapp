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
from src.modules.ticket.schemas import CreateTicketSchema, EditTicketSchema
from src.modules.ticket.services.status import ticket_status_service
from src.utils.exceptions.ticket import TicketNotFound
from src.utils.response import CustomResponse as cr
from src.utils.validations import TenantEntityValidator

logger = logging.getLogger(__name__)


class TicketServices:

    async def create_ticket(self, payload: CreateTicketSchema, user):
        """
        Create ticket for the organization
        """
        try:
            user_id = user.id
            data = dict(payload)
            
            data["created_by_id"] = user_id
            data["organization_id"] = user.attributes.get("organization_id")
            # for getting the default ticket status set by the organization

            print(f"Organization Id {data['organization_id']}")
            sts = await TicketStatus.find_one(
                where={
                    "is_default": True,
                    "organization_id": data["organization_id"],
                }
            )
            print(f"Ticket Status {sts}")
            if not sts:
                raise HTTPException(
                    status_code=500, detail="Ticket default status has not been set yet"
                )

            # for getting the default SLA set by the organization

            sla = await TicketSLA.find_one(
                where={
                    "is_default": True,
                    "organization_id": data["organization_id"],
                }
            )

            print(f"Ticket SLA {sla}")

            if not sla:
                raise HTTPException(
                    status_code=500, detail="SLA default has not been set yet"
                )
             
            data["status_id"] = sts.id
            data["sla_id"] = sla.id
            if data["assignees"] is not None:
                users = []
                for assigne_id in data["assignees"]:
                    usr = await User.find_one(where={"id": assigne_id})
                    users.append(usr)

                data["assignees"] = users
            print('ticket start validation')
            del data["assignees"]  # not assigning None to the db
            # validating the data
            
            tenant = TenantEntityValidator(
                    org_id=user.attributes.get("organization_id")
    
                )
         
            print(f"Creating ticket with data: {data}")
            print(f"creating ticket validation status start ")
            await tenant.validate(TicketPriority, data["priority_id"])
            await tenant.validate(TicketStatus, data["status_id"])
            await tenant.validate(TicketSLA, data["sla_id"])
            await tenant.validate(Team, data["department_id"])
            print(f"creating ticket validation status end")
            # generating the confirmation token using secrets
            data["confirmation_token"] = secrets.token_hex(32)
            
            
            record = await Ticket.create(**dict(data))
        
            tick = await Ticket.find_one(
                where={
                    "id": record.id,
                    "organization_id": data["organization_id"],
                },
                related_items=[selectinload(Ticket.customer)],
            )

            if not tick:
                return cr.error(
                    message="Error while processing ticket",
                    status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                )

            await self.validate_foreign_restrictions(data)

            # generating the confirmation token using secrets
            data["confirmation_token"] = await self.generate_secret_tokens()

            attachments = data.pop("attachments", None)

            # creating the ticket
            ticket = await Ticket.create(**data)

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
            tickets = [ticket.to_json() for ticket in all_tickets]
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
        # if no status then move to default
        if not sts:
            default_status = await TicketStatus.find_one(
                where={"organization_id": None, "is_default": True}
            )
            if default_status:
                return default_status
            else:
                raise HTTPException(
                    status_code=400, detail="Default status has not been set"
                )

        return sts

    async def get_default_ticket_sla(self, priority_id: int):
        """
        Returns the default tiket status set by the organization else move to default ticket status
        """
        sla = await TicketPriority.find_one(where={"id": priority_id})
        # if no sla then move to default
        if not sla:
            default_sla = await TicketSLA.find_one(
                where={"organization_id": None, "id": priority_id}
            )
            if default_sla:
                return default_sla
            else:
                raise HTTPException(
                    status_code=400,
                    detail="SLA with this priority has not been defined",
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

    async def get_attachments_id(self, attachments: list[str], ticket_id: int):
        """
        Registers the ticket attachments
        """
        print("Eta pugey")

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

        receiver = tick.customer.email if ticket.customer_id else tick.customer_email
        content = await self.get_confirmation_content(tick)

        email = NotificationFactory.create("email")
        email.send(
            subject="Ticket confirmation", recipients=[receiver], body_html=content
        )

    async def get_confirmation_content(self, ticket: Ticket):
        """
        Returns the simple confirmation html
        """
        name = ticket.customer.name if ticket.customer_id else ticket.customer_name
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
