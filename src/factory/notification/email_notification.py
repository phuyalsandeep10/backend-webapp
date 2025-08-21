import logging
import uuid

from arq import create_pool
from arq.connections import RedisSettings

from src.factory.notification.interface import NotificationInterface
from src.modules.ticket.enums import TicketLogActionEnum
from src.modules.ticket.models.ticket import Ticket
from src.tasks.ticket_task import send_ticket_task_email

logger = logging.getLogger(__name__)


class EmailNotification(NotificationInterface):
    """
    Email notification concrete class
    """

    async def send_ticket_email(
        self,
        subject: str,
        from_email: tuple[str, str],
        recipients: str,
        body_html: str,
        ticket: Ticket,
        mail_type: TicketLogActionEnum,
    ):
        try:
            # redis = await create_pool((RedisSettings()))
            # await redis.enqueue_job(
            #     "send_ticket_task_email",
            #     subject=subject,
            #     from_email=from_email,
            #     recipients=recipients,
            #     body_html=body_html,
            #     ticket_id=ticket.id,
            #     organization_id=ticket.organization_id,
            #     mail_type=mail_type,
            #     _job_id=str(uuid.uuid4()),
            # )
            send_ticket_task_email.send(
                subject=subject,
                from_email=from_email,
                recipients=recipients,
                body_html=body_html,
                ticket_id=ticket.id,
                organization_id=ticket.organization_id,
                mail_type=mail_type,
            )
            pass
        except Exception as e:
            logger.exception(e)
