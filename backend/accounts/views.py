"""
Views for accounts app
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import update_session_auth_hash
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import User, UserDetail, UserRole, UserPermission
from .serializers import (
    UserSerializer, UserDetailSerializer, UserProfileSerializer,
    UserDetailUpdateSerializer, PasswordChangeSerializer,
    UserRoleSerializer, UserPermissionSerializer, LoginSerializer,
    UserListSerializer, UserCreateSerializer
)
from .permissions import IsOwnerOrAdmin, IsSuperAdminOrAdmin


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token obtain view with user details"""
    
    @extend_schema(
        summary="User Login",
        description="Authenticate user and return JWT tokens with user profile",
        responses={
            200: OpenApiResponse(description="Login successful"),
            401: OpenApiResponse(description="Invalid credentials"),
        }
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Add user profile to response
            serializer = LoginSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                user = serializer.validated_data['user']
                user_data = UserProfileSerializer(user).data
                response.data['user'] = user_data
                
                # Update last login
                user.save(update_fields=['last_login'])
        
        return response


class UserProfileView(generics.RetrieveUpdateAPIView):
    """View for user profile management"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    @extend_schema(
        summary="Get User Profile",
        description="Retrieve current user's profile information"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class UserDetailUpdateView(generics.RetrieveUpdateAPIView):
    """View for updating user details"""
    serializer_class = UserDetailUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user_detail, created = UserDetail.objects.get_or_create(
            user=self.request.user,
            defaults={'created_by': self.request.user}
        )
        return user_detail

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @extend_schema(
        summary="Update User Details",
        description="Update current user's detailed information"
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Partially Update User Details",
        description="Partially update current user's detailed information"
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class PasswordChangeView(APIView):
    """View for changing user password"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Change Password",
        description="Change current user's password",
        request=PasswordChangeSerializer,
        responses={
            200: OpenApiResponse(description="Password changed successfully"),
            400: OpenApiResponse(description="Invalid data"),
        }
    )
    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Update session to prevent logout
            update_session_auth_hash(request, user)
            
            return Response({
                'message': _('Password changed successfully')
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListCreateView(generics.ListCreateAPIView):
    """View for listing and creating users (admin only)"""
    queryset = User.objects.all().select_related('detail')
    permission_classes = [IsSuperAdminOrAdmin]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @extend_schema(
        summary="List Users",
        description="Get list of all users (admin only)"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Create User",
        description="Create a new user (admin only)"
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View for user detail operations (admin only)"""
    queryset = User.objects.all().select_related('detail')
    serializer_class = UserSerializer
    permission_classes = [IsSuperAdminOrAdmin]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @extend_schema(
        summary="Get User Details",
        description="Retrieve specific user details (admin only)"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Update User",
        description="Update specific user (admin only)"
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Partially Update User",
        description="Partially update specific user (admin only)"
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary="Delete User",
        description="Delete specific user (admin only)"
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class UserRoleListCreateView(generics.ListCreateAPIView):
    """View for listing and creating user roles"""
    queryset = UserRole.objects.filter(is_active=True)
    serializer_class = UserRoleSerializer
    permission_classes = [IsSuperAdminOrAdmin]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @extend_schema(
        summary="List User Roles",
        description="Get list of all user roles"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Create User Role",
        description="Create a new user role"
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserRoleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View for user role detail operations"""
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [IsSuperAdminOrAdmin]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class UserPermissionListCreateView(generics.ListCreateAPIView):
    """View for listing and creating user permissions"""
    queryset = UserPermission.objects.filter(is_active=True)
    serializer_class = UserPermissionSerializer
    permission_classes = [IsSuperAdminOrAdmin]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @extend_schema(
        summary="List User Permissions",
        description="Get list of all user permissions"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Create User Permission",
        description="Create a new user permission"
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserPermissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View for user permission detail operations"""
    queryset = UserPermission.objects.all()
    serializer_class = UserPermissionSerializer
    permission_classes = [IsSuperAdminOrAdmin]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


@extend_schema(
    summary="Logout User",
    description="Logout user by blacklisting refresh token",
    request={"refresh": "string"},
    responses={
        200: OpenApiResponse(description="Logout successful"),
        400: OpenApiResponse(description="Invalid token"),
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """Logout user by blacklisting refresh token"""
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({
                'message': _('Logout successful')
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': _('Refresh token is required')
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': _('Invalid token')
        }, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Get Current User",
    description="Get current authenticated user information"
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def current_user_view(request):
    """Get current user information"""
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)