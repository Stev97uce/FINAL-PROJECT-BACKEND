"""
Test configuration
"""
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.fixture
def admin_token():
    """Mock admin JWT token"""
    from jose import jwt
    from app.config import settings
    
    payload = {
        "user_id": 1,
        "email": "admin@uce.edu.ec",
        "rol": "administrador"
    }
    
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token


@pytest.fixture
def user_token():
    """Mock user JWT token"""
    from jose import jwt
    from app.config import settings
    
    payload = {
        "user_id": 2,
        "email": "user@uce.edu.ec",
        "rol": "consultante"
    }
    
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token


@pytest.fixture
async def client():
    """Async HTTP client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
