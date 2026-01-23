"""
SQLAlchemy models for Supervision Service
Following Single Responsibility Principle - each model has one clear purpose
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class SupervisionAssignment(Base):
    """
    Assignment of a student to a supervisor
    Single Responsibility: Manage student-supervisor relationships
    """
    __tablename__ = "supervision_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    student_user_id = Column(Integer, nullable=False, index=True)  # From User Service
    supervisor_user_id = Column(Integer, nullable=False, index=True)  # From User Service
    specialty_area = Column(String(100), nullable=True)  # Clinical psychology, educational, etc.
    start_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False, default="active")  # active, completed, cancelled
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    feedbacks = relationship("SupervisionFeedback", back_populates="assignment", cascade="all, delete-orphan")
    sessions = relationship("SupervisionSession", back_populates="assignment", cascade="all, delete-orphan")


class SupervisionFeedback(Base):
    """
    Feedback provided by supervisor on student's clinical session notes
    Single Responsibility: Store and manage supervisor feedback
    """
    __tablename__ = "supervision_feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("supervision_assignments.id"), nullable=False, index=True)
    session_note_id = Column(String(50), nullable=False, index=True)  # MongoDB ObjectId from Clinical Service
    supervisor_id = Column(Integer, nullable=False, index=True)
    student_id = Column(Integer, nullable=False, index=True)
    
    # Feedback content
    feedback_text = Column(Text, nullable=False)
    strengths = Column(JSON, nullable=True)  # List of strengths observed
    areas_for_improvement = Column(JSON, nullable=True)  # List of areas to work on
    recommendations = Column(Text, nullable=True)
    rating = Column(Integer, nullable=True)  # 1-5 rating
    
    # Status
    is_read_by_student = Column(Boolean, nullable=False, default=False)
    read_at = Column(DateTime, nullable=True)
    
    # Timestamps
    reviewed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assignment = relationship("SupervisionAssignment", back_populates="feedbacks")


class SupervisionSession(Base):
    """
    Scheduled supervision meetings between student and supervisor
    Single Responsibility: Manage supervision meeting scheduling
    """
    __tablename__ = "supervision_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("supervision_assignments.id"), nullable=False, index=True)
    scheduled_date = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer, nullable=False, default=60)
    topic = Column(String(200), nullable=True)
    meeting_notes = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="scheduled")  # scheduled, completed, cancelled, rescheduled
    attendance_confirmed = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assignment = relationship("SupervisionAssignment", back_populates="sessions")
