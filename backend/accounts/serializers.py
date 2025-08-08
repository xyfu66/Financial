"""
Serializers for accounts app
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from .models import User, UserDetail, UserRoleModel, UserPermission


class UserDetailSerializer(serializers.ModelSerializer):
    """Serializer for UserDetail model"""
    
    class Meta:
        model = UserDetail
        fields = [
            'first_name', 'last_name', 'first_name_kana', 'last_name_kana',
            'addr', 'room_name', 'sex', 'birth_day', 'phone_number',
            'is_disabled', 'is_widow', 'is_household_head',
            'occupation', 'occupation_category', 'primary_income_source',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['full_name'] = instance.full_name
        data['full_name_kana'] = instance.full_name_kana
        return data


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    detail = UserDetailSerializer(read_only=True)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'is_active', 'is_staff', 'is_superuser',
            'date_joined', 'last_login', 'detail',
            'password', 'password_confirm'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, attrs):
        if 'password' in attrs and 'password_confirm' in attrs:
            if attrs['password'] != attrs['password_confirm']:
                raise serializers.ValidationError(_("Passwords don't match"))
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user

    def update(self, instance, validated_data):
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile (read-only)"""
    detail = UserDetailSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'is_active', 'date_joined', 'last_login', 'detail'
        ]
        read_only_fields = fields


class UserDetailUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user details"""
    
    class Meta:
        model = UserDetail
        fields = [
            'first_name', 'last_name', 'first_name_kana', 'last_name_kana',
            'addr', 'room_name', 'sex', 'birth_day', 'phone_number',
            'is_disabled', 'is_widow', 'is_household_head',
            'occupation', 'occupation_category', 'primary_income_source'
        ]

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(_("New passwords don't match"))
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(_("Old password is incorrect"))
        return value


class UserRoleSerializer(serializers.ModelSerializer):
    """Serializer for UserRoleModel model"""
    
    class Meta:
        model = UserRoleModel
        fields = [
            'id', 'role_name', 'role_description', 'permissions',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserPermissionSerializer(serializers.ModelSerializer):
    """Serializer for UserPermission model"""
    
    class Meta:
        model = UserPermission
        fields = [
            'id', 'permission_name', 'permission_description',
            'resource', 'action', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
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
                    _('Unable to log in with provided credentials.'),
                    code='authorization'
                )

            if not user.is_active:
                raise serializers.ValidationError(
                    _('User account is disabled.'),
                    code='authorization'
                )

            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                _('Must include "username" and "password".'),
                code='authorization'
            )


class UserListSerializer(serializers.ModelSerializer):
    """Serializer for user list (minimal fields)"""
    detail = UserDetailSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role', 'is_active',
            'date_joined', 'last_login', 'detail'
        ]
        read_only_fields = fields


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    detail = UserDetailSerializer(required=False)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'role', 'is_active', 'is_staff',
            'password', 'password_confirm', 'detail'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(_("Passwords don't match"))
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        detail_data = validated_data.pop('detail', {})
        password = validated_data.pop('password')
        
        user = User.objects.create_user(password=password, **validated_data)
        
        if detail_data:
            UserDetail.objects.create(user=user, **detail_data)
        
        return user