"""
Custom exceptions for the Personal Financial Management System
"""

from typing import Optional, Dict, Any

class CustomException(Exception):
    """Base custom exception class"""
    
    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 400,
        detail: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.detail = detail or {}
        super().__init__(self.message)

class AuthenticationError(CustomException):
    """Authentication related errors"""
    
    def __init__(self, message: str = "Authentication failed", detail: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=401,
            detail=detail
        )

class AuthorizationError(CustomException):
    """Authorization related errors"""
    
    def __init__(self, message: str = "Access denied", detail: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=403,
            detail=detail
        )

class ValidationError(CustomException):
    """Data validation errors"""
    
    def __init__(self, message: str, field: Optional[str] = None, detail: Optional[Dict[str, Any]] = None):
        detail = detail or {}
        if field:
            detail["field"] = field
        
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=422,
            detail=detail
        )

class NotFoundError(CustomException):
    """Resource not found errors"""
    
    def __init__(self, resource: str, identifier: Optional[str] = None, detail: Optional[Dict[str, Any]] = None):
        message = f"{resource} not found"
        if identifier:
            message += f" with identifier: {identifier}"
        
        detail = detail or {}
        detail["resource"] = resource
        if identifier:
            detail["identifier"] = identifier
        
        super().__init__(
            message=message,
            error_code="NOT_FOUND_ERROR",
            status_code=404,
            detail=detail
        )

class ConflictError(CustomException):
    """Resource conflict errors"""
    
    def __init__(self, message: str, resource: Optional[str] = None, detail: Optional[Dict[str, Any]] = None):
        detail = detail or {}
        if resource:
            detail["resource"] = resource
        
        super().__init__(
            message=message,
            error_code="CONFLICT_ERROR",
            status_code=409,
            detail=detail
        )

class BusinessLogicError(CustomException):
    """Business logic related errors"""
    
    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="BUSINESS_LOGIC_ERROR",
            status_code=400,
            detail=detail
        )

class FileProcessingError(CustomException):
    """File processing related errors"""
    
    def __init__(self, message: str, filename: Optional[str] = None, detail: Optional[Dict[str, Any]] = None):
        detail = detail or {}
        if filename:
            detail["filename"] = filename
        
        super().__init__(
            message=message,
            error_code="FILE_PROCESSING_ERROR",
            status_code=400,
            detail=detail
        )

class OCRProcessingError(CustomException):
    """OCR processing related errors"""
    
    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="OCR_PROCESSING_ERROR",
            status_code=500,
            detail=detail
        )

class DatabaseError(CustomException):
    """Database related errors"""
    
    def __init__(self, message: str, operation: Optional[str] = None, detail: Optional[Dict[str, Any]] = None):
        detail = detail or {}
        if operation:
            detail["operation"] = operation
        
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=500,
            detail=detail
        )

class ExternalServiceError(CustomException):
    """External service related errors"""
    
    def __init__(self, message: str, service: Optional[str] = None, detail: Optional[Dict[str, Any]] = None):
        detail = detail or {}
        if service:
            detail["service"] = service
        
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=502,
            detail=detail
        )

class RateLimitError(CustomException):
    """Rate limiting errors"""
    
    def __init__(self, message: str = "Rate limit exceeded", detail: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            status_code=429,
            detail=detail
        )

class ConfigurationError(CustomException):
    """Configuration related errors"""
    
    def __init__(self, message: str, config_key: Optional[str] = None, detail: Optional[Dict[str, Any]] = None):
        detail = detail or {}
        if config_key:
            detail["config_key"] = config_key
        
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            status_code=500,
            detail=detail
        )

# Specific business exceptions
class InsufficientPermissionError(AuthorizationError):
    """User doesn't have required permission"""
    
    def __init__(self, permission: str, detail: Optional[Dict[str, Any]] = None):
        detail = detail or {}
        detail["required_permission"] = permission
        
        super().__init__(
            message=f"Insufficient permission: {permission} required",
            detail=detail
        )

class AccountLockedError(AuthenticationError):
    """User account is locked"""
    
    def __init__(self, unlock_time: Optional[str] = None, detail: Optional[Dict[str, Any]] = None):
        detail = detail or {}
        if unlock_time:
            detail["unlock_time"] = unlock_time
        
        message = "Account is locked"
        if unlock_time:
            message += f" until {unlock_time}"
        
        super().__init__(message=message, detail=detail)

class InvalidTokenError(AuthenticationError):
    """Invalid or expired token"""
    
    def __init__(self, token_type: str = "access", detail: Optional[Dict[str, Any]] = None):
        detail = detail or {}
        detail["token_type"] = token_type
        
        super().__init__(
            message=f"Invalid or expired {token_type} token",
            detail=detail
        )

class DuplicateRecordError(ConflictError):
    """Duplicate record error"""
    
    def __init__(self, field: str, value: str, detail: Optional[Dict[str, Any]] = None):
        detail = detail or {}
        detail["field"] = field
        detail["value"] = value
        
        super().__init__(
            message=f"Record with {field} '{value}' already exists",
            detail=detail
        )

class InvalidFileTypeError(FileProcessingError):
    """Invalid file type error"""
    
    def __init__(self, filename: str, allowed_types: list, detail: Optional[Dict[str, Any]] = None):
        detail = detail or {}
        detail["allowed_types"] = allowed_types
        
        super().__init__(
            message=f"Invalid file type. Allowed types: {', '.join(allowed_types)}",
            filename=filename,
            detail=detail
        )

class FileSizeExceededError(FileProcessingError):
    """File size exceeded error"""
    
    def __init__(self, filename: str, max_size: int, actual_size: int, detail: Optional[Dict[str, Any]] = None):
        detail = detail or {}
        detail["max_size"] = max_size
        detail["actual_size"] = actual_size
        
        super().__init__(
            message=f"File size ({actual_size} bytes) exceeds maximum allowed size ({max_size} bytes)",
            filename=filename,
            detail=detail
        )

class CalculationError(BusinessLogicError):
    """Financial calculation error"""
    
    def __init__(self, calculation_type: str, message: str, detail: Optional[Dict[str, Any]] = None):
        detail = detail or {}
        detail["calculation_type"] = calculation_type
        
        super().__init__(
            message=f"Calculation error ({calculation_type}): {message}",
            detail=detail
        )

class ImportError(BusinessLogicError):
    """Data import error"""
    
    def __init__(self, row_number: Optional[int] = None, field: Optional[str] = None, 
                 message: str = "Import failed", detail: Optional[Dict[str, Any]] = None):
        detail = detail or {}
        if row_number:
            detail["row_number"] = row_number
        if field:
            detail["field"] = field
        
        error_message = message
        if row_number:
            error_message += f" at row {row_number}"
        if field:
            error_message += f" in field '{field}'"
        
        super().__init__(message=error_message, detail=detail)