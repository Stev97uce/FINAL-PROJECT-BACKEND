from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
from beanie import PydanticObjectId
from app.models import SessionNote, Session
from app.schemas import (
    SessionNoteCreate,
    SessionNoteUpdate,
    SessionNoteResponse,
    MessageResponse
)
from app.security import get_current_user, require_role
from app.dependencies import get_current_user_id
from app.events import publish_note_created

router = APIRouter(prefix="/session-notes", tags=["Session Notes"])


@router.post("", response_model=SessionNoteResponse, status_code=status.HTTP_201_CREATED)
async def create_session_note(
    note_data: SessionNoteCreate,
    current_user_id: int = Depends(get_current_user_id),
    current_user: dict = Depends(require_role("professional", "student", "admin"))
):
    """Create a new session note"""
    # Validate session exists
    if not PydanticObjectId.is_valid(note_data.session_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID format"
        )
    
    session = await Session.get(PydanticObjectId(note_data.session_id))
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    note = SessionNote(
        session_id=PydanticObjectId(note_data.session_id),
        author_id=current_user_id,
        presenting_problem=note_data.presenting_problem,
        session_summary=note_data.session_summary,
        techniques_used=note_data.techniques_used,
        interventions=note_data.interventions,
        homework_assigned=note_data.homework_assigned,
        progress_assessment=note_data.progress_assessment,
        next_session_plan=note_data.next_session_plan
    )
    await note.insert()
    
    # Update session with note ID
    session.notes_id = note.id
    await session.save()
    
    # Publish event
    publish_note_created(
        str(note.id),
        str(note.session_id),
        note.author_id
    )
    
    return SessionNoteResponse(
        id=str(note.id),
        session_id=str(note.session_id),
        author_id=note.author_id,
        note_date=note.note_date,
        presenting_problem=note.presenting_problem,
        session_summary=note.session_summary,
        techniques_used=note.techniques_used,
        interventions=note.interventions,
        homework_assigned=note.homework_assigned,
        progress_assessment=note.progress_assessment,
        next_session_plan=note.next_session_plan,
        supervisor_feedback_id=str(note.supervisor_feedback_id) if note.supervisor_feedback_id else None,
        created_at=note.created_at,
        updated_at=note.updated_at
    )


@router.get("", response_model=List[SessionNoteResponse])
async def list_session_notes(
    session_id: str = None,
    author_id: int = None,
    current_user: dict = Depends(get_current_user)
):
    """List session notes with optional filters"""
    query = {}
    if session_id:
        if not PydanticObjectId.is_valid(session_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid session ID format"
            )
        query["session_id"] = PydanticObjectId(session_id)
    if author_id:
        query["author_id"] = author_id
    
    notes = await SessionNote.find(query).sort("-note_date").to_list()
    
    return [
        SessionNoteResponse(
            id=str(note.id),
            session_id=str(note.session_id),
            author_id=note.author_id,
            note_date=note.note_date,
            presenting_problem=note.presenting_problem,
            session_summary=note.session_summary,
            techniques_used=note.techniques_used,
            interventions=note.interventions,
            homework_assigned=note.homework_assigned,
            progress_assessment=note.progress_assessment,
            next_session_plan=note.next_session_plan,
            supervisor_feedback_id=str(note.supervisor_feedback_id) if note.supervisor_feedback_id else None,
            created_at=note.created_at,
            updated_at=note.updated_at
        )
        for note in notes
    ]


@router.get("/{note_id}", response_model=SessionNoteResponse)
async def get_session_note(
    note_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific session note by ID"""
    if not PydanticObjectId.is_valid(note_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid note ID format"
        )
    
    note = await SessionNote.get(PydanticObjectId(note_id))
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session note not found"
        )
    
    return SessionNoteResponse(
        id=str(note.id),
        session_id=str(note.session_id),
        author_id=note.author_id,
        note_date=note.note_date,
        presenting_problem=note.presenting_problem,
        session_summary=note.session_summary,
        techniques_used=note.techniques_used,
        interventions=note.interventions,
        homework_assigned=note.homework_assigned,
        progress_assessment=note.progress_assessment,
        next_session_plan=note.next_session_plan,
        supervisor_feedback_id=str(note.supervisor_feedback_id) if note.supervisor_feedback_id else None,
        created_at=note.created_at,
        updated_at=note.updated_at
    )


@router.put("/{note_id}", response_model=SessionNoteResponse)
async def update_session_note(
    note_id: str,
    note_data: SessionNoteUpdate,
    current_user_id: int = Depends(get_current_user_id),
    current_user: dict = Depends(require_role("professional", "student", "admin"))
):
    """Update a session note"""
    if not PydanticObjectId.is_valid(note_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid note ID format"
        )
    
    note = await SessionNote.get(PydanticObjectId(note_id))
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session note not found"
        )
    
    # Only author or admin can edit
    if note.author_id != current_user_id and current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own notes"
        )
    
    # Update fields
    update_data = note_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(note, field, value)
    
    note.updated_at = datetime.utcnow()
    await note.save()
    
    return SessionNoteResponse(
        id=str(note.id),
        session_id=str(note.session_id),
        author_id=note.author_id,
        note_date=note.note_date,
        presenting_problem=note.presenting_problem,
        session_summary=note.session_summary,
        techniques_used=note.techniques_used,
        interventions=note.interventions,
        homework_assigned=note.homework_assigned,
        progress_assessment=note.progress_assessment,
        next_session_plan=note.next_session_plan,
        supervisor_feedback_id=str(note.supervisor_feedback_id) if note.supervisor_feedback_id else None,
        created_at=note.created_at,
        updated_at=note.updated_at
    )


@router.patch("/{note_id}/feedback", response_model=MessageResponse)
async def add_supervisor_feedback(
    note_id: str,
    feedback_id: str,
    current_user: dict = Depends(require_role("professional", "admin"))
):
    """Add supervisor feedback reference to a note"""
    if not PydanticObjectId.is_valid(note_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid note ID format"
        )
    
    if not PydanticObjectId.is_valid(feedback_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid feedback ID format"
        )
    
    note = await SessionNote.get(PydanticObjectId(note_id))
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session note not found"
        )
    
    note.supervisor_feedback_id = PydanticObjectId(feedback_id)
    note.updated_at = datetime.utcnow()
    await note.save()
    
    return MessageResponse(message="Supervisor feedback added successfully")


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session_note(
    note_id: str,
    current_user: dict = Depends(require_role("admin"))
):
    """Delete a session note (admin only)"""
    if not PydanticObjectId.is_valid(note_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid note ID format"
        )
    
    note = await SessionNote.get(PydanticObjectId(note_id))
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session note not found"
        )
    
    await note.delete()

