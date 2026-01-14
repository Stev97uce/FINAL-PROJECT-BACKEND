"""
Test models
"""
import pytest
from datetime import datetime
from app.models import (
    NotificationTemplate, NotificationLog, UserPreferences,
    InternalNotification, NotificationChannel, NotificationStatus
)


def test_notification_template_creation():
    """Test NotificationTemplate model creation"""
    template = NotificationTemplate(
        name="test_template",
        channel=NotificationChannel.EMAIL,
        event_type="test.event",
        subject="Test Subject",
        body="Test body with {{variable}}",
        variables=["variable"],
        active=True
    )
    
    assert template.name == "test_template"
    assert template.channel == NotificationChannel.EMAIL
    assert template.active == True
    assert "variable" in template.variables


def test_notification_log_creation():
    """Test NotificationLog model creation"""
    log = NotificationLog(
        notification_id="test-uuid",
        user_id=1,
        channel=NotificationChannel.EMAIL,
        event_type="test.event",
        recipient="test@example.com",
        subject="Test",
        body="Body",
        status=NotificationStatus.PENDING
    )
    
    assert log.notification_id == "test-uuid"
    assert log.user_id == 1
    assert log.status == NotificationStatus.PENDING
    assert log.retry_count == 0


def test_user_preferences_defaults():
    """Test UserPreferences default values"""
    prefs = UserPreferences(user_id=1)
    
    assert prefs.user_id == 1
    assert prefs.email_enabled == True
    assert prefs.whatsapp_enabled == True
    assert prefs.internal_enabled == True
    assert prefs.push_enabled == True
    assert prefs.quiet_hours_enabled == False


def test_internal_notification_creation():
    """Test InternalNotification model creation"""
    notification = InternalNotification(
        user_id=1,
        title="Test Notification",
        body="Test body",
        category="system",
        is_read=False
    )
    
    assert notification.user_id == 1
    assert notification.title == "Test Notification"
    assert notification.is_read == False
    assert notification.category == "system"
