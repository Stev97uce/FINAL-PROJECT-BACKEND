import pytest
import os
from fastapi.testclient import TestClient

# Set environment variables before importing app
# Only set defaults if not already set (allows CI/CD to override)
if "DB_USER" not in os.environ:
    os.environ["DB_USER"] = "root"
if "DB_PASSWORD" not in os.environ:
    os.environ["DB_PASSWORD"] = "root123"
if "DB_HOST" not in os.environ:
    os.environ["DB_HOST"] = "localhost"
if "DB_PORT" not in os.environ:
    os.environ["DB_PORT"] = "3306"
if "DB_NAME" not in os.environ:
    os.environ["DB_NAME"] = "auth_db"
if "REDIS_HOST" not in os.environ:
    os.environ["REDIS_HOST"] = "localhost"
if "REDIS_PORT" not in os.environ:
    os.environ["REDIS_PORT"] = "6379"
if "RABBITMQ_HOST" not in os.environ:
    os.environ["RABBITMQ_HOST"] = "localhost"
if "RABBITMQ_PORT" not in os.environ:
    os.environ["RABBITMQ_PORT"] = "5672"
if "RABBITMQ_USER" not in os.environ:
    os.environ["RABBITMQ_USER"] = "guest"
if "RABBITMQ_PASSWORD" not in os.environ:
    os.environ["RABBITMQ_PASSWORD"] = "guest"
if "JWT_SECRET_KEY" not in os.environ:
    os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"
if "JWT_ALGORITHM" not in os.environ:
    os.environ["JWT_ALGORITHM"] = "HS256"

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
