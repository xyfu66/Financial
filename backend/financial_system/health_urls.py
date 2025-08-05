"""
Health check URLs for monitoring and deployment
"""
from django.urls import path
from django.http import JsonResponse
from django.db import connection
from django.conf import settings
import redis
import logging

logger = logging.getLogger(__name__)

def health_check(request):
    """Basic health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'Personal Financial Management System',
        'version': '1.0.0'
    })

def health_check_detailed(request):
    """Detailed health check with database and cache connectivity"""
    health_status = {
        'status': 'healthy',
        'service': 'Personal Financial Management System',
        'version': '1.0.0',
        'checks': {}
    }
    
    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['checks']['database'] = 'healthy'
    except Exception as e:
        health_status['checks']['database'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'
        logger.error(f"Database health check failed: {e}")
    
    # Redis check
    try:
        redis_client = redis.from_url(settings.CELERY_BROKER_URL)
        redis_client.ping()
        health_status['checks']['redis'] = 'healthy'
    except Exception as e:
        health_status['checks']['redis'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'
        logger.error(f"Redis health check failed: {e}")
    
    return JsonResponse(health_status)

urlpatterns = [
    path('', health_check, name='health_check'),
    path('detailed/', health_check_detailed, name='health_check_detailed'),
]