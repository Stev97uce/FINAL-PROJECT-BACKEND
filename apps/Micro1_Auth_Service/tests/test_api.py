import pytest
import os
from fastapi.testclient import TestClient

# Set environment variables before importing app
os.environ.setdefault("DB_USER", "test")
os.environ.setdefault("DB_PASSWORD", "test")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "3306")
os.environ.setdefault("DB_NAME", "test_db")
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_PORT", "6379")
os.environ.setdefault("RABBITMQ_HOST", "localhost")
os.environ.setdefault("RABBITMQ_PORT", "5672")
os.environ.setdefault("RABBITMQ_USER", "guest")
os.environ.setdefault("RABBITMQ_PASSWORD", "guest")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-testing-only")
os.environ.setdefault("JWT_ALGORITHM", "HS256")

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
