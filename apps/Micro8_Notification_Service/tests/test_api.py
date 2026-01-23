"""
Test API endpoints
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint"""
    from app.main import app
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "notification-service"


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint"""
    from app.main import app
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "notification-service"
    assert data["status"] == "running"


@pytest.mark.asyncio
async def test_list_notifications_unauthorized():
    """Test listing notifications without auth"""
    from app.main import app
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/notifications")
    
    assert response.status_code == 403  # No auth header


@pytest.mark.asyncio
async def test_get_preferences_unauthorized():
    """Test getting preferences without auth"""
    from app.main import app
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/preferences")
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_templates_unauthorized():
    """Test listing templates without admin auth"""
    from app.main import app
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/admin/templates")
    
    assert response.status_code == 403
