from sqlalchemy import Column, Integer, String, Boolean, Enum, TIMESTAMP, ForeignKey, Index
from sqlalchemy.sql import func
from app.database import Base
import enum


class RolEnum(str, enum.Enum):
    CONSULTANTE = "consultante"
    RECEPCIONISTA = "recepcionista"
    ESTUDIANTE = "estudiante"
    PSICOLOGO_SUPERVISOR = "psicologo_supervisor"
    ADMINISTRADOR = "administrador"


class EstadoEnum(str, enum.Enum):
    PENDIENTE_VERIFICACION = "pendiente_verificacion"
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    SUSPENDIDO = "suspendido"


class TipoTokenEnum(str, enum.Enum):
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombres = Column(String(255), nullable=False)
    identificacion = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    telefono = Column(String(20), nullable=False)
    password_hash = Column(String(255), nullable=False)
    rol = Column(String(50), nullable=False)
    estado = Column(String(50), default="pendiente_verificacion")
    email_verificado = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )


class VerificationToken(Base):
    __tablename__ = "verification_tokens"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    tipo = Column(String(50), nullable=False)
    expira_en = Column(TIMESTAMP, nullable=False)
    usado = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(500), unique=True, nullable=False, index=True)
    expira_en = Column(TIMESTAMP, nullable=False)
    revocado = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
