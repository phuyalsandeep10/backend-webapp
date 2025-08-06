import logging

from src.factory.notification import NotificationInterface
from src.tasks import send_email

logger = logging.getLogger(__name__)


class EmailNotification(NotificationInterface):

    def send(
        self,
        subject: str,
        recipients: list[str],
        body_html: str,
        body_text: str = "",
    ):
        try:
            send_email(
                subject=subject,
                recipients=recipients,
                body_html=body_html,
                body_text=body_text,
            )
        except Exception as e:
            logger.exception(e)
