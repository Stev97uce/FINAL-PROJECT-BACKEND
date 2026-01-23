from fastapi import Depends
from typing import Optional
from app.security import get_current_user


async def get_current_user_id(current_user: dict = Depends(get_current_user)) -> int:
    """Get current user ID from token"""
    return current_user["id"]


async def get_current_user_role(current_user: dict = Depends(get_current_user)) -> str:
    """Get current user role from token"""
    return current_user["role"]
