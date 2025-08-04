"""
Custom permissions for User management
"""

from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Permission to only allow admin users to access the view.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_admin
        )


class IsAdminOrOwner(permissions.BasePermission):
    """
    Permission to allow admin users or object owners to access the view.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Admin users can access any object
        if request.user.is_admin:
            return True
        
        # Users can only access their own objects
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # For User objects, users can only access themselves
        if hasattr(obj, 'id') and hasattr(request.user, 'id'):
            return obj.id == request.user.id
        
        return False


class IsSuperAdminUser(permissions.BasePermission):
    """
    Permission to only allow super admin users to access the view.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_super_admin
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission to allow owners to edit their objects, others can only read.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return obj == request.user


class CanManageUsers(permissions.BasePermission):
    """
    Permission to check if user can manage other users.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.is_admin or request.user.has_permission('manage_users'))
        )


class CanViewAllData(permissions.BasePermission):
    """
    Permission to check if user can view all data.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.is_admin or request.user.has_permission('view_all_data'))
        )


class CanEditAllData(permissions.BasePermission):
    """
    Permission to check if user can edit all data.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.is_admin or request.user.has_permission('edit_all_data'))
        )


class CanDeleteData(permissions.BasePermission):
    """
    Permission to check if user can delete data.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.is_admin or request.user.has_permission('delete_data'))
        )


class CanImportData(permissions.BasePermission):
    """
    Permission to check if user can import data.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.is_admin or request.user.has_permission('import_data'))
        )


class CanExportData(permissions.BasePermission):
    """
    Permission to check if user can export data.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.is_admin or request.user.has_permission('export_data'))
        )


class ResourcePermission(permissions.BasePermission):
    """
    Generic permission class for resource-based permissions.
    """
    
    def __init__(self, resource_type, permission_type):
        self.resource_type = resource_type
        self.permission_type = permission_type
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Super admin has all permissions
        if request.user.is_super_admin:
            return True
        
        # Check specific permission
        return request.user.user_permissions.filter(
            resource_type=self.resource_type,
            permission_type=self.permission_type,
            is_granted=True
        ).exists()


def create_resource_permission(resource_type, permission_type):
    """
    Factory function to create resource-specific permission classes.
    """
    class CustomResourcePermission(ResourcePermission):
        def __init__(self):
            super().__init__(resource_type, permission_type)
    
    return CustomResourcePermission


# Pre-defined resource permissions
CanViewIncomes = create_resource_permission('incomes', 'view')
CanCreateIncomes = create_resource_permission('incomes', 'create')
CanEditIncomes = create_resource_permission('incomes', 'edit')
CanDeleteIncomes = create_resource_permission('incomes', 'delete')

CanViewExpenses = create_resource_permission('expenses', 'view')
CanCreateExpenses = create_resource_permission('expenses', 'create')
CanEditExpenses = create_resource_permission('expenses', 'edit')
CanDeleteExpenses = create_resource_permission('expenses', 'delete')

CanViewUsers = create_resource_permission('users', 'view')
CanCreateUsers = create_resource_permission('users', 'create')
CanEditUsers = create_resource_permission('users', 'edit')
CanDeleteUsers = create_resource_permission('users', 'delete')

CanViewReports = create_resource_permission('reports', 'view')
CanCreateReports = create_resource_permission('reports', 'create')
CanExportReports = create_resource_permission('reports', 'export')

CanViewSystem = create_resource_permission('system', 'view')
CanManageSystem = create_resource_permission('system', 'admin')

CanViewNotifications = create_resource_permission('notifications', 'view')
CanManageNotifications = create_resource_permission('notifications', 'admin')