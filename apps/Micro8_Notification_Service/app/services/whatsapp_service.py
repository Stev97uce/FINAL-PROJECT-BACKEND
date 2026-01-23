"""
WhatsApp service using Twilio
KISS principle: Simple WhatsApp delivery
"""
import logging
from twilio.rest import Client
from app.config import settings
from typing import Optional

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Simple Twilio WhatsApp service"""
    
    def __init__(self):
        self.client = None
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            try:
                self.client = Client(
                    settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN
                )
                logger.info("Twilio client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio: {e}")
    
    async def send_whatsapp(
        self,
        to_phone: str,
        message: str
    ) -> bool:
        """
        Send WhatsApp message via Twilio
        
        Args:
            to_phone: Phone number in format: +593999999999
            message: Message text (max 1600 chars)
        
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.client:
            logger.warning("Twilio not configured, skipping WhatsApp")
            return False
        
        try:
            # Ensure phone format
            if not to_phone.startswith("+"):
                to_phone = f"+{to_phone}"
            
            # Limit message length
            if len(message) > 1600:
                message = message[:1597] + "..."
            
            # Send message
            twilio_message = self.client.messages.create(
                from_=settings.TWILIO_WHATSAPP_FROM,
                to=f"whatsapp:{to_phone}",
                body=message
            )
            
            if twilio_message.sid:
                logger.info(f"WhatsApp sent successfully to {to_phone}")
                return True
            else:
                logger.error(f"Twilio returned no SID for {to_phone}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send WhatsApp to {to_phone}: {e}")
            return False


# Global instance
whatsapp_service = WhatsAppService()
