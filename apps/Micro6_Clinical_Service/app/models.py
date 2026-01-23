from beanie import Document, Link
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum
from beanie import PydanticObjectId


class RecordStatus(str, Enum):
    ACTIVE = "activo"
    CLOSED = "cerrado"
    PAUSED = "en_pausa"


class SessionType(str, Enum):
    INDIVIDUAL = "individual"
    GROUP = "grupal"
    FAMILY = "familiar"


class AttendanceStatus(str, Enum):
    ATTENDED = "asistio"
    JUSTIFIED_ABSENCE = "falta_justificada"
    UNJUSTIFIED_ABSENCE = "falta_injustificada"


class GoalStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    ACHIEVED = "achieved"
    MODIFIED = "modified"


class ProgressNote(BaseModel):
    """Progress note within a therapeutic goal (embedded document)"""
    note_date: datetime = Field(default_factory=datetime.utcnow)
    progress_description: str
    recorded_by: int  # user_id


class TherapeuticGoal(Document):
    """Therapeutic goals for clinical records"""
    clinical_record_id: PydanticObjectId
    goal_description: str
    target_date: Optional[datetime] = None
    status: GoalStatus = GoalStatus.PENDING
    progress_notes: List[ProgressNote] = Field(default_factory=list)
    created_by: int  # user_id
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "therapeutic_goals"
        indexes = [
            "clinical_record_id",
            "status",
            "created_by"
        ]


class SessionNote(Document):
    """Clinical session notes"""
    session_id: PydanticObjectId
    author_id: int  # user_id (student/professional)
    note_date: datetime = Field(default_factory=datetime.utcnow)
    presenting_problem: str  # Motivo de consulta
    session_summary: str  # Resumen de la sesión
    techniques_used: List[str] = Field(default_factory=list)
    interventions: List[str] = Field(default_factory=list)
    homework_assigned: Optional[str] = None  # Tareas para casa
    progress_assessment: Optional[str] = None
    next_session_plan: Optional[str] = None
    supervisor_feedback_id: Optional[PydanticObjectId] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "session_notes"
        indexes = [
            "session_id",
            "author_id",
            "note_date"
        ]


class Session(Document):
    """Clinical session record"""
    clinical_record_id: PydanticObjectId
    appointment_id: Optional[str] = None  # UUID from Appointment Service
    session_number: int
    session_date: datetime
    duration_minutes: int = 60
    session_type: SessionType = SessionType.INDIVIDUAL
    attendance_status: AttendanceStatus = AttendanceStatus.ATTENDED
    notes_id: Optional[PydanticObjectId] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "sessions"
        indexes = [
            "clinical_record_id",
            "appointment_id",
            "session_date",
            "attendance_status"
        ]


class ClinicalRecord(Document):
    """Main clinical record for a patient"""
    patient_id: int  # Reference to Patient Service
    therapist_id: int  # Professional assigned
    status: RecordStatus = RecordStatus.ACTIVE
    opening_date: datetime = Field(default_factory=datetime.utcnow)
    closing_date: Optional[datetime] = None
    diagnosis: List[str] = Field(default_factory=list)
    treatment_plan: Optional[str] = None
    additional_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "clinical_records"
        indexes = [
            "patient_id",
            "therapist_id",
            "status",
            "opening_date"
        ]
