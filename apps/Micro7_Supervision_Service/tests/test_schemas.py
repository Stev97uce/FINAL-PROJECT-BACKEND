"""
Unit tests for Pydantic schemas
"""
import pytest
from pydantic import ValidationError
from app.schemas import (
    SupervisionAssignmentCreate,
    SupervisionFeedbackCreate,
    SupervisionSessionCreate
)
from datetime import datetime


def test_assignment_create_valid():
    """Test valid assignment creation schema"""
    data = {
        "student_user_id": 3,
        "supervisor_user_id": 2,
        "specialty_area": "Psicología Clínica",
        "start_date": datetime.utcnow()
    }
    assignment = SupervisionAssignmentCreate(**data)
    assert assignment.student_user_id == 3
    assert assignment.supervisor_user_id == 2


def test_feedback_create_valid():
    """Test valid feedback creation schema"""
    data = {
        "assignment_id": 1,
        "session_note_id": "6964fe374f1147f710343c14",
        "student_id": 3,
        "feedback_text": "Excelente trabajo en la sesión",
        "strengths": ["Empatía", "Técnicas"],
        "rating": 4
    }
    feedback = SupervisionFeedbackCreate(**data)
    assert feedback.session_note_id == "6964fe374f1147f710343c14"
    assert feedback.rating == 4


def test_feedback_invalid_objectid():
    """Test feedback with invalid MongoDB ObjectId"""
    data = {
        "assignment_id": 1,
        "session_note_id": "invalid",  # Too short
        "student_id": 3,
        "feedback_text": "Test"
    }
    with pytest.raises(ValidationError):
        SupervisionFeedbackCreate(**data)


def test_feedback_invalid_rating():
    """Test feedback with invalid rating"""
    data = {
        "assignment_id": 1,
        "session_note_id": "6964fe374f1147f710343c14",
        "student_id": 3,
        "feedback_text": "Test",
        "rating": 6  # Should be 1-5
    }
    with pytest.raises(ValidationError):
        SupervisionFeedbackCreate(**data)


def test_session_create_valid():
    """Test valid session creation schema"""
    data = {
        "assignment_id": 1,
        "scheduled_date": datetime.utcnow(),
        "duration_minutes": 60
    }
    session = SupervisionSessionCreate(**data)
    assert session.assignment_id == 1
    assert session.duration_minutes == 60


def test_session_invalid_duration():
    """Test session with invalid duration"""
    data = {
        "assignment_id": 1,
        "scheduled_date": datetime.utcnow(),
        "duration_minutes": 10  # Less than 15
    }
    with pytest.raises(ValidationError):
        SupervisionSessionCreate(**data)


def test_feedback_short_text():
    """Test feedback with too short text"""
    data = {
        "assignment_id": 1,
        "session_note_id": "6964fe374f1147f710343c14",
        "student_id": 3,
        "feedback_text": "Short"  # Less than 10 characters
    }
    with pytest.raises(ValidationError):
        SupervisionFeedbackCreate(**data)
