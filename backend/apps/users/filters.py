"""
Filters for User models
"""

import django_filters
from django.db import models
from .models import User, UserDetail, UserRole, UserPermission


class UserFilter(django_filters.FilterSet):
    """
    Filter for User model
    """
    username = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    role = django_filters.ChoiceFilter(choices=User.ROLE_CHOICES)
    is_active = django_filters.BooleanFilter()
    created_at = django_filters.DateFromToRangeFilter()
    last_login = django_filters.DateFromToRangeFilter()
    
    # Filter by user detail fields
    first_name = django_filters.CharFilter(
        field_name='detail__first_name',
        lookup_expr='icontains'
    )
    last_name = django_filters.CharFilter(
        field_name='detail__last_name',
        lookup_expr='icontains'
    )
    occupation = django_filters.CharFilter(
        field_name='detail__occupation',
        lookup_expr='icontains'
    )
    occupation_category = django_filters.ChoiceFilter(
        field_name='detail__occupation_category',
        choices=UserDetail.OCCUPATION_CATEGORY_CHOICES
    )
    primary_income_source = django_filters.ChoiceFilter(
        field_name='detail__primary_income_source',
        choices=UserDetail.PRIMARY_INCOME_CHOICES
    )
    
    # Filter by account status
    is_locked = django_filters.BooleanFilter(method='filter_is_locked')
    has_failed_attempts = django_filters.BooleanFilter(method='filter_has_failed_attempts')
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'role', 'is_active', 'created_at',
            'last_login', 'first_name', 'last_name', 'occupation',
            'occupation_category', 'primary_income_source', 'is_locked',
            'has_failed_attempts'
        ]
    
    def filter_is_locked(self, queryset, name, value):
        """
        Filter users by account lock status
        """
        from django.utils import timezone
        if value:
            return queryset.filter(
                account_locked_until__gt=timezone.now()
            )
        else:
            return queryset.filter(
                models.Q(account_locked_until__isnull=True) |
                models.Q(account_locked_until__lte=timezone.now())
            )
    
    def filter_has_failed_attempts(self, queryset, name, value):
        """
        Filter users by failed login attempts
        """
        if value:
            return queryset.filter(failed_login_attempts__gt=0)
        else:
            return queryset.filter(failed_login_attempts=0)


class UserDetailFilter(django_filters.FilterSet):
    """
    Filter for UserDetail model
    """
    first_name = django_filters.CharFilter(lookup_expr='icontains')
    last_name = django_filters.CharFilter(lookup_expr='icontains')
    first_name_kana = django_filters.CharFilter(lookup_expr='icontains')
    last_name_kana = django_filters.CharFilter(lookup_expr='icontains')
    
    # Address filters
    prefecture = django_filters.CharFilter(lookup_expr='icontains')
    city = django_filters.CharFilter(lookup_expr='icontains')
    postal_code = django_filters.CharFilter(lookup_expr='exact')
    
    # Personal info filters
    sex = django_filters.ChoiceFilter(choices=UserDetail.SEX_CHOICES)
    birth_day = django_filters.DateFromToRangeFilter()
    age_range = django_filters.RangeFilter(method='filter_age_range')
    
    # Tax-related filters
    is_disabled = django_filters.BooleanFilter()
    is_widow = django_filters.BooleanFilter()
    is_household_head = django_filters.BooleanFilter()
    
    # Business info filters
    occupation = django_filters.CharFilter(lookup_expr='icontains')
    occupation_category = django_filters.ChoiceFilter(
        choices=UserDetail.OCCUPATION_CATEGORY_CHOICES
    )
    primary_income_source = django_filters.ChoiceFilter(
        choices=UserDetail.PRIMARY_INCOME_CHOICES
    )
    business_start_date = django_filters.DateFromToRangeFilter()
    
    # Blue tax return filters
    blue_tax_return_approved = django_filters.BooleanFilter()
    blue_tax_return_approval_date = django_filters.DateFromToRangeFilter()
    
    created_at = django_filters.DateFromToRangeFilter()
    updated_at = django_filters.DateFromToRangeFilter()
    
    class Meta:
        model = UserDetail
        fields = [
            'first_name', 'last_name', 'first_name_kana', 'last_name_kana',
            'prefecture', 'city', 'postal_code', 'sex', 'birth_day',
            'is_disabled', 'is_widow', 'is_household_head', 'occupation',
            'occupation_category', 'primary_income_source', 'business_start_date',
            'blue_tax_return_approved', 'blue_tax_return_approval_date',
            'created_at', 'updated_at'
        ]
    
    def filter_age_range(self, queryset, name, value):
        """
        Filter by age range
        """
        if value:
            from django.utils import timezone
            from datetime import date
            
            today = date.today()
            if value.start:
                max_birth_date = date(today.year - value.start, today.month, today.day)
                queryset = queryset.filter(birth_day__lte=max_birth_date)
            
            if value.stop:
                min_birth_date = date(today.year - value.stop, today.month, today.day)
                queryset = queryset.filter(birth_day__gte=min_birth_date)
        
        return queryset


class UserRoleFilter(django_filters.FilterSet):
    """
    Filter for UserRole model
    """
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()
    
    # Permission filters
    can_view_all_data = django_filters.BooleanFilter()
    can_edit_all_data = django_filters.BooleanFilter()
    can_delete_data = django_filters.BooleanFilter()
    can_import_data = django_filters.BooleanFilter()
    can_export_data = django_filters.BooleanFilter()
    can_manage_users = django_filters.BooleanFilter()
    can_manage_system = django_filters.BooleanFilter()
    
    created_at = django_filters.DateFromToRangeFilter()
    updated_at = django_filters.DateFromToRangeFilter()
    
    class Meta:
        model = UserRole
        fields = [
            'name', 'description', 'is_active', 'can_view_all_data',
            'can_edit_all_data', 'can_delete_data', 'can_import_data',
            'can_export_data', 'can_manage_users', 'can_manage_system',
            'created_at', 'updated_at'
        ]


class UserPermissionFilter(django_filters.FilterSet):
    """
    Filter for UserPermission model
    """
    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    user__username = django_filters.CharFilter(
        field_name='user__username',
        lookup_expr='icontains'
    )
    permission_type = django_filters.ChoiceFilter(
        choices=UserPermission.PERMISSION_TYPES
    )
    resource_type = django_filters.ChoiceFilter(
        choices=UserPermission.RESOURCE_TYPES
    )
    is_granted = django_filters.BooleanFilter()
    granted_by = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    granted_at = django_filters.DateFromToRangeFilter()
    
    class Meta:
        model = UserPermission
        fields = [
            'user', 'user__username', 'permission_type', 'resource_type',
            'is_granted', 'granted_by', 'granted_at'
        ]


class UserHistoryFilter(django_filters.FilterSet):
    """
    Filter for UserHistory model
    """
    user_id = django_filters.NumberFilter()
    username = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    action = django_filters.ChoiceFilter(
        choices=[
            ('CREATE', 'Created'),
            ('UPDATE', 'Updated'),
            ('DELETE', 'Deleted'),
            ('LOGIN', 'Login'),
            ('LOGOUT', 'Logout'),
            ('PASSWORD_CHANGE', 'Password Changed'),
            ('ROLE_CHANGE', 'Role Changed'),
        ]
    )
    changed_by = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    changed_at = django_filters.DateFromToRangeFilter()
    ip_address = django_filters.CharFilter(lookup_expr='exact')
    
    class Meta:
        model = 'UserHistory'  # String reference since it's in the same app
        fields = [
            'user_id', 'username', 'email', 'action', 'changed_by',
            'changed_at', 'ip_address'
        ]