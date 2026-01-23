"""
Supervision Session routes
Single Responsibility: Handle HTTP requests for supervision meetings
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import SupervisionSession, SupervisionAssignment
from app.schemas import (
    SupervisionSessionCreate,
    SupervisionSessionUpdate,
    SupervisionSessionResponse,
    MessageResponse
)
from app.security import get_current_user, require_role, get_current_user_id

router = APIRouter(prefix="/sessions", tags=["Supervision Sessions"])


@router.post("", response_model=SupervisionSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SupervisionSessionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("psicologo_supervisor", "admin"))
):
    """Create a new supervision session meeting"""
    # Verify assignment exists
    assignment = db.query(SupervisionAssignment).filter(
        SupervisionAssignment.id == session_data.assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    session = SupervisionSession(
        assignment_id=session_data.assignment_id,
        scheduled_date=session_data.scheduled_date,
        duration_minutes=session_data.duration_minutes,
        topic=session_data.topic,
        meeting_notes=session_data.meeting_notes,
        status="scheduled"
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return session


@router.get("", response_model=List[SupervisionSessionResponse])
async def list_sessions(
    assignment_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List supervision sessions with optional filters"""
    query = db.query(SupervisionSession)
    
    user_role = current_user.get("role")
    user_id = current_user.get("user_id")
    
    # Role-based filtering
    if user_role in ["estudiante", "psicologo_supervisor"]:
        # Get assignments where user is student or supervisor
        if user_role == "estudiante":
            assignments = db.query(SupervisionAssignment).filter(
                SupervisionAssignment.student_user_id == user_id
            ).all()
        else:
            assignments = db.query(SupervisionAssignment).filter(
                SupervisionAssignment.supervisor_user_id == user_id
            ).all()
        
        assignment_ids = [a.id for a in assignments]
        query = query.filter(SupervisionSession.assignment_id.in_(assignment_ids))
    
    # Apply additional filters
    if assignment_id:
        query = query.filter(SupervisionSession.assignment_id == assignment_id)
    if status:
        query = query.filter(SupervisionSession.status == status)
    
    sessions = query.order_by(SupervisionSession.scheduled_date.desc()).all()
    return sessions


@router.get("/{session_id}", response_model=SupervisionSessionResponse)
async def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific supervision session by ID"""
    session = db.query(SupervisionSession).filter(
        SupervisionSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Permission check
    user_role = current_user.get("role")
    user_id = current_user.get("user_id")
    
    if user_role in ["estudiante", "psicologo_supervisor"]:
        assignment = db.query(SupervisionAssignment).filter(
            SupervisionAssignment.id == session.assignment_id
        ).first()
        
        if user_role == "estudiante" and assignment.student_user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        elif user_role == "psicologo_supervisor" and assignment.supervisor_user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    return session


@router.put("/{session_id}", response_model=SupervisionSessionResponse)
async def update_session(
    session_id: int,
    session_data: SupervisionSessionUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("psicologo_supervisor", "admin"))
):
    """Update a supervision session"""
    session = db.query(SupervisionSession).filter(
        SupervisionSession.id == session_id
    ).first()
    
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
    db.commit()
    db.refresh(session)
    
    return session


@router.patch("/{session_id}/confirm", response_model=MessageResponse)
async def confirm_attendance(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("estudiante", "psicologo_supervisor", "admin"))
):
    """Confirm attendance for a supervision session"""
    session = db.query(SupervisionSession).filter(
        SupervisionSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    session.attendance_confirmed = True
    session.updated_at = datetime.utcnow()
    db.commit()
    
    return MessageResponse(message="Attendance confirmed")


@router.patch("/{session_id}/complete", response_model=MessageResponse)
async def complete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("psicologo_supervisor", "admin"))
):
    """Mark session as completed"""
    session = db.query(SupervisionSession).filter(
        SupervisionSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    session.status = "completed"
    session.updated_at = datetime.utcnow()
    db.commit()
    
    return MessageResponse(message="Session marked as completed")


@router.delete("/{session_id}", response_model=MessageResponse)
async def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("psicologo_supervisor", "admin"))
):
    """Delete a supervision session"""
    session = db.query(SupervisionSession).filter(
        SupervisionSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    db.delete(session)
    db.commit()
    
    return MessageResponse(message="Session deleted successfully")
