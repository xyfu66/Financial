"""
Audit middleware for logging user actions
"""
import json
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from .models import AuditLog, AuditActionType


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware to log user actions for audit purposes
    """
    
    def process_request(self, request):
        # Store request info for later use
        request.audit_info = {
            'ip_address': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'session_id': request.session.session_key if hasattr(request, 'session') else '',
        }
        return None
    
    def process_response(self, request, response):
        # Log API actions
        if (hasattr(request, 'user') and 
            not isinstance(request.user, AnonymousUser) and
            request.path.startswith('/api/') and
            request.method in ['POST', 'PUT', 'PATCH', 'DELETE']):
            
            action = self.get_action_from_method(request.method)
            
            try:
                AuditLog.objects.create(
                    user=request.user,
                    table_name=self.get_table_from_path(request.path),
                    action=action,
                    ip_address=getattr(request, 'audit_info', {}).get('ip_address'),
                    user_agent=getattr(request, 'audit_info', {}).get('user_agent'),
                    session_id=getattr(request, 'audit_info', {}).get('session_id'),
                )
            except Exception:
                # Don't break the request if audit logging fails
                pass
        
        return response
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def get_action_from_method(self, method):
        """Map HTTP method to audit action"""
        mapping = {
            'POST': AuditActionType.CREATE,
            'PUT': AuditActionType.UPDATE,
            'PATCH': AuditActionType.UPDATE,
            'DELETE': AuditActionType.DELETE,
        }
        return mapping.get(method, AuditActionType.UPDATE)
    
    def get_table_from_path(self, path):
        """Extract table name from API path"""
        parts = path.strip('/').split('/')
        if len(parts) >= 3:
            return parts[2]  # /api/v1/tablename/
        return 'unknown'