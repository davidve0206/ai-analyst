from src.agent.utilities.email_service import MailingService
from src.configuration.settings import app_settings
from src.configuration.logger import logger

if __name__ == "__main__":
    logger.info("Starting AI Agent Email Service...")
    mail_service = MailingService(app_settings)
    recipient = app_settings.email_recipient
    subject = "Test Email from AI Agent"
    body = "This is a test email sent from the AI Agent."

    mail_service.send_email(recipient, subject, body)