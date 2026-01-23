from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from app.models import RolEnum


# ============= Request Schemas =============

class RegisterRequest(BaseModel):
    nombres: str = Field(..., min_length=2, max_length=255)
    identificacion: str = Field(..., min_length=5, max_length=50)
    email: EmailStr
    telefono: str = Field(..., min_length=7, max_length=20)
    password: str = Field(..., min_length=8)
    rol: RolEnum = RolEnum.CONSULTANTE
    
    @validator('telefono')
    def validate_telefono(cls, v):
        # Eliminar espacios y guiones
        v = v.replace(" ", "").replace("-", "")
        if not v.isdigit():
            raise ValueError("El teléfono debe contener solo números")
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        if not any(c.isupper() for c in v):
            raise ValueError("La contraseña debe contener al menos una mayúscula")
        if not any(c.islower() for c in v):
            raise ValueError("La contraseña debe contener al menos una minúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("La contraseña debe contener al menos un número")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        if not any(c.isupper() for c in v):
            raise ValueError("La contraseña debe contener al menos una mayúscula")
        if not any(c.islower() for c in v):
            raise ValueError("La contraseña debe contener al menos una minúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("La contraseña debe contener al menos un número")
        return v


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ============= Response Schemas =============

class UserResponse(BaseModel):
    id: int
    nombres: str
    email: str
    rol: str
    
    class Config:
        from_attributes = True


class RegisterResponse(BaseModel):
    user_id: int
    message: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class MessageResponse(BaseModel):
    message: str


class TokenValidationResponse(BaseModel):
    user_id: int
    email: str
    rol: str


class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
