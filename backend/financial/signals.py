"""
Signals for financial app
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Income, Expense, Asset, TaxCalculation


@receiver(post_save, sender=Income)
def update_tax_calculation_on_income_change(sender, instance, **kwargs):
    """Update tax calculations when income is modified"""
    # TODO: Implement automatic tax calculation update
    pass


@receiver(post_save, sender=Expense)
def update_tax_calculation_on_expense_change(sender, instance, **kwargs):
    """Update tax calculations when expense is modified"""
    # TODO: Implement automatic tax calculation update
    pass


@receiver(post_save, sender=Asset)
def calculate_depreciation_on_asset_change(sender, instance, **kwargs):
    """Calculate depreciation when asset is modified"""
    # TODO: Implement automatic depreciation calculation
    pass