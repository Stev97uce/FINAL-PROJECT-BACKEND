"""
FastAPI dependency injection
KISS principle: Simple JWT validation
"""
from fastapi import Depends, HTTPException, status, Header
from typing import Dict, Optional

async def get_current_user(
    authorization: Optional[str] = Header(None)
) -> Dict:
    """Validate JWT token and extract user data"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    
    try:
        from jose import jwt, JWTError
        from app.config import settings
        
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        
        return {
            "user_id": user_id,
            "email": payload.get("email"),
            "rol": payload.get("rol")
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )


async def require_admin(
    current_user: Dict = Depends(get_current_user)
) -> Dict:
    """Require admin role"""
    if current_user.get("rol") != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user
