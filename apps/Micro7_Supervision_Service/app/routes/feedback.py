"""
Supervision Feedback routes
Single Responsibility: Handle HTTP requests for feedback operations
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import SupervisionFeedback, SupervisionAssignment
from app.schemas import (
    SupervisionFeedbackCreate,
    SupervisionFeedbackUpdate,
    SupervisionFeedbackResponse,
    MessageResponse
)
from app.security import get_current_user, require_role, get_current_user_id
from app.events import publish_feedback_added
import httpx

router = APIRouter(prefix="/feedback", tags=["Supervision Feedback"])


@router.post("", response_model=SupervisionFeedbackResponse, status_code=status.HTTP_201_CREATED)
async def create_feedback(
    feedback_data: SupervisionFeedbackCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    current_user: dict = Depends(require_role("psicologo_supervisor", "admin"))
):
    """
    Create supervisor feedback on a session note
    Integration with Clinical Service: Updates session_note.supervisor_feedback_id
    """
    # Verify assignment exists and supervisor is authorized
    assignment = db.query(SupervisionAssignment).filter(
        SupervisionAssignment.id == feedback_data.assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Verify supervisor is authorized for this assignment
    if current_user.get("role") != "admin" and assignment.supervisor_user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the assigned supervisor can provide feedback"
        )
    
    # Check if feedback already exists for this session note
    existing = db.query(SupervisionFeedback).filter(
        SupervisionFeedback.session_note_id == feedback_data.session_note_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Feedback already exists for this session note"
        )
    
    feedback = SupervisionFeedback(
        assignment_id=feedback_data.assignment_id,
        session_note_id=feedback_data.session_note_id,
        supervisor_id=current_user_id,
        student_id=feedback_data.student_id,
        feedback_text=feedback_data.feedback_text,
        strengths=feedback_data.strengths,
        areas_for_improvement=feedback_data.areas_for_improvement,
        recommendations=feedback_data.recommendations,
        rating=feedback_data.rating,
        reviewed_at=datetime.utcnow()
    )
    
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    
    # Publish event for Clinical Service and Notification Service
    publish_feedback_added(
        feedback_id=feedback.id,
        session_note_id=feedback.session_note_id,
        supervisor_id=feedback.supervisor_id,
        student_id=feedback.student_id,
        assignment_id=feedback.assignment_id,
        reviewed_at=feedback.reviewed_at.isoformat()
    )
    
    # Update Clinical Service session note with feedback_id
    try:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"http://clinical_service:8005/api/v1/session-notes/{feedback.session_note_id}/feedback",
                params={"feedback_id": str(feedback.id)},
                headers={"Authorization": f"Bearer {current_user.get('token', '')}"}
            )
            if response.status_code != 200:
                # Log error but don't fail the request
                print(f"Warning: Failed to update Clinical Service: {response.status_code}")
    except Exception as e:
        # Log error but don't fail the request
        print(f"Warning: Could not connect to Clinical Service: {e}")
    
    return feedback


@router.get("", response_model=List[SupervisionFeedbackResponse])
async def list_feedback(
    assignment_id: Optional[int] = Query(None),
    session_note_id: Optional[str] = Query(None),
    student_id: Optional[int] = Query(None),
    supervisor_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List feedback with optional filters
    Students can only see their own feedback
    Supervisors can see feedback they created
    """
    query = db.query(SupervisionFeedback)
    
    user_role = current_user.get("role")
    user_id = current_user.get("user_id")
    
    # Role-based filtering
    if user_role == "estudiante":
        query = query.filter(SupervisionFeedback.student_id == user_id)
    elif user_role == "psicologo_supervisor":
        query = query.filter(SupervisionFeedback.supervisor_id == user_id)
    
    # Apply additional filters
    if assignment_id:
        query = query.filter(SupervisionFeedback.assignment_id == assignment_id)
    if session_note_id:
        query = query.filter(SupervisionFeedback.session_note_id == session_note_id)
    if student_id:
        query = query.filter(SupervisionFeedback.student_id == student_id)
    if supervisor_id:
        query = query.filter(SupervisionFeedback.supervisor_id == supervisor_id)
    
    feedback_list = query.order_by(SupervisionFeedback.reviewed_at.desc()).all()
    return feedback_list


@router.get("/{feedback_id}", response_model=SupervisionFeedbackResponse)
async def get_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get specific feedback by ID"""
    feedback = db.query(SupervisionFeedback).filter(
        SupervisionFeedback.id == feedback_id
    ).first()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    
    # Permission check
    user_role = current_user.get("role")
    user_id = current_user.get("user_id")
    
    if user_role == "estudiante" and feedback.student_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    elif user_role == "psicologo_supervisor" and feedback.supervisor_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return feedback


@router.put("/{feedback_id}", response_model=SupervisionFeedbackResponse)
async def update_feedback(
    feedback_id: int,
    feedback_data: SupervisionFeedbackUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    current_user: dict = Depends(require_role("psicologo_supervisor", "admin"))
):
    """Update feedback (only by the supervisor who created it)"""
    feedback = db.query(SupervisionFeedback).filter(
        SupervisionFeedback.id == feedback_id
    ).first()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    
    # Verify supervisor owns this feedback
    if current_user.get("role") != "admin" and feedback.supervisor_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the supervisor who created this feedback can update it"
        )
    
    # Update fields
    update_data = feedback_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(feedback, field, value)
    
    feedback.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(feedback)
    
    return feedback


@router.patch("/{feedback_id}/mark-read", response_model=MessageResponse)
async def mark_feedback_read(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
    current_user: dict = Depends(require_role("estudiante", "admin"))
):
    """Mark feedback as read by student"""
    feedback = db.query(SupervisionFeedback).filter(
        SupervisionFeedback.id == feedback_id
    ).first()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    
    # Verify student owns this feedback
    if current_user.get("role") != "admin" and feedback.student_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    feedback.is_read_by_student = True
    feedback.read_at = datetime.utcnow()
    feedback.updated_at = datetime.utcnow()
    
    db.commit()
    
    return MessageResponse(message="Feedback marked as read")


@router.delete("/{feedback_id}", response_model=MessageResponse)
async def delete_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    """Delete feedback (admin only)"""
    feedback = db.query(SupervisionFeedback).filter(
        SupervisionFeedback.id == feedback_id
    ).first()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    
    db.delete(feedback)
    db.commit()
    
    return MessageResponse(message="Feedback deleted successfully")
