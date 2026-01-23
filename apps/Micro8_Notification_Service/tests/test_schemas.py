"""
Test schemas validation
"""
import pytest
from pydantic import ValidationError
from app.schemas import (
    TemplateCreate, TemplateUpdate, NotificationSendRequest,
    PreferencesUpdate, InternalNotificationCreate
)
from app.models import NotificationChannel


def test_template_create_valid():
    """Test valid TemplateCreate schema"""
    data = {
        "name": "test_template",
        "channel": "email",
        "event_type": "test.event",
        "subject": "Test",
        "body": "Body {{var}}",
        "variables": ["var"]
    }
    
    template = TemplateCreate(**data)
    assert template.name == "test_template"
    assert template.channel == NotificationChannel.EMAIL


def test_template_create_invalid_channel():
    """Test TemplateCreate with invalid channel"""
    data = {
        "name": "test",
        "channel": "invalid_channel",
        "event_type": "test",
        "body": "test"
    }
    
    with pytest.raises(ValidationError):
        TemplateCreate(**data)


def test_notification_send_request():
    """Test NotificationSendRequest schema"""
    data = {
        "user_id": 1,
        "channel": "email",
        "template_name": "test_template",
        "variables": {"name": "Test User"}
    }
    
    request = NotificationSendRequest(**data)
    assert request.user_id == 1
    assert request.channel == NotificationChannel.EMAIL
    assert request.variables["name"] == "Test User"


def test_preferences_update():
    """Test PreferencesUpdate schema"""
    data = {
        "email_enabled": False,
        "quiet_hours_enabled": True,
        "quiet_hours_start": "22:00"
    }
    
    prefs = PreferencesUpdate(**data)
    assert prefs.email_enabled == False
    assert prefs.quiet_hours_enabled == True


def test_internal_notification_create():
    """Test InternalNotificationCreate schema"""
    data = {
        "title": "Test",
        "body": "Test body",
        "category": "appointment"
    }
    
    notif = InternalNotificationCreate(**data)
    assert notif.title == "Test"
    assert notif.category == "appointment"
