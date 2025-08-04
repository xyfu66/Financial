"""
URL configuration for audit app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuditLogViewSet, SecurityDashboardView

# Create router and register viewsets
router = DefaultRouter()
router.register(r'logs', AuditLogViewSet, basename='auditlog')

app_name = 'audit'

urlpatterns = [
    # Security dashboard endpoint
    path('security/dashboard/', SecurityDashboardView.as_view(), name='security-dashboard'),
    
    # Router URLs
    path('', include(router.urls)),
]