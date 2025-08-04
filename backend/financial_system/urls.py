"""
URL configuration for financial_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# API Router
router = DefaultRouter()

# API URL patterns
api_patterns = [
    # Authentication endpoints
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # App-specific API endpoints
    path('users/', include('apps.users.urls')),
    path('business/', include('apps.business.urls')),
    path('system/', include('apps.system.urls')),
    path('files/', include('apps.files.urls')),
    path('audit/', include('apps.audit.urls')),
    
    # Router URLs
    path('', include(router.urls)),
]

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/v1/', include(api_patterns)),
    
    # Health check endpoint
    path('health/', include('apps.system.urls')),
    
    # API documentation (if needed)
    path('api-auth/', include('rest_framework.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customization
admin.site.site_header = "個人財務管理システム"
admin.site.site_title = "Financial System Admin"
admin.site.index_title = "システム管理"