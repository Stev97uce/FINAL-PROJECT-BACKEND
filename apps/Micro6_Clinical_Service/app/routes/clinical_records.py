from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
from beanie import PydanticObjectId
from app.models import ClinicalRecord, RecordStatus
from app.schemas import (
    ClinicalRecordCreate,
    ClinicalRecordUpdate,
    ClinicalRecordResponse,
    MessageResponse
)
from app.security import get_current_user, require_role
from app.dependencies import get_current_user_id
from app.events import publish_clinical_record_created

router = APIRouter(prefix="/clinical-records", tags=["Clinical Records"])


@router.post("", response_model=ClinicalRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_clinical_record(
    record_data: ClinicalRecordCreate,
    current_user_id: int = Depends(get_current_user_id),
    current_user: dict = Depends(require_role("professional", "admin"))
):
    """Create a new clinical record"""
    record = ClinicalRecord(
        patient_id=record_data.patient_id,
        therapist_id=record_data.therapist_id,
        diagnosis=record_data.diagnosis,
        treatment_plan=record_data.treatment_plan,
        additional_notes=record_data.additional_notes
    )
    await record.insert()
    
    # Publish event
    publish_clinical_record_created(
        str(record.id),
        record.patient_id,
        record.therapist_id
    )
    
    return ClinicalRecordResponse(
        id=str(record.id),
        patient_id=record.patient_id,
        therapist_id=record.therapist_id,
        status=record.status,
        opening_date=record.opening_date,
        closing_date=record.closing_date,
        diagnosis=record.diagnosis,
        treatment_plan=record.treatment_plan,
        additional_notes=record.additional_notes,
        created_at=record.created_at,
        updated_at=record.updated_at
    )


@router.get("", response_model=List[ClinicalRecordResponse])
async def list_clinical_records(
    patient_id: int = None,
    therapist_id: int = None,
    status_filter: RecordStatus = None,
    current_user: dict = Depends(get_current_user)
):
    """List clinical records with optional filters"""
    query = {}
    if patient_id:
        query["patient_id"] = patient_id
    if therapist_id:
        query["therapist_id"] = therapist_id
    if status_filter:
        query["status"] = status_filter
    
    records = await ClinicalRecord.find(query).to_list()
    
    return [
        ClinicalRecordResponse(
            id=str(record.id),
            patient_id=record.patient_id,
            therapist_id=record.therapist_id,
            status=record.status,
            opening_date=record.opening_date,
            closing_date=record.closing_date,
            diagnosis=record.diagnosis,
            treatment_plan=record.treatment_plan,
            additional_notes=record.additional_notes,
            created_at=record.created_at,
            updated_at=record.updated_at
        )
        for record in records
    ]


@router.get("/{record_id}", response_model=ClinicalRecordResponse)
async def get_clinical_record(
    record_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific clinical record by ID"""
    if not PydanticObjectId.is_valid(record_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid record ID format"
        )
    
    record = await ClinicalRecord.get(PydanticObjectId(record_id))
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical record not found"
        )
    
    return ClinicalRecordResponse(
        id=str(record.id),
        patient_id=record.patient_id,
        therapist_id=record.therapist_id,
        status=record.status,
        opening_date=record.opening_date,
        closing_date=record.closing_date,
        diagnosis=record.diagnosis,
        treatment_plan=record.treatment_plan,
        additional_notes=record.additional_notes,
        created_at=record.created_at,
        updated_at=record.updated_at
    )


@router.put("/{record_id}", response_model=ClinicalRecordResponse)
async def update_clinical_record(
    record_id: str,
    record_data: ClinicalRecordUpdate,
    current_user: dict = Depends(require_role("professional", "admin"))
):
    """Update a clinical record"""
    if not PydanticObjectId.is_valid(record_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid record ID format"
        )
    
    record = await ClinicalRecord.get(PydanticObjectId(record_id))
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical record not found"
        )
    
    # Update fields
    update_data = record_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)
    
    record.updated_at = datetime.utcnow()
    await record.save()
    
    return ClinicalRecordResponse(
        id=str(record.id),
        patient_id=record.patient_id,
        therapist_id=record.therapist_id,
        status=record.status,
        opening_date=record.opening_date,
        closing_date=record.closing_date,
        diagnosis=record.diagnosis,
        treatment_plan=record.treatment_plan,
        additional_notes=record.additional_notes,
        created_at=record.created_at,
        updated_at=record.updated_at
    )


@router.patch("/{record_id}/close", response_model=MessageResponse)
async def close_clinical_record(
    record_id: str,
    current_user: dict = Depends(require_role("professional", "admin"))
):
    """Close a clinical record"""
    if not PydanticObjectId.is_valid(record_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid record ID format"
        )
    
    record = await ClinicalRecord.get(PydanticObjectId(record_id))
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical record not found"
        )
    
    if record.status == RecordStatus.CLOSED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Clinical record is already closed"
        )
    
    record.status = RecordStatus.CLOSED
    record.closing_date = datetime.utcnow()
    record.updated_at = datetime.utcnow()
    await record.save()
    
    return MessageResponse(message="Clinical record closed successfully")


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_clinical_record(
    record_id: str,
    current_user: dict = Depends(require_role("admin"))
):
    """Delete a clinical record (admin only)"""
    if not PydanticObjectId.is_valid(record_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid record ID format"
        )
    
    record = await ClinicalRecord.get(PydanticObjectId(record_id))
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical record not found"
        )
    
    await record.delete()

