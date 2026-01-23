"""
Main notification service - Business logic
KISS principle: Simple notification orchestration
"""
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from app.models import (
    NotificationLog, NotificationTemplate, UserPreferences, 
    InternalNotification, NotificationChannel, NotificationStatus
)
from app.services import email_service, whatsapp_service, mqtt_service, template_service
from app.database import get_redis_client
from app.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """Core notification service - handles all notification delivery"""
    
    async def send_notification(
        self,
        user_id: int,
        channel: NotificationChannel,
        template_name: str,
        variables: Dict[str, Any],
        recipient: Optional[str] = None
    ) -> bool:
        """
        Send notification using specified template and channel
        
        Args:
            user_id: Target user ID
            channel: Notification channel
            template_name: Template name to use
            variables: Template variables
            recipient: Override recipient (email or phone)
        
        Returns:
            bool: True if sent successfully
        """
        try:
            # Check user preferences
            if not await self._check_preferences(user_id, channel):
                logger.info(f"User {user_id} has {channel} notifications disabled")
                return False
            
            # Check rate limiting
            if not self._check_rate_limit(user_id, channel):
                logger.warning(f"Rate limit exceeded for user {user_id} on {channel}")
                return False
            
            # Get template
            template = await NotificationTemplate.find_one(
                NotificationTemplate.name == template_name,
                NotificationTemplate.channel == channel,
                NotificationTemplate.active == True
            )
            
            if not template:
                logger.error(f"Template {template_name} not found for channel {channel}")
                return False
            
            # Validate variables
            if not template_service.validate_variables(template.variables, variables):
                logger.error(f"Missing required variables for template {template_name}")
                return False
            
            # Render template
            subject = None
            if template.subject:
                subject = template_service.render_template(template.subject, variables)
            body = template_service.render_template(template.body, variables)
            
            # Create log entry
            notification_id = str(uuid.uuid4())
            log = NotificationLog(
                notification_id=notification_id,
                user_id=user_id,
                channel=channel,
                event_type=template.event_type,
                template_id=str(template.id),
                recipient=recipient or "unknown",
                subject=subject,
                body=body,
                metadata=variables
            )
            
            # Send via appropriate channel
            success = False
            if channel == NotificationChannel.EMAIL:
                success = await email_service.send_email(
                    to_email=recipient or variables.get("email", ""),
                    subject=subject,
                    html_content=body
                )
            
            elif channel == NotificationChannel.WHATSAPP:
                success = await whatsapp_service.send_whatsapp(
                    to_phone=recipient or variables.get("phone", ""),
                    message=body
                )
            
            elif channel == NotificationChannel.INTERNAL:
                # Save to internal_notifications collection
                internal = InternalNotification(
                    user_id=user_id,
                    title=subject or "Notification",
                    body=body,
                    category=variables.get("category", "system"),
                    priority=variables.get("priority", "medium"),
                    action_url=variables.get("action_url"),
                    metadata=variables,
                    expires_at=datetime.utcnow() + timedelta(
                        days=settings.INTERNAL_NOTIFICATION_EXPIRY_DAYS
                    )
                )
                await internal.insert()
                success = True
            
            elif channel == NotificationChannel.MQTT:
                success = await mqtt_service.publish_notification(
                    user_id=user_id,
                    notification={
                        "notification_id": notification_id,
                        "title": subject or "Notification",
                        "body": body,
                        "category": variables.get("category", "system"),
                        "created_at": datetime.utcnow().isoformat(),
                        "action_url": variables.get("action_url")
                    }
                )
            
            # Update log
            if success:
                log.status = NotificationStatus.SENT
                log.sent_at = datetime.utcnow()
                self._increment_rate_limit(user_id, channel)
            else:
                log.status = NotificationStatus.FAILED
                log.error_message = "Delivery failed"
                log.next_retry_at = datetime.utcnow() + timedelta(
                    seconds=settings.RETRY_DELAYS[0]
                )
            
            await log.insert()
            return success
            
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False
    
    async def _check_preferences(self, user_id: int, channel: NotificationChannel) -> bool:
        """Check if user has enabled this notification channel"""
        prefs = await UserPreferences.find_one(UserPreferences.user_id == user_id)
        
        if not prefs:
            # Create default preferences
            prefs = UserPreferences(user_id=user_id)
            await prefs.insert()
            return True
        
        # Check channel preference
        if channel == NotificationChannel.EMAIL:
            return prefs.email_enabled
        elif channel == NotificationChannel.WHATSAPP:
            return prefs.whatsapp_enabled
        elif channel == NotificationChannel.INTERNAL:
            return prefs.internal_enabled
        elif channel == NotificationChannel.MQTT:
            return prefs.push_enabled
        
        return True
    
    def _check_rate_limit(self, user_id: int, channel: NotificationChannel) -> bool:
        """Check if rate limit is exceeded"""
        redis_client = get_redis_client()
        
        try:
            # Get limits
            if channel == NotificationChannel.EMAIL:
                limit = settings.RATE_LIMIT_EMAIL_PER_USER_DAY
                window = 86400  # 24 hours
            elif channel == NotificationChannel.WHATSAPP:
                limit = settings.RATE_LIMIT_WHATSAPP_PER_USER_DAY
                window = 86400
            elif channel == NotificationChannel.INTERNAL:
                limit = settings.RATE_LIMIT_INTERNAL_PER_USER_DAY
                window = 86400
            else:
                return True  # No limit for MQTT
            
            # Check count
            key = f"rate_limit:{channel}:{user_id}"
            count = redis_client.get(key)
            
            if count and int(count) >= limit:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True  # Allow on error
    
    def _increment_rate_limit(self, user_id: int, channel: NotificationChannel):
        """Increment rate limit counter"""
        redis_client = get_redis_client()
        
        try:
            if channel == NotificationChannel.EMAIL:
                window = 86400
            elif channel == NotificationChannel.WHATSAPP:
                window = 86400
            elif channel == NotificationChannel.INTERNAL:
                window = 86400
            else:
                return  # No limit for MQTT
            
            key = f"rate_limit:{channel}:{user_id}"
            redis_client.incr(key)
            redis_client.expire(key, window)
            
        except Exception as e:
            logger.error(f"Failed to increment rate limit: {e}")


# Global instance
notification_service = NotificationService()
