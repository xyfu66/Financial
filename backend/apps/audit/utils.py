"""
Audit utility functions
"""

import logging
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

# Get audit logger
audit_logger = logging.getLogger('audit')


def log_audit(user, action, model=None, object_id=None, old_values=None, new_values=None, changes=None, **kwargs):
    """
    Log audit event
    
    Args:
        user: User performing the action
        action: Action being performed
        model: Model name (optional)
        object_id: Object ID (optional)
        old_values: Old values before change (optional)
        new_values: New values after change (optional)
        changes: Summary of changes (optional)
        **kwargs: Additional fields for AuditLog
    """
    try:
        from apps.system.models import AuditLog
        
        # Get request information if available
        request = kwargs.pop('request', None)
        if not request:
            # Try to get request from thread local storage
            import threading
            request = getattr(threading.current_thread(), 'request', None)
        
        # Extract request information
        ip_address = kwargs.pop('ip_address', None)
        user_agent = kwargs.pop('user_agent', None)
        request_path = kwargs.pop('request_path', None)
        request_method = kwargs.pop('request_method', None)
        
        if request:
            if not ip_address:
                ip_address = get_client_ip(request)
            if not user_agent:
                user_agent = request.META.get('HTTP_USER_AGENT', '')
            if not request_path:
                request_path = request.path
            if not request_method:
                request_method = request.method
        
        # Create audit log entry
        audit_log = AuditLog.objects.create(
            user=user,
            username=user.username if user else 'Anonymous',
            user_role=user.role if user else None,
            action=action,
            model=model,
            object_id=str(object_id) if object_id else None,
            old_values=old_values,
            new_values=new_values,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
            request_path=request_path,
            request_method=request_method,
            **kwargs
        )
        
        # Also log to audit logger
        audit_logger.info(
            f"User: {user.username if user else 'Anonymous'} | "
            f"Action: {action} | "
            f"Model: {model} | "
            f"Object ID: {object_id} | "
            f"IP: {ip_address} | "
            f"Path: {request_path}"
        )
        
        return audit_log
        
    except Exception as e:
        # Log error but don't raise to avoid breaking the main operation
        logging.error(f"Failed to create audit log: {str(e)}")
        return None


def get_client_ip(request):
    """
    Get client IP address from request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_model_changes(old_instance, new_instance, exclude_fields=None):
    """
    Get changes between two model instances
    
    Args:
        old_instance: Original model instance
        new_instance: Updated model instance
        exclude_fields: List of fields to exclude from comparison
    
    Returns:
        dict: Dictionary of changes with old and new values
    """
    if exclude_fields is None:
        exclude_fields = ['updated_at', 'created_at']
    
    changes = {}
    old_values = {}
    new_values = {}
    
    # Get all fields from the model
    for field in new_instance._meta.fields:
        field_name = field.name
        
        if field_name in exclude_fields:
            continue
        
        old_value = getattr(old_instance, field_name, None)
        new_value = getattr(new_instance, field_name, None)
        
        # Convert to string for comparison
        old_str = str(old_value) if old_value is not None else None
        new_str = str(new_value) if new_value is not None else None
        
        if old_str != new_str:
            changes[field_name] = {
                'old': old_str,
                'new': new_str
            }
            old_values[field_name] = old_str
            new_values[field_name] = new_str
    
    return {
        'changes': changes,
        'old_values': old_values,
        'new_values': new_values
    }


def log_model_change(user, action, instance, old_instance=None, request=None):
    """
    Log model change with automatic change detection
    
    Args:
        user: User performing the action
        action: Action being performed (CREATE, UPDATE, DELETE)
        instance: Model instance
        old_instance: Original instance (for UPDATE actions)
        request: HTTP request object
    """
    model_name = instance.__class__.__name__
    object_id = instance.pk
    
    old_values = None
    new_values = None
    changes = None
    
    if action == 'UPDATE' and old_instance:
        change_data = get_model_changes(old_instance, instance)
        old_values = change_data['old_values']
        new_values = change_data['new_values']
        changes = change_data['changes']
    elif action == 'CREATE':
        # For create, capture the new values
        new_values = {}
        for field in instance._meta.fields:
            if field.name not in ['created_at', 'updated_at']:
                value = getattr(instance, field.name, None)
                new_values[field.name] = str(value) if value is not None else None
    elif action == 'DELETE':
        # For delete, capture the old values
        old_values = {}
        for field in instance._meta.fields:
            if field.name not in ['created_at', 'updated_at']:
                value = getattr(instance, field.name, None)
                old_values[field.name] = str(value) if value is not None else None
    
    return log_audit(
        user=user,
        action=action,
        model=model_name,
        object_id=object_id,
        old_values=old_values,
        new_values=new_values,
        changes=changes,
        request=request
    )


def log_security_event(user, event_type, details=None, severity='INFO', request=None):
    """
    Log security-related events
    
    Args:
        user: User involved in the event
        event_type: Type of security event
        details: Additional details about the event
        severity: Severity level (INFO, WARNING, ERROR, CRITICAL)
        request: HTTP request object
    """
    return log_audit(
        user=user,
        action=f'SECURITY_{event_type}',
        changes={
            'event_type': event_type,
            'details': details,
            'severity': severity
        },
        request=request
    )


def log_login_attempt(user, success, ip_address=None, user_agent=None, failure_reason=None):
    """
    Log login attempt
    
    Args:
        user: User attempting to login
        success: Whether login was successful
        ip_address: IP address of the attempt
        user_agent: User agent string
        failure_reason: Reason for failure (if applicable)
    """
    action = 'LOGIN' if success else 'LOGIN_FAILED'
    
    changes = {
        'success': success,
        'ip_address': ip_address,
        'user_agent': user_agent
    }
    
    if not success and failure_reason:
        changes['failure_reason'] = failure_reason
    
    return log_audit(
        user=user,
        action=action,
        changes=changes,
        ip_address=ip_address,
        user_agent=user_agent,
        success=success
    )


def log_file_operation(user, operation, file_path, file_size=None, request=None):
    """
    Log file operations (upload, download, delete)
    
    Args:
        user: User performing the operation
        operation: Type of operation (UPLOAD, DOWNLOAD, DELETE)
        file_path: Path to the file
        file_size: Size of the file in bytes
        request: HTTP request object
    """
    changes = {
        'operation': operation,
        'file_path': file_path
    }
    
    if file_size:
        changes['file_size'] = file_size
    
    return log_audit(
        user=user,
        action=f'FILE_{operation}',
        changes=changes,
        request=request
    )


def log_data_export(user, export_type, record_count=None, filters=None, request=None):
    """
    Log data export operations
    
    Args:
        user: User performing the export
        export_type: Type of export (CSV, PDF, EXCEL)
        record_count: Number of records exported
        filters: Filters applied to the export
        request: HTTP request object
    """
    changes = {
        'export_type': export_type,
        'record_count': record_count,
        'filters': filters,
        'timestamp': timezone.now().isoformat()
    }
    
    return log_audit(
        user=user,
        action='EXPORT',
        changes=changes,
        request=request
    )


def log_system_event(event_type, details=None, user=None):
    """
    Log system-level events
    
    Args:
        event_type: Type of system event
        details: Additional details about the event
        user: User associated with the event (if any)
    """
    return log_audit(
        user=user,
        action='SYSTEM',
        changes={
            'event_type': event_type,
            'details': details,
            'timestamp': timezone.now().isoformat()
        }
    )


class AuditContextManager:
    """
    Context manager for audit logging
    """
    
    def __init__(self, user, action, model=None, object_id=None):
        self.user = user
        self.action = action
        self.model = model
        self.object_id = object_id
        self.start_time = None
        self.audit_log = None
    
    def __enter__(self):
        self.start_time = timezone.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (timezone.now() - self.start_time).total_seconds()
        success = exc_type is None
        
        error_message = None
        if exc_type:
            error_message = str(exc_val)
        
        self.audit_log = log_audit(
            user=self.user,
            action=self.action,
            model=self.model,
            object_id=self.object_id,
            duration=duration,
            success=success,
            error_message=error_message
        )
        
        return False  # Don't suppress exceptions


def audit_operation(user, action, model=None, object_id=None):
    """
    Decorator/context manager for audit logging
    
    Usage:
        with audit_operation(user, 'CALCULATE', 'TaxCalculation', calc_id):
            # Perform operation
            pass
    """
    return AuditContextManager(user, action, model, object_id)