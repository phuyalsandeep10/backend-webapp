import logging
import uuid
from typing import Any, Optional

from arq import create_pool
from arq.connections import RedisSettings
from pydantic import EmailStr
from sqlalchemy.orm import selectinload
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from src.common.context import UserContext
from src.factory.notification import NotificationFactory
from src.modules.auth.models import User
from src.modules.sendgrid.services import decode_ticket, send_sendgrid_email
from src.modules.ticket.enums import TicketLogActionEnum, TicketMessageDirectionEnum
from src.modules.ticket.schemas import (
    CreateTicketMessageSchema,
    EditTicketMessageSchema,
    TicketMessageOutSchema,
)
from src.tasks.ticket_task import broadcast_ticket_message
from src.utils.exceptions.ticket import TicketMessageNotFound, TicketNotFound
from src.utils.get_templates import get_templates
from src.utils.response import CustomResponse as cr

from ..models.ticket import Ticket
from ..models.ticket_message import TicketMessage, TicketMessageVersions

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
            user = await User.find_one(where={"id": user_id})
            if not user:
                return
            data["sender"] = user.email
            data["direction"] = TicketMessageDirectionEnum.OUTGOING.value

            message = await TicketMessage.create(**data)
            if not message:
                return cr.error(message="Error while creating conversation")

            # saving in versions
            version = await self.check_previous_version(message_id=message.id)
            if not version:
                await self.save_in_versions(
                    message_id=message.id, versions=1, content=data["content"]
                )
            else:
                await self.save_in_versions(
                    message_id=message.id, versions=1, content=data["content"]
                )

            await self._send_email(ticket, data)
            await self.broadcast_ticket_message(
                user_email=data["sender"],
                message=data["content"],
                ticket_id=data["ticket_id"],
            )
            return cr.success(
                message="Successfully created a conversation",
                status_code=HTTP_201_CREATED,
            )

        except Exception as e:
            return cr.error(message=f"{e.detail if e.detail else str(e)}")

    async def edit_message(self, message_id: int, payload: EditTicketMessageSchema):
        try:
            message = await TicketMessage.find_one(where={"id": message_id})
            if not message:
                raise TicketMessageNotFound()
            await message.update(id=message.id, **payload.model_dump())
            version = await self.check_previous_version(message_id=message.id)
            print("The version", version)
            if not version:
                await self.save_in_versions(
                    message_id=message.id, versions=1, content=payload.content
                )
            else:
                await self.save_in_versions(
                    message_id=message.id, versions=version + 1, content=payload.content
                )
            return cr.success("Successfully updated message")

        except Exception as e:
            logger.exception(e)
            return cr.error(message=f"{str(e)}")

    async def save_message_from_email(self, from_email, to_email, recent_reply):
        try:
            cipher = to_email.split("<")[1].split("@")[0]
            org_id, ticket_id = decode_ticket(cipher)
            payload = {
                "ticket_id": ticket_id,
                "organization_id": org_id,
                "sender": from_email,
                "receiver": to_email,
                "direction": TicketMessageDirectionEnum.INCOMING.value,
                "content": recent_reply,
            }
            await TicketMessage.create(**payload)
            logger.info("Successfully saved message from email")

            email = from_email.split("<")[1].split(">")[0]

            await self.broadcast_ticket_message(
                user_email=email, message=recent_reply, ticket_id=ticket_id
            )
        except Exception as e:
            logging.exception("Error while saving message from email")

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

    async def broadcast_ticket_message(self, user_email, message, ticket_id):

        try:
            broadcast_ticket_message.send(
                user_email=user_email,
                message=message,
                ticket_id=ticket_id,
            )

            logger.info(f"Enqueued async broadcast job for TicketMessage")
        except Exception as e:
            logger.exception(f"Failed to enqueue broadcast job for TicketMessage : {e}")

    async def list_messages(self, ticket_id: int, limit: int, before: Optional[int]):
        try:
            ticket = await Ticket.find_one_without_tenant(where={"id": ticket_id})
            if not ticket:
                raise TicketNotFound()
            if not before:
                messages = await self.fetch_message_by_limit(
                    ticket_id=ticket_id, limit=limit
                )
                return cr.success(
                    data=[
                        message.to_json(TicketMessageOutSchema) for message in messages
                    ],
                    message="Successfully listed all the messages",
                )

            messages = await self.fetch_message_by_limit_and_before(
                ticket_id=ticket_id, limit=limit, before=before
            )
            return cr.success(
                data=[message.to_json(TicketMessageOutSchema) for message in messages],
                message="Successfully listed all the messages",
            )

        except Exception as e:
            return cr.error(
                message=f"{str(e)}",
            )

    async def fetch_message_by_limit(self, ticket_id: int, limit: int):
        try:
            messages = await TicketMessage.filter_without_tenant(
                where={"ticket_id": ticket_id}, limit=limit
            )
            if not messages:
                raise Exception("Ticket message not found")
            return messages
        except Exception as e:
            raise e

    async def fetch_message_by_limit_and_before(
        self, ticket_id: int, limit: int, before: int
    ):
        try:
            messages = await TicketMessage.filter_without_tenant(
                where={"id": {"lt": before}}, limit=limit
            )
            if not messages:
                raise Exception("Ticket message not found")
            return messages
        except Exception as e:

            raise e

    async def save_in_versions(self, message_id: int, versions: int, content: str):
        try:
            payload = dict(message_id=message_id, versions=versions, content=content)
            message_version = await TicketMessageVersions.create(**payload)
            if not message_version:
                raise
        except Exception as e:
            logger.error(f"Error while saving in ticket message versions {str(e)}")

    async def check_previous_version(self, message_id: int) -> int | None:
        """
        Returns None if message_id doesnt exists in relation else returns the latest version
        """
        try:
            messages = await TicketMessageVersions.filter(
                where={"message_id": message_id}
            )
            if not messages:
                return None
            # finding the largest version id
            msg = max(messages, key=lambda message: message.versions)
            return msg.versions

        except Exception as e:
            return None


ticket_conversation_service = TicketConversationServices()
