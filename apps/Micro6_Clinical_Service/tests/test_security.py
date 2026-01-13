import pytest
from app.security import create_access_token, verify_token
from datetime import timedelta
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials


def test_create_access_token():
    """Test JWT token creation"""
    data = {"sub": "123", "email": "test@uce.edu.ec", "role": "admin"}
    token = create_access_token(data)
    
    assert isinstance(token, str)
    assert len(token) > 0


def test_create_access_token_with_expiration():
    """Test JWT token creation with custom expiration"""
    data = {"sub": "123", "email": "test@uce.edu.ec", "role": "admin"}
    token = create_access_token(data, expires_delta=timedelta(minutes=15))
    
    assert isinstance(token, str)
    assert len(token) > 0
