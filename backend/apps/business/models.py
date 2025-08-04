"""
Business models for Financial System
Handles income and expense management for Japanese individual business owners
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
from apps.users.models import User


class IncomeCategory(models.Model):
    """
    Income category model
    Maps to T_Master_Income_Categories table
    """
    
    CATEGORY_TYPES = [
        ('business', '事業所得'),
        ('salary', '給与所得'),
        ('pension', '年金所得'),
        ('investment', '投資所得'),
        ('rental', '不動産所得'),
        ('capital_gains', '譲渡所得'),
        ('temporary', '一時所得'),
        ('miscellaneous', '雑所得'),
        ('other', 'その他'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='カテゴリ名')
    code = models.CharField(max_length=20, unique=True, verbose_name='カテゴリコード')
    category_type = models.CharField(
        max_length=20, 
        choices=CATEGORY_TYPES, 
        default='business',
        verbose_name='所得区分'
    )
    description = models.TextField(null=True, blank=True, verbose_name='説明')
    is_active = models.BooleanField(default=True, verbose_name='有効')
    
    # Tax-related fields for Japanese tax system
    is_taxable = models.BooleanField(default=True, verbose_name='課税対象')
    tax_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        verbose_name='税率(%)'
    )
    
    # Blue tax return related
    blue_tax_deduction_eligible = models.BooleanField(default=True, verbose_name='青色申告控除対象')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='created_income_categories'
    )
    
    class Meta:
        db_table = 'T_Master_Income_Categories'
        verbose_name = 'Income Category'
        verbose_name_plural = 'Income Categories'
        ordering = ['code', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['category_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class ExpenseCategory(models.Model):
    """
    Expense category model
    Maps to T_Master_Expense_Categories table
    """
    
    CATEGORY_TYPES = [
        ('cost_of_goods', '売上原価'),
        ('personnel', '人件費'),
        ('rent', '地代家賃'),
        ('utilities', '水道光熱費'),
        ('communication', '通信費'),
        ('travel', '旅費交通費'),
        ('entertainment', '接待交際費'),
        ('supplies', '消耗品費'),
        ('advertising', '広告宣伝費'),
        ('insurance', '保険料'),
        ('repairs', '修繕費'),
        ('depreciation', '減価償却費'),
        ('taxes', '租税公課'),
        ('professional_fees', '支払手数料'),
        ('interest', '支払利息'),
        ('welfare', '福利厚生費'),
        ('training', '研修費'),
        ('miscellaneous', '雑費'),
        ('other', 'その他'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='カテゴリ名')
    code = models.CharField(max_length=20, unique=True, verbose_name='カテゴリコード')
    category_type = models.CharField(
        max_length=20, 
        choices=CATEGORY_TYPES, 
        default='miscellaneous',
        verbose_name='経費区分'
    )
    description = models.TextField(null=True, blank=True, verbose_name='説明')
    is_active = models.BooleanField(default=True, verbose_name='有効')
    
    # Tax-related fields
    is_deductible = models.BooleanField(default=True, verbose_name='控除対象')
    deduction_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('100.00'),
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        verbose_name='控除率(%)'
    )
    
    # Blue tax return related
    blue_tax_deduction_eligible = models.BooleanField(default=True, verbose_name='青色申告控除対象')
    requires_receipt = models.BooleanField(default=True, verbose_name='領収書必要')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='created_expense_categories'
    )
    
    class Meta:
        db_table = 'T_Master_Expense_Categories'
        verbose_name = 'Expense Category'
        verbose_name_plural = 'Expense Categories'
        ordering = ['code', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['category_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Income(models.Model):
    """
    Income model
    Maps to T_Dat_Incomes table
    """
    
    PAYMENT_METHODS = [
        ('cash', '現金'),
        ('bank_transfer', '銀行振込'),
        ('credit_card', 'クレジットカード'),
        ('check', '小切手'),
        ('electronic', '電子マネー'),
        ('other', 'その他'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '未確定'),
        ('confirmed', '確定'),
        ('cancelled', 'キャンセル'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incomes')
    category = models.ForeignKey(IncomeCategory, on_delete=models.PROTECT, verbose_name='カテゴリ')
    
    # Basic income information
    date = models.DateField(verbose_name='日付')
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='金額'
    )
    description = models.CharField(max_length=200, verbose_name='摘要')
    notes = models.TextField(null=True, blank=True, verbose_name='備考')
    
    # Client/Source information
    client_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='取引先名')
    client_address = models.CharField(max_length=200, null=True, blank=True, verbose_name='取引先住所')
    client_phone = models.CharField(max_length=20, null=True, blank=True, verbose_name='取引先電話')
    
    # Payment information
    payment_method = models.CharField(
        max_length=20, 
        choices=PAYMENT_METHODS, 
        default='cash',
        verbose_name='支払方法'
    )
    payment_date = models.DateField(null=True, blank=True, verbose_name='入金日')
    invoice_number = models.CharField(max_length=50, null=True, blank=True, verbose_name='請求書番号')
    
    # Tax information
    tax_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='消費税額'
    )
    tax_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('10.00'),
        verbose_name='消費税率(%)'
    )
    is_tax_inclusive = models.BooleanField(default=True, verbose_name='税込み')
    
    # Status and tracking
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name='ステータス'
    )
    
    # File attachments
    receipt_file = models.FileField(
        upload_to='receipts/incomes/%Y/%m/', 
        null=True, 
        blank=True,
        verbose_name='領収書ファイル'
    )
    
    # OCR processing
    ocr_processed = models.BooleanField(default=False, verbose_name='OCR処理済み')
    ocr_confidence = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='OCR信頼度'
    )
    ocr_data = models.JSONField(null=True, blank=True, verbose_name='OCRデータ')
    
    # Audit fields
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
        verbose_name = 'Income'
        verbose_name_plural = 'Incomes'
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['category']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_date']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.date} - {self.description} - ¥{self.amount:,}"
    
    @property
    def amount_excluding_tax(self):
        """Calculate amount excluding tax"""
        if self.is_tax_inclusive:
            return self.amount - self.tax_amount
        return self.amount
    
    @property
    def amount_including_tax(self):
        """Calculate amount including tax"""
        if self.is_tax_inclusive:
            return self.amount
        return self.amount + self.tax_amount
    
    def calculate_tax_amount(self):
        """Calculate tax amount based on tax rate"""
        if self.is_tax_inclusive:
            # Tax amount = amount * tax_rate / (100 + tax_rate)
            return self.amount * self.tax_rate / (100 + self.tax_rate)
        else:
            # Tax amount = amount * tax_rate / 100
            return self.amount * self.tax_rate / 100
    
    def save(self, *args, **kwargs):
        # Auto-calculate tax amount if not provided
        if self.tax_amount == 0 and self.tax_rate > 0:
            self.tax_amount = self.calculate_tax_amount()
        super().save(*args, **kwargs)


class Expense(models.Model):
    """
    Expense model
    Maps to T_Dat_Expenses table
    """
    
    PAYMENT_METHODS = [
        ('cash', '現金'),
        ('bank_transfer', '銀行振込'),
        ('credit_card', 'クレジットカード'),
        ('debit_card', 'デビットカード'),
        ('check', '小切手'),
        ('electronic', '電子マネー'),
        ('other', 'その他'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '未確定'),
        ('confirmed', '確定'),
        ('cancelled', 'キャンセル'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT, verbose_name='カテゴリ')
    
    # Basic expense information
    date = models.DateField(verbose_name='日付')
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='金額'
    )
    description = models.CharField(max_length=200, verbose_name='摘要')
    notes = models.TextField(null=True, blank=True, verbose_name='備考')
    
    # Vendor/Supplier information
    vendor_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='支払先名')
    vendor_address = models.CharField(max_length=200, null=True, blank=True, verbose_name='支払先住所')
    vendor_phone = models.CharField(max_length=20, null=True, blank=True, verbose_name='支払先電話')
    
    # Payment information
    payment_method = models.CharField(
        max_length=20, 
        choices=PAYMENT_METHODS, 
        default='cash',
        verbose_name='支払方法'
    )
    payment_date = models.DateField(null=True, blank=True, verbose_name='支払日')
    receipt_number = models.CharField(max_length=50, null=True, blank=True, verbose_name='領収書番号')
    
    # Tax information
    tax_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='消費税額'
    )
    tax_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('10.00'),
        verbose_name='消費税率(%)'
    )
    is_tax_inclusive = models.BooleanField(default=True, verbose_name='税込み')
    
    # Business use percentage (for mixed personal/business expenses)
    business_use_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('100.00'),
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        verbose_name='事業使用割合(%)'
    )
    
    # Status and tracking
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name='ステータス'
    )
    
    # File attachments
    receipt_file = models.FileField(
        upload_to='receipts/expenses/%Y/%m/', 
        null=True, 
        blank=True,
        verbose_name='領収書ファイル'
    )
    
    # OCR processing
    ocr_processed = models.BooleanField(default=False, verbose_name='OCR処理済み')
    ocr_confidence = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='OCR信頼度'
    )
    ocr_data = models.JSONField(null=True, blank=True, verbose_name='OCRデータ')
    
    # Audit fields
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
        verbose_name = 'Expense'
        verbose_name_plural = 'Expenses'
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['category']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_date']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.date} - {self.description} - ¥{self.amount:,}"
    
    @property
    def amount_excluding_tax(self):
        """Calculate amount excluding tax"""
        if self.is_tax_inclusive:
            return self.amount - self.tax_amount
        return self.amount
    
    @property
    def amount_including_tax(self):
        """Calculate amount including tax"""
        if self.is_tax_inclusive:
            return self.amount
        return self.amount + self.tax_amount
    
    @property
    def business_deductible_amount(self):
        """Calculate business deductible amount"""
        return self.amount * self.business_use_percentage / 100
    
    def calculate_tax_amount(self):
        """Calculate tax amount based on tax rate"""
        if self.is_tax_inclusive:
            # Tax amount = amount * tax_rate / (100 + tax_rate)
            return self.amount * self.tax_rate / (100 + self.tax_rate)
        else:
            # Tax amount = amount * tax_rate / 100
            return self.amount * self.tax_rate / 100
    
    def save(self, *args, **kwargs):
        # Auto-calculate tax amount if not provided
        if self.tax_amount == 0 and self.tax_rate > 0:
            self.tax_amount = self.calculate_tax_amount()
        super().save(*args, **kwargs)


class TaxCalculation(models.Model):
    """
    Tax calculation model for period-based calculations
    """
    
    CALCULATION_TYPES = [
        ('monthly', '月次'),
        ('quarterly', '四半期'),
        ('annual', '年次'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tax_calculations')
    calculation_type = models.CharField(max_length=20, choices=CALCULATION_TYPES, verbose_name='計算区分')
    
    # Period information
    start_date = models.DateField(verbose_name='開始日')
    end_date = models.DateField(verbose_name='終了日')
    tax_year = models.IntegerField(verbose_name='税務年度')
    
    # Income totals
    total_income = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name='総収入')
    total_income_tax = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name='収入消費税')
    
    # Expense totals
    total_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name='総支出')
    total_expense_tax = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name='支出消費税')
    
    # Net calculations
    net_income = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name='純利益')
    net_tax = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name='純消費税')
    
    # Blue tax return deduction
    blue_tax_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name='青色申告控除')
    
    # Final taxable income
    taxable_income = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name='課税所得')
    
    # Calculation metadata
    calculation_data = models.JSONField(null=True, blank=True, verbose_name='計算データ')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    calculated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='performed_calculations'
    )
    
    class Meta:
        verbose_name = 'Tax Calculation'
        verbose_name_plural = 'Tax Calculations'
        ordering = ['-tax_year', '-end_date']
        unique_together = ['user', 'calculation_type', 'start_date', 'end_date']
        indexes = [
            models.Index(fields=['user', 'tax_year']),
            models.Index(fields=['calculation_type']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.calculation_type} - {self.start_date} to {self.end_date}"