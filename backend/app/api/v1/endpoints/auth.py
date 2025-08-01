"""
Authentication endpoints
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import structlog

from app.core.database import get_db
from app.core.security import (
    verify_password, get_password_hash, create_access_token, create_refresh_token,
    verify_token, security, validate_password_strength, AuditLogger
)
from app.core.exceptions import (
    AuthenticationError, ValidationError, AccountLockedError, 
    InvalidTokenError, NotFoundError
)
from app.models.user import User, UserDetail
from app.core.config import settings

logger = structlog.get_logger()
router = APIRouter()

# Pydantic models for request/response
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class UserRegistrationRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    first_name_kana: Optional[str] = None
    last_name_kana: Optional[str] = None

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token, "access")
    
    if not payload:
        raise InvalidTokenError("access")
    
    user_id = payload.get("sub")
    if not user_id:
        raise InvalidTokenError("access")
    
    user = db.query(User).filter(User.user_id == int(user_id)).first()
    if not user:
        raise NotFoundError("User", user_id)
    
    if not user.is_active:
        raise AuthenticationError("Account is deactivated")
    
    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise AccountLockedError(user.locked_until.isoformat())
    
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise AuthenticationError("Account is deactivated")
    return current_user

@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """User login endpoint"""
    try:
        # Find user by username or email
        user = db.query(User).filter(
            (User.username == login_data.username) | 
            (User.email == login_data.username)
        ).first()
        
        if not user:
            # Log failed login attempt
            AuditLogger.log_action(
                user_id=None,
                action="LOGIN",
                table_name="T_User",
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent"),
                additional_data={"username": login_data.username, "success": False}
            )
            raise AuthenticationError("Invalid username or password")
        
        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.utcnow():
            raise AccountLockedError(user.locked_until.isoformat())
        
        # Verify password
        if not verify_password(login_data.password, user.password_hash):
            # Increment failed login attempts
            user.failed_login_attempts += 1
            
            # Lock account after 5 failed attempts
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=30)
                logger.warning("Account locked due to failed login attempts", user_id=user.user_id)
            
            db.commit()
            
            # Log failed login attempt
            AuditLogger.log_action(
                user_id=user.user_id,
                action="LOGIN",
                table_name="T_User",
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent"),
                additional_data={"username": login_data.username, "success": False}
            )
            
            raise AuthenticationError("Invalid username or password")
        
        # Check if user is active
        if not user.is_active:
            raise AuthenticationError("Account is deactivated")
        
        # Reset failed login attempts on successful login
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Create tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.user_id), "username": user.username, "role": user.role},
            expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.user_id), "username": user.username}
        )
        
        # Get user details
        user_detail = db.query(UserDetail).filter(UserDetail.user_id == user.user_id).first()
        
        user_data = {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "first_name": user_detail.first_name if user_detail else None,
            "last_name": user_detail.last_name if user_detail else None,
        }
        
        # Log successful login
        AuditLogger.log_action(
            user_id=user.user_id,
            action="LOGIN",
            table_name="T_User",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            additional_data={"username": login_data.username, "success": True}
        )
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_data
        )
        
    except Exception as e:
        logger.error("Login error", error=str(e), username=login_data.username)
        if isinstance(e, (AuthenticationError, AccountLockedError)):
            raise
        raise AuthenticationError("Login failed")

@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(
    request: Request,
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token"""
    try:
        payload = verify_token(refresh_data.refresh_token, "refresh")
        
        if not payload:
            raise InvalidTokenError("refresh")
        
        user_id = payload.get("sub")
        if not user_id:
            raise InvalidTokenError("refresh")
        
        user = db.query(User).filter(User.user_id == int(user_id)).first()
        if not user or not user.is_active:
            raise AuthenticationError("User not found or inactive")
        
        # Create new tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.user_id), "username": user.username, "role": user.role},
            expires_delta=access_token_expires
        )
        new_refresh_token = create_refresh_token(
            data={"sub": str(user.user_id), "username": user.username}
        )
        
        # Get user details
        user_detail = db.query(UserDetail).filter(UserDetail.user_id == user.user_id).first()
        
        user_data = {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "first_name": user_detail.first_name if user_detail else None,
            "last_name": user_detail.last_name if user_detail else None,
        }
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_data
        )
        
    except Exception as e:
        logger.error("Token refresh error", error=str(e))
        if isinstance(e, (InvalidTokenError, AuthenticationError)):
            raise
        raise InvalidTokenError("refresh")

@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """User logout endpoint"""
    # Log logout
    AuditLogger.log_action(
        user_id=current_user.user_id,
        action="LOGOUT",
        table_name="T_User",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return {"message": "Successfully logged out"}

@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user information"""
    user_detail = db.query(UserDetail).filter(UserDetail.user_id == current_user.user_id).first()
    
    return {
        "user_id": current_user.user_id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "last_login": current_user.last_login,
        "created_at": current_user.created_at,
        "detail": {
            "first_name": user_detail.first_name if user_detail else None,
            "last_name": user_detail.last_name if user_detail else None,
            "first_name_kana": user_detail.first_name_kana if user_detail else None,
            "last_name_kana": user_detail.last_name_kana if user_detail else None,
            "phone_number": user_detail.phone_number if user_detail else None,
            "prefecture": user_detail.prefecture if user_detail else None,
            "city": user_detail.city if user_detail else None,
        } if user_detail else None
    }

@router.post("/change-password")
async def change_password(
    request: Request,
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise AuthenticationError("Current password is incorrect")
    
    # Validate new password strength
    is_strong, message = validate_password_strength(password_data.new_password)
    if not is_strong:
        raise ValidationError(message, "new_password")
    
    # Update password
    current_user.password_hash = get_password_hash(password_data.new_password)
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    # Log password change
    AuditLogger.log_action(
        user_id=current_user.user_id,
        action="UPDATE",
        table_name="T_User",
        record_id=str(current_user.user_id),
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        additional_data={"action": "password_change"}
    )
    
    return {"message": "Password changed successfully"}

@router.post("/register")
async def register_user(
    request: Request,
    user_data: UserRegistrationRequest,
    db: Session = Depends(get_db)
):
    """Register new user (if registration is enabled)"""
    # Check if username already exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        if existing_user.username == user_data.username:
            raise ValidationError("Username already exists", "username")
        else:
            raise ValidationError("Email already exists", "email")
    
    # Validate password strength
    is_strong, message = validate_password_strength(user_data.password)
    if not is_strong:
        raise ValidationError(message, "password")
    
    try:
        # Create user
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
            role="user",  # Default role
            is_active=True
        )
        
        db.add(new_user)
        db.flush()  # Get user_id
        
        # Create user detail
        user_detail = UserDetail(
            user_id=new_user.user_id,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            first_name_kana=user_data.first_name_kana,
            last_name_kana=user_data.last_name_kana
        )
        
        db.add(user_detail)
        db.commit()
        
        # Log user registration
        AuditLogger.log_action(
            user_id=new_user.user_id,
            action="CREATE",
            table_name="T_User",
            record_id=str(new_user.user_id),
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            additional_data={"action": "user_registration"}
        )
        
        return {
            "message": "User registered successfully",
            "user_id": new_user.user_id,
            "username": new_user.username
        }
        
    except Exception as e:
        db.rollback()
        logger.error("User registration error", error=str(e))
        raise ValidationError("Registration failed")