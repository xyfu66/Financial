"""
Notification models
"""
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User, UserRole


class NotificationType(models.TextChoices):
    INFO = 'INFO', _('Info')
    WARNING = 'WARNING', _('Warning')
    MAINTENANCE = 'MAINTENANCE', _('Maintenance')
    URGENT = 'URGENT', _('Urgent')


class Notification(models.Model):
    """
    System notification model
    Maps to T_Notification table in PostgreSQL
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='notification_id')
    title = models.CharField(_('title'), max_length=200)
    message = models.TextField(_('message'))
    notification_type = models.CharField(
        _('notification type'),
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.INFO
    )
    is_active = models.BooleanField(_('is active'), default=True)
    start_date = models.DateTimeField(_('start date'), null=True, blank=True)
    end_date = models.DateTimeField(_('end date'), null=True, blank=True)
    target_roles = models.JSONField(_('target roles'), default=list, blank=True)
    priority = models.IntegerField(_('priority'), default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_notifications'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_notifications'
    )

    class Meta:
        db_table = 'T_Notification'
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return self.title