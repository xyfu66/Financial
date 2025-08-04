"""
Views for User management
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login, logout
from django.utils import timezone
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import User, UserDetail, UserRole, UserPermission
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    UserListSerializer, UserProfileSerializer, PasswordChangeSerializer,
    LoginSerializer, UserDetailSerializer, UserRoleSerializer,
    UserPermissionSerializer
)
from .permissions import IsAdminOrOwner, IsAdminUser
from .filters import UserFilter


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User model
    Provides CRUD operations for users
    """
    queryset = User.objects.all().select_related('detail').prefetch_related('user_permissions')
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = UserFilter
    search_fields = ['username', 'email', 'detail__first_name', 'detail__last_name']
    ordering_fields = ['username', 'email', 'created_at', 'last_login']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'list':
            return UserListSerializer
        elif self.action == 'profile':
            return UserProfileSerializer
        return UserSerializer
    
    def get_queryset(self):
        """
        Filter queryset based on user permissions
        """
        user = self.request.user
        if user.is_super_admin:
            return self.queryset
        elif user.is_admin:
            # Admins can see all users except super admins
            return self.queryset.exclude(role='super_admin')
        else:
            # Regular users can only see themselves
            return self.queryset.filter(id=user.id)
    
    def perform_create(self, serializer):
        """
        Create user with audit logging
        """
        with transaction.atomic():
            user = serializer.save()
            # Log user creation in audit
            from apps.audit.utils import log_audit
            log_audit(
                user=self.request.user,
                action='CREATE',
                model='User',
                object_id=user.id,
                changes={'created': True}
            )
    
    def perform_update(self, serializer):
        """
        Update user with audit logging
        """
        old_instance = self.get_object()
        old_data = UserSerializer(old_instance).data
        
        with transaction.atomic():
            user = serializer.save()
            new_data = UserSerializer(user).data
            
            # Log user update in audit
            from apps.audit.utils import log_audit
            log_audit(
                user=self.request.user,
                action='UPDATE',
                model='User',
                object_id=user.id,
                old_values=old_data,
                new_values=new_data
            )
    
    def perform_destroy(self, instance):
        """
        Soft delete user (deactivate instead of delete)
        """
        with transaction.atomic():
            instance.is_active = False
            instance.save()
            
            # Log user deactivation in audit
            from apps.audit.utils import log_audit
            log_audit(
                user=self.request.user,
                action='DEACTIVATE',
                model='User',
                object_id=instance.id,
                changes={'is_active': False}
            )
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def profile(self, request):
        """
        Get current user's profile
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'], permission_classes=[permissions.IsAuthenticated])
    def update_profile(self, request):
        """
        Update current user's profile
        """
        serializer = UserUpdateSerializer(
            request.user, 
            data=request.data, 
            partial=request.method == 'PATCH'
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request):
        """
        Change user's password
        """
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Password changed successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsAdminUser])
    def activate(self, request, pk=None):
        """
        Activate a user account
        """
        user = self.get_object()
        user.is_active = True
        user.save()
        
        # Log user activation in audit
        from apps.audit.utils import log_audit
        log_audit(
            user=request.user,
            action='ACTIVATE',
            model='User',
            object_id=user.id,
            changes={'is_active': True}
        )
        
        return Response({'message': 'User activated successfully'})
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsAdminUser])
    def deactivate(self, request, pk=None):
        """
        Deactivate a user account
        """
        user = self.get_object()
        if user.is_super_admin and not request.user.is_super_admin:
            return Response(
                {'error': 'Cannot deactivate super admin'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user.is_active = False
        user.save()
        
        # Log user deactivation in audit
        from apps.audit.utils import log_audit
        log_audit(
            user=request.user,
            action='DEACTIVATE',
            model='User',
            object_id=user.id,
            changes={'is_active': False}
        )
        
        return Response({'message': 'User deactivated successfully'})
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsAdminUser])
    def unlock_account(self, request, pk=None):
        """
        Unlock a user account
        """
        user = self.get_object()
        user.account_locked_until = None
        user.failed_login_attempts = 0
        user.save()
        
        # Log account unlock in audit
        from apps.audit.utils import log_audit
        log_audit(
            user=request.user,
            action='UNLOCK',
            model='User',
            object_id=user.id,
            changes={'account_unlocked': True}
        )
        
        return Response({'message': 'Account unlocked successfully'})


class LoginView(APIView):
    """
    User login view with JWT token generation
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """
        Authenticate user and return JWT tokens
        """
        serializer = LoginSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Reset failed login attempts on successful login
            if user.failed_login_attempts > 0:
                user.failed_login_attempts = 0
                user.save(update_fields=['failed_login_attempts'])
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # Update last login
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            # Log successful login
            from apps.audit.utils import log_audit
            log_audit(
                user=user,
                action='LOGIN',
                model='User',
                object_id=user.id,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return Response({
                'access': str(access_token),
                'refresh': str(refresh),
                'user': UserProfileSerializer(user).data
            })
        
        # Handle failed login attempt
        username = request.data.get('username')
        if username:
            try:
                user = User.objects.get(username=username)
                user.failed_login_attempts += 1
                
                # Lock account after 5 failed attempts
                if user.failed_login_attempts >= 5:
                    user.account_locked_until = timezone.now() + timezone.timedelta(minutes=30)
                
                user.save(update_fields=['failed_login_attempts', 'account_locked_until'])
                
                # Log failed login attempt
                from apps.audit.utils import log_audit
                log_audit(
                    user=user,
                    action='LOGIN_FAILED',
                    model='User',
                    object_id=user.id,
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
            except User.DoesNotExist:
                pass
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        """
        Get client IP address
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LogoutView(APIView):
    """
    User logout view
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Logout user and blacklist refresh token
        """
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Log logout
            from apps.audit.utils import log_audit
            log_audit(
                user=request.user,
                action='LOGOUT',
                model='User',
                object_id=request.user.id
            )
            
            return Response({'message': 'Successfully logged out'})
        except Exception as e:
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserRoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for UserRole model
    """
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class UserPermissionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for UserPermission model
    """
    queryset = UserPermission.objects.all().select_related('user', 'granted_by')
    serializer_class = UserPermissionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user', 'permission_type', 'resource_type', 'is_granted']
    ordering_fields = ['granted_at']
    ordering = ['-granted_at']
    
    def perform_create(self, serializer):
        """
        Create permission with granted_by field
        """
        serializer.save(granted_by=self.request.user)


class UserDetailViewSet(viewsets.ModelViewSet):
    """
    ViewSet for UserDetail model
    """
    queryset = UserDetail.objects.all().select_related('user')
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['first_name', 'last_name', 'occupation']
    filterset_fields = ['sex', 'occupation_category', 'primary_income_source']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']
    
    def get_queryset(self):
        """
        Filter queryset based on user permissions
        """
        user = self.request.user
        if user.is_admin:
            return self.queryset
        else:
            # Regular users can only see their own detail
            return self.queryset.filter(user=user)