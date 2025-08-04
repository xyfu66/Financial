"""
Custom user manager for Financial System
"""

from django.contrib.auth.models import BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):
    """
    Custom user manager for the User model
    """
    
    def create_user(self, username, email, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password.
        """
        if not username:
            raise ValueError('The Username field must be set')
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.password_changed_at = timezone.now()
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'super_admin')
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(username, email, password, **extra_fields)
    
    def create_admin(self, username, email, password=None, **extra_fields):
        """
        Create and return an admin user.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_active', True)
        
        return self.create_user(username, email, password, **extra_fields)
    
    def active_users(self):
        """
        Return only active users
        """
        return self.filter(is_active=True)
    
    def admins(self):
        """
        Return admin and super admin users
        """
        return self.filter(role__in=['admin', 'super_admin'], is_active=True)
    
    def regular_users(self):
        """
        Return regular users only
        """
        return self.filter(role='user', is_active=True)
    
    def locked_users(self):
        """
        Return users whose accounts are currently locked
        """
        return self.filter(
            account_locked_until__gt=timezone.now(),
            is_active=True
        )
    
    def unlock_user(self, user):
        """
        Unlock a user account
        """
        user.account_locked_until = None
        user.failed_login_attempts = 0
        user.save(update_fields=['account_locked_until', 'failed_login_attempts'])
        return user