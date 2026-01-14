"""
MongoDB models using Beanie ODM
KISS principle: Simple, focused models
"""
from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class NotificationChannel(str, Enum):
    """Notification delivery channels"""
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    INTERNAL = "internal"
    MQTT = "mqtt"


class NotificationStatus(str, Enum):
    """Notification delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"


class NotificationPriority(str, Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class NotificationTemplate(Document):
    """
    Email/WhatsApp/Internal notification templates
    """
    name: Indexed(str, unique=True)  # e.g., "email_verification"
    channel: NotificationChannel
    event_type: str  # e.g., "user.registered"
    subject: Optional[str] = None  # For emails
    body: str  # Jinja2 template with {{variables}}
    variables: List[str] = []  # Required variables
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "notification_templates"
        indexes = [
            "event_type",
            "channel"
        ]


class NotificationLog(Document):
    """
    Delivery history and tracking
    """
    notification_id: Indexed(str)  # UUID
    user_id: Indexed(int)
    channel: NotificationChannel
    event_type: str
    status: NotificationStatus = NotificationStatus.PENDING
    template_id: Optional[str] = None
    recipient: str  # Email or phone number
    subject: Optional[str] = None
    body: str
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    next_retry_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "notification_logs"
        indexes = [
            "user_id",
            "status",
            "created_at",
            "next_retry_at"
        ]


class UserPreferences(Document):
    """
    User notification preferences per channel
    """
    user_id: Indexed(int, unique=True)
    email_enabled: bool = True
    whatsapp_enabled: bool = True
    internal_enabled: bool = True
    push_enabled: bool = True
    quiet_hours_enabled: bool = False
    quiet_hours_start: Optional[str] = "22:00"  # HH:MM format
    quiet_hours_end: Optional[str] = "08:00"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "user_preferences"


class InternalNotification(Document):
    """
    In-app notifications stored in MongoDB
    """
    user_id: Indexed(int)
    title: str
    body: str
    category: str  # "appointment", "supervision", "system"
    priority: NotificationPriority = NotificationPriority.MEDIUM
    is_read: bool = False
    read_at: Optional[datetime] = None
    action_url: Optional[str] = None
    metadata: Dict[str, Any] = {}
    created_at: Indexed(datetime) = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None  # TTL for auto-cleanup
    
    class Settings:
        name = "internal_notifications"
        indexes = [
            [("user_id", 1), ("is_read", 1)],
            [("user_id", 1), ("created_at", -1)]
        ]
