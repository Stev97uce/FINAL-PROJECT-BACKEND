"""
Pydantic schemas for request/response validation
Interface Segregation Principle - specific schemas for different operations
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


# ==================== Supervision Assignment Schemas ====================

class SupervisionAssignmentCreate(BaseModel):
    """Schema for creating a new supervision assignment"""
    student_user_id: int = Field(..., description="Student user ID from User Service")
    supervisor_user_id: int = Field(..., description="Supervisor user ID from User Service")
    specialty_area: Optional[str] = Field(None, max_length=100)
    start_date: datetime
    end_date: Optional[datetime] = None
    notes: Optional[str] = None


class SupervisionAssignmentUpdate(BaseModel):
    """Schema for updating an assignment"""
    specialty_area: Optional[str] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class SupervisionAssignmentResponse(BaseModel):
    """Schema for assignment response"""
    id: int
    student_user_id: int
    supervisor_user_id: int
    specialty_area: Optional[str]
    start_date: datetime
    end_date: Optional[datetime]
    status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Supervision Feedback Schemas ====================

class SupervisionFeedbackCreate(BaseModel):
    """Schema for creating supervisor feedback"""
    assignment_id: int
    session_note_id: str = Field(..., description="MongoDB ObjectId from Clinical Service")
    student_id: int
    feedback_text: str = Field(..., min_length=10)
    strengths: Optional[List[str]] = Field(default_factory=list)
    areas_for_improvement: Optional[List[str]] = Field(default_factory=list)
    recommendations: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    
    @field_validator('session_note_id')
    @classmethod
    def validate_object_id(cls, v):
        """Validate MongoDB ObjectId format"""
        if len(v) != 24:
            raise ValueError('Invalid MongoDB ObjectId format')
        return v


class SupervisionFeedbackUpdate(BaseModel):
    """Schema for updating feedback"""
    feedback_text: Optional[str] = Field(None, min_length=10)
    strengths: Optional[List[str]] = None
    areas_for_improvement: Optional[List[str]] = None
    recommendations: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)


class SupervisionFeedbackResponse(BaseModel):
    """Schema for feedback response"""
    id: int
    assignment_id: int
    session_note_id: str
    supervisor_id: int
    student_id: int
    feedback_text: str
    strengths: Optional[List[str]]
    areas_for_improvement: Optional[List[str]]
    recommendations: Optional[str]
    rating: Optional[int]
    is_read_by_student: bool
    read_at: Optional[datetime]
    reviewed_at: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Supervision Session Schemas ====================

class SupervisionSessionCreate(BaseModel):
    """Schema for creating a supervision session"""
    assignment_id: int
    scheduled_date: datetime
    duration_minutes: int = Field(default=60, ge=15, le=240)
    topic: Optional[str] = Field(None, max_length=200)
    meeting_notes: Optional[str] = None


class SupervisionSessionUpdate(BaseModel):
    """Schema for updating a session"""
    scheduled_date: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=15, le=240)
    topic: Optional[str] = None
    meeting_notes: Optional[str] = None
    status: Optional[str] = None
    attendance_confirmed: Optional[bool] = None


class SupervisionSessionResponse(BaseModel):
    """Schema for session response"""
    id: int
    assignment_id: int
    scheduled_date: datetime
    duration_minutes: int
    topic: Optional[str]
    meeting_notes: Optional[str]
    status: str
    attendance_confirmed: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Generic Schemas ====================

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str


class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str


# ==================== Event Schemas ====================

class ClinicalSessionRecordedEvent(BaseModel):
    """Event schema for clinical.session_recorded from Clinical Service"""
    session_note_id: str
    session_id: str
    student_id: int
    clinical_record_id: str
    recorded_at: datetime


class SupervisionFeedbackAddedEvent(BaseModel):
    """Event schema for supervision.feedback_added"""
    feedback_id: int
    session_note_id: str
    supervisor_id: int
    student_id: int
    assignment_id: int
    reviewed_at: datetime
