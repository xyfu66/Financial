"""
URL configuration for users app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, LoginView, LogoutView, UserRoleViewSet,
    UserPermissionViewSet, UserDetailViewSet
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'roles', UserRoleViewSet, basename='userrole')
router.register(r'permissions', UserPermissionViewSet, basename='userpermission')
router.register(r'details', UserDetailViewSet, basename='userdetail')

app_name = 'users'

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    
    # Router URLs
    path('', include(router.urls)),
]