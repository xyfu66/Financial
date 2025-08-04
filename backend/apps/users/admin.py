"""
Admin configuration for User models
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserDetail, UserRole, UserPermission, UserHistory, UserDetailHistory


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin configuration for User model
    """
    list_display = [
        'username', 'email', 'role', 'is_active', 'is_staff',
        'created_at', 'last_login', 'failed_login_attempts'
    ]
    list_filter = [
        'role', 'is_active', 'is_staff', 'is_superuser',
        'created_at', 'last_login'
    ]
    search_fields = ['username', 'email', 'detail__first_name', 'detail__last_name']
    ordering = ['-created_at']
    readonly_fields = [
        'created_at', 'updated_at', 'last_login', 'password_changed_at',
        'failed_login_attempts', 'account_locked_until'
    ]
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('email',)}),
        (_('Permissions'), {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'created_at', 'updated_at', 'password_changed_at')
        }),
        (_('Security'), {
            'fields': ('failed_login_attempts', 'account_locked_until'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('detail')


@admin.register(UserDetail)
class UserDetailAdmin(admin.ModelAdmin):
    """
    Admin configuration for UserDetail model
    """
    list_display = [
        'user', 'full_name', 'sex', 'occupation_category',
        'primary_income_source', 'blue_tax_return_approved', 'created_at'
    ]
    list_filter = [
        'sex', 'occupation_category', 'primary_income_source',
        'blue_tax_return_approved', 'is_disabled', 'is_widow',
        'is_household_head', 'created_at'
    ]
    search_fields = [
        'user__username', 'first_name', 'last_name',
        'first_name_kana', 'last_name_kana', 'occupation'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('User'), {'fields': ('user',)}),
        (_('Personal Information'), {
            'fields': (
                'first_name', 'last_name', 'first_name_kana', 'last_name_kana',
                'sex', 'birth_day', 'phone_number'
            )
        }),
        (_('Address'), {
            'fields': ('postal_code', 'prefecture', 'city', 'addr', 'room_name'),
            'classes': ('collapse',)
        }),
        (_('Tax Information'), {
            'fields': ('is_disabled', 'is_widow', 'is_household_head'),
            'classes': ('collapse',)
        }),
        (_('Business Information'), {
            'fields': (
                'occupation', 'occupation_category', 'primary_income_source',
                'business_start_date', 'blue_tax_return_approved',
                'blue_tax_return_approval_date'
            )
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """
    Admin configuration for UserRole model
    """
    list_display = [
        'name', 'is_active', 'can_manage_users', 'can_manage_system',
        'created_at'
    ]
    list_filter = [
        'is_active', 'can_view_all_data', 'can_edit_all_data',
        'can_delete_data', 'can_import_data', 'can_export_data',
        'can_manage_users', 'can_manage_system', 'created_at'
    ]
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {'fields': ('name', 'description', 'is_active')}),
        (_('Data Permissions'), {
            'fields': (
                'can_view_all_data', 'can_edit_all_data', 'can_delete_data',
                'can_import_data', 'can_export_data'
            )
        }),
        (_('System Permissions'), {
            'fields': ('can_manage_users', 'can_manage_system')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    """
    Admin configuration for UserPermission model
    """
    list_display = [
        'user', 'permission_type', 'resource_type', 'is_granted',
        'granted_by', 'granted_at'
    ]
    list_filter = [
        'permission_type', 'resource_type', 'is_granted', 'granted_at'
    ]
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['granted_at']
    
    fieldsets = (
        (None, {
            'fields': ('user', 'permission_type', 'resource_type', 'is_granted')
        }),
        (_('Grant Information'), {
            'fields': ('granted_by', 'granted_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'granted_by')


@admin.register(UserHistory)
class UserHistoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for UserHistory model
    """
    list_display = [
        'user_id', 'username', 'action', 'changed_by', 'changed_at', 'ip_address'
    ]
    list_filter = ['action', 'changed_at']
    search_fields = ['username', 'email', 'ip_address']
    readonly_fields = [
        'user_id', 'username', 'email', 'role', 'is_active', 'action',
        'changed_by', 'changed_at', 'ip_address', 'user_agent',
        'old_values', 'new_values'
    ]
    
    fieldsets = (
        (_('User Information'), {
            'fields': ('user_id', 'username', 'email', 'role', 'is_active')
        }),
        (_('Action'), {
            'fields': ('action',)
        }),
        (_('Audit Information'), {
            'fields': ('changed_by', 'changed_at', 'ip_address', 'user_agent')
        }),
        (_('Changes'), {
            'fields': ('old_values', 'new_values'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(UserDetailHistory)
class UserDetailHistoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for UserDetailHistory model
    """
    list_display = [
        'user_detail_id', 'user_id', 'action', 'changed_by', 'changed_at'
    ]
    list_filter = ['action', 'changed_at']
    search_fields = ['user_id']
    readonly_fields = [
        'user_detail_id', 'user_id', 'action', 'detail_data',
        'changed_by', 'changed_at', 'ip_address', 'old_values', 'new_values'
    ]
    
    fieldsets = (
        (_('Reference Information'), {
            'fields': ('user_detail_id', 'user_id', 'action')
        }),
        (_('Detail Data'), {
            'fields': ('detail_data',),
            'classes': ('collapse',)
        }),
        (_('Audit Information'), {
            'fields': ('changed_by', 'changed_at', 'ip_address')
        }),
        (_('Changes'), {
            'fields': ('old_values', 'new_values'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


# Customize admin site
admin.site.site_header = "個人財務管理システム"
admin.site.site_title = "Financial System Admin"
admin.site.index_title = "システム管理"