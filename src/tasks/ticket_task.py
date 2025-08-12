import asyncio
import logging

from src.config.celery import celery_app
from src.config.mail import mail_sender
from src.config.settings import settings
from src.modules.sendgrid.services import send_sendgrid_email
from src.modules.ticket.enums import TicketLogActionEnum, TicketLogEntityEnum
from src.modules.ticket.models.ticket import Ticket
from src.modules.ticket.models.ticket_log import TicketLog

logger = logging.getLogger(__name__)


@celery_app.task
def send_email(
    subject: str,
    recipients: str,
    body_html: str,
    from_email: tuple[str, str],
    ticket_id: int,
):
    try:
        logger.info(f"Sending {subject} email")
        send_sendgrid_email(
            from_email=from_email,
            to_email=recipients,
            subject=subject,
            html_content=body_html,
        )
        # saving to the log
        ticket = asyncio.run(Ticket.find_one(where={"id": ticket_id}))
        if not ticket:
            raise Exception("Ticket doesn't belong to any organization")

        log_data = {
            "ticket_id": ticket_id,
            "organization_id": ticket.organization_id,
            "entity_type": TicketLogEntityEnum.TICKET,
            "action": TicketLogActionEnum.CONFIRMATION_EMAIL_SENT,
        }
        asyncio.run(TicketLog.create(**log_data))
    except Exception as e:
        logger.exception(e)
        ticket = asyncio.run(Ticket.find_one(where={"id": ticket_id}))
        if not ticket:
            raise Exception("Ticket doesn't belong to any organization")

        log_data = {
            "ticket_id": ticket_id,
            "organization_id": ticket.organization_id,
            "entity_type": TicketLogEntityEnum.TICKET,
            "action": TicketLogActionEnum.CONFIRMATION_EMAIL_SENT_FAILED,
            "description": f"Error while sending confirmation mail {str(e)}",
        }
        asyncio.run(TicketLog.create(**log_data))
