from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings
import httpx
from typing import Dict, Any

security = HTTPBearer()

async def verify_token_with_auth_service(token: str) -> Dict[str, Any]:
    """Verify token by calling auth-service validate endpoint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.AUTH_SERVICE_URL}/api/auth/validate",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token validation failed"
                )
    except httpx.RequestError:
        # Fallback to local JWT verification if auth-service is unreachable
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Get current authenticated user"""
    token = credentials.credentials
    user_data = await verify_token_with_auth_service(token)
    return user_data

def require_role(required_roles: list[str]):
    """Dependency to check user roles"""
    async def role_checker(current_user: Dict = Depends(get_current_user)):
        user_role = current_user.get("rol")
        if user_role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required roles: {required_roles}"
            )
        return current_user
    return role_checker

def get_client_info(request: Request) -> Dict[str, str]:
    """Extract client IP and user agent from request"""
    return {
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent")
    }
