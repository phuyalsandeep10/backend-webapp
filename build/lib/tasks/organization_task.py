from src.config.celery import celery_app
from src.config.mail import mail_sender


@celery_app.task
def send_invitation_email(email: str):
    print(f"Sending invitation email to {email}")
    mail_sender.send(
        subject="Invitation",
        recipients=[email],
        body_html=f"Invitation email. Your invitation is pending.",
        body_text="This is a test email.",
    )
