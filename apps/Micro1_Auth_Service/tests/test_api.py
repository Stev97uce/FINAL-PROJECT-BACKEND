import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["service"] == "auth-service"

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "service" in response.json()

def test_register_missing_fields():
    """Test registration with missing fields"""
    response = client.post(
        "/api/auth/register",
        json={"email": "test@test.com"}
    )
    assert response.status_code == 422

def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "nonexistent@test.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code in [400, 401]

def test_validate_without_token():
    """Test validate endpoint without token"""
    response = client.get("/api/auth/validate")
    assert response.status_code == 403

def test_refresh_without_token():
    """Test refresh endpoint without token"""
    response = client.post("/api/auth/refresh")
    assert response.status_code == 422
