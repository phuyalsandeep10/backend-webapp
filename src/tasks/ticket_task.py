import logging

from src.config.celery import celery_app
from src.config.mail import mail_sender
from src.config.settings import settings
from src.modules.sendgrid.services import send_sendgrid_email

logger = logging.getLogger(__name__)


@celery_app.task
def send_email(
    subject: str,
    recipients: str,
    body_html: str,
    from_email: tuple[str, str],
    body_text: str = "",
):
    logger.info(f"Sending {subject} email")
    send_sendgrid_email(
        from_email=from_email,
        to_email=recipients,
        subject=subject,
        html_content=body_html,
    )
    # mail_sender.send(
    #     subject=subject,
    #     recipients=recipients,
    #     body_html=body_html,
    #     body_text=body_text,
    # )
