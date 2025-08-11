import logging

from src.factory.notification.interface import NotificationInterface
from src.tasks import send_email

logger = logging.getLogger(__name__)


class EmailNotification(NotificationInterface):
    """
    Email notification concrete class
    """

    def send(
        self,
        subject: str,
        from_email: str,
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
                body_text=body_text,
            )
        except Exception as e:
            logger.exception(e)
