from sqlalchemy import Column, Integer, String, Date, Text, JSON, DateTime
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, nullable=False, index=True)
    
    # Personal Information
    direccion = Column(String(255))
    ciudad = Column(String(100))
    pais = Column(String(100), default="Ecuador")
    fecha_nacimiento = Column(Date)
    genero = Column(String(20))
    telefono_alternativo = Column(String(20))
    
    # Emergency Contact
    contacto_emergencia_nombre = Column(String(150))
    contacto_emergencia_telefono = Column(String(20))
    
    # Professional Information
    ocupacion = Column(String(100))
    institucion = Column(String(150))
    
    # Medical and Preferences
    notas_medicas = Column(Text)
    preferencias = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    accion = Column(String(100), nullable=False)
    descripcion = Column(Text)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
