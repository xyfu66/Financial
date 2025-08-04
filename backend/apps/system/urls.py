"""
URL configuration for system app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    NotificationViewSet, SystemHealthView, SystemConfigurationViewSet,
    BackupLogViewSet, HealthCheckView
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'configurations', SystemConfigurationViewSet, basename='systemconfiguration')
router.register(r'backup-logs', BackupLogViewSet, basename='backuplog')

app_name = 'system'

urlpatterns = [
    # Health check endpoint
    path('health/', HealthCheckView.as_view(), name='health-check'),
    
    # System health endpoint
    path('health/detailed/', SystemHealthView.as_view(), name='system-health'),
    
    # Router URLs
    path('', include(router.urls)),
]