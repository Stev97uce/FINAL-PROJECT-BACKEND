from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
from beanie import PydanticObjectId
from app.models import Session, ClinicalRecord
from app.schemas import SessionCreate, SessionUpdate, SessionResponse, MessageResponse
from app.security import get_current_user, require_role
from app.dependencies import get_current_user_id
from app.events import publish_session_recorded

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    current_user_id: int = Depends(get_current_user_id),
    current_user: dict = Depends(require_role("professional", "student", "admin"))
):
    """Create a new session"""
    # Validate clinical record exists
    if not PydanticObjectId.is_valid(session_data.clinical_record_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid clinical record ID format"
        )
    
    record = await ClinicalRecord.get(PydanticObjectId(session_data.clinical_record_id))
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical record not found"
        )
    
    session = Session(
        clinical_record_id=PydanticObjectId(session_data.clinical_record_id),
        appointment_id=session_data.appointment_id,
        session_number=session_data.session_number,
        session_date=session_data.session_date,
        duration_minutes=session_data.duration_minutes,
        session_type=session_data.session_type,
        attendance_status=session_data.attendance_status
    )
    await session.insert()
    
    # Publish event
    publish_session_recorded(
        str(session.id),
        str(session.clinical_record_id),
        session.session_number
    )
    
    return SessionResponse(
        id=str(session.id),
        clinical_record_id=str(session.clinical_record_id),
        appointment_id=session.appointment_id,
        session_number=session.session_number,
        session_date=session.session_date,
        duration_minutes=session.duration_minutes,
        session_type=session.session_type,
        attendance_status=session.attendance_status,
        notes_id=str(session.notes_id) if session.notes_id else None,
        created_at=session.created_at,
        updated_at=session.updated_at
    )


@router.get("", response_model=List[SessionResponse])
async def list_sessions(
    clinical_record_id: str = None,
    current_user: dict = Depends(get_current_user)
):
    """List sessions with optional filter by clinical record"""
    query = {}
    if clinical_record_id:
        if not PydanticObjectId.is_valid(clinical_record_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid clinical record ID format"
            )
        query["clinical_record_id"] = PydanticObjectId(clinical_record_id)
    
    sessions = await Session.find(query).sort("-session_date").to_list()
    
    return [
        SessionResponse(
            id=str(session.id),
            clinical_record_id=str(session.clinical_record_id),
            appointment_id=session.appointment_id,
            session_number=session.session_number,
            session_date=session.session_date,
            duration_minutes=session.duration_minutes,
            session_type=session.session_type,
            attendance_status=session.attendance_status,
            notes_id=str(session.notes_id) if session.notes_id else None,
            created_at=session.created_at,
            updated_at=session.updated_at
        )
        for session in sessions
    ]


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific session by ID"""
    if not PydanticObjectId.is_valid(session_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID format"
        )
    
    session = await Session.get(PydanticObjectId(session_id))
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return SessionResponse(
        id=str(session.id),
        clinical_record_id=str(session.clinical_record_id),
        appointment_id=session.appointment_id,
        session_number=session.session_number,
        session_date=session.session_date,
        duration_minutes=session.duration_minutes,
        session_type=session.session_type,
        attendance_status=session.attendance_status,
        notes_id=str(session.notes_id) if session.notes_id else None,
        created_at=session.created_at,
        updated_at=session.updated_at
    )


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: str,
    session_data: SessionUpdate,
    current_user: dict = Depends(require_role("professional", "student", "admin"))
):
    """Update a session"""
    if not PydanticObjectId.is_valid(session_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID format"
        )
    
    session = await Session.get(PydanticObjectId(session_id))
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Update fields
    update_data = session_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(session, field, value)
    
    session.updated_at = datetime.utcnow()
    await session.save()
    
    return SessionResponse(
        id=str(session.id),
        clinical_record_id=str(session.clinical_record_id),
        appointment_id=session.appointment_id,
        session_number=session.session_number,
        session_date=session.session_date,
        duration_minutes=session.duration_minutes,
        session_type=session.session_type,
        attendance_status=session.attendance_status,
        notes_id=str(session.notes_id) if session.notes_id else None,
        created_at=session.created_at,
        updated_at=session.updated_at
    )


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: str,
    current_user: dict = Depends(require_role("admin"))
):
    """Delete a session (admin only)"""
    if not PydanticObjectId.is_valid(session_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID format"
        )
    
    session = await Session.get(PydanticObjectId(session_id))
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    await session.delete()

