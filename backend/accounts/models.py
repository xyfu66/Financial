"""
User models for Personal Financial Management System
"""
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator


class UserRole(models.TextChoices):
    SUPER_ADMIN = 'super_admin', _('Super Admin')
    ADMIN = 'admin', _('Admin')
    USER = 'user', _('User')


class GenderType(models.TextChoices):
    MALE = 'male', _('Male')
    FEMALE = 'female', _('Female')
    OTHER = 'other', _('Other')


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    Maps to T_User table in PostgreSQL
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='user_id')
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.USER,
        help_text=_('User role in the system')
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Designates whether this user should be treated as active.')
    )
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    last_login = models.DateTimeField(_('last login'), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_users'
    )
    updated_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_users'
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'T_User'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.username

    @property
    def is_super_admin(self):
        return self.role == UserRole.SUPER_ADMIN

    @property
    def is_admin(self):
        return self.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]

    def has_permission(self, permission_name):
        """Check if user has specific permission"""
        if self.is_super_admin:
            return True
        # TODO: Implement permission checking logic
        return False


class UserDetail(models.Model):
    """
    User detail information
    Maps to T_User_Detail table in PostgreSQL
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='detail_id')
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='detail',
        db_column='user_id'
    )
    first_name = models.CharField(_('first name'), max_length=100, blank=True)
    last_name = models.CharField(_('last name'), max_length=100, blank=True)
    first_name_kana = models.CharField(_('first name (kana)'), max_length=100, blank=True)
    last_name_kana = models.CharField(_('last name (kana)'), max_length=100, blank=True)
    addr = models.TextField(_('address'), blank=True)
    room_name = models.CharField(_('room/building name'), max_length=200, blank=True)
    sex = models.CharField(
        _('gender'),
        max_length=10,
        choices=GenderType.choices,
        blank=True,
        null=True
    )
    birth_day = models.DateField(_('birth date'), null=True, blank=True)
    phone_number = models.CharField(
        _('phone number'),
        max_length=20,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^[\d\-\+\(\)\s]+$',
                message=_('Enter a valid phone number.')
            )
        ]
    )
    is_disabled = models.BooleanField(_('is disabled'), default=False)
    is_widow = models.BooleanField(_('is widow'), default=False)
    is_household_head = models.BooleanField(_('is household head'), default=False)
    occupation = models.CharField(_('occupation'), max_length=200, blank=True)
    occupation_category = models.CharField(_('occupation category'), max_length=100, blank=True)
    primary_income_source = models.CharField(_('primary income source'), max_length=200, blank=True)
    tax_number = models.CharField(
        _('tax number (encrypted)'),
        max_length=50,
        blank=True,
        help_text=_('My Number (encrypted)')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_user_details'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_user_details'
    )

    class Meta:
        db_table = 'T_User_Detail'
        verbose_name = _('User Detail')
        verbose_name_plural = _('User Details')
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['last_name', 'first_name']),
        ]

    def __str__(self):
        if self.last_name and self.first_name:
            return f"{self.last_name} {self.first_name}"
        return str(self.user)

    @property
    def full_name(self):
        """Return full name in Japanese format (last name first)"""
        if self.last_name and self.first_name:
            return f"{self.last_name} {self.first_name}"
        return ""

    @property
    def full_name_kana(self):
        """Return full name in kana"""
        if self.last_name_kana and self.first_name_kana:
            return f"{self.last_name_kana} {self.first_name_kana}"
        return ""


class UserRole(models.Model):
    """
    Role management table
    Maps to T_User_Role table in PostgreSQL
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='role_id')
    role_name = models.CharField(_('role name'), max_length=50, unique=True)
    role_description = models.TextField(_('role description'), blank=True)
    permissions = models.JSONField(_('permissions'), default=dict, blank=True)
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_roles'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_roles'
    )

    class Meta:
        db_table = 'T_User_Role'
        verbose_name = _('User Role')
        verbose_name_plural = _('User Roles')

    def __str__(self):
        return self.role_name


class UserPermission(models.Model):
    """
    Permission management table
    Maps to T_User_Permission table in PostgreSQL
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='permission_id')
    permission_name = models.CharField(_('permission name'), max_length=100, unique=True)
    permission_description = models.TextField(_('permission description'), blank=True)
    resource = models.CharField(_('resource'), max_length=100)
    action = models.CharField(_('action'), max_length=50)
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_permissions'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_permissions'
    )

    class Meta:
        db_table = 'T_User_Permission'
        verbose_name = _('User Permission')
        verbose_name_plural = _('User Permissions')
        unique_together = ['resource', 'action']

    def __str__(self):
        return f"{self.resource}:{self.action}"


# History models for audit trail
class UserHistory(models.Model):
    """
    User history table for audit trail
    Maps to T_User_History table in PostgreSQL
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='history_id')
    user_id = models.UUIDField()
    username = models.CharField(max_length=150)
    email = models.EmailField()
    password_hash = models.CharField(max_length=128, db_column='password_hash')
    role = models.CharField(max_length=20)
    is_active = models.BooleanField()
    is_staff = models.BooleanField()
    is_superuser = models.BooleanField()
    date_joined = models.DateTimeField()
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    created_by = models.UUIDField(null=True, blank=True)
    updated_by = models.UUIDField(null=True, blank=True)
    history_created_at = models.DateTimeField(auto_now_add=True)
    history_action = models.CharField(max_length=10)  # INSERT, UPDATE, DELETE

    class Meta:
        db_table = 'T_User_History'
        verbose_name = _('User History')
        verbose_name_plural = _('User History')


class UserDetailHistory(models.Model):
    """
    User detail history table for audit trail
    Maps to T_User_Detail_History table in PostgreSQL
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='history_id')
    detail_id = models.UUIDField()
    user_id = models.UUIDField()
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    first_name_kana = models.CharField(max_length=100, blank=True)
    last_name_kana = models.CharField(max_length=100, blank=True)
    addr = models.TextField(blank=True)
    room_name = models.CharField(max_length=200, blank=True)
    sex = models.CharField(max_length=10, blank=True, null=True)
    birth_day = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    is_disabled = models.BooleanField()
    is_widow = models.BooleanField()
    is_household_head = models.BooleanField()
    occupation = models.CharField(max_length=200, blank=True)
    occupation_category = models.CharField(max_length=100, blank=True)
    primary_income_source = models.CharField(max_length=200, blank=True)
    tax_number = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    created_by = models.UUIDField(null=True, blank=True)
    updated_by = models.UUIDField(null=True, blank=True)
    history_created_at = models.DateTimeField(auto_now_add=True)
    history_action = models.CharField(max_length=10)  # INSERT, UPDATE, DELETE

    class Meta:
        db_table = 'T_User_Detail_History'
        verbose_name = _('User Detail History')
        verbose_name_plural = _('User Detail History')