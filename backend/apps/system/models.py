"""
System models for Financial System
Handles notifications, audit logs, and system management
"""

from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from apps.users.models import User


class Notification(models.Model):
    """
    Notification model
    Maps to T_Notification table
    """
    
    NOTIFICATION_TYPES = [
        ('INFO', '情報'),
        ('WARNING', '警告'),
        ('MAINTENANCE', 'メンテナンス'),
        ('URGENT', '緊急'),
        ('SUCCESS', '成功'),
        ('ERROR', 'エラー'),
    ]
    
    PRIORITY_LEVELS = [
        ('LOW', '低'),
        ('NORMAL', '通常'),
        ('HIGH', '高'),
        ('CRITICAL', '重要'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='タイトル')
    message = models.TextField(verbose_name='メッセージ')
    notification_type = models.CharField(
        max_length=20, 
        choices=NOTIFICATION_TYPES, 
        default='INFO',
        verbose_name='通知タイプ'
    )
    priority = models.CharField(
        max_length=20, 
        choices=PRIORITY_LEVELS, 
        default='NORMAL',
        verbose_name='優先度'
    )
    
    # Targeting
    target_users = models.ManyToManyField(
        User, 
        blank=True, 
        related_name='targeted_notifications',
        verbose_name='対象ユーザー'
    )
    target_roles = models.JSONField(
        default=list, 
        blank=True,
        verbose_name='対象ロール'
    )
    is_global = models.BooleanField(default=False, verbose_name='全体通知')
    
    # Status and timing
    is_active = models.BooleanField(default=True, verbose_name='有効')
    start_date = models.DateTimeField(default=timezone.now, verbose_name='開始日時')
    end_date = models.DateTimeField(null=True, blank=True, verbose_name='終了日時')
    
    # Display settings
    show_on_login = models.BooleanField(default=False, verbose_name='ログイン時表示')
    show_on_dashboard = models.BooleanField(default=True, verbose_name='ダッシュボード表示')
    is_dismissible = models.BooleanField(default=True, verbose_name='閉じる可能')
    auto_dismiss_after = models.IntegerField(
        null=True, 
        blank=True, 
        verbose_name='自動閉じる時間（秒）'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='created_notifications'
    )
    
    # Statistics
    view_count = models.IntegerField(default=0, verbose_name='表示回数')
    click_count = models.IntegerField(default=0, verbose_name='クリック回数')
    
    class Meta:
        db_table = 'T_Notification'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['is_active', 'start_date', 'end_date']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['priority']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_notification_type_display()})"
    
    @property
    def is_current(self):
        """Check if notification is currently active"""
        now = timezone.now()
        if not self.is_active:
            return False
        if self.start_date > now:
            return False
        if self.end_date and self.end_date < now:
            return False
        return True
    
    def is_visible_to_user(self, user):
        """Check if notification is visible to specific user"""
        if not self.is_current:
            return False
        
        if self.is_global:
            return True
        
        # Check target users
        if self.target_users.filter(id=user.id).exists():
            return True
        
        # Check target roles
        if user.role in self.target_roles:
            return True
        
        return False
    
    def increment_view_count(self):
        """Increment view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def increment_click_count(self):
        """Increment click count"""
        self.click_count += 1
        self.save(update_fields=['click_count'])


class NotificationRead(models.Model):
    """
    Track which notifications have been read by which users
    """
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)
    dismissed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['notification', 'user']
        verbose_name = 'Notification Read Status'
        verbose_name_plural = 'Notification Read Statuses'
        indexes = [
            models.Index(fields=['user', 'read_at']),
            models.Index(fields=['notification']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.notification.title}"


class AuditLog(models.Model):
    """
    Audit log model
    Maps to T_Audit_Log table
    """
    
    ACTION_CHOICES = [
        ('CREATE', '作成'),
        ('UPDATE', '更新'),
        ('DELETE', '削除'),
        ('LOGIN', 'ログイン'),
        ('LOGOUT', 'ログアウト'),
        ('LOGIN_FAILED', 'ログイン失敗'),
        ('PASSWORD_CHANGE', 'パスワード変更'),
        ('ROLE_CHANGE', 'ロール変更'),
        ('ACTIVATE', 'アクティベート'),
        ('DEACTIVATE', '非アクティベート'),
        ('UNLOCK', 'アンロック'),
        ('EXPORT', 'エクスポート'),
        ('IMPORT', 'インポート'),
        ('VIEW', '閲覧'),
        ('DOWNLOAD', 'ダウンロード'),
        ('UPLOAD', 'アップロード'),
        ('CALCULATE', '計算'),
        ('APPROVE', '承認'),
        ('REJECT', '拒否'),
        ('SYSTEM', 'システム'),
    ]
    
    # User information
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='ユーザー'
    )
    username = models.CharField(max_length=150, verbose_name='ユーザー名')
    user_role = models.CharField(max_length=20, null=True, blank=True, verbose_name='ユーザーロール')
    
    # Action information
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name='アクション')
    model = models.CharField(max_length=100, null=True, blank=True, verbose_name='モデル')
    object_id = models.CharField(max_length=100, null=True, blank=True, verbose_name='オブジェクトID')
    
    # Generic foreign key for linking to any model
    content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Change tracking
    old_values = models.JSONField(null=True, blank=True, verbose_name='変更前の値')
    new_values = models.JSONField(null=True, blank=True, verbose_name='変更後の値')
    changes = models.JSONField(null=True, blank=True, verbose_name='変更内容')
    
    # Request information
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IPアドレス')
    user_agent = models.TextField(null=True, blank=True, verbose_name='ユーザーエージェント')
    request_path = models.CharField(max_length=500, null=True, blank=True, verbose_name='リクエストパス')
    request_method = models.CharField(max_length=10, null=True, blank=True, verbose_name='リクエストメソッド')
    
    # Additional metadata
    session_key = models.CharField(max_length=40, null=True, blank=True, verbose_name='セッションキー')
    extra_data = models.JSONField(null=True, blank=True, verbose_name='追加データ')
    
    # Timing
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='タイムスタンプ')
    duration = models.FloatField(null=True, blank=True, verbose_name='処理時間（秒）')
    
    # Status
    success = models.BooleanField(default=True, verbose_name='成功')
    error_message = models.TextField(null=True, blank=True, verbose_name='エラーメッセージ')
    
    class Meta:
        db_table = 'T_Audit_Log'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['model', 'object_id']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['success']),
        ]
    
    def __str__(self):
        return f"{self.username} - {self.action} - {self.timestamp}"
    
    @classmethod
    def log_action(cls, user, action, model=None, object_id=None, **kwargs):
        """
        Convenience method to create audit log entries
        """
        return cls.objects.create(
            user=user,
            username=user.username if user else 'Anonymous',
            user_role=user.role if user else None,
            action=action,
            model=model,
            object_id=str(object_id) if object_id else None,
            **kwargs
        )


class SystemHealth(models.Model):
    """
    System health monitoring model
    """
    
    COMPONENT_TYPES = [
        ('DATABASE', 'データベース'),
        ('CACHE', 'キャッシュ'),
        ('STORAGE', 'ストレージ'),
        ('EMAIL', 'メール'),
        ('OCR', 'OCR'),
        ('BACKUP', 'バックアップ'),
        ('API', 'API'),
        ('SYSTEM', 'システム'),
    ]
    
    STATUS_CHOICES = [
        ('HEALTHY', '正常'),
        ('WARNING', '警告'),
        ('CRITICAL', '重要'),
        ('DOWN', '停止'),
    ]
    
    component = models.CharField(max_length=50, choices=COMPONENT_TYPES, verbose_name='コンポーネント')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name='ステータス')
    message = models.TextField(null=True, blank=True, verbose_name='メッセージ')
    
    # Metrics
    response_time = models.FloatField(null=True, blank=True, verbose_name='応答時間（秒）')
    cpu_usage = models.FloatField(null=True, blank=True, verbose_name='CPU使用率（%）')
    memory_usage = models.FloatField(null=True, blank=True, verbose_name='メモリ使用率（%）')
    disk_usage = models.FloatField(null=True, blank=True, verbose_name='ディスク使用率（%）')
    
    # Additional metrics as JSON
    metrics = models.JSONField(null=True, blank=True, verbose_name='追加メトリクス')
    
    # Timing
    checked_at = models.DateTimeField(auto_now_add=True, verbose_name='チェック日時')
    
    class Meta:
        verbose_name = 'System Health'
        verbose_name_plural = 'System Health Checks'
        ordering = ['-checked_at']
        indexes = [
            models.Index(fields=['component', 'checked_at']),
            models.Index(fields=['status']),
            models.Index(fields=['checked_at']),
        ]
    
    def __str__(self):
        return f"{self.component} - {self.status} - {self.checked_at}"


class SystemConfiguration(models.Model):
    """
    System configuration model for storing system-wide settings
    """
    
    CONFIG_TYPES = [
        ('STRING', '文字列'),
        ('INTEGER', '整数'),
        ('FLOAT', '小数'),
        ('BOOLEAN', 'ブール値'),
        ('JSON', 'JSON'),
        ('DATE', '日付'),
        ('DATETIME', '日時'),
    ]
    
    key = models.CharField(max_length=100, unique=True, verbose_name='キー')
    value = models.TextField(verbose_name='値')
    value_type = models.CharField(
        max_length=20, 
        choices=CONFIG_TYPES, 
        default='STRING',
        verbose_name='値の型'
    )
    description = models.TextField(null=True, blank=True, verbose_name='説明')
    
    # Categorization
    category = models.CharField(max_length=50, null=True, blank=True, verbose_name='カテゴリ')
    is_sensitive = models.BooleanField(default=False, verbose_name='機密情報')
    is_system = models.BooleanField(default=False, verbose_name='システム設定')
    
    # Validation
    validation_regex = models.CharField(max_length=200, null=True, blank=True, verbose_name='検証正規表現')
    min_value = models.FloatField(null=True, blank=True, verbose_name='最小値')
    max_value = models.FloatField(null=True, blank=True, verbose_name='最大値')
    allowed_values = models.JSONField(null=True, blank=True, verbose_name='許可値')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='更新者'
    )
    
    class Meta:
        verbose_name = 'System Configuration'
        verbose_name_plural = 'System Configurations'
        ordering = ['category', 'key']
        indexes = [
            models.Index(fields=['key']),
            models.Index(fields=['category']),
            models.Index(fields=['is_system']),
        ]
    
    def __str__(self):
        return f"{self.key} = {self.value}"
    
    def get_typed_value(self):
        """Return value converted to appropriate type"""
        if self.value_type == 'INTEGER':
            return int(self.value)
        elif self.value_type == 'FLOAT':
            return float(self.value)
        elif self.value_type == 'BOOLEAN':
            return self.value.lower() in ('true', '1', 'yes', 'on')
        elif self.value_type == 'JSON':
            import json
            return json.loads(self.value)
        elif self.value_type == 'DATE':
            from datetime import datetime
            return datetime.strptime(self.value, '%Y-%m-%d').date()
        elif self.value_type == 'DATETIME':
            from datetime import datetime
            return datetime.fromisoformat(self.value)
        else:
            return self.value
    
    @classmethod
    def get_config(cls, key, default=None):
        """Get configuration value by key"""
        try:
            config = cls.objects.get(key=key)
            return config.get_typed_value()
        except cls.DoesNotExist:
            return default
    
    @classmethod
    def set_config(cls, key, value, value_type='STRING', user=None, **kwargs):
        """Set configuration value"""
        config, created = cls.objects.get_or_create(
            key=key,
            defaults={
                'value': str(value),
                'value_type': value_type,
                'updated_by': user,
                **kwargs
            }
        )
        
        if not created:
            config.value = str(value)
            config.value_type = value_type
            config.updated_by = user
            for k, v in kwargs.items():
                setattr(config, k, v)
            config.save()
        
        return config


class BackupLog(models.Model):
    """
    Backup operation log model
    """
    
    BACKUP_TYPES = [
        ('FULL', 'フルバックアップ'),
        ('INCREMENTAL', '増分バックアップ'),
        ('DIFFERENTIAL', '差分バックアップ'),
        ('MANUAL', '手動バックアップ'),
    ]
    
    STATUS_CHOICES = [
        ('RUNNING', '実行中'),
        ('SUCCESS', '成功'),
        ('FAILED', '失敗'),
        ('CANCELLED', 'キャンセル'),
    ]
    
    backup_type = models.CharField(max_length=20, choices=BACKUP_TYPES, verbose_name='バックアップタイプ')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name='ステータス')
    
    # File information
    file_path = models.CharField(max_length=500, null=True, blank=True, verbose_name='ファイルパス')
    file_size = models.BigIntegerField(null=True, blank=True, verbose_name='ファイルサイズ（バイト）')
    
    # Timing
    started_at = models.DateTimeField(verbose_name='開始日時')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完了日時')
    duration = models.FloatField(null=True, blank=True, verbose_name='実行時間（秒）')
    
    # Details
    tables_backed_up = models.JSONField(null=True, blank=True, verbose_name='バックアップテーブル')
    records_count = models.IntegerField(null=True, blank=True, verbose_name='レコード数')
    error_message = models.TextField(null=True, blank=True, verbose_name='エラーメッセージ')
    
    # Metadata
    triggered_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='実行者'
    )
    
    class Meta:
        verbose_name = 'Backup Log'
        verbose_name_plural = 'Backup Logs'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['status', 'started_at']),
            models.Index(fields=['backup_type']),
            models.Index(fields=['started_at']),
        ]
    
    def __str__(self):
        return f"{self.backup_type} - {self.status} - {self.started_at}"
    
    @property
    def duration_formatted(self):
        """Return formatted duration"""
        if self.duration:
            minutes, seconds = divmod(int(self.duration), 60)
            hours, minutes = divmod(minutes, 60)
            if hours:
                return f"{hours}h {minutes}m {seconds}s"
            elif minutes:
                return f"{minutes}m {seconds}s"
            else:
                return f"{seconds}s"
        return None