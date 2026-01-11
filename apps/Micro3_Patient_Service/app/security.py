from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from .config import settings
from typing import Optional

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Verifica el token JWT y retorna el payload
    """
    token = credentials.credentials
    
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(payload: dict = Depends(verify_token)) -> dict:
    """
    Obtiene el usuario actual desde el token
    """
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: user_id no encontrado"
        )
    
    return {
        "user_id": user_id,
        "email": payload.get("email"),
        "role": payload.get("role"),
        "is_verified": payload.get("is_verified", False)
    }

def require_role(required_roles: list):
    """
    Decorator para verificar que el usuario tenga uno de los roles requeridos
    """
    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role")
        if user_role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permiso denegado. Se requiere uno de los siguientes roles: {', '.join(required_roles)}"
            )
        return current_user
    return role_checker

# Roles específicos
async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Solo administradores"""
    return await require_role(["administrador"])(current_user)

async def require_recepcionista(current_user: dict = Depends(get_current_user)) -> dict:
    """Administradores y recepcionistas"""
    return await require_role(["administrador", "recepcionista"])(current_user)

async def require_psicologo(current_user: dict = Depends(get_current_user)) -> dict:
    """Administradores, supervisores y estudiantes"""
    return await require_role(["administrador", "psicologo_supervisor", "estudiante"])(current_user)
