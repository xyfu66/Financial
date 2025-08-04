"""
Serializers for Business models
"""

from rest_framework import serializers
from decimal import Decimal
from django.utils import timezone
from .models import IncomeCategory, ExpenseCategory, Income, Expense, TaxCalculation


class IncomeCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for IncomeCategory model
    """
    
    class Meta:
        model = IncomeCategory
        fields = [
            'id', 'name', 'code', 'category_type', 'description', 'is_active',
            'is_taxable', 'tax_rate', 'blue_tax_deduction_eligible',
            'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by']
    
    def validate_code(self, value):
        """
        Validate that code is unique
        """
        if self.instance:
            # Update case - exclude current instance
            if IncomeCategory.objects.exclude(pk=self.instance.pk).filter(code=value).exists():
                raise serializers.ValidationError("Category code must be unique.")
        else:
            # Create case
            if IncomeCategory.objects.filter(code=value).exists():
                raise serializers.ValidationError("Category code must be unique.")
        return value


class ExpenseCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for ExpenseCategory model
    """
    
    class Meta:
        model = ExpenseCategory
        fields = [
            'id', 'name', 'code', 'category_type', 'description', 'is_active',
            'is_deductible', 'deduction_rate', 'blue_tax_deduction_eligible',
            'requires_receipt', 'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by']
    
    def validate_code(self, value):
        """
        Validate that code is unique
        """
        if self.instance:
            # Update case - exclude current instance
            if ExpenseCategory.objects.exclude(pk=self.instance.pk).filter(code=value).exists():
                raise serializers.ValidationError("Category code must be unique.")
        else:
            # Create case
            if ExpenseCategory.objects.filter(code=value).exists():
                raise serializers.ValidationError("Category code must be unique.")
        return value


class IncomeSerializer(serializers.ModelSerializer):
    """
    Serializer for Income model
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_code = serializers.CharField(source='category.code', read_only=True)
    amount_excluding_tax = serializers.ReadOnlyField()
    amount_including_tax = serializers.ReadOnlyField()
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Income
        fields = [
            'id', 'user', 'category', 'category_name', 'category_code',
            'date', 'amount', 'description', 'notes',
            'client_name', 'client_address', 'client_phone',
            'payment_method', 'payment_date', 'invoice_number',
            'tax_amount', 'tax_rate', 'is_tax_inclusive',
            'status', 'receipt_file', 'ocr_processed', 'ocr_confidence', 'ocr_data',
            'amount_excluding_tax', 'amount_including_tax', 'user_name',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'created_by', 'updated_by',
            'ocr_processed', 'ocr_confidence', 'ocr_data'
        ]
    
    def validate_amount(self, value):
        """
        Validate amount is positive
        """
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value
    
    def validate_date(self, value):
        """
        Validate date is not in the future
        """
        if value > timezone.now().date():
            raise serializers.ValidationError("Date cannot be in the future.")
        return value
    
    def validate_payment_date(self, value):
        """
        Validate payment date if provided
        """
        if value and value > timezone.now().date():
            raise serializers.ValidationError("Payment date cannot be in the future.")
        return value
    
    def validate(self, attrs):
        """
        Cross-field validation
        """
        # Validate payment date is not before income date
        if attrs.get('payment_date') and attrs.get('date'):
            if attrs['payment_date'] < attrs['date']:
                raise serializers.ValidationError({
                    'payment_date': 'Payment date cannot be before income date.'
                })
        
        # Validate tax amount if tax rate is provided
        if attrs.get('tax_rate', 0) > 0 and not attrs.get('tax_amount'):
            amount = attrs.get('amount', Decimal('0'))
            tax_rate = attrs.get('tax_rate', Decimal('0'))
            is_tax_inclusive = attrs.get('is_tax_inclusive', True)
            
            if is_tax_inclusive:
                attrs['tax_amount'] = amount * tax_rate / (100 + tax_rate)
            else:
                attrs['tax_amount'] = amount * tax_rate / 100
        
        return attrs


class IncomeCreateSerializer(IncomeSerializer):
    """
    Serializer for creating Income records
    """
    
    def create(self, validated_data):
        """
        Create income with user from request
        """
        request = self.context.get('request')
        if request and request.user:
            validated_data['user'] = request.user
            validated_data['created_by'] = request.user
        
        return super().create(validated_data)


class IncomeUpdateSerializer(IncomeSerializer):
    """
    Serializer for updating Income records
    """
    
    def update(self, instance, validated_data):
        """
        Update income with updated_by from request
        """
        request = self.context.get('request')
        if request and request.user:
            validated_data['updated_by'] = request.user
        
        return super().update(instance, validated_data)


class ExpenseSerializer(serializers.ModelSerializer):
    """
    Serializer for Expense model
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_code = serializers.CharField(source='category.code', read_only=True)
    amount_excluding_tax = serializers.ReadOnlyField()
    amount_including_tax = serializers.ReadOnlyField()
    business_deductible_amount = serializers.ReadOnlyField()
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Expense
        fields = [
            'id', 'user', 'category', 'category_name', 'category_code',
            'date', 'amount', 'description', 'notes',
            'vendor_name', 'vendor_address', 'vendor_phone',
            'payment_method', 'payment_date', 'receipt_number',
            'tax_amount', 'tax_rate', 'is_tax_inclusive',
            'business_use_percentage', 'status', 'receipt_file',
            'ocr_processed', 'ocr_confidence', 'ocr_data',
            'amount_excluding_tax', 'amount_including_tax', 'business_deductible_amount',
            'user_name', 'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'created_by', 'updated_by',
            'ocr_processed', 'ocr_confidence', 'ocr_data'
        ]
    
    def validate_amount(self, value):
        """
        Validate amount is positive
        """
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value
    
    def validate_date(self, value):
        """
        Validate date is not in the future
        """
        if value > timezone.now().date():
            raise serializers.ValidationError("Date cannot be in the future.")
        return value
    
    def validate_payment_date(self, value):
        """
        Validate payment date if provided
        """
        if value and value > timezone.now().date():
            raise serializers.ValidationError("Payment date cannot be in the future.")
        return value
    
    def validate_business_use_percentage(self, value):
        """
        Validate business use percentage
        """
        if value < 0 or value > 100:
            raise serializers.ValidationError("Business use percentage must be between 0 and 100.")
        return value
    
    def validate(self, attrs):
        """
        Cross-field validation
        """
        # Validate payment date is not before expense date
        if attrs.get('payment_date') and attrs.get('date'):
            if attrs['payment_date'] < attrs['date']:
                raise serializers.ValidationError({
                    'payment_date': 'Payment date cannot be before expense date.'
                })
        
        # Validate tax amount if tax rate is provided
        if attrs.get('tax_rate', 0) > 0 and not attrs.get('tax_amount'):
            amount = attrs.get('amount', Decimal('0'))
            tax_rate = attrs.get('tax_rate', Decimal('0'))
            is_tax_inclusive = attrs.get('is_tax_inclusive', True)
            
            if is_tax_inclusive:
                attrs['tax_amount'] = amount * tax_rate / (100 + tax_rate)
            else:
                attrs['tax_amount'] = amount * tax_rate / 100
        
        return attrs


class ExpenseCreateSerializer(ExpenseSerializer):
    """
    Serializer for creating Expense records
    """
    
    def create(self, validated_data):
        """
        Create expense with user from request
        """
        request = self.context.get('request')
        if request and request.user:
            validated_data['user'] = request.user
            validated_data['created_by'] = request.user
        
        return super().create(validated_data)


class ExpenseUpdateSerializer(ExpenseSerializer):
    """
    Serializer for updating Expense records
    """
    
    def update(self, instance, validated_data):
        """
        Update expense with updated_by from request
        """
        request = self.context.get('request')
        if request and request.user:
            validated_data['updated_by'] = request.user
        
        return super().update(instance, validated_data)


class TaxCalculationSerializer(serializers.ModelSerializer):
    """
    Serializer for TaxCalculation model
    """
    user_name = serializers.CharField(source='user.username', read_only=True)
    calculated_by_name = serializers.CharField(source='calculated_by.username', read_only=True)
    
    class Meta:
        model = TaxCalculation
        fields = [
            'id', 'user', 'user_name', 'calculation_type',
            'start_date', 'end_date', 'tax_year',
            'total_income', 'total_income_tax', 'total_expenses', 'total_expense_tax',
            'net_income', 'net_tax', 'blue_tax_deduction', 'taxable_income',
            'calculation_data', 'created_at', 'updated_at',
            'calculated_by', 'calculated_by_name'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'calculated_by',
            'total_income', 'total_income_tax', 'total_expenses', 'total_expense_tax',
            'net_income', 'net_tax', 'taxable_income'
        ]
    
    def validate(self, attrs):
        """
        Validate date range
        """
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        
        if start_date and end_date:
            if start_date >= end_date:
                raise serializers.ValidationError({
                    'end_date': 'End date must be after start date.'
                })
        
        return attrs


class IncomeListSerializer(serializers.ModelSerializer):
    """
    Serializer for Income list view (minimal fields)
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    amount_including_tax = serializers.ReadOnlyField()
    
    class Meta:
        model = Income
        fields = [
            'id', 'date', 'amount', 'amount_including_tax', 'description',
            'category_name', 'status', 'payment_date', 'created_at'
        ]


class ExpenseListSerializer(serializers.ModelSerializer):
    """
    Serializer for Expense list view (minimal fields)
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    amount_including_tax = serializers.ReadOnlyField()
    business_deductible_amount = serializers.ReadOnlyField()
    
    class Meta:
        model = Expense
        fields = [
            'id', 'date', 'amount', 'amount_including_tax', 'business_deductible_amount',
            'description', 'category_name', 'status', 'payment_date', 'created_at'
        ]


class FinancialSummarySerializer(serializers.Serializer):
    """
    Serializer for financial summary data
    """
    period_start = serializers.DateField()
    period_end = serializers.DateField()
    total_income = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=15, decimal_places=2)
    net_income = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_income_tax = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_expense_tax = serializers.DecimalField(max_digits=15, decimal_places=2)
    net_tax = serializers.DecimalField(max_digits=15, decimal_places=2)
    
    # Category breakdowns
    income_by_category = serializers.DictField(child=serializers.DecimalField(max_digits=15, decimal_places=2))
    expenses_by_category = serializers.DictField(child=serializers.DecimalField(max_digits=15, decimal_places=2))
    
    # Monthly data
    monthly_data = serializers.ListField(
        child=serializers.DictField(
            child=serializers.DecimalField(max_digits=15, decimal_places=2)
        )
    )


class BulkImportSerializer(serializers.Serializer):
    """
    Serializer for bulk import operations
    """
    file = serializers.FileField()
    import_type = serializers.ChoiceField(choices=['income', 'expense'])
    skip_duplicates = serializers.BooleanField(default=True)
    validate_only = serializers.BooleanField(default=False)
    
    def validate_file(self, value):
        """
        Validate uploaded file
        """
        if not value.name.endswith(('.csv', '.xlsx', '.xls')):
            raise serializers.ValidationError("File must be CSV or Excel format.")
        
        # Check file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size must be less than 10MB.")
        
        return value