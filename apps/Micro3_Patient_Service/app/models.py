from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from .database import Base

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

class Patient(Base):
    """
    Modelo para Consultantes/Pacientes
    """
    __tablename__ = "patients"
    
    # Identificador
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, unique=True, index=True)  # FK a Auth/User Service
    
    # Información Personal
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    cedula = Column(String(10), unique=True, nullable=False, index=True)
    fecha_nacimiento = Column(Date, nullable=False)
    genero = Column(SQLEnum(Genero), nullable=False)
    estado_civil = Column(SQLEnum(EstadoCivil), nullable=False)
    
    # Contacto
    telefono = Column(String(20), nullable=False)
    telefono_emergencia = Column(String(20), nullable=True)
    contacto_emergencia_nombre = Column(String(200), nullable=True)
    contacto_emergencia_relacion = Column(String(100), nullable=True)
    
    # Dirección
    direccion = Column(Text, nullable=False)
    ciudad = Column(String(100), nullable=False)
    provincia = Column(String(100), nullable=False)
    
    # Información Médica
    tipo_sangre = Column(SQLEnum(TipoSangre), default=TipoSangre.DESCONOCIDO)
    alergias = Column(Text, nullable=True)
    medicamentos_actuales = Column(Text, nullable=True)
    condiciones_medicas = Column(Text, nullable=True)
    
    # Información Laboral/Académica
    ocupacion = Column(String(200), nullable=True)
    institucion = Column(String(200), nullable=True)
    
    # Motivo de Consulta Inicial
    motivo_consulta_inicial = Column(Text, nullable=False)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=True)  # user_id del que creó el registro
    updated_by = Column(Integer, nullable=True)  # user_id del que actualizó
    
    # Relaciones
    expedientes = relationship("Expediente", back_populates="patient", cascade="all, delete-orphan")

class Expediente(Base):
    """
    Modelo para Expedientes Clínicos
    """
    __tablename__ = "expedientes"
    
    # Identificador
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    codigo_expediente = Column(String(50), unique=True, nullable=False, index=True)  # EXP-2024-0001
    
    # Información del Expediente
    fecha_apertura = Column(Date, nullable=False, default=datetime.utcnow)
    fecha_cierre = Column(Date, nullable=True)
    estado = Column(SQLEnum(EstadoExpediente), default=EstadoExpediente.ACTIVO)
    
    # Asignaciones
    psicologo_asignado_id = Column(Integer, nullable=True, index=True)  # FK a User Service (role=estudiante)
    supervisor_asignado_id = Column(Integer, nullable=True, index=True)  # FK a User Service (role=psicologo_supervisor)
    
    # Diagnóstico y Plan
    diagnostico_inicial = Column(Text, nullable=True)
    plan_tratamiento = Column(Text, nullable=True)
    objetivos_terapeuticos = Column(Text, nullable=True)
    
    # Observaciones y Notas
    observaciones_generales = Column(Text, nullable=True)
    antecedentes_personales = Column(Text, nullable=True)
    antecedentes_familiares = Column(Text, nullable=True)
    
    # Resumen del Proceso
    numero_sesiones = Column(Integer, default=0)
    ultima_sesion_fecha = Column(DateTime, nullable=True)
    
    # Motivo de Cierre
    motivo_cierre = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    
    # Relaciones
    patient = relationship("Patient", back_populates="expedientes")
