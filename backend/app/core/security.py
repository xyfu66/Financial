"""
Security utilities and middleware
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import structlog
import time
from starlette.middleware.base import BaseHTTPMiddleware

from .config import settings

logger = structlog.get_logger()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token handler
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Check token type
        if payload.get("type") != token_type:
            return None
            
        # Check expiration
        exp = payload.get("exp")
        if exp is None or datetime.utcnow() > datetime.fromtimestamp(exp):
            return None
            
        return payload
    except JWTError as e:
        logger.warning("JWT verification failed", error=str(e))
        return None

def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is strong"

class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for adding security headers and rate limiting"""
    
    def __init__(self, app):
        super().__init__(app)
        self.rate_limit_store = {}  # In production, use Redis
    
    async def dispatch(self, request: Request, call_next):
        # Add security headers
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' https:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none';"
        )
        
        return response
    
    def check_rate_limit(self, client_ip: str) -> bool:
        """Simple rate limiting check"""
        current_time = time.time()
        minute_window = int(current_time // 60)
        
        key = f"{client_ip}:{minute_window}"
        
        if key not in self.rate_limit_store:
            self.rate_limit_store[key] = 0
        
        self.rate_limit_store[key] += 1
        
        # Clean old entries
        keys_to_remove = [k for k in self.rate_limit_store.keys() 
                         if int(k.split(':')[1]) < minute_window - 1]
        for k in keys_to_remove:
            del self.rate_limit_store[k]
        
        return self.rate_limit_store[key] <= settings.RATE_LIMIT_PER_MINUTE

def check_permissions(user_role: str, required_permission: str) -> bool:
    """Check if user role has required permission"""
    # Define role-based permissions
    role_permissions = {
        "super_admin": [
            # All permissions
            "income_create", "income_read", "income_update", "income_delete", "income_import", "income_export",
            "expense_create", "expense_read", "expense_update", "expense_delete", "expense_import", "expense_export",
            "user_create", "user_read", "user_update", "user_delete",
            "system_read", "system_update",
            "report_read", "report_export"
        ],
        "admin": [
            # Business data permissions
            "income_create", "income_read", "income_update", "income_delete", "income_import", "income_export",
            "expense_create", "expense_read", "expense_update", "expense_delete", "expense_import", "expense_export",
            # Limited user management
            "user_read", "user_update",
            # System read only
            "system_read",
            # Reports
            "report_read", "report_export"
        ],
        "user": [
            # Own data only
            "income_create", "income_read", "income_update", "income_import", "income_export",
            "expense_create", "expense_read", "expense_update", "expense_import", "expense_export",
            # Reports
            "report_read", "report_export"
        ]
    }
    
    return required_permission in role_permissions.get(user_role, [])

class PermissionChecker:
    """Permission checking utility"""
    
    def __init__(self, required_permission: str):
        self.required_permission = required_permission
    
    def __call__(self, current_user: dict) -> bool:
        if not current_user:
            return False
        
        user_role = current_user.get("role", "user")
        return check_permissions(user_role, self.required_permission)

def sanitize_input(data: str) -> str:
    """Basic input sanitization"""
    if not isinstance(data, str):
        return data
    
    # Remove potentially dangerous characters
    dangerous_chars = ["<", ">", "&", "\"", "'", "/", "\\"]
    for char in dangerous_chars:
        data = data.replace(char, "")
    
    return data.strip()

def validate_file_type(filename: str) -> bool:
    """Validate uploaded file type"""
    if not filename:
        return False
    
    file_extension = filename.lower().split('.')[-1] if '.' in filename else ''
    allowed_extensions = [ext.lstrip('.') for ext in settings.ALLOWED_FILE_TYPES]
    
    return file_extension in allowed_extensions

def generate_secure_filename(original_filename: str) -> str:
    """Generate secure filename for uploads"""
    import uuid
    import os
    
    # Get file extension
    _, ext = os.path.splitext(original_filename)
    
    # Generate UUID-based filename
    secure_name = f"{uuid.uuid4().hex}{ext}"
    
    return secure_name

class AuditLogger:
    """Audit logging utility"""
    
    @staticmethod
    def log_action(
        user_id: Optional[int],
        action: str,
        table_name: str,
        record_id: Optional[str] = None,
        old_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        additional_data: Optional[Dict] = None
    ):
        """Log audit action"""
        logger.info(
            "Audit log entry",
            user_id=user_id,
            action=action,
            table_name=table_name,
            record_id=record_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            additional_data=additional_data
        )