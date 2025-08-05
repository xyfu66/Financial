"""
Signals for accounts app
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import User, UserDetail, UserHistory, UserDetailHistory


@receiver(post_save, sender=User)
def create_user_detail(sender, instance, created, **kwargs):
    """Create UserDetail when User is created"""
    if created:
        UserDetail.objects.get_or_create(
            user=instance,
            defaults={'created_by': instance}
        )


@receiver(post_save, sender=User)
def create_user_history(sender, instance, created, **kwargs):
    """Create history record when User is saved"""
    action = 'INSERT' if created else 'UPDATE'
    
    UserHistory.objects.create(
        user_id=instance.id,
        username=instance.username,
        email=instance.email,
        password_hash=instance.password,
        role=instance.role,
        is_active=instance.is_active,
        is_staff=instance.is_staff,
        is_superuser=instance.is_superuser,
        date_joined=instance.date_joined,
        last_login=instance.last_login,
        created_at=instance.created_at,
        updated_at=instance.updated_at,
        created_by=instance.created_by.id if instance.created_by else None,
        updated_by=instance.updated_by.id if instance.updated_by else None,
        history_action=action
    )


@receiver(post_delete, sender=User)
def create_user_delete_history(sender, instance, **kwargs):
    """Create history record when User is deleted"""
    UserHistory.objects.create(
        user_id=instance.id,
        username=instance.username,
        email=instance.email,
        password_hash=instance.password,
        role=instance.role,
        is_active=instance.is_active,
        is_staff=instance.is_staff,
        is_superuser=instance.is_superuser,
        date_joined=instance.date_joined,
        last_login=instance.last_login,
        created_at=instance.created_at,
        updated_at=instance.updated_at,
        created_by=instance.created_by.id if instance.created_by else None,
        updated_by=instance.updated_by.id if instance.updated_by else None,
        history_action='DELETE'
    )


@receiver(post_save, sender=UserDetail)
def create_user_detail_history(sender, instance, created, **kwargs):
    """Create history record when UserDetail is saved"""
    action = 'INSERT' if created else 'UPDATE'
    
    UserDetailHistory.objects.create(
        detail_id=instance.id,
        user_id=instance.user.id,
        first_name=instance.first_name,
        last_name=instance.last_name,
        first_name_kana=instance.first_name_kana,
        last_name_kana=instance.last_name_kana,
        addr=instance.addr,
        room_name=instance.room_name,
        sex=instance.sex,
        birth_day=instance.birth_day,
        phone_number=instance.phone_number,
        is_disabled=instance.is_disabled,
        is_widow=instance.is_widow,
        is_household_head=instance.is_household_head,
        occupation=instance.occupation,
        occupation_category=instance.occupation_category,
        primary_income_source=instance.primary_income_source,
        tax_number=instance.tax_number,
        created_at=instance.created_at,
        updated_at=instance.updated_at,
        created_by=instance.created_by.id if instance.created_by else None,
        updated_by=instance.updated_by.id if instance.updated_by else None,
        history_action=action
    )


@receiver(post_delete, sender=UserDetail)
def create_user_detail_delete_history(sender, instance, **kwargs):
    """Create history record when UserDetail is deleted"""
    UserDetailHistory.objects.create(
        detail_id=instance.id,
        user_id=instance.user.id,
        first_name=instance.first_name,
        last_name=instance.last_name,
        first_name_kana=instance.first_name_kana,
        last_name_kana=instance.last_name_kana,
        addr=instance.addr,
        room_name=instance.room_name,
        sex=instance.sex,
        birth_day=instance.birth_day,
        phone_number=instance.phone_number,
        is_disabled=instance.is_disabled,
        is_widow=instance.is_widow,
        is_household_head=instance.is_household_head,
        occupation=instance.occupation,
        occupation_category=instance.occupation_category,
        primary_income_source=instance.primary_income_source,
        tax_number=instance.tax_number,
        created_at=instance.created_at,
        updated_at=instance.updated_at,
        created_by=instance.created_by.id if instance.created_by else None,
        updated_by=instance.updated_by.id if instance.updated_by else None,
        history_action='DELETE'
    )