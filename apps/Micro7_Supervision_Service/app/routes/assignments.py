"""
Supervision Assignment routes
Single Responsibility: Handle HTTP requests for assignments
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import SupervisionAssignment
from app.schemas import (
    SupervisionAssignmentCreate,
    SupervisionAssignmentUpdate,
    SupervisionAssignmentResponse,
    MessageResponse
)
from app.security import get_current_user, require_role, get_current_user_id

router = APIRouter(prefix="/assignments", tags=["Supervision Assignments"])


@router.post("", response_model=SupervisionAssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    assignment_data: SupervisionAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "coordinador"))
):
    """
    Create a new supervision assignment
    Only coordinador and admin can create assignments
    """
    # Check if student already has an active assignment
    existing = db.query(SupervisionAssignment).filter(
        SupervisionAssignment.student_user_id == assignment_data.student_user_id,
        SupervisionAssignment.status == "active"
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Student already has an active supervision assignment with supervisor {existing.supervisor_user_id}"
        )
    
    assignment = SupervisionAssignment(
        student_user_id=assignment_data.student_user_id,
        supervisor_user_id=assignment_data.supervisor_user_id,
        specialty_area=assignment_data.specialty_area,
        start_date=assignment_data.start_date,
        end_date=assignment_data.end_date,
        notes=assignment_data.notes,
        status="active"
    )
    
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    
    return assignment


@router.get("", response_model=List[SupervisionAssignmentResponse])
async def list_assignments(
    student_user_id: Optional[int] = Query(None),
    supervisor_user_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List supervision assignments with optional filters
    Students can only see their own assignments
    Supervisors can see assignments where they are the supervisor
    Coordinators and admins can see all
    """
    query = db.query(SupervisionAssignment)
    
    user_role = current_user.get("role")
    user_id = current_user.get("user_id")
    
    # Role-based filtering
    if user_role == "estudiante":
        query = query.filter(SupervisionAssignment.student_user_id == user_id)
    elif user_role == "psicologo_supervisor":
        query = query.filter(SupervisionAssignment.supervisor_user_id == user_id)
    # coordinador and admin can see all
    
    # Apply additional filters
    if student_user_id:
        query = query.filter(SupervisionAssignment.student_user_id == student_user_id)
    if supervisor_user_id:
        query = query.filter(SupervisionAssignment.supervisor_user_id == supervisor_user_id)
    if status:
        query = query.filter(SupervisionAssignment.status == status)
    
    assignments = query.order_by(SupervisionAssignment.created_at.desc()).all()
    return assignments


@router.get("/{assignment_id}", response_model=SupervisionAssignmentResponse)
async def get_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific assignment by ID"""
    assignment = db.query(SupervisionAssignment).filter(
        SupervisionAssignment.id == assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Permission check
    user_role = current_user.get("role")
    user_id = current_user.get("user_id")
    
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
    
    return assignment


@router.put("/{assignment_id}", response_model=SupervisionAssignmentResponse)
async def update_assignment(
    assignment_id: int,
    assignment_data: SupervisionAssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "coordinador"))
):
    """Update an assignment"""
    assignment = db.query(SupervisionAssignment).filter(
        SupervisionAssignment.id == assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Update fields
    update_data = assignment_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(assignment, field, value)
    
    assignment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(assignment)
    
    return assignment


@router.patch("/{assignment_id}/deactivate", response_model=MessageResponse)
async def deactivate_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "coordinador"))
):
    """Deactivate/complete an assignment"""
    assignment = db.query(SupervisionAssignment).filter(
        SupervisionAssignment.id == assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    assignment.status = "completed"
    assignment.end_date = datetime.utcnow()
    assignment.updated_at = datetime.utcnow()
    
    db.commit()
    
    return MessageResponse(message="Assignment deactivated successfully")


@router.delete("/{assignment_id}", response_model=MessageResponse)
async def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    """Delete an assignment (admin only)"""
    assignment = db.query(SupervisionAssignment).filter(
        SupervisionAssignment.id == assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    db.delete(assignment)
    db.commit()
    
    return MessageResponse(message="Assignment deleted successfully")
