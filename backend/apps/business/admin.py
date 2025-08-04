"""
Admin configuration for Business models
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum
from .models import IncomeCategory, ExpenseCategory, Income, Expense, TaxCalculation


@admin.register(IncomeCategory)
class IncomeCategoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for IncomeCategory model
    """
    list_display = [
        'code', 'name', 'category_type', 'is_active', 'is_taxable',
        'tax_rate', 'blue_tax_deduction_eligible', 'created_at'
    ]
    list_filter = [
        'category_type', 'is_active', 'is_taxable', 'blue_tax_deduction_eligible',
        'created_at'
    ]
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['code', 'name']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'category_type', 'description', 'is_active')
        }),
        (_('Tax Information'), {
            'fields': ('is_taxable', 'tax_rate', 'blue_tax_deduction_eligible')
        }),
        (_('Audit Information'), {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for ExpenseCategory model
    """
    list_display = [
        'code', 'name', 'category_type', 'is_active', 'is_deductible',
        'deduction_rate', 'requires_receipt', 'created_at'
    ]
    list_filter = [
        'category_type', 'is_active', 'is_deductible', 'blue_tax_deduction_eligible',
        'requires_receipt', 'created_at'
    ]
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['code', 'name']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'category_type', 'description', 'is_active')
        }),
        (_('Deduction Information'), {
            'fields': ('is_deductible', 'deduction_rate', 'blue_tax_deduction_eligible', 'requires_receipt')
        }),
        (_('Audit Information'), {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    """
    Admin configuration for Income model
    """
    list_display = [
        'date', 'user', 'category', 'description', 'amount',
        'tax_amount', 'status', 'payment_date', 'created_at'
    ]
    list_filter = [
        'status', 'payment_method', 'is_tax_inclusive', 'category',
        'date', 'payment_date', 'created_at', 'ocr_processed'
    ]
    search_fields = [
        'description', 'client_name', 'invoice_number', 'user__username'
    ]
    readonly_fields = [
        'amount_excluding_tax', 'amount_including_tax', 'created_at',
        'updated_at', 'ocr_processed', 'ocr_confidence', 'ocr_data'
    ]
    date_hierarchy = 'date'
    ordering = ['-date', '-created_at']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('user', 'category', 'date', 'amount', 'description', 'notes')
        }),
        (_('Client Information'), {
            'fields': ('client_name', 'client_address', 'client_phone'),
            'classes': ('collapse',)
        }),
        (_('Payment Information'), {
            'fields': ('payment_method', 'payment_date', 'invoice_number', 'status')
        }),
        (_('Tax Information'), {
            'fields': ('tax_rate', 'tax_amount', 'is_tax_inclusive', 'amount_excluding_tax', 'amount_including_tax')
        }),
        (_('File & OCR'), {
            'fields': ('receipt_file', 'ocr_processed', 'ocr_confidence', 'ocr_data'),
            'classes': ('collapse',)
        }),
        (_('Audit Information'), {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'category', 'created_by', 'updated_by')


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    """
    Admin configuration for Expense model
    """
    list_display = [
        'date', 'user', 'category', 'description', 'amount',
        'business_use_percentage', 'business_deductible_amount',
        'status', 'payment_date', 'created_at'
    ]
    list_filter = [
        'status', 'payment_method', 'is_tax_inclusive', 'category',
        'date', 'payment_date', 'created_at', 'ocr_processed'
    ]
    search_fields = [
        'description', 'vendor_name', 'receipt_number', 'user__username'
    ]
    readonly_fields = [
        'amount_excluding_tax', 'amount_including_tax', 'business_deductible_amount',
        'created_at', 'updated_at', 'ocr_processed', 'ocr_confidence', 'ocr_data'
    ]
    date_hierarchy = 'date'
    ordering = ['-date', '-created_at']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('user', 'category', 'date', 'amount', 'description', 'notes')
        }),
        (_('Vendor Information'), {
            'fields': ('vendor_name', 'vendor_address', 'vendor_phone'),
            'classes': ('collapse',)
        }),
        (_('Payment Information'), {
            'fields': ('payment_method', 'payment_date', 'receipt_number', 'status')
        }),
        (_('Tax & Business Information'), {
            'fields': (
                'tax_rate', 'tax_amount', 'is_tax_inclusive',
                'business_use_percentage', 'amount_excluding_tax',
                'amount_including_tax', 'business_deductible_amount'
            )
        }),
        (_('File & OCR'), {
            'fields': ('receipt_file', 'ocr_processed', 'ocr_confidence', 'ocr_data'),
            'classes': ('collapse',)
        }),
        (_('Audit Information'), {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'category', 'created_by', 'updated_by')


@admin.register(TaxCalculation)
class TaxCalculationAdmin(admin.ModelAdmin):
    """
    Admin configuration for TaxCalculation model
    """
    list_display = [
        'user', 'calculation_type', 'tax_year', 'start_date', 'end_date',
        'total_income', 'total_expenses', 'net_income', 'taxable_income',
        'created_at'
    ]
    list_filter = [
        'calculation_type', 'tax_year', 'created_at'
    ]
    search_fields = ['user__username']
    readonly_fields = [
        'total_income', 'total_income_tax', 'total_expenses', 'total_expense_tax',
        'net_income', 'net_tax', 'taxable_income', 'created_at', 'updated_at'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-tax_year', '-end_date', '-created_at']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('user', 'calculation_type', 'tax_year', 'start_date', 'end_date')
        }),
        (_('Income Totals'), {
            'fields': ('total_income', 'total_income_tax')
        }),
        (_('Expense Totals'), {
            'fields': ('total_expenses', 'total_expense_tax')
        }),
        (_('Net Calculations'), {
            'fields': ('net_income', 'net_tax', 'blue_tax_deduction', 'taxable_income')
        }),
        (_('Calculation Data'), {
            'fields': ('calculation_data',),
            'classes': ('collapse',)
        }),
        (_('Audit Information'), {
            'fields': ('calculated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'calculated_by')


# Custom admin actions
@admin.action(description='Mark selected incomes as confirmed')
def mark_incomes_confirmed(modeladmin, request, queryset):
    """Mark selected incomes as confirmed"""
    updated = queryset.update(status='confirmed')
    modeladmin.message_user(
        request,
        f'{updated} income(s) were successfully marked as confirmed.'
    )


@admin.action(description='Mark selected expenses as confirmed')
def mark_expenses_confirmed(modeladmin, request, queryset):
    """Mark selected expenses as confirmed"""
    updated = queryset.update(status='confirmed')
    modeladmin.message_user(
        request,
        f'{updated} expense(s) were successfully marked as confirmed.'
    )


@admin.action(description='Calculate totals for selected period')
def calculate_period_totals(modeladmin, request, queryset):
    """Calculate totals for selected tax calculations"""
    for calculation in queryset:
        # Recalculate totals
        from django.db.models import Sum
        
        incomes = Income.objects.filter(
            user=calculation.user,
            date__gte=calculation.start_date,
            date__lte=calculation.end_date,
            status='confirmed'
        )
        
        expenses = Expense.objects.filter(
            user=calculation.user,
            date__gte=calculation.start_date,
            date__lte=calculation.end_date,
            status='confirmed'
        )
        
        calculation.total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
        calculation.total_income_tax = incomes.aggregate(Sum('tax_amount'))['tax_amount__sum'] or 0
        calculation.total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
        calculation.total_expense_tax = expenses.aggregate(Sum('tax_amount'))['tax_amount__sum'] or 0
        
        calculation.net_income = calculation.total_income - calculation.total_expenses
        calculation.net_tax = calculation.total_income_tax - calculation.total_expense_tax
        calculation.taxable_income = max(calculation.net_income - calculation.blue_tax_deduction, 0)
        
        calculation.save()
    
    modeladmin.message_user(
        request,
        f'{queryset.count()} tax calculation(s) were successfully recalculated.'
    )


# Add actions to admin classes
IncomeAdmin.actions = [mark_incomes_confirmed]
ExpenseAdmin.actions = [mark_expenses_confirmed]
TaxCalculationAdmin.actions = [calculate_period_totals]


# Custom admin site configuration
class BusinessAdminSite(admin.AdminSite):
    """
    Custom admin site for business management
    """
    site_header = "財務管理システム"
    site_title = "Business Admin"
    index_title = "業務管理"


# Register models with custom admin site
business_admin_site = BusinessAdminSite(name='business_admin')
business_admin_site.register(IncomeCategory, IncomeCategoryAdmin)
business_admin_site.register(ExpenseCategory, ExpenseCategoryAdmin)
business_admin_site.register(Income, IncomeAdmin)
business_admin_site.register(Expense, ExpenseAdmin)
business_admin_site.register(TaxCalculation, TaxCalculationAdmin)