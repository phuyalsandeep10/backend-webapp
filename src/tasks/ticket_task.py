import logging

from src.config.celery import celery_app
from src.config.mail import mail_sender
from src.config.settings import settings

logger = logging.getLogger(__name__)


@celery_app.task
def send_email(
    subject: str,
    recipients: list[str],
    body_html: str,
    body_text: str = "",
):
    logger.info(f"Sending {subject} email")
    mail_sender.send(
        subject=subject,
        recipients=recipients,
        body_html=body_html,
        body_text=body_text,
    )
    # body_html=f"<div><h1>Please verify the ticket confirmation</h1><a href='{settings.FRONTEND_URL}/ticket-confirm/{ticket_id}/{token}'>Verify ticket</a></div>",
