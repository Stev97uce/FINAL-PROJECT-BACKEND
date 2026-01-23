from sqlalchemy.orm import Session
from fastapi import Depends
from .database import get_db
from .security import get_current_user

def get_db_session(db: Session = Depends(get_db)):
    """Dependency para obtener sesión de base de datos"""
    return db

def get_current_user_dependency(current_user: dict = Depends(get_current_user)):
    """Dependency para obtener usuario actual"""
    return current_user
