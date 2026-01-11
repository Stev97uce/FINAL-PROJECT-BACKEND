from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime, date
from enum import Enum

# Enums
class TipoSangre(str, Enum):
    A_POSITIVO = "A+"
    A_NEGATIVO = "A-"
    B_POSITIVO = "B+"
    B_NEGATIVO = "B-"
    AB_POSITIVO = "AB+"
    AB_NEGATIVO = "AB-"
    O_POSITIVO = "O+"
    O_NEGATIVO = "O-"
    DESCONOCIDO = "Desconocido"

class EstadoCivil(str, Enum):
    SOLTERO = "Soltero/a"
    CASADO = "Casado/a"
    DIVORCIADO = "Divorciado/a"
    VIUDO = "Viudo/a"
    UNION_LIBRE = "Unión libre"

class Genero(str, Enum):
    MASCULINO = "Masculino"
    FEMENINO = "Femenino"
    OTRO = "Otro"
    PREFIERO_NO_DECIR = "Prefiero no decir"

class EstadoExpediente(str, Enum):
    ACTIVO = "Activo"
    INACTIVO = "Inactivo"
    CERRADO = "Cerrado"
    ARCHIVADO = "Archivado"

# Patient Schemas
class PatientBase(BaseModel):
    user_id: int
    nombres: str = Field(..., min_length=2, max_length=100)
    apellidos: str = Field(..., min_length=2, max_length=100)
    cedula: str = Field(..., min_length=10, max_length=10, pattern=r'^\d{10}$')
    fecha_nacimiento: date
    genero: Genero
    estado_civil: EstadoCivil
    telefono: str = Field(..., pattern=r'^\d{10}$')
    telefono_emergencia: Optional[str] = Field(None, pattern=r'^\d{10}$')
    contacto_emergencia_nombre: Optional[str] = Field(None, max_length=200)
    contacto_emergencia_relacion: Optional[str] = Field(None, max_length=100)
    direccion: str
    ciudad: str = Field(..., max_length=100)
    provincia: str = Field(..., max_length=100)
    tipo_sangre: TipoSangre = TipoSangre.DESCONOCIDO
    alergias: Optional[str] = None
    medicamentos_actuales: Optional[str] = None
    condiciones_medicas: Optional[str] = None
    ocupacion: Optional[str] = Field(None, max_length=200)
    institucion: Optional[str] = Field(None, max_length=200)
    motivo_consulta_inicial: str
    
    @validator('cedula')
    def validate_cedula(cls, v):
        if not v.isdigit() or len(v) != 10:
            raise ValueError('Cédula debe tener exactamente 10 dígitos numéricos')
        return v
    
    @validator('fecha_nacimiento')
    def validate_fecha_nacimiento(cls, v):
        if v > date.today():
            raise ValueError('La fecha de nacimiento no puede ser futura')
        edad = (date.today() - v).days // 365
        if edad < 0 or edad > 120:
            raise ValueError('Edad inválida')
        return v

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    nombres: Optional[str] = Field(None, min_length=2, max_length=100)
    apellidos: Optional[str] = Field(None, min_length=2, max_length=100)
    fecha_nacimiento: Optional[date] = None
    genero: Optional[Genero] = None
    estado_civil: Optional[EstadoCivil] = None
    telefono: Optional[str] = Field(None, pattern=r'^\d{10}$')
    telefono_emergencia: Optional[str] = Field(None, pattern=r'^\d{10}$')
    contacto_emergencia_nombre: Optional[str] = Field(None, max_length=200)
    contacto_emergencia_relacion: Optional[str] = Field(None, max_length=100)
    direccion: Optional[str] = None
    ciudad: Optional[str] = Field(None, max_length=100)
    provincia: Optional[str] = Field(None, max_length=100)
    tipo_sangre: Optional[TipoSangre] = None
    alergias: Optional[str] = None
    medicamentos_actuales: Optional[str] = None
    condiciones_medicas: Optional[str] = None
    ocupacion: Optional[str] = Field(None, max_length=200)
    institucion: Optional[str] = Field(None, max_length=200)
    motivo_consulta_inicial: Optional[str] = None
    is_active: Optional[bool] = None

class PatientResponse(PatientBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int]
    updated_by: Optional[int]
    
    class Config:
        from_attributes = True

# Expediente Schemas
class ExpedienteBase(BaseModel):
    patient_id: int
    codigo_expediente: Optional[str] = None  # Se genera automáticamente
    fecha_apertura: Optional[date] = None
    estado: EstadoExpediente = EstadoExpediente.ACTIVO
    psicologo_asignado_id: Optional[int] = None
    supervisor_asignado_id: Optional[int] = None
    diagnostico_inicial: Optional[str] = None
    plan_tratamiento: Optional[str] = None
    objetivos_terapeuticos: Optional[str] = None
    observaciones_generales: Optional[str] = None
    antecedentes_personales: Optional[str] = None
    antecedentes_familiares: Optional[str] = None

class ExpedienteCreate(ExpedienteBase):
    pass

class ExpedienteUpdate(BaseModel):
    estado: Optional[EstadoExpediente] = None
    psicologo_asignado_id: Optional[int] = None
    supervisor_asignado_id: Optional[int] = None
    diagnostico_inicial: Optional[str] = None
    plan_tratamiento: Optional[str] = None
    objetivos_terapeuticos: Optional[str] = None
    observaciones_generales: Optional[str] = None
    antecedentes_personales: Optional[str] = None
    antecedentes_familiares: Optional[str] = None
    numero_sesiones: Optional[int] = None
    ultima_sesion_fecha: Optional[datetime] = None
    fecha_cierre: Optional[date] = None
    motivo_cierre: Optional[str] = None

class ExpedienteResponse(ExpedienteBase):
    id: int
    codigo_expediente: str
    fecha_apertura: date
    fecha_cierre: Optional[date]
    numero_sesiones: int
    ultima_sesion_fecha: Optional[datetime]
    motivo_cierre: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int]
    updated_by: Optional[int]
    
    class Config:
        from_attributes = True

class ExpedienteWithPatient(ExpedienteResponse):
    patient: PatientResponse
    
    class Config:
        from_attributes = True

# Response Models
class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    status_code: int
