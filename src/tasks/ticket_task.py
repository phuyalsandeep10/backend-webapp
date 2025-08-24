import logging
from time import sleep

import dramatiq
from pydantic import EmailStr
from sqlalchemy.orm import selectinload

from src.factory.notification import NotificationFactory
from src.modules.sendgrid.services import send_sendgrid_email
from src.modules.ticket.enums import TicketLogActionEnum, TicketLogEntityEnum
from src.modules.ticket.models.ticket_log import TicketLog
from src.modules.ticket.models.ticket_message import TicketMessage
from src.socket_config import ticket_ns
from src.utils.get_templates import get_templates

logger = logging.getLogger(__name__)


@dramatiq.actor
async def send_ticket_task_email(
    subject: str,
    recipients: str,
    body_html: str,
    from_email: tuple[str, str],
    ticket_id: int,
    organization_id: int,
    mail_type: TicketLogActionEnum,
):
    try:
        logger.info(f"Sending {subject} email")
        send_sendgrid_email(
            from_email=from_email,
            to_email=recipients,
            subject=subject,
            html_content=body_html,
            ticket_id=ticket_id,
            org_id=organization_id,
        )
        # saving to the log
        log_data = {
            "ticket_id": ticket_id,
            "organization_id": organization_id,
            "entity_type": TicketLogEntityEnum.TICKET,
            "action": mail_type,
        }
        await TicketLog.create(**log_data)
    except Exception as e:
        logger.exception(e)
        log_data = {
            "ticket_id": ticket_id,
            "organization_id": organization_id,
            "entity_type": TicketLogEntityEnum.TICKET,
            "action": TicketLogActionEnum.EMAIL_SENT_FAILED,
            "description": f"Error while sending {mail_type}",
        }
        await TicketLog.create(**log_data)


@dramatiq.actor
async def send_ticket_task_message_email(
    subject: str,
    recipients: str,
    from_email: tuple[str, str],
    ticket_id: int,
    organization_id: int,
    delay: int,
    mail_type: TicketLogActionEnum,
):
    try:
        logger.info(f"Sending {subject} email")

        if delay:
            sleep(delay)

        ticket = await Ticket.find_one_without_tenant(
            where={"id": ticket_id}, related_items=selectinload(Ticket.organization)
        )
        messages = await TicketMessage.filter_without_tenant(
            where={"ticket_id": ticket_id}
        )
        html_content = {"messages": messages, "ticket": ticket}
        template = await get_templates(
            name="ticket/ticket-message.html", content=html_content
        )
        send_sendgrid_email(
            from_email=from_email,
            to_email=recipients,
            subject=subject,
            html_content=template,
            ticket_id=ticket_id,
            org_id=organization_id,
        )
        # saving to the log
        log_data = {
            "ticket_id": ticket_id,
            "organization_id": organization_id,
            "entity_type": TicketLogEntityEnum.TICKET,
            "action": mail_type,
        }
        await TicketLog.create(**log_data)
    except Exception as e:
        logger.exception(e)
        log_data = {
            "ticket_id": ticket_id,
            "organization_id": organization_id,
            "entity_type": TicketLogEntityEnum.TICKET,
            "action": TicketLogActionEnum.EMAIL_SENT_FAILED,
            "description": f"Error while sending {mail_type}",
        }
        await TicketLog.create(**log_data)


@dramatiq.actor
async def broadcast_ticket_message(user_email: EmailStr, message: str, ticket_id: int):
    try:
        logger.info("Broadcasting ticket message")
        await ticket_ns.broadcast_message(
            user_email=user_email, message=message, ticket_id=ticket_id
        )
    except Exception as e:
        logger.error(e)
        logger.error("Error while broadcasting ticket message")
