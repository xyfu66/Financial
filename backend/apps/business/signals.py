"""
Signals for Business models
"""

from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal
from .models import Income, Expense, IncomeCategory, ExpenseCategory, TaxCalculation


@receiver(pre_save, sender=Income)
def income_pre_save(sender, instance, **kwargs):
    """
    Handle income pre-save operations
    """
    # Auto-calculate tax amount if not provided
    if instance.tax_rate > 0 and instance.tax_amount == 0:
        instance.tax_amount = instance.calculate_tax_amount()
    
    # Set updated_by if available from request
    request = getattr(instance, '_request', None)
    if request and hasattr(request, 'user') and request.user.is_authenticated:
        if instance.pk:  # Update case
            instance.updated_by = request.user
        else:  # Create case
            instance.created_by = request.user


@receiver(pre_save, sender=Expense)
def expense_pre_save(sender, instance, **kwargs):
    """
    Handle expense pre-save operations
    """
    # Auto-calculate tax amount if not provided
    if instance.tax_rate > 0 and instance.tax_amount == 0:
        instance.tax_amount = instance.calculate_tax_amount()
    
    # Set updated_by if available from request
    request = getattr(instance, '_request', None)
    if request and hasattr(request, 'user') and request.user.is_authenticated:
        if instance.pk:  # Update case
            instance.updated_by = request.user
        else:  # Create case
            instance.created_by = request.user


@receiver(post_save, sender=Income)
def income_post_save(sender, instance, created, **kwargs):
    """
    Handle income post-save operations
    """
    # Log income creation/update in audit
    action = 'CREATE' if created else 'UPDATE'
    
    try:
        from apps.audit.utils import log_audit
        request = getattr(instance, '_request', None)
        user = getattr(request, 'user', None) if request else None
        
        log_audit(
            user=user or instance.user,
            action=action,
            model='Income',
            object_id=instance.id,
            changes={
                'amount': str(instance.amount),
                'category': instance.category.name,
                'date': instance.date.isoformat(),
                'status': instance.status
            }
        )
    except ImportError:
        # Audit app not available yet
        pass


@receiver(post_save, sender=Expense)
def expense_post_save(sender, instance, created, **kwargs):
    """
    Handle expense post-save operations
    """
    # Log expense creation/update in audit
    action = 'CREATE' if created else 'UPDATE'
    
    try:
        from apps.audit.utils import log_audit
        request = getattr(instance, '_request', None)
        user = getattr(request, 'user', None) if request else None
        
        log_audit(
            user=user or instance.user,
            action=action,
            model='Expense',
            object_id=instance.id,
            changes={
                'amount': str(instance.amount),
                'category': instance.category.name,
                'date': instance.date.isoformat(),
                'status': instance.status,
                'business_use_percentage': str(instance.business_use_percentage)
            }
        )
    except ImportError:
        # Audit app not available yet
        pass


@receiver(post_delete, sender=Income)
def income_post_delete(sender, instance, **kwargs):
    """
    Handle income deletion
    """
    try:
        from apps.audit.utils import log_audit
        request = getattr(instance, '_request', None)
        user = getattr(request, 'user', None) if request else None
        
        log_audit(
            user=user or instance.user,
            action='DELETE',
            model='Income',
            object_id=instance.id,
            changes={
                'deleted_amount': str(instance.amount),
                'deleted_category': instance.category.name,
                'deleted_date': instance.date.isoformat()
            }
        )
    except ImportError:
        # Audit app not available yet
        pass


@receiver(post_delete, sender=Expense)
def expense_post_delete(sender, instance, **kwargs):
    """
    Handle expense deletion
    """
    try:
        from apps.audit.utils import log_audit
        request = getattr(instance, '_request', None)
        user = getattr(request, 'user', None) if request else None
        
        log_audit(
            user=user or instance.user,
            action='DELETE',
            model='Expense',
            object_id=instance.id,
            changes={
                'deleted_amount': str(instance.amount),
                'deleted_category': instance.category.name,
                'deleted_date': instance.date.isoformat()
            }
        )
    except ImportError:
        # Audit app not available yet
        pass


@receiver(post_save, sender=IncomeCategory)
def income_category_post_save(sender, instance, created, **kwargs):
    """
    Handle income category creation/update
    """
    action = 'CREATE' if created else 'UPDATE'
    
    try:
        from apps.audit.utils import log_audit
        request = getattr(instance, '_request', None)
        user = getattr(request, 'user', None) if request else None
        
        log_audit(
            user=user or instance.created_by,
            action=action,
            model='IncomeCategory',
            object_id=instance.id,
            changes={
                'name': instance.name,
                'code': instance.code,
                'category_type': instance.category_type,
                'is_active': instance.is_active
            }
        )
    except ImportError:
        # Audit app not available yet
        pass


@receiver(post_save, sender=ExpenseCategory)
def expense_category_post_save(sender, instance, created, **kwargs):
    """
    Handle expense category creation/update
    """
    action = 'CREATE' if created else 'UPDATE'
    
    try:
        from apps.audit.utils import log_audit
        request = getattr(instance, '_request', None)
        user = getattr(request, 'user', None) if request else None
        
        log_audit(
            user=user or instance.created_by,
            action=action,
            model='ExpenseCategory',
            object_id=instance.id,
            changes={
                'name': instance.name,
                'code': instance.code,
                'category_type': instance.category_type,
                'is_active': instance.is_active
            }
        )
    except ImportError:
        # Audit app not available yet
        pass


@receiver(post_save, sender=TaxCalculation)
def tax_calculation_post_save(sender, instance, created, **kwargs):
    """
    Handle tax calculation creation/update
    """
    action = 'CREATE' if created else 'UPDATE'
    
    try:
        from apps.audit.utils import log_audit
        request = getattr(instance, '_request', None)
        user = getattr(request, 'user', None) if request else None
        
        log_audit(
            user=user or instance.calculated_by,
            action=action,
            model='TaxCalculation',
            object_id=instance.id,
            changes={
                'calculation_type': instance.calculation_type,
                'tax_year': instance.tax_year,
                'start_date': instance.start_date.isoformat(),
                'end_date': instance.end_date.isoformat(),
                'total_income': str(instance.total_income),
                'total_expenses': str(instance.total_expenses),
                'net_income': str(instance.net_income),
                'taxable_income': str(instance.taxable_income)
            }
        )
    except ImportError:
        # Audit app not available yet
        pass


# Signal to validate business rules
@receiver(pre_save, sender=Income)
def validate_income_business_rules(sender, instance, **kwargs):
    """
    Validate income business rules before saving
    """
    # Ensure payment date is not before income date
    if instance.payment_date and instance.payment_date < instance.date:
        raise ValueError("Payment date cannot be before income date")
    
    # Ensure tax amount is reasonable
    if instance.tax_amount > instance.amount:
        raise ValueError("Tax amount cannot be greater than total amount")
    
    # Validate category is active
    if not instance.category.is_active:
        raise ValueError("Cannot use inactive category")


@receiver(pre_save, sender=Expense)
def validate_expense_business_rules(sender, instance, **kwargs):
    """
    Validate expense business rules before saving
    """
    # Ensure payment date is not before expense date
    if instance.payment_date and instance.payment_date < instance.date:
        raise ValueError("Payment date cannot be before expense date")
    
    # Ensure tax amount is reasonable
    if instance.tax_amount > instance.amount:
        raise ValueError("Tax amount cannot be greater than total amount")
    
    # Ensure business use percentage is valid
    if instance.business_use_percentage < 0 or instance.business_use_percentage > 100:
        raise ValueError("Business use percentage must be between 0 and 100")
    
    # Validate category is active
    if not instance.category.is_active:
        raise ValueError("Cannot use inactive category")


# Signal to update related calculations when income/expense changes
@receiver(post_save, sender=Income)
@receiver(post_save, sender=Expense)
@receiver(post_delete, sender=Income)
@receiver(post_delete, sender=Expense)
def invalidate_tax_calculations(sender, instance, **kwargs):
    """
    Invalidate related tax calculations when income/expense changes
    """
    # Find tax calculations that might be affected
    user = instance.user
    date = instance.date
    
    # Find calculations that include this date
    affected_calculations = TaxCalculation.objects.filter(
        user=user,
        start_date__lte=date,
        end_date__gte=date
    )
    
    # Mark them for recalculation (you could add a needs_recalculation field)
    for calc in affected_calculations:
        calc.updated_at = timezone.now()
        calc.save(update_fields=['updated_at'])


# Signal to create default categories for new users
@receiver(post_save, sender='users.User')
def create_default_categories_for_user(sender, instance, created, **kwargs):
    """
    Create default income and expense categories for new users
    """
    if created and not instance.is_superuser:
        # Create default income categories
        default_income_categories = [
            {'name': '事業収入', 'code': 'BUS001', 'category_type': 'business'},
            {'name': '給与収入', 'code': 'SAL001', 'category_type': 'salary'},
            {'name': 'その他収入', 'code': 'OTH001', 'category_type': 'other'},
        ]
        
        for cat_data in default_income_categories:
            IncomeCategory.objects.get_or_create(
                code=cat_data['code'],
                defaults={
                    'name': cat_data['name'],
                    'category_type': cat_data['category_type'],
                    'created_by': instance
                }
            )
        
        # Create default expense categories
        default_expense_categories = [
            {'name': '消耗品費', 'code': 'SUP001', 'category_type': 'supplies'},
            {'name': '通信費', 'code': 'COM001', 'category_type': 'communication'},
            {'name': '旅費交通費', 'code': 'TRA001', 'category_type': 'travel'},
            {'name': '接待交際費', 'code': 'ENT001', 'category_type': 'entertainment'},
            {'name': '地代家賃', 'code': 'REN001', 'category_type': 'rent'},
            {'name': '水道光熱費', 'code': 'UTI001', 'category_type': 'utilities'},
            {'name': 'その他経費', 'code': 'OTH001', 'category_type': 'other'},
        ]
        
        for cat_data in default_expense_categories:
            ExpenseCategory.objects.get_or_create(
                code=cat_data['code'],
                defaults={
                    'name': cat_data['name'],
                    'category_type': cat_data['category_type'],
                    'created_by': instance
                }
            )


# Signal to handle file cleanup when records are deleted
@receiver(post_delete, sender=Income)
@receiver(post_delete, sender=Expense)
def cleanup_receipt_files(sender, instance, **kwargs):
    """
    Clean up receipt files when income/expense records are deleted
    """
    if instance.receipt_file:
        try:
            import os
            if os.path.isfile(instance.receipt_file.path):
                os.remove(instance.receipt_file.path)
        except Exception:
            # File might not exist or be accessible
            pass


# Signal to handle OCR processing status updates
@receiver(post_save, sender=Income)
@receiver(post_save, sender=Expense)
def handle_ocr_processing(sender, instance, created, **kwargs):
    """
    Handle OCR processing when receipt files are uploaded
    """
    if instance.receipt_file and not instance.ocr_processed:
        # Queue OCR processing task (if using Celery)
        try:
            from .tasks import process_receipt_ocr
            process_receipt_ocr.delay(sender.__name__, instance.id)
        except ImportError:
            # Celery not available, process synchronously
            pass