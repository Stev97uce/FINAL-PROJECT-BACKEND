"""
Integration tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "Supervision Service"
    assert data["version"] == "1.0.0"


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Supervision Service"
    assert data["version"] == "1.0.0"
    assert data["docs"] == "/docs"


def test_assignments_unauthorized():
    """Test assignments endpoint without authentication"""
    response = client.get("/api/v1/assignments")
    assert response.status_code == 403  # No token provided


def test_feedback_unauthorized():
    """Test feedback endpoint without authentication"""
    response = client.get("/api/v1/feedback")
    assert response.status_code == 403


def test_sessions_unauthorized():
    """Test sessions endpoint without authentication"""
    response = client.get("/api/v1/sessions")
    assert response.status_code == 403


def test_invalid_endpoint():
    """Test non-existent endpoint"""
    response = client.get("/api/v1/nonexistent")
    assert response.status_code == 404
