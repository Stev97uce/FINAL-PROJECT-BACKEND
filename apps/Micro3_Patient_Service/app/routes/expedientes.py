from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from .. import models, schemas
from ..database import get_db
from ..security import get_current_user, require_psicologo
from ..events import get_rabbitmq_publisher

router = APIRouter(prefix="/api/v1/expedientes", tags=["Expedientes"])

def generate_expediente_code(db: Session) -> str:
    """Genera un código único para el expediente: EXP-YYYY-NNNN"""
    year = datetime.now().year
    
    # Contar expedientes del año actual
    count = db.query(models.Expediente).filter(
        models.Expediente.codigo_expediente.like(f"EXP-{year}-%")
    ).count()
    
    next_number = count + 1
    return f"EXP-{year}-{next_number:04d}"

@router.post("/", response_model=schemas.ExpedienteResponse, status_code=status.HTTP_201_CREATED)
async def create_expediente(
    expediente_data: schemas.ExpedienteCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_psicologo),
    rabbitmq = Depends(get_rabbitmq_publisher)
):
    """
    Crear un nuevo expediente clínico
    Requiere rol: estudiante, supervisor o administrador
    """
    # Verificar que el paciente exista
    patient = db.query(models.Patient).filter(models.Patient.id == expediente_data.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente con ID {expediente_data.patient_id} no encontrado"
        )
    
    # Verificar si ya existe un expediente activo para este paciente
    existing = db.query(models.Expediente).filter(
        models.Expediente.patient_id == expediente_data.patient_id,
        models.Expediente.estado == models.EstadoExpediente.ACTIVO
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El paciente ya tiene un expediente activo (código: {existing.codigo_expediente})"
        )
    
    # Generar código de expediente
    codigo = generate_expediente_code(db)
    
    # Crear expediente
    expediente_dict = expediente_data.model_dump(exclude={"codigo_expediente", "fecha_apertura"})
    expediente = models.Expediente(
        **expediente_dict,
        codigo_expediente=codigo,
        fecha_apertura=expediente_data.fecha_apertura or date.today(),
        created_by=current_user["user_id"],
        updated_by=current_user["user_id"]
    )
    
    db.add(expediente)
    db.commit()
    db.refresh(expediente)
    
    # Publicar evento
    rabbitmq.publish_event("expediente.created", {
        "expediente_id": expediente.id,
        "patient_id": expediente.patient_id,
        "codigo_expediente": expediente.codigo_expediente,
        "psicologo_asignado_id": expediente.psicologo_asignado_id,
        "supervisor_asignado_id": expediente.supervisor_asignado_id,
        "created_by": current_user["user_id"],
        "created_at": expediente.created_at.isoformat()
    })
    
    return expediente

@router.get("/", response_model=List[schemas.ExpedienteResponse])
async def list_expedientes(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    estado: Optional[schemas.EstadoExpediente] = Query(None, description="Filtrar por estado"),
    psicologo_id: Optional[int] = Query(None, description="Filtrar por psicólogo asignado"),
    supervisor_id: Optional[int] = Query(None, description="Filtrar por supervisor"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_psicologo)
):
    """
    Listar expedientes con filtros
    Requiere rol: estudiante, supervisor o administrador
    """
    query = db.query(models.Expediente)
    
    # Filtros
    if estado:
        query = query.filter(models.Expediente.estado == estado)
    
    if psicologo_id:
        query = query.filter(models.Expediente.psicologo_asignado_id == psicologo_id)
    
    if supervisor_id:
        query = query.filter(models.Expediente.supervisor_asignado_id == supervisor_id)
    
    # Los estudiantes solo ven sus propios expedientes
    if current_user["role"] == "estudiante":
        query = query.filter(models.Expediente.psicologo_asignado_id == current_user["user_id"])
    
    expedientes = query.offset(skip).limit(limit).all()
    return expedientes

@router.get("/{expediente_id}", response_model=schemas.ExpedienteResponse)
async def get_expediente(
    expediente_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_psicologo)
):
    """
    Obtener un expediente por ID
    Requiere rol: estudiante, supervisor o administrador
    """
    expediente = db.query(models.Expediente).filter(models.Expediente.id == expediente_id).first()
    if not expediente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expediente con ID {expediente_id} no encontrado"
        )
    
    # Verificar permisos: estudiantes solo ven sus expedientes
    if current_user["role"] == "estudiante" and expediente.psicologo_asignado_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver este expediente"
        )
    
    return expediente

@router.get("/by-patient/{patient_id}", response_model=List[schemas.ExpedienteResponse])
async def get_expedientes_by_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_psicologo)
):
    """
    Obtener todos los expedientes de un paciente
    Requiere rol: estudiante, supervisor o administrador
    """
    # Verificar que el paciente exista
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente con ID {patient_id} no encontrado"
        )
    
    query = db.query(models.Expediente).filter(models.Expediente.patient_id == patient_id)
    
    # Los estudiantes solo ven expedientes que les pertenecen
    if current_user["role"] == "estudiante":
        query = query.filter(models.Expediente.psicologo_asignado_id == current_user["user_id"])
    
    expedientes = query.all()
    return expedientes

@router.get("/by-codigo/{codigo}", response_model=schemas.ExpedienteResponse)
async def get_expediente_by_codigo(
    codigo: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_psicologo)
):
    """
    Obtener un expediente por código (EXP-YYYY-NNNN)
    Requiere rol: estudiante, supervisor o administrador
    """
    expediente = db.query(models.Expediente).filter(models.Expediente.codigo_expediente == codigo).first()
    if not expediente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expediente con código {codigo} no encontrado"
        )
    
    # Verificar permisos
    if current_user["role"] == "estudiante" and expediente.psicologo_asignado_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver este expediente"
        )
    
    return expediente

@router.put("/{expediente_id}", response_model=schemas.ExpedienteResponse)
async def update_expediente(
    expediente_id: int,
    expediente_data: schemas.ExpedienteUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_psicologo),
    rabbitmq = Depends(get_rabbitmq_publisher)
):
    """
    Actualizar un expediente
    Requiere rol: estudiante (solo sus expedientes), supervisor o administrador
    """
    expediente = db.query(models.Expediente).filter(models.Expediente.id == expediente_id).first()
    if not expediente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expediente con ID {expediente_id} no encontrado"
        )
    
    # Verificar permisos: estudiantes solo editan sus expedientes
    if current_user["role"] == "estudiante" and expediente.psicologo_asignado_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para editar este expediente"
        )
    
    # Actualizar campos
    update_data = expediente_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(expediente, field, value)
    
    expediente.updated_by = current_user["user_id"]
    expediente.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(expediente)
    
    # Publicar evento
    rabbitmq.publish_event("expediente.updated", {
        "expediente_id": expediente.id,
        "patient_id": expediente.patient_id,
        "codigo_expediente": expediente.codigo_expediente,
        "estado": expediente.estado,
        "updated_by": current_user["user_id"],
        "updated_at": expediente.updated_at.isoformat()
    })
    
    return expediente

@router.post("/{expediente_id}/close", response_model=schemas.ExpedienteResponse)
async def close_expediente(
    expediente_id: int,
    motivo_cierre: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_psicologo),
    rabbitmq = Depends(get_rabbitmq_publisher)
):
    """
    Cerrar un expediente
    Requiere rol: estudiante (solo sus expedientes), supervisor o administrador
    """
    expediente = db.query(models.Expediente).filter(models.Expediente.id == expediente_id).first()
    if not expediente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expediente con ID {expediente_id} no encontrado"
        )
    
    # Verificar permisos
    if current_user["role"] == "estudiante" and expediente.psicologo_asignado_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para cerrar este expediente"
        )
    
    if expediente.estado == models.EstadoExpediente.CERRADO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El expediente ya está cerrado"
        )
    
    # Cerrar expediente
    expediente.estado = models.EstadoExpediente.CERRADO
    expediente.fecha_cierre = date.today()
    expediente.motivo_cierre = motivo_cierre
    expediente.updated_by = current_user["user_id"]
    expediente.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(expediente)
    
    # Publicar evento
    rabbitmq.publish_event("expediente.closed", {
        "expediente_id": expediente.id,
        "patient_id": expediente.patient_id,
        "codigo_expediente": expediente.codigo_expediente,
        "fecha_cierre": expediente.fecha_cierre.isoformat(),
        "motivo_cierre": motivo_cierre,
        "closed_by": current_user["user_id"]
    })
    
    return expediente
