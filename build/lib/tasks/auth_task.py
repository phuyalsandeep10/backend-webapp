from src.config.celery import celery_app
from src.config.mail import mail_sender


@celery_app.task
def send_verification_email(email: str, token: str):
    print(f"Sending verification email to {email} with token {token}")
    mail_sender.send(
        subject="Email Verification",
        recipients=[email],
        body_html=f"<p>Email Verification Token: {token}</p>",
        body_text="This is a test email.",
    )


@celery_app.task
def send_forgot_password_email(email: str, token: str):
    print(f"Sending forgot password email to {email} with token {token}")
    mail_sender.send(
        subject="Forgot Password",
        recipients=[email],
        body_html=f"<p>Forgot Password Token: {token}</p>",
        body_text="This is a test email.",
    )
