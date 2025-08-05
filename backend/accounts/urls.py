"""
URL configuration for accounts app
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # User profile management
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('profile/details/', views.UserDetailUpdateView.as_view(), name='user-detail-update'),
    path('profile/password/', views.PasswordChangeView.as_view(), name='password-change'),
    path('current/', views.current_user_view, name='current-user'),
    path('logout/', views.logout_view, name='logout'),
    
    # User management (admin only)
    path('users/', views.UserListCreateView.as_view(), name='user-list-create'),
    path('users/<uuid:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    
    # Role management
    path('roles/', views.UserRoleListCreateView.as_view(), name='role-list-create'),
    path('roles/<uuid:pk>/', views.UserRoleDetailView.as_view(), name='role-detail'),
    
    # Permission management
    path('permissions/', views.UserPermissionListCreateView.as_view(), name='permission-list-create'),
    path('permissions/<uuid:pk>/', views.UserPermissionDetailView.as_view(), name='permission-detail'),
]