"""
Unit tests for Supervision Service
"""
import pytest
from datetime import datetime
from app.models import SupervisionAssignment, SupervisionFeedback, SupervisionSession


def test_supervision_assignment_creation():
    """Test SupervisionAssignment model creation"""
    assignment = SupervisionAssignment(
        student_user_id=3,
        supervisor_user_id=2,
        specialty_area="Psicología Clínica",
        start_date=datetime.utcnow(),
        status="active"
    )
    assert assignment.student_user_id == 3
    assert assignment.supervisor_user_id == 2
    assert assignment.status == "active"
    assert assignment.specialty_area == "Psicología Clínica"


def test_supervision_feedback_creation():
    """Test SupervisionFeedback model creation"""
    feedback = SupervisionFeedback(
        assignment_id=1,
        session_note_id="6964fe374f1147f710343c14",
        supervisor_id=2,
        student_id=3,
        feedback_text="Excelente trabajo",
        strengths=["Empatía", "Técnicas"],
        areas_for_improvement=["Profundización"],
        rating=4
    )
    assert feedback.session_note_id == "6964fe374f1147f710343c14"
    assert feedback.rating == 4
    assert len(feedback.strengths) == 2
    assert feedback.is_read_by_student is False


def test_supervision_session_creation():
    """Test SupervisionSession model creation"""
    session = SupervisionSession(
        assignment_id=1,
        scheduled_date=datetime.utcnow(),
        duration_minutes=60,
        topic="Revisión de casos",
        status="scheduled"
    )
    assert session.assignment_id == 1
    assert session.duration_minutes == 60
    assert session.status == "scheduled"
    assert session.attendance_confirmed is False


def test_assignment_default_values():
    """Test default values in SupervisionAssignment"""
    assignment = SupervisionAssignment(
        student_user_id=1,
        supervisor_user_id=2,
        start_date=datetime.utcnow()
    )
    assert assignment.status == "active"
    assert assignment.created_at is not None
    assert assignment.updated_at is not None


def test_feedback_default_values():
    """Test default values in SupervisionFeedback"""
    feedback = SupervisionFeedback(
        assignment_id=1,
        session_note_id="6964fe374f1147f710343c14",
        supervisor_id=2,
        student_id=3,
        feedback_text="Test feedback"
    )
    assert feedback.is_read_by_student is False
    assert feedback.read_at is None
    assert feedback.reviewed_at is not None
    assert feedback.created_at is not None
