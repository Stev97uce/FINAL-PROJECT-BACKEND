from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import date, datetime
from enum import Enum

# Enums
class Genero(str, Enum):
    masculino = "masculino"
    femenino = "femenino"
    otro = "otro"
    prefiere_no_decir = "prefiere_no_decir"

# Request Schemas
class UserProfileCreate(BaseModel):
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    pais: str = "Ecuador"
    fecha_nacimiento: Optional[date] = None
    genero: Optional[Genero] = None
    telefono_alternativo: Optional[str] = None
    contacto_emergencia_nombre: Optional[str] = None
    contacto_emergencia_telefono: Optional[str] = None
    ocupacion: Optional[str] = None
    institucion: Optional[str] = None
    notas_medicas: Optional[str] = None
    preferencias: Optional[Dict[str, Any]] = Field(default_factory=dict)

class UserProfileUpdate(BaseModel):
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    genero: Optional[Genero] = None
    telefono_alternativo: Optional[str] = None
    contacto_emergencia_nombre: Optional[str] = None
    contacto_emergencia_telefono: Optional[str] = None
    ocupacion: Optional[str] = None
    institucion: Optional[str] = None
    notas_medicas: Optional[str] = None
    preferencias: Optional[Dict[str, Any]] = None

class ActivityLogCreate(BaseModel):
    accion: str
    descripcion: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

# Response Schemas
class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    direccion: Optional[str]
    ciudad: Optional[str]
    pais: str
    fecha_nacimiento: Optional[date]
    genero: Optional[str]
    telefono_alternativo: Optional[str]
    contacto_emergencia_nombre: Optional[str]
    contacto_emergencia_telefono: Optional[str]
    ocupacion: Optional[str]
    institucion: Optional[str]
    notas_medicas: Optional[str]
    preferencias: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class ActivityLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    accion: str
    descripcion: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

class MessageResponse(BaseModel):
    message: str

class UserInfoResponse(BaseModel):
    """Complete user information from auth-service"""
    id: int
    nombres: str
    email: str
    rol: str
    estado: str
    email_verificado: bool

class CompleteUserResponse(BaseModel):
    """Combined user info from auth-service and user-service"""
    auth_info: UserInfoResponse
    profile: Optional[UserProfileResponse]
