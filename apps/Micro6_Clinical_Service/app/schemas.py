from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models import RecordStatus, SessionType, AttendanceStatus, GoalStatus


# Clinical Record Schemas
class ClinicalRecordCreate(BaseModel):
    patient_id: int
    therapist_id: int
    diagnosis: List[str] = Field(default_factory=list)
    treatment_plan: Optional[str] = None
    additional_notes: Optional[str] = None


class ClinicalRecordUpdate(BaseModel):
    diagnosis: Optional[List[str]] = None
    treatment_plan: Optional[str] = None
    additional_notes: Optional[str] = None
    status: Optional[RecordStatus] = None


class ClinicalRecordResponse(BaseModel):
    id: str
    patient_id: int
    therapist_id: int
    status: RecordStatus
    opening_date: datetime
    closing_date: Optional[datetime]
    diagnosis: List[str]
    treatment_plan: Optional[str]
    additional_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Session Schemas
class SessionCreate(BaseModel):
    clinical_record_id: str
    appointment_id: Optional[str] = None
    session_number: int
    session_date: datetime
    duration_minutes: int = 60
    session_type: SessionType = SessionType.INDIVIDUAL
    attendance_status: AttendanceStatus = AttendanceStatus.ATTENDED


class SessionUpdate(BaseModel):
    session_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    session_type: Optional[SessionType] = None
    attendance_status: Optional[AttendanceStatus] = None


class SessionResponse(BaseModel):
    id: str
    clinical_record_id: str
    appointment_id: Optional[str]
    session_number: int
    session_date: datetime
    duration_minutes: int
    session_type: SessionType
    attendance_status: AttendanceStatus
    notes_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Session Note Schemas
class SessionNoteCreate(BaseModel):
    session_id: str
    presenting_problem: str
    session_summary: str
    techniques_used: List[str] = Field(default_factory=list)
    interventions: List[str] = Field(default_factory=list)
    homework_assigned: Optional[str] = None
    progress_assessment: Optional[str] = None
    next_session_plan: Optional[str] = None


class SessionNoteUpdate(BaseModel):
    presenting_problem: Optional[str] = None
    session_summary: Optional[str] = None
    techniques_used: Optional[List[str]] = None
    interventions: Optional[List[str]] = None
    homework_assigned: Optional[str] = None
    progress_assessment: Optional[str] = None
    next_session_plan: Optional[str] = None


class SessionNoteResponse(BaseModel):
    id: str
    session_id: str
    author_id: int
    note_date: datetime
    presenting_problem: str
    session_summary: str
    techniques_used: List[str]
    interventions: List[str]
    homework_assigned: Optional[str]
    progress_assessment: Optional[str]
    next_session_plan: Optional[str]
    supervisor_feedback_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Therapeutic Goal Schemas
class ProgressNoteCreate(BaseModel):
    progress_description: str


class ProgressNoteResponse(BaseModel):
    note_date: datetime
    progress_description: str
    recorded_by: int

    class Config:
        from_attributes = True


class TherapeuticGoalCreate(BaseModel):
    clinical_record_id: str
    goal_description: str
    target_date: Optional[datetime] = None


class TherapeuticGoalUpdate(BaseModel):
    goal_description: Optional[str] = None
    target_date: Optional[datetime] = None
    status: Optional[GoalStatus] = None


class TherapeuticGoalResponse(BaseModel):
    id: str
    clinical_record_id: str
    goal_description: str
    target_date: Optional[datetime]
    status: GoalStatus
    progress_notes: List[ProgressNoteResponse]
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Generic Responses
class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    detail: str
