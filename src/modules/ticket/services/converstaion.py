import logging
from typing import Any

from pydantic import EmailStr
from sqlalchemy.orm import selectinload
from starlette.status import HTTP_201_CREATED

from src.common.context import UserContext
from src.factory.notification import NotificationFactory
from src.modules.sendgrid.services import send_sendgrid_email
from src.modules.ticket.enums import TicketLogActionEnum, TicketMessageDirectionEnum
from src.modules.ticket.schemas import CreateTicketMessageSchema
from src.utils.exceptions.ticket import TicketNotFound
from src.utils.get_templates import get_templates
from src.utils.response import CustomResponse as cr

from ..models.ticket import Ticket
from ..models.ticket_message import TicketMessage

logger = logging.getLogger(__name__)


class TicketConversationServices:
    """
    Methods and attributes related to the ticket converstaion
    """

    async def send_message(self, payload: CreateTicketMessageSchema):
        """
        sends the message
        """
        try:
            data = payload.model_dump(exclude_none=True)
            ticket = await self.ticket_exists(data["ticket_id"])
            if not ticket:
                raise TicketNotFound()

            user_id = UserContext.get()
            data["sender_id"] = user_id
            data["direction"] = TicketMessageDirectionEnum.OUTGOING.value

            conversation = await TicketMessage.create(**data)
            if not conversation:
                return cr.error(message="Error while creating conversation")

            await self._send_email(ticket, data)
            return cr.success(
                message="Successfully created a conversation",
                status_code=HTTP_201_CREATED,
            )

        except Exception as e:
            return cr.error(message=f"{e.detail if e.detail else str(e)}")

    async def ticket_exists(self, ticket_id: int) -> Ticket | None:
        try:
            ticket = await Ticket.find_one(
                where={"id": ticket_id}, related_items=selectinload(Ticket.organization)
            )
            if not ticket:
                return None
            return ticket
        except Exception as e:
            return None

    async def _send_email(self, ticket: Ticket, data: dict[str, Any]):
        try:
            # getting the history messages of that ticket_id
            messages = await TicketMessage.filter(where={"ticket_id": ticket.id})
            email = NotificationFactory.create("email")
            html_content = {"messages": messages, "ticket": ticket}
            template = await get_templates(
                name="ticket/ticket-message.html", content=html_content
            )
            await email.send_ticket_email(
                subject="Ticket Conversation Response",
                recipients=data["receiver"],
                body_html=template,
                from_email=(ticket.sender_domain, ticket.organization.name),
                ticket=ticket,
                mail_type=TicketLogActionEnum.CONFIRMATION_EMAIL_SENT,
            )
        except Exception as e:
            logger.exception(e)


ticket_conversation_service = TicketConversationServices()
