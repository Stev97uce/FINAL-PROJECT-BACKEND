from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
from beanie import PydanticObjectId
from app.models import TherapeuticGoal, ClinicalRecord, GoalStatus, ProgressNote
from app.schemas import (
    TherapeuticGoalCreate,
    TherapeuticGoalUpdate,
    TherapeuticGoalResponse,
    ProgressNoteCreate,
    ProgressNoteResponse,
    MessageResponse
)
from app.security import get_current_user, require_role
from app.dependencies import get_current_user_id
from app.events import publish_goal_achieved

router = APIRouter(prefix="/therapeutic-goals", tags=["Therapeutic Goals"])


@router.post("", response_model=TherapeuticGoalResponse, status_code=status.HTTP_201_CREATED)
async def create_therapeutic_goal(
    goal_data: TherapeuticGoalCreate,
    current_user_id: int = Depends(get_current_user_id),
    current_user: dict = Depends(require_role("professional", "student", "admin"))
):
    """Create a new therapeutic goal"""
    # Validate clinical record exists
    if not PydanticObjectId.is_valid(goal_data.clinical_record_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid clinical record ID format"
        )
    
    record = await ClinicalRecord.get(PydanticObjectId(goal_data.clinical_record_id))
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical record not found"
        )
    
    goal = TherapeuticGoal(
        clinical_record_id=PydanticObjectId(goal_data.clinical_record_id),
        goal_description=goal_data.goal_description,
        target_date=goal_data.target_date,
        created_by=current_user_id
    )
    await goal.insert()
    
    return TherapeuticGoalResponse(
        id=str(goal.id),
        clinical_record_id=str(goal.clinical_record_id),
        goal_description=goal.goal_description,
        target_date=goal.target_date,
        status=goal.status,
        progress_notes=[],
        created_by=goal.created_by,
        created_at=goal.created_at,
        updated_at=goal.updated_at
    )


@router.get("", response_model=List[TherapeuticGoalResponse])
async def list_therapeutic_goals(
    clinical_record_id: str = None,
    status_filter: GoalStatus = None,
    current_user: dict = Depends(get_current_user)
):
    """List therapeutic goals with optional filters"""
    query = {}
    if clinical_record_id:
        if not PydanticObjectId.is_valid(clinical_record_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid clinical record ID format"
            )
        query["clinical_record_id"] = PydanticObjectId(clinical_record_id)
    if status_filter:
        query["status"] = status_filter
    
    goals = await TherapeuticGoal.find(query).sort("-created_at").to_list()
    
    return [
        TherapeuticGoalResponse(
            id=str(goal.id),
            clinical_record_id=str(goal.clinical_record_id),
            goal_description=goal.goal_description,
            target_date=goal.target_date,
            status=goal.status,
            progress_notes=[
                ProgressNoteResponse(
                    note_date=pn.note_date,
                    progress_description=pn.progress_description,
                    recorded_by=pn.recorded_by
                )
                for pn in goal.progress_notes
            ],
            created_by=goal.created_by,
            created_at=goal.created_at,
            updated_at=goal.updated_at
        )
        for goal in goals
    ]


@router.get("/{goal_id}", response_model=TherapeuticGoalResponse)
async def get_therapeutic_goal(
    goal_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific therapeutic goal by ID"""
    if not PydanticObjectId.is_valid(goal_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid goal ID format"
        )
    
    goal = await TherapeuticGoal.get(PydanticObjectId(goal_id))
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Therapeutic goal not found"
        )
    
    return TherapeuticGoalResponse(
        id=str(goal.id),
        clinical_record_id=str(goal.clinical_record_id),
        goal_description=goal.goal_description,
        target_date=goal.target_date,
        status=goal.status,
        progress_notes=[
            ProgressNoteResponse(
                note_date=pn.note_date,
                progress_description=pn.progress_description,
                recorded_by=pn.recorded_by
            )
            for pn in goal.progress_notes
        ],
        created_by=goal.created_by,
        created_at=goal.created_at,
        updated_at=goal.updated_at
    )


@router.put("/{goal_id}", response_model=TherapeuticGoalResponse)
async def update_therapeutic_goal(
    goal_id: str,
    goal_data: TherapeuticGoalUpdate,
    current_user: dict = Depends(require_role("professional", "student", "admin"))
):
    """Update a therapeutic goal"""
    if not PydanticObjectId.is_valid(goal_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid goal ID format"
        )
    
    goal = await TherapeuticGoal.get(PydanticObjectId(goal_id))
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Therapeutic goal not found"
        )
    
    # Update fields
    update_data = goal_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(goal, field, value)
    
    goal.updated_at = datetime.utcnow()
    await goal.save()
    
    # Publish event if achieved
    if goal.status == GoalStatus.ACHIEVED:
        publish_goal_achieved(str(goal.id), str(goal.clinical_record_id))
    
    return TherapeuticGoalResponse(
        id=str(goal.id),
        clinical_record_id=str(goal.clinical_record_id),
        goal_description=goal.goal_description,
        target_date=goal.target_date,
        status=goal.status,
        progress_notes=[
            ProgressNoteResponse(
                note_date=pn.note_date,
                progress_description=pn.progress_description,
                recorded_by=pn.recorded_by
            )
            for pn in goal.progress_notes
        ],
        created_by=goal.created_by,
        created_at=goal.created_at,
        updated_at=goal.updated_at
    )


@router.post("/{goal_id}/progress", response_model=MessageResponse)
async def add_progress_note(
    goal_id: str,
    progress_data: ProgressNoteCreate,
    current_user_id: int = Depends(get_current_user_id),
    current_user: dict = Depends(require_role("professional", "student", "admin"))
):
    """Add a progress note to a therapeutic goal"""
    if not PydanticObjectId.is_valid(goal_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid goal ID format"
        )
    
    goal = await TherapeuticGoal.get(PydanticObjectId(goal_id))
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Therapeutic goal not found"
        )
    
    progress_note = ProgressNote(
        progress_description=progress_data.progress_description,
        recorded_by=current_user_id
    )
    
    goal.progress_notes.append(progress_note)
    goal.updated_at = datetime.utcnow()
    await goal.save()
    
    return MessageResponse(message="Progress note added successfully")


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_therapeutic_goal(
    goal_id: str,
    current_user: dict = Depends(require_role("admin"))
):
    """Delete a therapeutic goal (admin only)"""
    if not PydanticObjectId.is_valid(goal_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid goal ID format"
        )
    
    goal = await TherapeuticGoal.get(PydanticObjectId(goal_id))
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Therapeutic goal not found"
        )
    
    await goal.delete()

