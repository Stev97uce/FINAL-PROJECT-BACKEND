"""
Email service using SendGrid
KISS principle: Simple email delivery
"""
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from app.config import settings
from typing import Optional

logger = logging.getLogger(__name__)


class EmailService:
    """Simple SendGrid email service"""
    
    def __init__(self):
        self.client = None
        if settings.SENDGRID_API_KEY:
            try:
                self.client = SendGridAPIClient(settings.SENDGRID_API_KEY)
                logger.info("SendGrid client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize SendGrid: {e}")
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None
    ) -> bool:
        """
        Send email via SendGrid
        
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.client:
            logger.warning("SendGrid not configured, skipping email")
            return False
        
        try:
            message = Mail(
                from_email=Email(settings.SENDGRID_FROM_EMAIL, settings.SENDGRID_FROM_NAME),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            
            if plain_content:
                message.add_content(Content("text/plain", plain_content))
            
            response = self.client.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"SendGrid returned status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False


# Global instance
email_service = EmailService()
