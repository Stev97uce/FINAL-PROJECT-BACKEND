from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from app.database import get_db
from app.schemas import (
    RegisterRequest, RegisterResponse,
    LoginRequest, LoginResponse,
    ForgotPasswordRequest, ResetPasswordRequest,
    RefreshTokenRequest, RefreshTokenResponse,
    MessageResponse, UserResponse, TokenValidationResponse
)
from app.models import User, VerificationToken, RefreshToken, RolEnum, EstadoEnum, TipoTokenEnum
from app.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    decode_access_token, generate_verification_token
)
from app.events import (
    publish_user_registered,
    publish_user_verified,
    publish_password_reset_requested
)
from app.dependencies import get_current_user, require_admin
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user (consultantes only - self registration)
    For other roles, use /register-staff endpoint with admin authentication
    """
    # Only allow consultante role in public registration
    if data.rol != RolEnum.CONSULTANTE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo se permite auto-registro para consultantes. Para otros roles, use /api/auth/register-staff con autenticación de administrador."
        )
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # Check if identificacion already exists
    existing_id = db.query(User).filter(User.identificacion == data.identificacion).first()
    if existing_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La identificación ya está registrada"
        )
    
    # Hash password
    password_hash = hash_password(data.password)
    
    # Create user
    new_user = User(
        nombres=data.nombres,
        identificacion=data.identificacion,
        email=data.email,
        telefono=data.telefono,
        password_hash=password_hash,
        rol=data.rol,
        estado=EstadoEnum.PENDIENTE_VERIFICACION,
        email_verificado=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate verification token
    token = generate_verification_token()
    expiration = datetime.utcnow() + timedelta(hours=24)
    
    verification_token = VerificationToken(
        user_id=new_user.id,
        token=token,
        tipo=TipoTokenEnum.EMAIL_VERIFICATION,
        expira_en=expiration,
        usado=False
    )
    
    db.add(verification_token)
    db.commit()
    
    # Publish event
    publish_user_registered(
        user_id=new_user.id,
        email=new_user.email,
        nombres=new_user.nombres,
        rol=new_user.rol.value,
        telefono=new_user.telefono
    )
    
    return RegisterResponse(
        user_id=new_user.id,
        message="Usuario registrado exitosamente. Por favor verifica tu email."
    )


@router.post("/register-staff", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_staff(
    data: RegisterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Register a user with special role (requires admin authentication)
    Roles: recepcionista, estudiante, psicologo_supervisor, administrador
    """
    # Prevent registration of consultante through this endpoint
    if data.rol == RolEnum.CONSULTANTE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use /api/auth/register para registrar consultantes"
        )
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # Check if identificacion already exists
    existing_id = db.query(User).filter(User.identificacion == data.identificacion).first()
    if existing_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La identificación ya está registrada"
        )
    
    # Hash password
    password_hash = hash_password(data.password)
    
    # Create user
    new_user = User(
        nombres=data.nombres,
        identificacion=data.identificacion,
        email=data.email,
        telefono=data.telefono,
        password_hash=password_hash,
        rol=data.rol,
        estado=EstadoEnum.PENDIENTE_VERIFICACION,
        email_verificado=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate verification token
    token = generate_verification_token()
    expiration = datetime.utcnow() + timedelta(hours=24)
    
    verification_token = VerificationToken(
        user_id=new_user.id,
        token=token,
        tipo=TipoTokenEnum.EMAIL_VERIFICATION,
        expira_en=expiration,
        usado=False
    )
    
    db.add(verification_token)
    db.commit()
    
    # Publish event
    publish_user_registered(
        user_id=new_user.id,
        email=new_user.email,
        nombres=new_user.nombres,
        rol=new_user.rol.value,
        telefono=new_user.telefono
    )
    
    return RegisterResponse(
        user_id=new_user.id,
        message=f"Usuario {data.rol.value} registrado exitosamente. Se ha enviado un email de verificación."
    )


@router.get("/verify-email/{token}", response_model=MessageResponse)
async def verify_email(token: str, db: Session = Depends(get_db)):
    """Verify email with token"""
    # Find token
    verification = db.query(VerificationToken).filter(
        VerificationToken.token == token,
        VerificationToken.tipo == TipoTokenEnum.EMAIL_VERIFICATION
    ).first()
    
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token de verificación no encontrado"
        )
    
    # Check if already used
    if verification.usado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este token ya fue utilizado"
        )
    
    # Check if expired
    if datetime.utcnow() > verification.expira_en:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El token de verificación ha expirado"
        )
    
    # Get user
    user = db.query(User).filter(User.id == verification.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Update user
    user.email_verificado = True
    user.estado = EstadoEnum.ACTIVO
    
    # Mark token as used
    verification.usado = True
    
    db.commit()
    
    # Publish event
    publish_user_verified(user_id=user.id, email=user.email)
    
    return MessageResponse(message="Email verificado exitosamente")


@router.post("/login", response_model=LoginResponse)
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Login with email and password"""
    # Find user
    user = db.query(User).filter(User.email == data.email).first()
    
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos"
        )
    
    # Check if email is verified
    if not user.email_verificado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Por favor verifica tu email antes de iniciar sesión"
        )
    
    # Check if user is active
    if user.estado != EstadoEnum.ACTIVO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta no está activa. Contacta al administrador."
        )
    
    # Create access token
    access_token = create_access_token({
        "user_id": user.id,
        "email": user.email,
        "rol": user.rol.value
    })
    
    # Create refresh token
    refresh_token_value = create_refresh_token()
    refresh_expiration = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    
    refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token_value,
        expira_en=refresh_expiration,
        revocado=False
    )
    
    db.add(refresh_token)
    db.commit()
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token_value,
        user=UserResponse(
            id=user.id,
            nombres=user.nombres,
            email=user.email,
            rol=user.rol.value
        )
    )


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Request password reset"""
    # Find user (don't reveal if email exists)
    user = db.query(User).filter(User.email == data.email).first()
    
    if user:
        # Generate reset token
        token = generate_verification_token()
        expiration = datetime.utcnow() + timedelta(hours=1)
        
        reset_token = VerificationToken(
            user_id=user.id,
            token=token,
            tipo=TipoTokenEnum.PASSWORD_RESET,
            expira_en=expiration,
            usado=False
        )
        
        db.add(reset_token)
        db.commit()
        
        # Publish event
        publish_password_reset_requested(
            email=user.email,
            token=token,
            expira_en=expiration.isoformat() + "Z"
        )
    
    # Always return success to not reveal if email exists
    return MessageResponse(
        message="Si el email existe, recibirás instrucciones para restablecer tu contraseña"
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password with token"""
    # Find token
    reset_token = db.query(VerificationToken).filter(
        VerificationToken.token == data.token,
        VerificationToken.tipo == TipoTokenEnum.PASSWORD_RESET
    ).first()
    
    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token de restablecimiento no encontrado"
        )
    
    # Check if already used
    if reset_token.usado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este token ya fue utilizado"
        )
    
    # Check if expired
    if datetime.utcnow() > reset_token.expira_en:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El token de restablecimiento ha expirado"
        )
    
    # Get user
    user = db.query(User).filter(User.id == reset_token.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Update password
    user.password_hash = hash_password(data.new_password)
    
    # Mark token as used
    reset_token.usado = True
    
    db.commit()
    
    return MessageResponse(message="Contraseña restablecida exitosamente")


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_access_token(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token"""
    # Find refresh token
    refresh_token = db.query(RefreshToken).filter(
        RefreshToken.token == data.refresh_token
    ).first()
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido"
        )
    
    # Check if revoked
    if refresh_token.revocado:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token revocado"
        )
    
    # Check if expired
    if datetime.utcnow() > refresh_token.expira_en:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expirado"
        )
    
    # Get user
    user = db.query(User).filter(User.id == refresh_token.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Create new access token
    access_token = create_access_token({
        "user_id": user.id,
        "email": user.email,
        "rol": user.rol.value
    })
    
    return RefreshTokenResponse(access_token=access_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Logout and revoke refresh token"""
    # Find and revoke refresh token
    refresh_token = db.query(RefreshToken).filter(
        RefreshToken.token == data.refresh_token,
        RefreshToken.user_id == current_user.id
    ).first()
    
    if refresh_token:
        refresh_token.revocado = True
        db.commit()
    
    return MessageResponse(message="Sesión cerrada exitosamente")


@router.get("/validate", response_model=TokenValidationResponse)
async def validate_token(current_user: User = Depends(get_current_user)):
    """Validate JWT token (for internal microservices)"""
    return TokenValidationResponse(
        user_id=current_user.id,
        email=current_user.email,
        rol=current_user.rol.value
    )
