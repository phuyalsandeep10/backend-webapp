import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional

from src.config.settings import settings


class EmailSender:
    def __init__(
        self,
        smtp_server: str,
        sender: str,
        smtp_port: int = 587,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_tls: bool = True,
        use_ssl: bool = False,
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.use_ssl = use_ssl
        self.sender = sender
        print(f"Connecting to {self.smtp_server}:{self.smtp_port} as {self.username}")

    def send(
        self,
        subject: str,
        recipients: List[str],
        body_text: Optional[str] = None,
        body_html: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
    ):
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.sender
        msg["To"] = ", ".join(recipients)
        if cc:
            msg["Cc"] = ", ".join(cc)

        if body_text:
            msg.attach(MIMEText(body_text, "plain"))
        if body_html:
            msg.attach(MIMEText(body_html, "html"))

        all_recipients = recipients + (cc or []) + (bcc or [])

        if self.use_ssl:
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL(
                self.smtp_server, self.smtp_port, context=context, timeout=10
            )
        else:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)

        with server:
            if self.use_tls and not self.use_ssl:
                server.starttls(context=ssl.create_default_context())
            if self.username and self.password:
                server.login(self.username, self.password)
            server.sendmail(self.sender, all_recipients, msg.as_string())


mail_sender = EmailSender(
    smtp_server=settings.SMTP_SERVER,
    sender="info@chatboq.com",
    smtp_port=settings.SMTP_PORT,
    username=settings.SMTP_USERNAME,
    password=settings.SMTP_PASSWORD,
    use_tls=False,
    use_ssl=True,
)
