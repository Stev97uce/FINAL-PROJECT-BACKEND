"""
Dependencies for authentication and authorization
KISS principle: Simple JWT validation
"""
from fastapi import Header, HTTPException, status
from jose import JWTError, jwt
from typing import Optional, Dict
from app.config import settings


async def get_current_user(authorization: Optional[str] = Header(None)) -> Dict:
    """
    Validate JWT token and return user info
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    token = authorization.replace("Bearer ", "")
    
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        user_id: int = payload.get("user_id")
        email: str = payload.get("email")
        rol: str = payload.get("rol")
        
        if user_id is None or email is None or rol is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        return {
            "user_id": user_id,
            "email": email,
            "rol": rol
        }
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}"
        )


async def require_admin(current_user: Dict = None) -> Dict:
    """
    Require administrator role
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    if current_user["rol"] not in ["administrador", "coordinador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator or coordinator role required"
        )
    
    return current_user


async def check_template_permission(template, current_user: Dict) -> bool:
    """
    Check if user has permission to use template
    """
    if not template.required_roles:
        return True
    
    if current_user["rol"] in ["administrador", "coordinador"]:
        return True
    
    if current_user["rol"] in template.required_roles:
        return True
    
    return False
