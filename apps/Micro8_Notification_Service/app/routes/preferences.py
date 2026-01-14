"""
User preferences endpoints
KISS principle: Simple preference management
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict
from app.dependencies import get_current_user
from app.models import UserPreferences
from app.schemas import PreferencesUpdate, PreferencesResponse
from datetime import datetime

router = APIRouter(prefix="/api/v1/preferences", tags=["preferences"])


@router.get("", response_model=PreferencesResponse)
async def get_preferences(
    current_user: Dict = Depends(get_current_user)
):
    """Get user's notification preferences"""
    user_id = current_user["user_id"]
    
    prefs = await UserPreferences.find_one(UserPreferences.user_id == user_id)
    
    if not prefs:
        # Create default preferences
        prefs = UserPreferences(user_id=user_id)
        await prefs.insert()
    
    return PreferencesResponse(
        user_id=prefs.user_id,
        email_enabled=prefs.email_enabled,
        whatsapp_enabled=prefs.whatsapp_enabled,
        internal_enabled=prefs.internal_enabled,
        push_enabled=prefs.push_enabled,
        quiet_hours_enabled=prefs.quiet_hours_enabled,
        quiet_hours_start=prefs.quiet_hours_start,
        quiet_hours_end=prefs.quiet_hours_end
    )


@router.put("", response_model=PreferencesResponse)
async def update_preferences(
    preferences: PreferencesUpdate,
    current_user: Dict = Depends(get_current_user)
):
    """Update user's notification preferences"""
    user_id = current_user["user_id"]
    
    prefs = await UserPreferences.find_one(UserPreferences.user_id == user_id)
    
    if not prefs:
        prefs = UserPreferences(user_id=user_id)
    
    # Update fields
    update_data = preferences.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(prefs, key, value)
    
    prefs.updated_at = datetime.utcnow()
    
    if prefs.id:
        await prefs.save()
    else:
        await prefs.insert()
    
    return PreferencesResponse(
        user_id=prefs.user_id,
        email_enabled=prefs.email_enabled,
        whatsapp_enabled=prefs.whatsapp_enabled,
        internal_enabled=prefs.internal_enabled,
        push_enabled=prefs.push_enabled,
        quiet_hours_enabled=prefs.quiet_hours_enabled,
        quiet_hours_start=prefs.quiet_hours_start,
        quiet_hours_end=prefs.quiet_hours_end
    )
