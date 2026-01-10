from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import UserProfile, ActivityLog
from app.schemas import (
    UserProfileCreate,
    UserProfileUpdate,
    UserProfileResponse,
    ActivityLogCreate,
    ActivityLogResponse,
    MessageResponse,
    CompleteUserResponse,
    UserInfoResponse
)
from app.security import get_current_user, require_role, get_client_info
from app.events import get_event_publisher
from typing import List, Dict, Any
import httpx
from app.config import settings
from datetime import datetime

router = APIRouter(prefix="/api/users", tags=["users"])

# Helper function to get user info from auth-service
async def get_user_from_auth_service(user_id: int, token: str) -> Dict[str, Any]:
    """Fetch user info from auth-service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.AUTH_SERVICE_URL}/api/auth/users/{user_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
    except httpx.RequestError:
        return None

# Helper function to log activity
def log_activity(
    db: Session,
    user_id: int,
    accion: str,
    descripcion: str = None,
    client_info: Dict = None
):
    """Create activity log entry"""
    activity = ActivityLog(
        user_id=user_id,
        accion=accion,
        descripcion=descripcion,
        ip_address=client_info.get("ip_address") if client_info else None,
        user_agent=client_info.get("user_agent") if client_info else None
    )
    db.add(activity)
    db.commit()

@router.post("/profile", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    data: UserProfileCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    """Create user profile"""
    user_id = current_user.get("user_id")
    
    # Check if profile already exists
    existing_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists. Use PUT to update."
        )
    
    # Create profile
    profile = UserProfile(
        user_id=user_id,
        direccion=data.direccion,
        ciudad=data.ciudad,
        pais=data.pais,
        fecha_nacimiento=data.fecha_nacimiento,
        genero=data.genero.value if data.genero else None,
        telefono_alternativo=data.telefono_alternativo,
        contacto_emergencia_nombre=data.contacto_emergencia_nombre,
        contacto_emergencia_telefono=data.contacto_emergencia_telefono,
        ocupacion=data.ocupacion,
        institucion=data.institucion,
        notas_medicas=data.notas_medicas,
        preferencias=data.preferencias or {}
    )
    
    db.add(profile)
    db.commit()
    db.refresh(profile)
    
    # Log activity
    client_info = get_client_info(request)
    log_activity(db, user_id, "profile_created", "Usuario creó su perfil", client_info)
    
    # Publish event
    event_publisher = get_event_publisher()
    event_publisher.publish_event(
        "user.profile_created",
        {
            "user_id": user_id,
            "profile_id": profile.id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    
    return profile

@router.get("/profile", response_model=UserProfileResponse)
async def get_my_profile(
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    """Get current user's profile"""
    user_id = current_user.get("user_id")
    
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return profile

@router.put("/profile", response_model=UserProfileResponse)
async def update_profile(
    data: UserProfileUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    """Update user profile"""
    user_id = current_user.get("user_id")
    
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Create one first."
        )
    
    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    
    if "genero" in update_data and update_data["genero"]:
        update_data["genero"] = update_data["genero"].value
    
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    db.commit()
    db.refresh(profile)
    
    # Log activity
    client_info = get_client_info(request)
    log_activity(db, user_id, "profile_updated", "Usuario actualizó su perfil", client_info)
    
    # Publish event
    event_publisher = get_event_publisher()
    event_publisher.publish_event(
        "user.profile_updated",
        {
            "user_id": user_id,
            "profile_id": profile.id,
            "updated_fields": list(update_data.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    
    return profile

@router.get("/profile/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(require_role(["administrador", "supervisor"]))
):
    """Get any user's profile (admin/supervisor only)"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return profile

@router.get("/complete/{user_id}", response_model=CompleteUserResponse)
async def get_complete_user_info(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(require_role(["administrador", "supervisor"]))
):
    """Get complete user information (auth + profile)"""
    # Get auth info
    token = request.headers.get("authorization", "").replace("Bearer ", "")
    auth_info = await get_user_from_auth_service(user_id, token)
    
    if not auth_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in auth service"
        )
    
    # Get profile
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    return CompleteUserResponse(
        auth_info=UserInfoResponse(**auth_info),
        profile=profile
    )

@router.get("/activity", response_model=List[ActivityLogResponse])
async def get_my_activity(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    """Get current user's activity logs"""
    user_id = current_user.get("user_id")
    
    logs = db.query(ActivityLog)\
        .filter(ActivityLog.user_id == user_id)\
        .order_by(ActivityLog.created_at.desc())\
        .limit(limit)\
        .all()
    
    return logs

@router.get("/activity/{user_id}", response_model=List[ActivityLogResponse])
async def get_user_activity(
    user_id: int,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(require_role(["administrador"]))
):
    """Get any user's activity logs (admin only)"""
    logs = db.query(ActivityLog)\
        .filter(ActivityLog.user_id == user_id)\
        .order_by(ActivityLog.created_at.desc())\
        .limit(limit)\
        .all()
    
    return logs

@router.post("/activity", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_activity_log(
    data: ActivityLogCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    """Create manual activity log entry"""
    user_id = current_user.get("user_id")
    client_info = get_client_info(request)
    
    log_activity(
        db,
        user_id,
        data.accion,
        data.descripcion,
        client_info if not data.ip_address else {
            "ip_address": data.ip_address,
            "user_agent": data.user_agent
        }
    )
    
    return MessageResponse(message="Activity logged successfully")
