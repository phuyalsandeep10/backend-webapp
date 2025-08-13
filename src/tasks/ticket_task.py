import logging
from contextvars import ContextVar

from src.modules.sendgrid.services import send_sendgrid_email
from src.modules.ticket.enums import TicketLogActionEnum, TicketLogEntityEnum
from src.modules.ticket.models.ticket import Ticket
from src.modules.ticket.models.ticket_log import TicketLog

logger = logging.getLogger(__name__)


async def send_email(
    ctx,
    subject: str,
    recipients: str,
    body_html: str,
    from_email: tuple[str, str],
    ticket_id: int,
    organization_id: int,
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
        log_data = {
            "ticket_id": ticket_id,
            "organization_id": organization_id,
            "entity_type": TicketLogEntityEnum.TICKET,
            "action": TicketLogActionEnum.CONFIRMATION_EMAIL_SENT,
        }
        await TicketLog.create(**log_data)
    except Exception as e:
        logger.exception(e)
        log_data = {
            "ticket_id": ticket_id,
            "organization_id": organization_id,
            "entity_type": TicketLogEntityEnum.TICKET,
            "action": TicketLogActionEnum.CONFIRMATION_EMAIL_SENT_FAILED,
            "description": f"Error while sending confirmation mail",
        }
        await TicketLog.create(**log_data)
