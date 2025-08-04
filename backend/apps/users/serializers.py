"""
Serializers for User models
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, UserDetail, UserRole, UserPermission


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for UserDetail model
    """
    full_name = serializers.ReadOnlyField()
    full_name_kana = serializers.ReadOnlyField()
    
    class Meta:
        model = UserDetail
        fields = [
            'first_name', 'last_name', 'first_name_kana', 'last_name_kana',
            'postal_code', 'prefecture', 'city', 'addr', 'room_name',
            'sex', 'birth_day', 'phone_number',
            'is_disabled', 'is_widow', 'is_household_head',
            'occupation', 'occupation_category', 'primary_income_source',
            'business_start_date', 'blue_tax_return_approved', 
            'blue_tax_return_approval_date', 'full_name', 'full_name_kana',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class UserPermissionSerializer(serializers.ModelSerializer):
    """
    Serializer for UserPermission model
    """
    
    class Meta:
        model = UserPermission
        fields = [
            'id', 'permission_type', 'resource_type', 'is_granted',
            'granted_by', 'granted_at'
        ]
        read_only_fields = ['granted_by', 'granted_at']


class UserRoleSerializer(serializers.ModelSerializer):
    """
    Serializer for UserRole model
    """
    
    class Meta:
        model = UserRole
        fields = [
            'id', 'name', 'description', 'is_active',
            'can_view_all_data', 'can_edit_all_data', 'can_delete_data',
            'can_import_data', 'can_export_data', 'can_manage_users',
            'can_manage_system', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    """
    detail = UserDetailSerializer(read_only=True)
    user_permissions = UserPermissionSerializer(many=True, read_only=True)
    is_admin = serializers.ReadOnlyField()
    is_super_admin = serializers.ReadOnlyField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role', 'is_active', 'is_staff',
            'is_superuser', 'created_at', 'updated_at', 'last_login',
            'failed_login_attempts', 'account_locked_until',
            'password_changed_at', 'detail', 'user_permissions',
            'is_admin', 'is_super_admin', 'password'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'last_login', 'failed_login_attempts',
            'account_locked_until', 'password_changed_at'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def create(self, validated_data):
        """
        Create a new user with encrypted password
        """
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        """
        Update user instance
        """
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new users
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    detail = UserDetailSerializer(required=False)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'role', 'is_active', 'detail'
        ]
    
    def validate(self, attrs):
        """
        Validate password confirmation
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        """
        Create user with detail information
        """
        validated_data.pop('password_confirm')
        detail_data = validated_data.pop('detail', None)
        
        user = User.objects.create_user(**validated_data)
        
        if detail_data:
            UserDetail.objects.create(user=user, **detail_data)
        
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user information
    """
    detail = UserDetailSerializer(required=False)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'role', 'is_active', 'detail'
        ]
    
    def update(self, instance, validated_data):
        """
        Update user and detail information
        """
        detail_data = validated_data.pop('detail', None)
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update detail fields
        if detail_data:
            if hasattr(instance, 'detail'):
                detail_serializer = UserDetailSerializer(
                    instance.detail, data=detail_data, partial=True
                )
                if detail_serializer.is_valid():
                    detail_serializer.save()
            else:
                UserDetail.objects.create(user=instance, **detail_data)
        
        return instance


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate_old_password(self, value):
        """
        Validate old password
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value
    
    def validate(self, attrs):
        """
        Validate new password confirmation
        """
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs
    
    def save(self):
        """
        Save new password
        """
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        """
        Validate user credentials
        """
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(
                request=self.context.get('request'),
                username=username,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError(
                    'Unable to log in with provided credentials.'
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    'User account is disabled.'
                )
            
            # Check if account is locked
            from django.utils import timezone
            if (user.account_locked_until and 
                user.account_locked_until > timezone.now()):
                raise serializers.ValidationError(
                    'Account is temporarily locked due to multiple failed login attempts.'
                )
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                'Must include "username" and "password".'
            )


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile (read-only)
    """
    detail = UserDetailSerializer(read_only=True)
    user_permissions = UserPermissionSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role', 'is_active',
            'created_at', 'last_login', 'detail', 'user_permissions'
        ]
        read_only_fields = fields


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer for user list (minimal fields)
    """
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role', 'is_active',
            'created_at', 'last_login', 'full_name'
        ]
        read_only_fields = fields
    
    def get_full_name(self, obj):
        """
        Get user's full name from detail
        """
        if hasattr(obj, 'detail'):
            return obj.detail.full_name
        return obj.username