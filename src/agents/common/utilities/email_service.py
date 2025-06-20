import smtplib
import ssl
from email.message import EmailMessage

from src.configuration.settings import Settings
from src.configuration.logger import logger


class MailingService:
    _sender: str
    _username: str
    _password: str
    _server: str
    _port: int
    _use_ssl: bool = True  # Default to SSL, can be overridden by settings

    def __init__(self, env: Settings):
        self._username = env.email_username
        self._password = env.email_password
        self._server = env.email_host
        self._port = env.email_port
        self._sender = f"AI Agent <{env.email_username}>"
        self._use_ssl = env.email_use_ssl

    def send_email(self, recipient: str, subject: str, body: str) -> bool:
        """
        Sends an email with a simple (and unsecure) SMTP connection.

        Returns a boolean representing whether the email sent correctly.
        """

        try:
            # Create message
            message = EmailMessage()
            message.set_content(body)
            message["Subject"] = subject
            message["From"] = self._sender
            message["To"] = recipient

            server_context = ssl.create_default_context() if self._use_ssl else None
            server = (
                smtplib.SMTP_SSL(self._server, self._port, context=server_context)
                if self._use_ssl
                else smtplib.SMTP(self._server, self._port)
            )
            if self._port == 587:
                server.starttls()
            if self._username and self._password:
                server.login(self._username, self._password)
            server.send_message(message)
            server.quit()

            logger.info(f"Email sent successfully to {recipient}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
