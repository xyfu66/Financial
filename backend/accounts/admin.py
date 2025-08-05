"""
Admin configuration for accounts app
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserDetail, UserRole, UserPermission


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model"""
    
    list_display = ['username', 'email', 'role', 'is_active', 'is_staff', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff', 'is_superuser', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Audit'), {'fields': ('created_by', 'updated_by')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']


@admin.register(UserDetail)
class UserDetailAdmin(admin.ModelAdmin):
    """Admin configuration for UserDetail model"""
    
    list_display = ['user', 'full_name', 'phone_number', 'occupation', 'created_at']
    list_filter = ['sex', 'is_disabled', 'is_widow', 'is_household_head', 'created_at']
    search_fields = ['user__username', 'first_name', 'last_name', 'phone_number']
    ordering = ['-created_at']
    
    fieldsets = (
        (_('User'), {'fields': ('user',)}),
        (_('Personal Information'), {
            'fields': ('first_name', 'last_name', 'first_name_kana', 'last_name_kana', 'sex', 'birth_day')
        }),
        (_('Contact Information'), {
            'fields': ('phone_number', 'addr', 'room_name')
        }),
        (_('Status'), {
            'fields': ('is_disabled', 'is_widow', 'is_household_head')
        }),
        (_('Occupation'), {
            'fields': ('occupation', 'occupation_category', 'primary_income_source')
        }),
        (_('Tax Information'), {
            'fields': ('tax_number',),
            'classes': ('collapse',)
        }),
        (_('Audit'), {'fields': ('created_by', 'updated_by', 'created_at', 'updated_at')}),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """Admin configuration for UserRole model"""
    
    list_display = ['role_name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['role_name', 'role_description']
    ordering = ['role_name']
    
    fieldsets = (
        (None, {'fields': ('role_name', 'role_description', 'is_active')}),
        (_('Permissions'), {'fields': ('permissions',)}),
        (_('Audit'), {'fields': ('created_by', 'updated_by', 'created_at', 'updated_at')}),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    """Admin configuration for UserPermission model"""
    
    list_display = ['permission_name', 'resource', 'action', 'is_active', 'created_at']
    list_filter = ['resource', 'action', 'is_active', 'created_at']
    search_fields = ['permission_name', 'resource', 'action']
    ordering = ['resource', 'action']
    
    fieldsets = (
        (None, {'fields': ('permission_name', 'permission_description', 'is_active')}),
        (_('Permission Details'), {'fields': ('resource', 'action')}),
        (_('Audit'), {'fields': ('created_by', 'updated_by', 'created_at', 'updated_at')}),
    )
    
    readonly_fields = ['created_at', 'updated_at']


# Customize admin site
admin.site.site_header = _('Personal Financial Management System')
admin.site.site_title = _('Financial Management Admin')
admin.site.index_title = _('Welcome to Financial Management Administration')