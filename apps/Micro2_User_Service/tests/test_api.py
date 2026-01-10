import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["service"] == "user-service"

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "service" in response.json()

def test_get_profile_without_token():
    """Test get profile without authentication"""
    response = client.get("/api/users/profile")
    assert response.status_code == 403

def test_create_profile_without_token():
    """Test create profile without authentication"""
    response = client.post(
        "/api/users/profile",
        json={"ciudad": "Quito"}
    )
    assert response.status_code == 403

def test_get_activity_without_token():
    """Test get activity without authentication"""
    response = client.get("/api/users/activity")
    assert response.status_code == 403
