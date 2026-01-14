"""
Pydantic schemas for request/response validation
KISS principle: Simple validation schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models import NotificationChannel, NotificationStatus, NotificationPriority


# Template Schemas
class TemplateCreate(BaseModel):
    name: str
    channel: NotificationChannel
    event_type: str
    subject: Optional[str] = None
    body: str
    variables: List[str] = []
    active: bool = True


class TemplateUpdate(BaseModel):
    subject: Optional[str] = None
    body: Optional[str] = None
    variables: Optional[List[str]] = None
    active: Optional[bool] = None


class TemplateResponse(BaseModel):
    id: str
    name: str
    channel: NotificationChannel
    event_type: str
    subject: Optional[str]
    body: str
    variables: List[str]
    active: bool
    created_at: datetime


# Notification Schemas
class NotificationSendRequest(BaseModel):
    user_id: int
    channel: NotificationChannel
    template_name: str
    variables: Dict[str, Any] = {}
    recipient: Optional[str] = None  # Override recipient


class NotificationResponse(BaseModel):
    id: str
    user_id: int
    title: str
    body: str
    category: str
    priority: NotificationPriority
    is_read: bool
    action_url: Optional[str]
    created_at: datetime


class InternalNotificationCreate(BaseModel):
    title: str
    body: str
    category: str = "system"
    priority: NotificationPriority = NotificationPriority.MEDIUM
    action_url: Optional[str] = None


# Preferences Schemas
class PreferencesUpdate(BaseModel):
    email_enabled: Optional[bool] = None
    whatsapp_enabled: Optional[bool] = None
    internal_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None


class PreferencesResponse(BaseModel):
    user_id: int
    email_enabled: bool
    whatsapp_enabled: bool
    internal_enabled: bool
    push_enabled: bool
    quiet_hours_enabled: bool
    quiet_hours_start: Optional[str]
    quiet_hours_end: Optional[str]


# Delivery Log Schemas
class DeliveryLogResponse(BaseModel):
    id: str
    notification_id: str
    user_id: int
    channel: NotificationChannel
    status: NotificationStatus
    recipient: str
    subject: Optional[str]
    sent_at: Optional[datetime]
    error_message: Optional[str]
    retry_count: int
    created_at: datetime


# Stats Schema
class StatsResponse(BaseModel):
    total_sent: int
    total_delivered: int
    total_failed: int
    by_channel: Dict[str, int]
    by_status: Dict[str, int]
