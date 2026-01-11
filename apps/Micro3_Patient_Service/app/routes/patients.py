from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime, date
from .. import models, schemas
from ..database import get_db
from ..security import get_current_user, require_recepcionista, require_psicologo
from ..events import get_rabbitmq_publisher

router = APIRouter(prefix="/api/v1/patients", tags=["Patients"])

@router.post("/", response_model=schemas.PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient_data: schemas.PatientCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_recepcionista),
    rabbitmq = Depends(get_rabbitmq_publisher)
):
    """
    Crear un nuevo paciente/consultante
    Requiere rol: recepcionista o administrador
    """
    # Verificar que no exista un paciente con la misma cédula
    existing = db.query(models.Patient).filter(models.Patient.cedula == patient_data.cedula).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un paciente con cédula {patient_data.cedula}"
        )
    
    # Verificar que no exista un paciente con el mismo user_id
    existing_user = db.query(models.Patient).filter(models.Patient.user_id == patient_data.user_id).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un paciente asociado al user_id {patient_data.user_id}"
        )
    
    # Crear paciente
    patient = models.Patient(
        **patient_data.model_dump(),
        created_by=current_user["user_id"],
        updated_by=current_user["user_id"]
    )
    
    db.add(patient)
    db.commit()
    db.refresh(patient)
    
    # Publicar evento
    rabbitmq.publish_event("patient.created", {
        "patient_id": patient.id,
        "user_id": patient.user_id,
        "nombres": patient.nombres,
        "apellidos": patient.apellidos,
        "cedula": patient.cedula,
        "created_by": current_user["user_id"],
        "created_at": patient.created_at.isoformat()
    })
    
    return patient

@router.get("/", response_model=List[schemas.PatientResponse])
async def list_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None, description="Buscar por nombres, apellidos o cédula"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_recepcionista)
):
    """
    Listar todos los pacientes con paginación y búsqueda
    Requiere rol: recepcionista o administrador
    """
    query = db.query(models.Patient)
    
    # Filtrar por estado
    if is_active is not None:
        query = query.filter(models.Patient.is_active == is_active)
    
    # Búsqueda
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                models.Patient.nombres.ilike(search_pattern),
                models.Patient.apellidos.ilike(search_pattern),
                models.Patient.cedula.ilike(search_pattern)
            )
        )
    
    patients = query.offset(skip).limit(limit).all()
    return patients

@router.get("/{patient_id}", response_model=schemas.PatientResponse)
async def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_psicologo)
):
    """
    Obtener un paciente por ID
    Requiere rol: estudiante, supervisor o administrador
    """
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente con ID {patient_id} no encontrado"
        )
    return patient

@router.get("/by-user/{user_id}", response_model=schemas.PatientResponse)
async def get_patient_by_user_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener un paciente por user_id
    Los consultantes pueden ver su propia información
    """
    patient = db.query(models.Patient).filter(models.Patient.user_id == user_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente con user_id {user_id} no encontrado"
        )
    
    # Verificar permisos: solo el mismo usuario o staff
    if current_user["user_id"] != user_id and current_user["role"] not in ["administrador", "recepcionista", "psicologo_supervisor", "estudiante"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver este paciente"
        )
    
    return patient

@router.get("/by-cedula/{cedula}", response_model=schemas.PatientResponse)
async def get_patient_by_cedula(
    cedula: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_recepcionista)
):
    """
    Obtener un paciente por cédula
    Requiere rol: recepcionista o administrador
    """
    patient = db.query(models.Patient).filter(models.Patient.cedula == cedula).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente con cédula {cedula} no encontrado"
        )
    return patient

@router.put("/{patient_id}", response_model=schemas.PatientResponse)
async def update_patient(
    patient_id: int,
    patient_data: schemas.PatientUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_recepcionista),
    rabbitmq = Depends(get_rabbitmq_publisher)
):
    """
    Actualizar un paciente
    Requiere rol: recepcionista o administrador
    """
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente con ID {patient_id} no encontrado"
        )
    
    # Actualizar campos
    update_data = patient_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)
    
    patient.updated_by = current_user["user_id"]
    patient.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(patient)
    
    # Publicar evento
    rabbitmq.publish_event("patient.updated", {
        "patient_id": patient.id,
        "user_id": patient.user_id,
        "updated_by": current_user["user_id"],
        "updated_at": patient.updated_at.isoformat()
    })
    
    return patient

@router.delete("/{patient_id}", response_model=schemas.MessageResponse)
async def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_recepcionista),
    rabbitmq = Depends(get_rabbitmq_publisher)
):
    """
    Eliminar (soft delete) un paciente
    Requiere rol: recepcionista o administrador
    """
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente con ID {patient_id} no encontrado"
        )
    
    # Soft delete
    patient.is_active = False
    patient.updated_by = current_user["user_id"]
    patient.updated_at = datetime.utcnow()
    
    db.commit()
    
    # Publicar evento
    rabbitmq.publish_event("patient.deleted", {
        "patient_id": patient.id,
        "user_id": patient.user_id,
        "deleted_by": current_user["user_id"],
        "deleted_at": datetime.utcnow().isoformat()
    })
    
    return schemas.MessageResponse(
        message="Paciente desactivado exitosamente",
        detail=f"Paciente {patient.nombres} {patient.apellidos} ha sido desactivado"
    )
