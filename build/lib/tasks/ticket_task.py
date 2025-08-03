import logging

from src.config.celery import celery_app
from src.config.mail import mail_sender
from src.config.settings import settings

logger = logging.getLogger(__name__)


@celery_app.task
def send_ticket_verification_email(email: str, token: str, ticket_id: str):
    logger.info(f"Sending ticket verification email to {email}")
    mail_sender.send(
        subject="Ticket Email Verification",
        recipients=[email],
        body_html=f"<div><h1>Please verify the ticket confirmation</h1><a href='{settings.FRONTEND_URL}/ticket-confirm/{ticket_id}/{token}'>Verify ticket</a></div>",
        body_text="Ticket verification email",
    )
