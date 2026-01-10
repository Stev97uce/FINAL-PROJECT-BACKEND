import pytest
import os
from fastapi.testclient import TestClient

# Set environment variables before importing app
os.environ.setdefault("DB_USER", "test")
os.environ.setdefault("DB_PASSWORD", "test")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_NAME", "test_db")
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_PORT", "6379")
os.environ.setdefault("RABBITMQ_HOST", "localhost")
os.environ.setdefault("RABBITMQ_PORT", "5672")
os.environ.setdefault("RABBITMQ_USER", "guest")
os.environ.setdefault("RABBITMQ_PASSWORD", "guest")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-testing-only")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("AUTH_SERVICE_URL", "http://localhost:8000")

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
