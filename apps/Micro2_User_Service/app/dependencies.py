from fastapi import Depends
from app.database import get_db
from app.security import get_current_user
from sqlalchemy.orm import Session
from typing import Dict, Any

def get_db_session() -> Session:
    """Alias for database dependency"""
    return Depends(get_db)

def get_authenticated_user() -> Dict[str, Any]:
    """Alias for authentication dependency"""
    return Depends(get_current_user)
