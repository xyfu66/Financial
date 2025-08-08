"""
Custom permissions for accounts app
"""
from rest_framework import permissions
from .models import UserRole


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to only allow owners of an object or admins to access it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Write permissions are only allowed to the owner or admin
        if hasattr(obj, 'user'):
            return obj.user == request.user or request.user.is_admin
        
        return obj == request.user or request.user.is_admin


class IsSuperAdminOrAdmin(permissions.BasePermission):
    """
    Permission to only allow super admins or admins to access.
    """
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]
        )


class IsSuperAdmin(permissions.BasePermission):
    """
    Permission to only allow super admins to access.
    """
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == UserRole.SUPER_ADMIN
        )


class IsOwner(permissions.BasePermission):
    """
    Permission to only allow owners of an object to access it.
    """
    
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return obj == request.user


class CanManageUsers(permissions.BasePermission):
    """
    Permission for user management operations
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Super admins can do everything
        if request.user.role == UserRole.SUPER_ADMIN:
            return True
        
        # Admins can manage regular users
        if request.user.role == UserRole.ADMIN:
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Super admins can manage anyone
        if request.user.role == UserRole.SUPER_ADMIN:
            return True
        
        # Admins can manage regular users but not other admins or super admins
        if request.user.role == UserRole.ADMIN:
            return obj.role == UserRole.USER
        
        return False


class CanViewFinancialData(permissions.BasePermission):
    """
    Permission for viewing financial data
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Users can only view their own data
        if hasattr(obj, 'user'):
            return obj.user == request.user or request.user.is_admin
        
        return request.user.is_admin


class CanManageFinancialData(permissions.BasePermission):
    """
    Permission for managing financial data
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Users can only manage their own data
        if hasattr(obj, 'user'):
            return obj.user == request.user or request.user.is_admin
        
        return request.user.is_admin


class CanExportData(permissions.BasePermission):
    """
    Permission for exporting data
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # All authenticated users can export their own data
        return True
    
    def has_object_permission(self, request, view, obj):
        # Users can only export their own data
        if hasattr(obj, 'user'):
            return obj.user == request.user or request.user.is_admin
        
        return request.user.is_admin


class CanProcessOCR(permissions.BasePermission):
    """
    Permission for OCR processing
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Users can only process OCR for their own files
        if hasattr(obj, 'user'):
            return obj.user == request.user or request.user.is_admin
        
        return request.user.is_admin


class CanViewAuditLogs(permissions.BasePermission):
    """
    Permission for viewing audit logs
    """
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]
        )


class CanManageNotifications(permissions.BasePermission):
    """
    Permission for managing system notifications
    """
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in [UserRoleChoices.SUPER_ADMIN, UserRoleChoices.ADMIN]
        )