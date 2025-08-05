"""
Financial models for Personal Financial Management System
"""
import uuid
from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User


class IncomeCategory(models.Model):
    """
    Income category master table
    Maps to T_Master_Income_Categories table in PostgreSQL
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='category_id')
    category_code = models.CharField(_('category code'), max_length=20, unique=True)
    category_name = models.CharField(_('category name'), max_length=100)
    category_name_en = models.CharField(_('category name (English)'), max_length=100, blank=True)
    description = models.TextField(_('description'), blank=True)
    tax_deductible = models.BooleanField(_('tax deductible'), default=False)
    is_business_income = models.BooleanField(_('is business income'), default=True)
    sort_order = models.IntegerField(_('sort order'), default=0)
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_income_categories'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_income_categories'
    )

    class Meta:
        db_table = 'T_Master_Income_Categories'
        verbose_name = _('Income Category')
        verbose_name_plural = _('Income Categories')
        ordering = ['sort_order', 'category_name']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['category_code']),
        ]

    def __str__(self):
        return self.category_name


class ExpenseCategory(models.Model):
    """
    Expense category master table
    Maps to T_Master_Expense_Categories table in PostgreSQL
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='category_id')
    category_code = models.CharField(_('category code'), max_length=20, unique=True)
    category_name = models.CharField(_('category name'), max_length=100)
    category_name_en = models.CharField(_('category name (English)'), max_length=100, blank=True)
    description = models.TextField(_('description'), blank=True)
    tax_deductible = models.BooleanField(_('tax deductible'), default=True)
    is_business_expense = models.BooleanField(_('is business expense'), default=True)
    depreciation_years = models.IntegerField(
        _('depreciation years'),
        null=True,
        blank=True,
        help_text=_('Number of years for depreciation calculation')
    )
    sort_order = models.IntegerField(_('sort order'), default=0)
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_expense_categories'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_expense_categories'
    )

    class Meta:
        db_table = 'T_Master_Expense_Categories'
        verbose_name = _('Expense Category')
        verbose_name_plural = _('Expense Categories')
        ordering = ['sort_order', 'category_name']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['category_code']),
        ]

    def __str__(self):
        return self.category_name


class Income(models.Model):
    """
    Income data table
    Maps to T_Dat_Incomes table in PostgreSQL
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='income_id')
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='incomes',
        db_column='user_id'
    )
    category = models.ForeignKey(
        IncomeCategory,
        on_delete=models.PROTECT,
        related_name='incomes',
        db_column='category_id'
    )
    income_date = models.DateField(_('income date'))
    description = models.TextField(_('description'))
    client_name = models.CharField(_('client name'), max_length=200, blank=True)
    client_address = models.TextField(_('client address'), blank=True)
    invoice_number = models.CharField(_('invoice number'), max_length=100, blank=True)
    amount = models.DecimalField(
        _('amount'),
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )
    tax_amount = models.DecimalField(
        _('tax amount'),
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    currency = models.CharField(_('currency'), max_length=3, default='JPY')
    payment_method = models.CharField(
        _('payment method'),
        max_length=50,
        blank=True,
        help_text=_('Cash, Bank Transfer, Credit Card, etc.')
    )
    payment_date = models.DateField(_('payment date'), null=True, blank=True)
    is_paid = models.BooleanField(_('is paid'), default=False)
    receipt_file_path = models.CharField(_('receipt file path'), max_length=500, blank=True)
    notes = models.TextField(_('notes'), blank=True)
    ocr_processed = models.BooleanField(_('OCR processed'), default=False)
    ocr_confidence = models.DecimalField(
        _('OCR confidence'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))]
    )
    ocr_data = models.JSONField(_('OCR data'), default=dict, blank=True)
    tags = models.CharField(
        _('tags'),
        max_length=500,
        blank=True,
        help_text=_('Comma-separated tags')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_incomes'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_incomes'
    )

    class Meta:
        db_table = 'T_Dat_Incomes'
        verbose_name = _('Income')
        verbose_name_plural = _('Incomes')
        ordering = ['-income_date', '-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['category']),
            models.Index(fields=['income_date']),
            models.Index(fields=['amount']),
            models.Index(fields=['is_paid']),
            models.Index(fields=['created_at']),
            models.Index(fields=['user', 'income_date']),
        ]

    def __str__(self):
        return f"{self.description} - {self.amount} {self.currency}"

    @property
    def net_amount(self):
        """Calculate net amount (amount - tax_amount)"""
        return self.amount - self.tax_amount

    def get_tags_list(self):
        """Return tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []


class Expense(models.Model):
    """
    Expense data table
    Maps to T_Dat_Expenses table in PostgreSQL
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='expense_id')
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='expenses',
        db_column='user_id'
    )
    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.PROTECT,
        related_name='expenses',
        db_column='category_id'
    )
    expense_date = models.DateField(_('expense date'))
    description = models.TextField(_('description'))
    vendor_name = models.CharField(_('vendor name'), max_length=200, blank=True)
    vendor_address = models.TextField(_('vendor address'), blank=True)
    receipt_number = models.CharField(_('receipt number'), max_length=100, blank=True)
    amount = models.DecimalField(
        _('amount'),
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )
    tax_amount = models.DecimalField(
        _('tax amount'),
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    currency = models.CharField(_('currency'), max_length=3, default='JPY')
    payment_method = models.CharField(
        _('payment method'),
        max_length=50,
        blank=True,
        help_text=_('Cash, Bank Transfer, Credit Card, etc.')
    )
    payment_date = models.DateField(_('payment date'), null=True, blank=True)
    is_paid = models.BooleanField(_('is paid'), default=False)
    receipt_file_path = models.CharField(_('receipt file path'), max_length=500, blank=True)
    business_use_percentage = models.DecimalField(
        _('business use percentage'),
        max_digits=5,
        decimal_places=2,
        default=Decimal('100.00'),
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))]
    )
    notes = models.TextField(_('notes'), blank=True)
    ocr_processed = models.BooleanField(_('OCR processed'), default=False)
    ocr_confidence = models.DecimalField(
        _('OCR confidence'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))]
    )
    ocr_data = models.JSONField(_('OCR data'), default=dict, blank=True)
    tags = models.CharField(
        _('tags'),
        max_length=500,
        blank=True,
        help_text=_('Comma-separated tags')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_expenses'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_expenses'
    )

    class Meta:
        db_table = 'T_Dat_Expenses'
        verbose_name = _('Expense')
        verbose_name_plural = _('Expenses')
        ordering = ['-expense_date', '-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['category']),
            models.Index(fields=['expense_date']),
            models.Index(fields=['amount']),
            models.Index(fields=['is_paid']),
            models.Index(fields=['created_at']),
            models.Index(fields=['user', 'expense_date']),
        ]

    def __str__(self):
        return f"{self.description} - {self.amount} {self.currency}"

    @property
    def net_amount(self):
        """Calculate net amount (amount - tax_amount)"""
        return self.amount - self.tax_amount

    @property
    def deductible_amount(self):
        """Calculate deductible amount based on business use percentage"""
        return self.amount * self.business_use_percentage / Decimal('100')

    def get_tags_list(self):
        """Return tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []


class Asset(models.Model):
    """
    Asset management table for depreciation calculations
    Maps to T_Dat_Assets table in PostgreSQL
    """
    DEPRECIATION_METHODS = [
        ('straight_line', _('Straight Line')),
        ('declining_balance', _('Declining Balance')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='asset_id')
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assets',
        db_column='user_id'
    )
    expense = models.ForeignKey(
        Expense,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assets',
        db_column='expense_id',
        help_text=_('Link to original purchase expense')
    )
    asset_name = models.CharField(_('asset name'), max_length=200)
    asset_category = models.CharField(_('asset category'), max_length=100, blank=True)
    purchase_date = models.DateField(_('purchase date'))
    purchase_amount = models.DecimalField(
        _('purchase amount'),
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )
    depreciation_method = models.CharField(
        _('depreciation method'),
        max_length=50,
        choices=DEPRECIATION_METHODS,
        default='straight_line'
    )
    useful_life_years = models.IntegerField(
        _('useful life years'),
        validators=[MinValueValidator(1)]
    )
    salvage_value = models.DecimalField(
        _('salvage value'),
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    accumulated_depreciation = models.DecimalField(
        _('accumulated depreciation'),
        max_digits=15,
        decimal_places=2,
        default=Decimal('0')
    )
    disposal_date = models.DateField(_('disposal date'), null=True, blank=True)
    disposal_amount = models.DecimalField(
        _('disposal amount'),
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )
    is_active = models.BooleanField(_('is active'), default=True)
    notes = models.TextField(_('notes'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_assets'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_assets'
    )

    class Meta:
        db_table = 'T_Dat_Assets'
        verbose_name = _('Asset')
        verbose_name_plural = _('Assets')
        ordering = ['-purchase_date', 'asset_name']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['purchase_date']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.asset_name

    @property
    def annual_depreciation(self):
        """Calculate annual depreciation amount"""
        if self.depreciation_method == 'straight_line':
            return (self.purchase_amount - self.salvage_value) / Decimal(str(self.useful_life_years))
        else:  # declining_balance
            return self.purchase_amount * Decimal('0.2')  # Simplified 20% declining balance

    @property
    def book_value(self):
        """Calculate current book value"""
        return self.purchase_amount - self.accumulated_depreciation


class TaxCalculation(models.Model):
    """
    Tax calculation results table
    Maps to T_Dat_Tax_Calculations table in PostgreSQL
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='calculation_id')
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tax_calculations',
        db_column='user_id'
    )
    calculation_year = models.IntegerField(_('calculation year'))
    calculation_period_start = models.DateField(_('calculation period start'))
    calculation_period_end = models.DateField(_('calculation period end'))
    total_income = models.DecimalField(
        _('total income'),
        max_digits=15,
        decimal_places=2,
        default=Decimal('0')
    )
    total_expenses = models.DecimalField(
        _('total expenses'),
        max_digits=15,
        decimal_places=2,
        default=Decimal('0')
    )
    total_deductible_expenses = models.DecimalField(
        _('total deductible expenses'),
        max_digits=15,
        decimal_places=2,
        default=Decimal('0')
    )
    basic_deduction = models.DecimalField(
        _('basic deduction'),
        max_digits=15,
        decimal_places=2,
        default=Decimal('480000')  # 基礎控除
    )
    blue_form_deduction = models.DecimalField(
        _('blue form deduction'),
        max_digits=15,
        decimal_places=2,
        default=Decimal('0')  # 青色申告特別控除
    )
    other_deductions = models.DecimalField(
        _('other deductions'),
        max_digits=15,
        decimal_places=2,
        default=Decimal('0')
    )
    income_tax = models.DecimalField(
        _('income tax'),
        max_digits=15,
        decimal_places=2,
        default=Decimal('0')
    )
    resident_tax = models.DecimalField(
        _('resident tax'),
        max_digits=15,
        decimal_places=2,
        default=Decimal('0')
    )
    business_tax = models.DecimalField(
        _('business tax'),
        max_digits=15,
        decimal_places=2,
        default=Decimal('0')
    )
    calculation_notes = models.TextField(_('calculation notes'), blank=True)
    is_final = models.BooleanField(_('is final'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_tax_calculations'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_tax_calculations'
    )

    class Meta:
        db_table = 'T_Dat_Tax_Calculations'
        verbose_name = _('Tax Calculation')
        verbose_name_plural = _('Tax Calculations')
        ordering = ['-calculation_year', '-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['calculation_year']),
            models.Index(fields=['calculation_period_start', 'calculation_period_end']),
        ]

    def __str__(self):
        return f"Tax Calculation {self.calculation_year} - {self.user.username}"

    @property
    def net_income(self):
        """Calculate net income (total_income - total_deductible_expenses)"""
        return self.total_income - self.total_deductible_expenses

    @property
    def total_deductions(self):
        """Calculate total deductions"""
        return self.basic_deduction + self.blue_form_deduction + self.other_deductions

    @property
    def taxable_income(self):
        """Calculate taxable income"""
        return max(self.net_income - self.total_deductions, Decimal('0'))

    @property
    def total_tax(self):
        """Calculate total tax amount"""
        return self.income_tax + self.resident_tax + self.business_tax


class FileUpload(models.Model):
    """
    File upload tracking table
    Maps to T_Dat_File_Uploads table in PostgreSQL
    """
    UPLOAD_TYPES = [
        ('income_receipt', _('Income Receipt')),
        ('expense_receipt', _('Expense Receipt')),
        ('document', _('Document')),
        ('tax_document', _('Tax Document')),
        ('other', _('Other')),
    ]

    OCR_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='upload_id')
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='file_uploads',
        db_column='user_id'
    )
    original_filename = models.CharField(_('original filename'), max_length=255)
    stored_filename = models.CharField(_('stored filename'), max_length=255)
    file_path = models.CharField(_('file path'), max_length=500)
    file_size = models.BigIntegerField(_('file size'))
    file_type = models.CharField(_('file type'), max_length=100)
    mime_type = models.CharField(_('MIME type'), max_length=100, blank=True)
    upload_type = models.CharField(
        _('upload type'),
        max_length=50,
        choices=UPLOAD_TYPES,
        default='document'
    )
    related_record_id = models.UUIDField(
        _('related record ID'),
        null=True,
        blank=True,
        help_text=_('Can reference income_id, expense_id, etc.')
    )
    related_table = models.CharField(
        _('related table'),
        max_length=100,
        blank=True,
        help_text=_('Table name of related record')
    )
    ocr_status = models.CharField(
        _('OCR status'),
        max_length=20,
        choices=OCR_STATUS_CHOICES,
        default='pending'
    )
    ocr_result = models.JSONField(_('OCR result'), default=dict, blank=True)
    is_processed = models.BooleanField(_('is processed'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_file_uploads'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_file_uploads'
    )

    class Meta:
        db_table = 'T_Dat_File_Uploads'
        verbose_name = _('File Upload')
        verbose_name_plural = _('File Uploads')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['upload_type']),
            models.Index(fields=['related_table', 'related_record_id']),
            models.Index(fields=['ocr_status']),
        ]

    def __str__(self):
        return self.original_filename