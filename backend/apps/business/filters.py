"""
Filters for Business models
"""

import django_filters
from django.db import models
from .models import IncomeCategory, ExpenseCategory, Income, Expense, TaxCalculation


class IncomeCategoryFilter(django_filters.FilterSet):
    """
    Filter for IncomeCategory model
    """
    name = django_filters.CharFilter(lookup_expr='icontains')
    code = django_filters.CharFilter(lookup_expr='icontains')
    category_type = django_filters.ChoiceFilter(choices=IncomeCategory.CATEGORY_TYPES)
    is_active = django_filters.BooleanFilter()
    is_taxable = django_filters.BooleanFilter()
    blue_tax_deduction_eligible = django_filters.BooleanFilter()
    tax_rate_range = django_filters.RangeFilter(field_name='tax_rate')
    created_at = django_filters.DateFromToRangeFilter()
    
    class Meta:
        model = IncomeCategory
        fields = [
            'name', 'code', 'category_type', 'is_active', 'is_taxable',
            'blue_tax_deduction_eligible', 'tax_rate_range', 'created_at'
        ]


class ExpenseCategoryFilter(django_filters.FilterSet):
    """
    Filter for ExpenseCategory model
    """
    name = django_filters.CharFilter(lookup_expr='icontains')
    code = django_filters.CharFilter(lookup_expr='icontains')
    category_type = django_filters.ChoiceFilter(choices=ExpenseCategory.CATEGORY_TYPES)
    is_active = django_filters.BooleanFilter()
    is_deductible = django_filters.BooleanFilter()
    blue_tax_deduction_eligible = django_filters.BooleanFilter()
    requires_receipt = django_filters.BooleanFilter()
    deduction_rate_range = django_filters.RangeFilter(field_name='deduction_rate')
    created_at = django_filters.DateFromToRangeFilter()
    
    class Meta:
        model = ExpenseCategory
        fields = [
            'name', 'code', 'category_type', 'is_active', 'is_deductible',
            'blue_tax_deduction_eligible', 'requires_receipt',
            'deduction_rate_range', 'created_at'
        ]


class IncomeFilter(django_filters.FilterSet):
    """
    Filter for Income model
    """
    date = django_filters.DateFromToRangeFilter()
    amount = django_filters.RangeFilter()
    description = django_filters.CharFilter(lookup_expr='icontains')
    client_name = django_filters.CharFilter(lookup_expr='icontains')
    category = django_filters.ModelChoiceFilter(queryset=IncomeCategory.objects.filter(is_active=True))
    category__name = django_filters.CharFilter(
        field_name='category__name',
        lookup_expr='icontains'
    )
    category__code = django_filters.CharFilter(
        field_name='category__code',
        lookup_expr='icontains'
    )
    category__category_type = django_filters.ChoiceFilter(
        field_name='category__category_type',
        choices=IncomeCategory.CATEGORY_TYPES
    )
    payment_method = django_filters.ChoiceFilter(choices=Income.PAYMENT_METHODS)
    payment_date = django_filters.DateFromToRangeFilter()
    status = django_filters.ChoiceFilter(choices=Income.STATUS_CHOICES)
    is_tax_inclusive = django_filters.BooleanFilter()
    tax_rate = django_filters.RangeFilter()
    tax_amount = django_filters.RangeFilter()
    invoice_number = django_filters.CharFilter(lookup_expr='icontains')
    
    # OCR related filters
    ocr_processed = django_filters.BooleanFilter()
    ocr_confidence = django_filters.RangeFilter()
    has_receipt = django_filters.BooleanFilter(method='filter_has_receipt')
    
    # Date filters
    created_at = django_filters.DateFromToRangeFilter()
    updated_at = django_filters.DateFromToRangeFilter()
    
    # Year and month filters
    year = django_filters.NumberFilter(field_name='date__year')
    month = django_filters.NumberFilter(field_name='date__month')
    quarter = django_filters.NumberFilter(method='filter_quarter')
    
    # User filters (for admin users)
    user = django_filters.ModelChoiceFilter(queryset=None)  # Will be set in __init__
    user__username = django_filters.CharFilter(
        field_name='user__username',
        lookup_expr='icontains'
    )
    
    class Meta:
        model = Income
        fields = [
            'date', 'amount', 'description', 'client_name', 'category',
            'payment_method', 'payment_date', 'status', 'is_tax_inclusive',
            'tax_rate', 'tax_amount', 'invoice_number', 'ocr_processed',
            'ocr_confidence', 'has_receipt', 'created_at', 'updated_at',
            'year', 'month', 'quarter', 'user', 'user__username'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set user queryset based on request user permissions
        request = getattr(self, 'request', None)
        if request and hasattr(request, 'user'):
            if request.user.is_admin:
                from apps.users.models import User
                self.filters['user'].queryset = User.objects.all()
            else:
                # Regular users can only filter their own data
                self.filters['user'].queryset = request.user.__class__.objects.filter(id=request.user.id)
    
    def filter_has_receipt(self, queryset, name, value):
        """
        Filter by whether income has receipt file
        """
        if value:
            return queryset.exclude(receipt_file='')
        else:
            return queryset.filter(receipt_file='')
    
    def filter_quarter(self, queryset, name, value):
        """
        Filter by quarter (1-4)
        """
        if value in [1, 2, 3, 4]:
            start_month = (value - 1) * 3 + 1
            end_month = value * 3
            return queryset.filter(
                date__month__gte=start_month,
                date__month__lte=end_month
            )
        return queryset


class ExpenseFilter(django_filters.FilterSet):
    """
    Filter for Expense model
    """
    date = django_filters.DateFromToRangeFilter()
    amount = django_filters.RangeFilter()
    description = django_filters.CharFilter(lookup_expr='icontains')
    vendor_name = django_filters.CharFilter(lookup_expr='icontains')
    category = django_filters.ModelChoiceFilter(queryset=ExpenseCategory.objects.filter(is_active=True))
    category__name = django_filters.CharFilter(
        field_name='category__name',
        lookup_expr='icontains'
    )
    category__code = django_filters.CharFilter(
        field_name='category__code',
        lookup_expr='icontains'
    )
    category__category_type = django_filters.ChoiceFilter(
        field_name='category__category_type',
        choices=ExpenseCategory.CATEGORY_TYPES
    )
    payment_method = django_filters.ChoiceFilter(choices=Expense.PAYMENT_METHODS)
    payment_date = django_filters.DateFromToRangeFilter()
    status = django_filters.ChoiceFilter(choices=Expense.STATUS_CHOICES)
    is_tax_inclusive = django_filters.BooleanFilter()
    tax_rate = django_filters.RangeFilter()
    tax_amount = django_filters.RangeFilter()
    business_use_percentage = django_filters.RangeFilter()
    receipt_number = django_filters.CharFilter(lookup_expr='icontains')
    
    # OCR related filters
    ocr_processed = django_filters.BooleanFilter()
    ocr_confidence = django_filters.RangeFilter()
    has_receipt = django_filters.BooleanFilter(method='filter_has_receipt')
    
    # Date filters
    created_at = django_filters.DateFromToRangeFilter()
    updated_at = django_filters.DateFromToRangeFilter()
    
    # Year and month filters
    year = django_filters.NumberFilter(field_name='date__year')
    month = django_filters.NumberFilter(field_name='date__month')
    quarter = django_filters.NumberFilter(method='filter_quarter')
    
    # User filters (for admin users)
    user = django_filters.ModelChoiceFilter(queryset=None)  # Will be set in __init__
    user__username = django_filters.CharFilter(
        field_name='user__username',
        lookup_expr='icontains'
    )
    
    # Business deduction filters
    is_fully_deductible = django_filters.BooleanFilter(method='filter_fully_deductible')
    business_deductible_amount = django_filters.RangeFilter(method='filter_business_deductible_amount')
    
    class Meta:
        model = Expense
        fields = [
            'date', 'amount', 'description', 'vendor_name', 'category',
            'payment_method', 'payment_date', 'status', 'is_tax_inclusive',
            'tax_rate', 'tax_amount', 'business_use_percentage', 'receipt_number',
            'ocr_processed', 'ocr_confidence', 'has_receipt', 'created_at',
            'updated_at', 'year', 'month', 'quarter', 'user', 'user__username',
            'is_fully_deductible', 'business_deductible_amount'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set user queryset based on request user permissions
        request = getattr(self, 'request', None)
        if request and hasattr(request, 'user'):
            if request.user.is_admin:
                from apps.users.models import User
                self.filters['user'].queryset = User.objects.all()
            else:
                # Regular users can only filter their own data
                self.filters['user'].queryset = request.user.__class__.objects.filter(id=request.user.id)
    
    def filter_has_receipt(self, queryset, name, value):
        """
        Filter by whether expense has receipt file
        """
        if value:
            return queryset.exclude(receipt_file='')
        else:
            return queryset.filter(receipt_file='')
    
    def filter_quarter(self, queryset, name, value):
        """
        Filter by quarter (1-4)
        """
        if value in [1, 2, 3, 4]:
            start_month = (value - 1) * 3 + 1
            end_month = value * 3
            return queryset.filter(
                date__month__gte=start_month,
                date__month__lte=end_month
            )
        return queryset
    
    def filter_fully_deductible(self, queryset, name, value):
        """
        Filter by whether expense is fully deductible (100% business use)
        """
        if value:
            return queryset.filter(business_use_percentage=100)
        else:
            return queryset.exclude(business_use_percentage=100)
    
    def filter_business_deductible_amount(self, queryset, name, value):
        """
        Filter by business deductible amount range
        """
        if value:
            # Calculate business deductible amount and filter
            if value.start:
                queryset = queryset.extra(
                    where=["amount * business_use_percentage / 100 >= %s"],
                    params=[value.start]
                )
            if value.stop:
                queryset = queryset.extra(
                    where=["amount * business_use_percentage / 100 <= %s"],
                    params=[value.stop]
                )
        return queryset


class TaxCalculationFilter(django_filters.FilterSet):
    """
    Filter for TaxCalculation model
    """
    calculation_type = django_filters.ChoiceFilter(choices=TaxCalculation.CALCULATION_TYPES)
    tax_year = django_filters.NumberFilter()
    tax_year_range = django_filters.RangeFilter(field_name='tax_year')
    start_date = django_filters.DateFromToRangeFilter()
    end_date = django_filters.DateFromToRangeFilter()
    
    # Amount filters
    total_income = django_filters.RangeFilter()
    total_expenses = django_filters.RangeFilter()
    net_income = django_filters.RangeFilter()
    taxable_income = django_filters.RangeFilter()
    blue_tax_deduction = django_filters.RangeFilter()
    
    # Date filters
    created_at = django_filters.DateFromToRangeFilter()
    updated_at = django_filters.DateFromToRangeFilter()
    
    # User filters (for admin users)
    user = django_filters.ModelChoiceFilter(queryset=None)  # Will be set in __init__
    user__username = django_filters.CharFilter(
        field_name='user__username',
        lookup_expr='icontains'
    )
    calculated_by = django_filters.ModelChoiceFilter(queryset=None)  # Will be set in __init__
    
    class Meta:
        model = TaxCalculation
        fields = [
            'calculation_type', 'tax_year', 'tax_year_range', 'start_date', 'end_date',
            'total_income', 'total_expenses', 'net_income', 'taxable_income',
            'blue_tax_deduction', 'created_at', 'updated_at', 'user',
            'user__username', 'calculated_by'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set user queryset based on request user permissions
        request = getattr(self, 'request', None)
        if request and hasattr(request, 'user'):
            if request.user.is_admin:
                from apps.users.models import User
                self.filters['user'].queryset = User.objects.all()
                self.filters['calculated_by'].queryset = User.objects.all()
            else:
                # Regular users can only filter their own data
                self.filters['user'].queryset = request.user.__class__.objects.filter(id=request.user.id)
                self.filters['calculated_by'].queryset = request.user.__class__.objects.all()


class FinancialSummaryFilter(django_filters.FilterSet):
    """
    Filter for financial summary queries
    """
    start_date = django_filters.DateFilter()
    end_date = django_filters.DateFilter()
    year = django_filters.NumberFilter()
    month = django_filters.NumberFilter()
    quarter = django_filters.NumberFilter(method='filter_quarter')
    category_type = django_filters.CharFilter(method='filter_category_type')
    
    def filter_quarter(self, queryset, name, value):
        """
        Filter by quarter (1-4)
        """
        if value in [1, 2, 3, 4]:
            start_month = (value - 1) * 3 + 1
            end_month = value * 3
            return queryset.filter(
                date__month__gte=start_month,
                date__month__lte=end_month
            )
        return queryset
    
    def filter_category_type(self, queryset, name, value):
        """
        Filter by category type
        """
        return queryset.filter(category__category_type=value)