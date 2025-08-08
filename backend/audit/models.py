"""
Audit models
"""
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User


class AuditActionType(models.TextChoices):
    CREATE = 'CREATE', _('Create')
    UPDATE = 'UPDATE', _('Update')
    DELETE = 'DELETE', _('Delete')
    LOGIN = 'LOGIN', _('Login')
    LOGOUT = 'LOGOUT', _('Logout')
    IMPORT = 'IMPORT', _('Import')
    EXPORT = 'EXPORT', _('Export')


class AuditLog(models.Model):
    """
    Audit log model
    Maps to T_Audit_Log table in PostgreSQL
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='log_id')
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        db_column='user_id'
    )
    table_name = models.CharField(_('table name'), max_length=100)
    record_id = models.UUIDField(_('record ID'), null=True, blank=True)
    action = models.CharField(
        _('action'),
        max_length=20,
        choices=AuditActionType.choices
    )
    old_values = models.JSONField(_('old values'), default=dict, blank=True)
    new_values = models.JSONField(_('new values'), default=dict, blank=True)
    ip_address = models.GenericIPAddressField(_('IP address'), null=True, blank=True)
    user_agent = models.TextField(_('user agent'), blank=True)
    session_id = models.CharField(_('session ID'), max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'T_Audit_Log'
        verbose_name = _('Audit Log')
        verbose_name_plural = _('Audit Logs')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action} on {self.table_name} by {self.user}"