import os
from pathlib import Path
import smtplib
import ssl
from email import encoders
from email.message import EmailMessage
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional, Union

from src.configuration.logger import default_logger
from src.configuration.settings import Settings


class MailingService:
    _sender: str
    _username: str
    _password: str
    _server: str
    _port: int
    _use_ssl: bool = True  # Default to SSL, can be overridden by settings

    def __init__(self, env: Settings):
        self._username = env.email_username
        self._password = (
            env.email_password.get_secret_value() if env.email_password else None
        )
        self._server = env.email_host
        self._port = env.email_port
        self._sender = f"AI Agent <{env.email_username}>"
        self._use_ssl = env.email_use_ssl

        default_logger.info(
            f"MailingService initialized with server: {self._server}, port: {self._port}, use_ssl: {self._use_ssl}"
        )

    def send_email(
        self,
        recipients: Union[str, List[str]],
        subject: str,
        body: str,
        attachments: Optional[List[Path]] = None,
    ) -> bool:
        """
        Sends an email with optional attachments to one or more recipients.

        Args:
            recipients: Email address(es) of the recipient(s) - can be a string or list of strings
            subject: Email subject
            body: Email body content
            attachments: Optional list of file paths to attach to the email

        Returns:
            Boolean representing whether the email sent correctly to all recipients.
        """

        try:
            # Normalize recipients to a list
            if isinstance(recipients, str):
                recipient_list = [recipients]
            else:
                recipient_list = recipients

            # Validate that we have recipients
            if not recipient_list:
                default_logger.error("No recipients provided")
                return False

            # Create recipients string for logging and email headers
            recipients_str = ", ".join(recipient_list)

            # Create message - use MIMEMultipart if attachments are present
            if attachments:
                message = MIMEMultipart()
                message["Subject"] = subject
                message["From"] = self._sender
                message["To"] = recipients_str

                # Add body as text part
                message.attach(MIMEText(body, "plain"))

                # Add attachments
                for attachment_path in attachments:
                    if attachment_path.is_file() and attachment_path.exists():
                        with open(attachment_path, "rb") as attachment:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(attachment.read())

                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            f"attachment; filename= {os.path.basename(attachment_path)}",
                        )
                        message.attach(part)
                    else:
                        default_logger.warning(
                            f"Attachment file not found: {attachment_path}"
                        )
            else:
                # Use simple EmailMessage for emails without attachments
                message = EmailMessage()
                message.set_content(body)
                message["Subject"] = subject
                message["From"] = self._sender
                message["To"] = recipients_str

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

            default_logger.info(f"Email sent successfully to {recipients_str}")
            return True
        except Exception as e:
            default_logger.error(f"Failed to send email: {e}")
            return False
