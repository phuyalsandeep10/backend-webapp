import logging

from arq import create_pool
from arq.connections import RedisSettings

from src.factory.notification.interface import NotificationInterface
from src.modules.ticket.models.ticket import Ticket
from src.tasks import send_email

logger = logging.getLogger(__name__)


class EmailNotification(NotificationInterface):
    """
    Email notification concrete class
    """

    def send(
        self,
        subject: str,
        from_email: tuple[str, str],
        recipients: list[str],
        body_html: str,
        body_text: str = "",
    ):
        try:
            send_email.delay(
                from_email=from_email,
                subject=subject,
                recipients=recipients,
                body_html=body_html,
            )
        except Exception as e:
            logger.exception(e)

    async def send_ticket_email(
        self,
        subject: str,
        from_email: tuple[str, str],
        recipients: list[str],
        body_html: str,
        ticket: Ticket,
        mail_type: str,
    ):
        try:
            redis = await create_pool((RedisSettings()))
            await redis.enqueue_job(
                "send_email",
                subject=subject,
                from_email=from_email,
                recipients=recipients,
                body_html=body_html,
                ticket_id=ticket.id,
                organization_id=ticket.organization_id,
                mail_type=mail_type,
            )
        except Exception as e:
            logger.exception(e)
