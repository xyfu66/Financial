"""
User models for Financial System
Based on Japanese individual business owner requirements
"""

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model for Financial System
    Maps to T_User table in database schema
    """
    
    ROLE_CHOICES = [
        ('super_admin', 'Super Administrator'),
        ('admin', 'Administrator'),
        ('user', 'Regular User'),
    ]
    
    # Basic user information
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Username may only contain letters, numbers and @/./+/-/_ characters.'
        )]
    )
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=128)  # Maps to password field
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    # Security fields
    failed_login_attempts = models.IntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    password_changed_at = models.DateTimeField(default=timezone.now)
    
    # Django required fields
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        db_table = 'T_User'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.username
    
    @property
    def is_admin(self):
        return self.role in ['admin', 'super_admin']
    
    @property
    def is_super_admin(self):
        return self.role == 'super_admin'
    
    def has_permission(self, permission):
        """Check if user has specific permission"""
        if self.is_super_admin:
            return True
        return self.user_permissions.filter(codename=permission).exists()


class UserHistory(models.Model):
    """
    User history model for audit trail
    Maps to T_User_History table
    """
    
    ACTION_CHOICES = [
        ('CREATE', 'Created'),
        ('UPDATE', 'Updated'),
        ('DELETE', 'Deleted'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('PASSWORD_CHANGE', 'Password Changed'),
        ('ROLE_CHANGE', 'Role Changed'),
    ]
    
    user_id = models.IntegerField()  # Reference to original user
    username = models.CharField(max_length=150)
    email = models.EmailField()
    role = models.CharField(max_length=20)
    is_active = models.BooleanField()
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    
    # Audit fields
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    
    # Change tracking
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    
    class Meta:
        db_table = 'T_User_History'
        verbose_name = 'User History'
        verbose_name_plural = 'User Histories'
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['action']),
            models.Index(fields=['changed_at']),
        ]


class UserDetail(models.Model):
    """
    User detailed information model
    Maps to T_User_Detail table for Japanese business owner information
    """
    
    SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    OCCUPATION_CATEGORY_CHOICES = [
        ('agriculture', '農業'),
        ('forestry', '林業'),
        ('fishery', '漁業'),
        ('mining', '鉱業'),
        ('construction', '建設業'),
        ('manufacturing', '製造業'),
        ('electricity', '電気・ガス・熱供給・水道業'),
        ('information', '情報通信業'),
        ('transport', '運輸業'),
        ('wholesale', '卸売業'),
        ('retail', '小売業'),
        ('finance', '金融・保険業'),
        ('real_estate', '不動産業'),
        ('professional', '専門・技術サービス業'),
        ('accommodation', '宿泊・飲食サービス業'),
        ('lifestyle', '生活関連サービス業'),
        ('education', '教育・学習支援業'),
        ('medical', '医療・福祉'),
        ('entertainment', '娯楽業'),
        ('other_services', 'その他サービス業'),
        ('other', 'その他'),
    ]
    
    PRIMARY_INCOME_CHOICES = [
        ('business', '事業所得'),
        ('salary', '給与所得'),
        ('pension', '年金'),
        ('investment', '投資所得'),
        ('rental', '不動産所得'),
        ('other', 'その他'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='detail')
    
    # Personal information
    first_name = models.CharField(max_length=50, verbose_name='名')
    last_name = models.CharField(max_length=50, verbose_name='姓')
    first_name_kana = models.CharField(max_length=50, null=True, blank=True, verbose_name='名（カナ）')
    last_name_kana = models.CharField(max_length=50, null=True, blank=True, verbose_name='姓（カナ）')
    
    # Address information
    postal_code = models.CharField(max_length=8, null=True, blank=True, verbose_name='郵便番号')
    prefecture = models.CharField(max_length=20, null=True, blank=True, verbose_name='都道府県')
    city = models.CharField(max_length=50, null=True, blank=True, verbose_name='市区町村')
    addr = models.CharField(max_length=200, null=True, blank=True, verbose_name='住所')
    room_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='建物名・部屋番号')
    
    # Personal details
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, null=True, blank=True, verbose_name='性別')
    birth_day = models.DateField(null=True, blank=True, verbose_name='生年月日')
    phone_number = models.CharField(max_length=15, null=True, blank=True, verbose_name='電話番号')
    
    # Tax-related information for Japanese individual business owners
    is_disabled = models.BooleanField(default=False, verbose_name='障害者')
    is_widow = models.BooleanField(default=False, verbose_name='寡婦・寡夫')
    is_household_head = models.BooleanField(default=False, verbose_name='世帯主')
    
    # Business information
    occupation = models.CharField(max_length=100, null=True, blank=True, verbose_name='職業')
    occupation_category = models.CharField(
        max_length=50, 
        choices=OCCUPATION_CATEGORY_CHOICES, 
        null=True, 
        blank=True, 
        verbose_name='業種'
    )
    primary_income_source = models.CharField(
        max_length=20, 
        choices=PRIMARY_INCOME_CHOICES, 
        default='business', 
        verbose_name='主な収入源'
    )
    business_start_date = models.DateField(null=True, blank=True, verbose_name='事業開始日')
    
    # Blue tax return (青色申告) information
    blue_tax_return_approved = models.BooleanField(default=False, verbose_name='青色申告承認')
    blue_tax_return_approval_date = models.DateField(null=True, blank=True, verbose_name='青色申告承認日')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'T_User_Detail'
        verbose_name = 'User Detail'
        verbose_name_plural = 'User Details'
    
    def __str__(self):
        return f"{self.last_name} {self.first_name}"
    
    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name}"
    
    @property
    def full_name_kana(self):
        if self.last_name_kana and self.first_name_kana:
            return f"{self.last_name_kana} {self.first_name_kana}"
        return ""


class UserDetailHistory(models.Model):
    """
    User detail history model for audit trail
    Maps to T_User_Detail_History table
    """
    
    ACTION_CHOICES = [
        ('CREATE', 'Created'),
        ('UPDATE', 'Updated'),
        ('DELETE', 'Deleted'),
    ]
    
    user_detail_id = models.IntegerField()  # Reference to original user detail
    user_id = models.IntegerField()  # Reference to user
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    
    # Store all the detail fields as JSON for flexibility
    detail_data = models.JSONField()
    
    # Audit fields
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Change tracking
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    
    class Meta:
        db_table = 'T_User_Detail_History'
        verbose_name = 'User Detail History'
        verbose_name_plural = 'User Detail Histories'
        indexes = [
            models.Index(fields=['user_detail_id']),
            models.Index(fields=['user_id']),
            models.Index(fields=['action']),
            models.Index(fields=['changed_at']),
        ]


class UserRole(models.Model):
    """
    Role management model
    Maps to T_User_Role table
    """
    
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Permissions
    can_view_all_data = models.BooleanField(default=False)
    can_edit_all_data = models.BooleanField(default=False)
    can_delete_data = models.BooleanField(default=False)
    can_import_data = models.BooleanField(default=False)
    can_export_data = models.BooleanField(default=False)
    can_manage_users = models.BooleanField(default=False)
    can_manage_system = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'T_User_Role'
        verbose_name = 'User Role'
        verbose_name_plural = 'User Roles'
    
    def __str__(self):
        return self.name


class UserPermission(models.Model):
    """
    Permission management model
    Maps to T_User_Permission table
    """
    
    PERMISSION_TYPES = [
        ('view', 'View'),
        ('create', 'Create'),
        ('edit', 'Edit'),
        ('delete', 'Delete'),
        ('import', 'Import'),
        ('export', 'Export'),
        ('admin', 'Admin'),
    ]
    
    RESOURCE_TYPES = [
        ('incomes', 'Incomes'),
        ('expenses', 'Expenses'),
        ('users', 'Users'),
        ('system', 'System'),
        ('reports', 'Reports'),
        ('notifications', 'Notifications'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_permissions')
    permission_type = models.CharField(max_length=20, choices=PERMISSION_TYPES)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    is_granted = models.BooleanField(default=True)
    
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='granted_permissions')
    granted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'T_User_Permission'
        verbose_name = 'User Permission'
        verbose_name_plural = 'User Permissions'
        unique_together = ['user', 'permission_type', 'resource_type']
        indexes = [
            models.Index(fields=['user', 'permission_type']),
            models.Index(fields=['resource_type']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.permission_type} {self.resource_type}"