-- Business Data Tables for Personal Financial Management System
-- SQL Server 2019 Compatible

USE FinancialManagement;
GO

-- Master Tables for Categories
-- T_Master_Income_Categories: Income category master table
CREATE TABLE T_Master_Income_Categories (
    category_id INT IDENTITY(1,1) PRIMARY KEY,
    category_code NVARCHAR(20) NOT NULL UNIQUE,
    category_name NVARCHAR(100) NOT NULL,
    category_name_en NVARCHAR(100) NULL,
    description NVARCHAR(MAX) NULL,
    tax_category NVARCHAR(50) NULL,
    is_business_income BIT NOT NULL DEFAULT 1,
    is_active BIT NOT NULL DEFAULT 1,
    sort_order INT NOT NULL DEFAULT 0,
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    
    INDEX IX_T_Master_Income_Categories_code (category_code),
    INDEX IX_T_Master_Income_Categories_active_sort (is_active, sort_order)
);
GO

-- T_Master_Expense_Categories: Expense category master table
CREATE TABLE T_Master_Expense_Categories (
    category_id INT IDENTITY(1,1) PRIMARY KEY,
    category_code NVARCHAR(20) NOT NULL UNIQUE,
    category_name NVARCHAR(100) NOT NULL,
    category_name_en NVARCHAR(100) NULL,
    description NVARCHAR(MAX) NULL,
    tax_deductible BIT NOT NULL DEFAULT 1,
    deduction_rate DECIMAL(5,2) NOT NULL DEFAULT 100.00 CHECK (deduction_rate BETWEEN 0 AND 100),
    requires_receipt BIT NOT NULL DEFAULT 1,
    is_active BIT NOT NULL DEFAULT 1,
    sort_order INT NOT NULL DEFAULT 0,
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    
    INDEX IX_T_Master_Expense_Categories_code (category_code),
    INDEX IX_T_Master_Expense_Categories_active_sort (is_active, sort_order)
);
GO

-- T_Dat_Incomes: Income data table
CREATE TABLE T_Dat_Incomes (
    income_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    category_id INT NOT NULL,
    
    -- Basic income information
    income_date DATE NOT NULL,
    amount DECIMAL(15,2) NOT NULL CHECK (amount >= 0),
    tax_amount DECIMAL(15,2) NOT NULL DEFAULT 0.00 CHECK (tax_amount >= 0),
    net_amount DECIMAL(15,2) NOT NULL CHECK (net_amount >= 0),
    
    -- Description and details
    description NVARCHAR(500) NOT NULL,
    client_name NVARCHAR(200) NULL,
    invoice_number NVARCHAR(100) NULL,
    payment_method NVARCHAR(50) NULL,
    
    -- Receipt and documentation
    receipt_number NVARCHAR(100) NULL,
    has_receipt BIT NOT NULL DEFAULT 0,
    receipt_file_path NVARCHAR(500) NULL,
    
    -- OCR and processing information
    ocr_processed BIT NOT NULL DEFAULT 0,
    ocr_confidence DECIMAL(5,2) NULL CHECK (ocr_confidence BETWEEN 0 AND 100),
    ocr_data NVARCHAR(MAX) NULL,
    
    -- Status and workflow
    status NVARCHAR(20) NOT NULL DEFAULT 'DRAFT' CHECK (status IN ('DRAFT', 'CONFIRMED', 'PROCESSED')),
    is_recurring BIT NOT NULL DEFAULT 0,
    recurring_frequency NVARCHAR(20) NULL CHECK (recurring_frequency IN ('MONTHLY', 'QUARTERLY', 'YEARLY') OR recurring_frequency IS NULL),
    
    -- Audit fields
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    created_by INT NOT NULL,
    updated_by INT NOT NULL,
    
    FOREIGN KEY (user_id) REFERENCES T_User(user_id),
    FOREIGN KEY (category_id) REFERENCES T_Master_Income_Categories(category_id),
    FOREIGN KEY (created_by) REFERENCES T_User(user_id),
    FOREIGN KEY (updated_by) REFERENCES T_User(user_id),
    
    INDEX IX_T_Dat_Incomes_user_date (user_id, income_date),
    INDEX IX_T_Dat_Incomes_category (category_id),
    INDEX IX_T_Dat_Incomes_status (status),
    INDEX IX_T_Dat_Incomes_date_amount (income_date, amount)
);
GO

-- T_Dat_Expenses: Expense data table
CREATE TABLE T_Dat_Expenses (
    expense_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    category_id INT NOT NULL,
    
    -- Basic expense information
    expense_date DATE NOT NULL,
    amount DECIMAL(15,2) NOT NULL CHECK (amount >= 0),
    tax_amount DECIMAL(15,2) NOT NULL DEFAULT 0.00 CHECK (tax_amount >= 0),
    net_amount DECIMAL(15,2) NOT NULL CHECK (net_amount >= 0),
    
    -- Description and details
    description NVARCHAR(500) NOT NULL,
    vendor_name NVARCHAR(200) NULL,
    vendor_address NVARCHAR(500) NULL,
    payment_method NVARCHAR(50) NULL,
    
    -- Receipt and documentation
    receipt_number NVARCHAR(100) NULL,
    has_receipt BIT NOT NULL DEFAULT 0,
    receipt_file_path NVARCHAR(500) NULL,
    
    -- Business purpose and deduction
    business_purpose NVARCHAR(MAX) NULL,
    deduction_percentage DECIMAL(5,2) NOT NULL DEFAULT 100.00 CHECK (deduction_percentage BETWEEN 0 AND 100),
    deductible_amount AS (amount * deduction_percentage / 100.00) PERSISTED,
    
    -- OCR and processing information
    ocr_processed BIT NOT NULL DEFAULT 0,
    ocr_confidence DECIMAL(5,2) NULL CHECK (ocr_confidence BETWEEN 0 AND 100),
    ocr_data NVARCHAR(MAX) NULL,
    
    -- Status and workflow
    status NVARCHAR(20) NOT NULL DEFAULT 'DRAFT' CHECK (status IN ('DRAFT', 'CONFIRMED', 'PROCESSED')),
    is_recurring BIT NOT NULL DEFAULT 0,
    recurring_frequency NVARCHAR(20) NULL CHECK (recurring_frequency IN ('MONTHLY', 'QUARTERLY', 'YEARLY') OR recurring_frequency IS NULL),
    
    -- Location information (for travel expenses, etc.)
    location NVARCHAR(200) NULL,
    travel_purpose NVARCHAR(500) NULL,
    
    -- Audit fields
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    created_by INT NOT NULL,
    updated_by INT NOT NULL,
    
    FOREIGN KEY (user_id) REFERENCES T_User(user_id),
    FOREIGN KEY (category_id) REFERENCES T_Master_Expense_Categories(category_id),
    FOREIGN KEY (created_by) REFERENCES T_User(user_id),
    FOREIGN KEY (updated_by) REFERENCES T_User(user_id),
    
    INDEX IX_T_Dat_Expenses_user_date (user_id, expense_date),
    INDEX IX_T_Dat_Expenses_category (category_id),
    INDEX IX_T_Dat_Expenses_status (status),
    INDEX IX_T_Dat_Expenses_date_amount (expense_date, amount),
    INDEX IX_T_Dat_Expenses_deductible (deductible_amount)
);
GO

-- T_Financial_Summary: Pre-calculated financial summary for reporting
CREATE TABLE T_Financial_Summary (
    summary_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    
    -- Period information
    period_type NVARCHAR(20) NOT NULL CHECK (period_type IN ('MONTHLY', 'QUARTERLY', 'YEARLY')),
    period_year INT NOT NULL,
    period_month INT NULL CHECK (period_month BETWEEN 1 AND 12),
    period_quarter INT NULL CHECK (period_quarter BETWEEN 1 AND 4),
    
    -- Income summary
    total_income DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    total_income_tax DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    net_income DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    
    -- Expense summary
    total_expenses DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    total_deductible_expenses DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    total_expense_tax DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    
    -- Profit calculation
    gross_profit AS (total_income - total_expenses) PERSISTED,
    net_profit AS (net_income - total_deductible_expenses) PERSISTED,
    
    -- Tax calculations
    estimated_income_tax DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    estimated_consumption_tax DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    
    -- Status
    is_finalized BIT NOT NULL DEFAULT 0,
    calculation_date DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    
    FOREIGN KEY (user_id) REFERENCES T_User(user_id),
    
    INDEX IX_T_Financial_Summary_user_period (user_id, period_type, period_year, period_month),
    INDEX IX_T_Financial_Summary_calculation_date (calculation_date),
    
    -- Ensure unique summary per user per period
    CONSTRAINT UQ_T_Financial_Summary_user_period UNIQUE (user_id, period_type, period_year, period_month, period_quarter)
);
GO

-- Additional System Tables
-- T_System_Config: System configuration table
CREATE TABLE T_System_Config (
    config_id INT IDENTITY(1,1) PRIMARY KEY,
    config_key NVARCHAR(100) NOT NULL UNIQUE,
    config_value NVARCHAR(MAX) NOT NULL,
    config_type NVARCHAR(20) NOT NULL DEFAULT 'STRING' CHECK (config_type IN ('STRING', 'INTEGER', 'BOOLEAN', 'JSON')),
    description NVARCHAR(MAX) NULL,
    is_system BIT NOT NULL DEFAULT 0,
    is_encrypted BIT NOT NULL DEFAULT 0,
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    updated_by INT NULL,
    
    FOREIGN KEY (updated_by) REFERENCES T_User(user_id),
    INDEX IX_T_System_Config_key (config_key)
);
GO

-- T_File_Upload: File upload tracking table
CREATE TABLE T_File_Upload (
    file_id INT IDENTITY(1,1) PRIMARY KEY,
    original_filename NVARCHAR(255) NOT NULL,
    stored_filename NVARCHAR(255) NOT NULL,
    file_path NVARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL CHECK (file_size > 0),
    file_type NVARCHAR(50) NOT NULL,
    file_extension NVARCHAR(10) NOT NULL,
    upload_purpose NVARCHAR(50) NOT NULL CHECK (upload_purpose IN ('INCOME_IMPORT', 'EXPENSE_IMPORT', 'OCR_PROCESSING', 'RECEIPT')),
    processing_status NVARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK (processing_status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')),
    processing_result NVARCHAR(MAX) NULL,
    error_message NVARCHAR(MAX) NULL,
    uploaded_by INT NOT NULL,
    uploaded_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    processed_at DATETIME2 NULL,
    is_deleted BIT NOT NULL DEFAULT 0,
    deleted_at DATETIME2 NULL,
    
    FOREIGN KEY (uploaded_by) REFERENCES T_User(user_id),
    INDEX IX_T_File_Upload_uploaded_by_date (uploaded_by, uploaded_at),
    INDEX IX_T_File_Upload_status (processing_status),
    INDEX IX_T_File_Upload_purpose (upload_purpose)
);
GO

-- T_System_Health: System health monitoring table
CREATE TABLE T_System_Health (
    health_id INT IDENTITY(1,1) PRIMARY KEY,
    component NVARCHAR(50) NOT NULL CHECK (component IN ('DATABASE', 'API', 'OCR_SERVICE', 'FILE_SYSTEM')),
    status NVARCHAR(20) NOT NULL CHECK (status IN ('HEALTHY', 'WARNING', 'CRITICAL', 'DOWN')),
    response_time_ms INT NULL CHECK (response_time_ms >= 0),
    error_message NVARCHAR(MAX) NULL,
    additional_info NVARCHAR(MAX) NULL,
    checked_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    
    INDEX IX_T_System_Health_component_time (component, checked_at),
    INDEX IX_T_System_Health_status (status)
);
GO

PRINT 'Business tables created successfully!';