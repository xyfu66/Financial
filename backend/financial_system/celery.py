"""
Celery configuration for Personal Financial Management System
"""
import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financial_system.settings')

app = Celery('financial_system')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery beat schedule for periodic tasks
app.conf.beat_schedule = {
    'process-pending-ocr-files': {
        'task': 'ocr_service.tasks.process_pending_ocr_files',
        'schedule': 300.0,  # Every 5 minutes
    },
    'cleanup-old-audit-logs': {
        'task': 'audit.tasks.cleanup_old_audit_logs',
        'schedule': 86400.0,  # Daily
    },
    'calculate-monthly-depreciation': {
        'task': 'financial.tasks.calculate_monthly_depreciation',
        'schedule': 86400.0,  # Daily
    },
}

app.conf.timezone = settings.TIME_ZONE

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')