"""
Business data models for income and expense management
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from decimal import Decimal
from app.core.database import Base

class IncomeCategory(Base):
    """
    T_Master_Income_Categories: Income category master table
    """
    __tablename__ = "T_Master_Income_Categories"
    
    category_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category_code = Column(String(20), unique=True, nullable=False, index=True)
    category_name = Column(String(100), nullable=False)
    category_name_en = Column(String(100))  # English name
    description = Column(Text)
    tax_category = Column(String(50))  # For Japanese tax classification
    is_business_income = Column(Boolean, default=True)  # Business vs personal income
    is_active = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    incomes = relationship("Income", back_populates="category")

class ExpenseCategory(Base):
    """
    T_Master_Expense_Categories: Expense category master table
    """
    __tablename__ = "T_Master_Expense_Categories"
    
    category_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category_code = Column(String(20), unique=True, nullable=False, index=True)
    category_name = Column(String(100), nullable=False)
    category_name_en = Column(String(100))  # English name
    description = Column(Text)
    tax_deductible = Column(Boolean, default=True)  # Whether this expense is tax deductible
    deduction_rate = Column(Numeric(5, 2), default=100.00)  # Percentage deductible (0-100)
    requires_receipt = Column(Boolean, default=True)  # Whether receipt is required
    is_active = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    expenses = relationship("Expense", back_populates="category")

class Income(Base):
    """
    T_Dat_Incomes: Income data table
    """
    __tablename__ = "T_Dat_Incomes"
    
    income_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("T_User.user_id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("T_Master_Income_Categories.category_id"), nullable=False)
    
    # Basic income information
    income_date = Column(Date, nullable=False, index=True)
    amount = Column(Numeric(15, 2), nullable=False)  # Income amount
    tax_amount = Column(Numeric(15, 2), default=0.00)  # Tax withheld
    net_amount = Column(Numeric(15, 2), nullable=False)  # Net amount received
    
    # Description and details
    description = Column(String(500), nullable=False)
    client_name = Column(String(200))  # Client or payer name
    invoice_number = Column(String(100))  # Invoice reference
    payment_method = Column(String(50))  # Cash, bank transfer, etc.
    
    # Receipt and documentation
    receipt_number = Column(String(100))
    has_receipt = Column(Boolean, default=False)
    receipt_file_path = Column(String(500))
    
    # OCR and processing information
    ocr_processed = Column(Boolean, default=False)
    ocr_confidence = Column(Numeric(5, 2))  # OCR confidence score (0-100)
    ocr_data = Column(Text)  # Raw OCR extracted data
    
    # Status and workflow
    status = Column(String(20), default="DRAFT")  # DRAFT, CONFIRMED, PROCESSED
    is_recurring = Column(Boolean, default=False)
    recurring_frequency = Column(String(20))  # MONTHLY, QUARTERLY, YEARLY
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey("T_User.user_id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("T_User.user_id"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="incomes", foreign_keys=[user_id])
    category = relationship("IncomeCategory", back_populates="incomes")

class Expense(Base):
    """
    T_Dat_Expenses: Expense data table
    """
    __tablename__ = "T_Dat_Expenses"
    
    expense_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("T_User.user_id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("T_Master_Expense_Categories.category_id"), nullable=False)
    
    # Basic expense information
    expense_date = Column(Date, nullable=False, index=True)
    amount = Column(Numeric(15, 2), nullable=False)  # Expense amount
    tax_amount = Column(Numeric(15, 2), default=0.00)  # Consumption tax
    net_amount = Column(Numeric(15, 2), nullable=False)  # Amount excluding tax
    
    # Description and details
    description = Column(String(500), nullable=False)
    vendor_name = Column(String(200))  # Vendor or supplier name
    vendor_address = Column(String(500))  # Vendor address
    payment_method = Column(String(50))  # Cash, credit card, bank transfer, etc.
    
    # Receipt and documentation
    receipt_number = Column(String(100))
    has_receipt = Column(Boolean, default=False)
    receipt_file_path = Column(String(500))
    
    # Business purpose and deduction
    business_purpose = Column(Text)  # Business justification for expense
    deduction_percentage = Column(Numeric(5, 2), default=100.00)  # Percentage for business use
    deductible_amount = Column(Numeric(15, 2))  # Calculated deductible amount
    
    # OCR and processing information
    ocr_processed = Column(Boolean, default=False)
    ocr_confidence = Column(Numeric(5, 2))  # OCR confidence score (0-100)
    ocr_data = Column(Text)  # Raw OCR extracted data
    
    # Status and workflow
    status = Column(String(20), default="DRAFT")  # DRAFT, CONFIRMED, PROCESSED
    is_recurring = Column(Boolean, default=False)
    recurring_frequency = Column(String(20))  # MONTHLY, QUARTERLY, YEARLY
    
    # Location information (for travel expenses, etc.)
    location = Column(String(200))
    travel_purpose = Column(String(500))
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey("T_User.user_id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("T_User.user_id"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="expenses", foreign_keys=[user_id])
    category = relationship("ExpenseCategory", back_populates="expenses")

class FinancialSummary(Base):
    """
    T_Financial_Summary: Pre-calculated financial summary for reporting
    """
    __tablename__ = "T_Financial_Summary"
    
    summary_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("T_User.user_id"), nullable=False, index=True)
    
    # Period information
    period_type = Column(String(20), nullable=False)  # MONTHLY, QUARTERLY, YEARLY
    period_year = Column(Integer, nullable=False, index=True)
    period_month = Column(Integer, nullable=True, index=True)  # For monthly summaries
    period_quarter = Column(Integer, nullable=True)  # For quarterly summaries
    
    # Income summary
    total_income = Column(Numeric(15, 2), default=0.00)
    total_income_tax = Column(Numeric(15, 2), default=0.00)
    net_income = Column(Numeric(15, 2), default=0.00)
    
    # Expense summary
    total_expenses = Column(Numeric(15, 2), default=0.00)
    total_deductible_expenses = Column(Numeric(15, 2), default=0.00)
    total_expense_tax = Column(Numeric(15, 2), default=0.00)
    
    # Profit calculation
    gross_profit = Column(Numeric(15, 2), default=0.00)  # Income - Expenses
    net_profit = Column(Numeric(15, 2), default=0.00)    # After tax adjustments
    
    # Tax calculations
    estimated_income_tax = Column(Numeric(15, 2), default=0.00)
    estimated_consumption_tax = Column(Numeric(15, 2), default=0.00)
    
    # Status
    is_finalized = Column(Boolean, default=False)
    calculation_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)