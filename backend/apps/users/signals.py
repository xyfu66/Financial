"""
Signals for User models
"""

from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import User, UserDetail, UserHistory, UserDetailHistory


@receiver(post_save, sender=User)
def create_user_history(sender, instance, created, **kwargs):
    """
    Create user history record when user is created or updated
    """
    action = 'CREATE' if created else 'UPDATE'
    
    # Get the request from thread local storage if available
    request = getattr(instance, '_request', None)
    changed_by = getattr(request, 'user', None) if request else None
    ip_address = None
    user_agent = None
    
    if request:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    UserHistory.objects.create(
        user_id=instance.id,
        username=instance.username,
        email=instance.email,
        role=instance.role,
        is_active=instance.is_active,
        action=action,
        changed_by=changed_by,
        ip_address=ip_address,
        user_agent=user_agent
    )


@receiver(post_save, sender=UserDetail)
def create_user_detail_history(sender, instance, created, **kwargs):
    """
    Create user detail history record when user detail is created or updated
    """
    action = 'CREATE' if created else 'UPDATE'
    
    # Get the request from thread local storage if available
    request = getattr(instance, '_request', None)
    changed_by = getattr(request, 'user', None) if request else None
    ip_address = None
    
    if request:
        ip_address = get_client_ip(request)
    
    # Serialize detail data
    detail_data = {
        'first_name': instance.first_name,
        'last_name': instance.last_name,
        'first_name_kana': instance.first_name_kana,
        'last_name_kana': instance.last_name_kana,
        'postal_code': instance.postal_code,
        'prefecture': instance.prefecture,
        'city': instance.city,
        'addr': instance.addr,
        'room_name': instance.room_name,
        'sex': instance.sex,
        'birth_day': instance.birth_day.isoformat() if instance.birth_day else None,
        'phone_number': instance.phone_number,
        'is_disabled': instance.is_disabled,
        'is_widow': instance.is_widow,
        'is_household_head': instance.is_household_head,
        'occupation': instance.occupation,
        'occupation_category': instance.occupation_category,
        'primary_income_source': instance.primary_income_source,
        'business_start_date': instance.business_start_date.isoformat() if instance.business_start_date else None,
        'blue_tax_return_approved': instance.blue_tax_return_approved,
        'blue_tax_return_approval_date': instance.blue_tax_return_approval_date.isoformat() if instance.blue_tax_return_approval_date else None,
    }
    
    UserDetailHistory.objects.create(
        user_detail_id=instance.id,
        user_id=instance.user.id,
        action=action,
        detail_data=detail_data,
        changed_by=changed_by,
        ip_address=ip_address
    )


@receiver(post_delete, sender=User)
def create_user_delete_history(sender, instance, **kwargs):
    """
    Create user history record when user is deleted
    """
    # Get the request from thread local storage if available
    request = getattr(instance, '_request', None)
    changed_by = getattr(request, 'user', None) if request else None
    ip_address = None
    user_agent = None
    
    if request:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    UserHistory.objects.create(
        user_id=instance.id,
        username=instance.username,
        email=instance.email,
        role=instance.role,
        is_active=instance.is_active,
        action='DELETE',
        changed_by=changed_by,
        ip_address=ip_address,
        user_agent=user_agent
    )


@receiver(post_delete, sender=UserDetail)
def create_user_detail_delete_history(sender, instance, **kwargs):
    """
    Create user detail history record when user detail is deleted
    """
    # Get the request from thread local storage if available
    request = getattr(instance, '_request', None)
    changed_by = getattr(request, 'user', None) if request else None
    ip_address = None
    
    if request:
        ip_address = get_client_ip(request)
    
    # Serialize detail data
    detail_data = {
        'first_name': instance.first_name,
        'last_name': instance.last_name,
        'first_name_kana': instance.first_name_kana,
        'last_name_kana': instance.last_name_kana,
        'postal_code': instance.postal_code,
        'prefecture': instance.prefecture,
        'city': instance.city,
        'addr': instance.addr,
        'room_name': instance.room_name,
        'sex': instance.sex,
        'birth_day': instance.birth_day.isoformat() if instance.birth_day else None,
        'phone_number': instance.phone_number,
        'is_disabled': instance.is_disabled,
        'is_widow': instance.is_widow,
        'is_household_head': instance.is_household_head,
        'occupation': instance.occupation,
        'occupation_category': instance.occupation_category,
        'primary_income_source': instance.primary_income_source,
        'business_start_date': instance.business_start_date.isoformat() if instance.business_start_date else None,
        'blue_tax_return_approved': instance.blue_tax_return_approved,
        'blue_tax_return_approval_date': instance.blue_tax_return_approval_date.isoformat() if instance.blue_tax_return_approval_date else None,
    }
    
    UserDetailHistory.objects.create(
        user_detail_id=instance.id,
        user_id=instance.user.id,
        action='DELETE',
        detail_data=detail_data,
        changed_by=changed_by,
        ip_address=ip_address
    )


@receiver(pre_save, sender=User)
def user_pre_save(sender, instance, **kwargs):
    """
    Handle user pre-save operations
    """
    # Update password_changed_at when password is changed
    if instance.pk:
        try:
            old_instance = User.objects.get(pk=instance.pk)
            if old_instance.password != instance.password:
                instance.password_changed_at = timezone.now()
        except User.DoesNotExist:
            pass


def get_client_ip(request):
    """
    Get client IP address from request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# Middleware to attach request to model instances
class RequestMiddleware:
    """
    Middleware to attach request object to model instances
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Store request in thread local storage
        import threading
        if not hasattr(threading.current_thread(), 'request'):
            threading.current_thread().request = request
        
        response = self.get_response(request)
        
        # Clean up
        if hasattr(threading.current_thread(), 'request'):
            delattr(threading.current_thread(), 'request')
        
        return response


def get_current_request():
    """
    Get current request from thread local storage
    """
    import threading
    return getattr(threading.current_thread(), 'request', None)


# Signal to create default user detail when user is created
@receiver(post_save, sender=User)
def create_user_detail(sender, instance, created, **kwargs):
    """
    Create empty user detail when user is created
    """
    if created and not hasattr(instance, 'detail'):
        UserDetail.objects.create(user=instance)


# Signal to handle user role changes
@receiver(pre_save, sender=User)
def handle_role_change(sender, instance, **kwargs):
    """
    Handle user role changes and update permissions accordingly
    """
    if instance.pk:
        try:
            old_instance = User.objects.get(pk=instance.pk)
            if old_instance.role != instance.role:
                # Log role change
                request = get_current_request()
                changed_by = getattr(request, 'user', None) if request else None
                ip_address = get_client_ip(request) if request else None
                user_agent = request.META.get('HTTP_USER_AGENT', '') if request else ''
                
                UserHistory.objects.create(
                    user_id=instance.id,
                    username=instance.username,
                    email=instance.email,
                    role=instance.role,
                    is_active=instance.is_active,
                    action='ROLE_CHANGE',
                    changed_by=changed_by,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    old_values={'role': old_instance.role},
                    new_values={'role': instance.role}
                )
                
                # Update staff status based on role
                if instance.role in ['admin', 'super_admin']:
                    instance.is_staff = True
                else:
                    instance.is_staff = False
                
                # Update superuser status
                if instance.role == 'super_admin':
                    instance.is_superuser = True
                else:
                    instance.is_superuser = False
                    
        except User.DoesNotExist:
            pass