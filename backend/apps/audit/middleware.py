"""
Audit middleware for automatic logging
"""

import time
import json
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from .utils import log_audit, get_client_ip


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware to automatically log API requests and responses
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """
        Process incoming request
        """
        # Store request start time
        request._audit_start_time = time.time()
        
        # Store request data for audit logging
        request._audit_data = {
            'method': request.method,
            'path': request.path,
            'ip_address': get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'content_type': request.META.get('CONTENT_TYPE', ''),
            'query_params': dict(request.GET),
        }
        
        # Store request body for POST/PUT/PATCH requests (be careful with sensitive data)
        if request.method in ['POST', 'PUT', 'PATCH'] and request.content_type == 'application/json':
            try:
                if hasattr(request, 'body') and request.body:
                    body = json.loads(request.body.decode('utf-8'))
                    # Remove sensitive fields
                    sensitive_fields = ['password', 'password_confirm', 'token', 'secret']
                    for field in sensitive_fields:
                        if field in body:
                            body[field] = '***REDACTED***'
                    request._audit_data['request_body'] = body
            except (json.JSONDecodeError, UnicodeDecodeError):
                # If we can't parse the body, just note that there was a body
                request._audit_data['request_body'] = '***UNPARSEABLE***'
        
        return None
    
    def process_response(self, request, response):
        """
        Process outgoing response
        """
        # Skip audit logging for certain paths
        skip_paths = [
            '/admin/',
            '/static/',
            '/media/',
            '/favicon.ico',
            '/health/',
        ]
        
        if any(request.path.startswith(path) for path in skip_paths):
            return response
        
        # Calculate request duration
        duration = None
        if hasattr(request, '_audit_start_time'):
            duration = time.time() - request._audit_start_time
        
        # Get user
        user = getattr(request, 'user', None)
        if user and user.is_anonymous:
            user = None
        
        # Determine action based on method and response status
        action = self._determine_action(request, response)
        
        # Log the request
        try:
            audit_data = getattr(request, '_audit_data', {})
            
            log_audit(
                user=user,
                action=action,
                request_path=audit_data.get('path'),
                request_method=audit_data.get('method'),
                ip_address=audit_data.get('ip_address'),
                user_agent=audit_data.get('user_agent'),
                duration=duration,
                success=200 <= response.status_code < 400,
                error_message=self._get_error_message(response) if response.status_code >= 400 else None,
                extra_data={
                    'status_code': response.status_code,
                    'content_type': response.get('Content-Type', ''),
                    'query_params': audit_data.get('query_params', {}),
                    'request_body': audit_data.get('request_body'),
                }
            )
        except Exception as e:
            # Don't let audit logging break the response
            import logging
            logging.error(f"Audit logging failed: {str(e)}")
        
        return response
    
    def _determine_action(self, request, response):
        """
        Determine the action based on request method and response
        """
        method = request.method.upper()
        
        if method == 'GET':
            return 'VIEW'
        elif method == 'POST':
            if 200 <= response.status_code < 300:
                return 'CREATE'
            else:
                return 'CREATE_FAILED'
        elif method == 'PUT':
            if 200 <= response.status_code < 300:
                return 'UPDATE'
            else:
                return 'UPDATE_FAILED'
        elif method == 'PATCH':
            if 200 <= response.status_code < 300:
                return 'UPDATE'
            else:
                return 'UPDATE_FAILED'
        elif method == 'DELETE':
            if 200 <= response.status_code < 300:
                return 'DELETE'
            else:
                return 'DELETE_FAILED'
        else:
            return f'{method}_REQUEST'
    
    def _get_error_message(self, response):
        """
        Extract error message from response
        """
        try:
            if hasattr(response, 'content'):
                content = response.content.decode('utf-8')
                if response.get('Content-Type', '').startswith('application/json'):
                    data = json.loads(content)
                    if isinstance(data, dict):
                        return data.get('error', data.get('detail', str(data)))
                return content[:500]  # Limit error message length
        except:
            pass
        
        return f"HTTP {response.status_code}"


class SecurityMiddleware(MiddlewareMixin):
    """
    Security middleware for additional security checks
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """
        Process security checks on incoming requests
        """
        # Check for suspicious patterns
        self._check_suspicious_patterns(request)
        
        # Rate limiting check (basic implementation)
        self._check_rate_limiting(request)
        
        return None
    
    def _check_suspicious_patterns(self, request):
        """
        Check for suspicious request patterns
        """
        suspicious_patterns = [
            'script',
            'javascript:',
            '<script',
            'eval(',
            'union select',
            'drop table',
            '../',
            '..\\',
        ]
        
        # Check URL path
        path_lower = request.path.lower()
        for pattern in suspicious_patterns:
            if pattern in path_lower:
                self._log_security_event(
                    request,
                    'SUSPICIOUS_PATH',
                    f"Suspicious pattern '{pattern}' found in path: {request.path}"
                )
                break
        
        # Check query parameters
        for key, value in request.GET.items():
            value_lower = str(value).lower()
            for pattern in suspicious_patterns:
                if pattern in value_lower:
                    self._log_security_event(
                        request,
                        'SUSPICIOUS_QUERY',
                        f"Suspicious pattern '{pattern}' found in query parameter '{key}': {value}"
                    )
                    break
    
    def _check_rate_limiting(self, request):
        """
        Basic rate limiting check
        """
        # This is a simple implementation - in production, use Redis or similar
        from django.core.cache import cache
        
        ip_address = get_client_ip(request)
        cache_key = f"rate_limit_{ip_address}"
        
        # Get current request count
        current_count = cache.get(cache_key, 0)
        
        # Check if limit exceeded (100 requests per minute)
        if current_count > 100:
            self._log_security_event(
                request,
                'RATE_LIMIT_EXCEEDED',
                f"Rate limit exceeded for IP {ip_address}: {current_count} requests"
            )
        
        # Increment counter
        cache.set(cache_key, current_count + 1, 60)  # 60 seconds
    
    def _log_security_event(self, request, event_type, details):
        """
        Log security event
        """
        try:
            from .utils import log_security_event
            
            user = getattr(request, 'user', None)
            if user and user.is_anonymous:
                user = None
            
            log_security_event(
                user=user,
                event_type=event_type,
                details=details,
                severity='WARNING',
                request=request
            )
        except Exception as e:
            import logging
            logging.error(f"Security event logging failed: {str(e)}")


class RequestContextMiddleware(MiddlewareMixin):
    """
    Middleware to store request in thread local storage for access in signals
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """
        Store request in thread local storage
        """
        import threading
        threading.current_thread().request = request
        return None
    
    def process_response(self, request, response):
        """
        Clean up thread local storage
        """
        import threading
        if hasattr(threading.current_thread(), 'request'):
            delattr(threading.current_thread(), 'request')
        return response
    
    def process_exception(self, request, exception):
        """
        Clean up thread local storage on exception
        """
        import threading
        if hasattr(threading.current_thread(), 'request'):
            delattr(threading.current_thread(), 'request')
        return None