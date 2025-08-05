-- Personal Financial Management System - Business Tables
-- PostgreSQL 14+ Business Data Tables Creation Script

-- Connect to the database
\c financial_system;

-- ============================================================================
-- Master Data Tables (Categories)
-- ============================================================================

-- T_Master_Income_Categories: Income category master table
CREATE TABLE T_Master_Income_Categories (
    category_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_code VARCHAR(20) UNIQUE NOT NULL,
    category_name VARCHAR(100) NOT NULL,
    category_name_en VARCHAR(100),
    description TEXT,
    tax_deductible BOOLEAN NOT NULL DEFAULT FALSE,
    is_business_income BOOLEAN NOT NULL DEFAULT TRUE,
    sort_order INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES T_User(user_id),
    updated_by UUID REFERENCES T_User(user_id)
);

-- T_Master_Expense_Categories: Expense category master table
CREATE TABLE T_Master_Expense_Categories (
    category_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_code VARCHAR(20) UNIQUE NOT NULL,
    category_name VARCHAR(100) NOT NULL,
    category_name_en VARCHAR(100),
    description TEXT,
    tax_deductible BOOLEAN NOT NULL DEFAULT TRUE,
    is_business_expense BOOLEAN NOT NULL DEFAULT TRUE,
    depreciation_years INTEGER, -- For assets that need depreciation
    sort_order INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES T_User(user_id),
    updated_by UUID REFERENCES T_User(user_id)
);

-- ============================================================================
-- Business Data Tables
-- ============================================================================

-- T_Dat_Incomes: Income data table
CREATE TABLE T_Dat_Incomes (
    income_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES T_User(user_id) ON DELETE CASCADE,
    category_id UUID NOT NULL REFERENCES T_Master_Income_Categories(category_id),
    income_date DATE NOT NULL,
    description TEXT NOT NULL,
    client_name VARCHAR(200),
    client_address TEXT,
    invoice_number VARCHAR(100),
    amount DECIMAL(15,2) NOT NULL CHECK (amount >= 0),
    tax_amount DECIMAL(15,2) DEFAULT 0 CHECK (tax_amount >= 0),
    net_amount DECIMAL(15,2) GENERATED ALWAYS AS (amount - tax_amount) STORED,
    currency VARCHAR(3) NOT NULL DEFAULT 'JPY',
    payment_method VARCHAR(50), -- 現金, 銀行振込, クレジットカード, etc.
    payment_date DATE,
    is_paid BOOLEAN NOT NULL DEFAULT FALSE,
    receipt_file_path VARCHAR(500),
    notes TEXT,
    ocr_processed BOOLEAN NOT NULL DEFAULT FALSE,
    ocr_confidence DECIMAL(5,2),
    ocr_data JSONB,
    tags VARCHAR(500), -- Comma-separated tags
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES T_User(user_id),
    updated_by UUID REFERENCES T_User(user_id)
);

-- T_Dat_Expenses: Expense data table
CREATE TABLE T_Dat_Expenses (
    expense_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES T_User(user_id) ON DELETE CASCADE,
    category_id UUID NOT NULL REFERENCES T_Master_Expense_Categories(category_id),
    expense_date DATE NOT NULL,
    description TEXT NOT NULL,
    vendor_name VARCHAR(200),
    vendor_address TEXT,
    receipt_number VARCHAR(100),
    amount DECIMAL(15,2) NOT NULL CHECK (amount >= 0),
    tax_amount DECIMAL(15,2) DEFAULT 0 CHECK (tax_amount >= 0),
    net_amount DECIMAL(15,2) GENERATED ALWAYS AS (amount - tax_amount) STORED,
    currency VARCHAR(3) NOT NULL DEFAULT 'JPY',
    payment_method VARCHAR(50), -- 現金, 銀行振込, クレジットカード, etc.
    payment_date DATE,
    is_paid BOOLEAN NOT NULL DEFAULT FALSE,
    receipt_file_path VARCHAR(500),
    business_use_percentage DECIMAL(5,2) DEFAULT 100.00 CHECK (business_use_percentage >= 0 AND business_use_percentage <= 100),
    deductible_amount DECIMAL(15,2) GENERATED ALWAYS AS (amount * business_use_percentage / 100) STORED,
    notes TEXT,
    ocr_processed BOOLEAN NOT NULL DEFAULT FALSE,
    ocr_confidence DECIMAL(5,2),
    ocr_data JSONB,
    tags VARCHAR(500), -- Comma-separated tags
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES T_User(user_id),
    updated_by UUID REFERENCES T_User(user_id)
);

-- T_Dat_Assets: Asset management table (for depreciation)
CREATE TABLE T_Dat_Assets (
    asset_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES T_User(user_id) ON DELETE CASCADE,
    expense_id UUID REFERENCES T_Dat_Expenses(expense_id), -- Link to original purchase
    asset_name VARCHAR(200) NOT NULL,
    asset_category VARCHAR(100),
    purchase_date DATE NOT NULL,
    purchase_amount DECIMAL(15,2) NOT NULL CHECK (purchase_amount >= 0),
    depreciation_method VARCHAR(50) NOT NULL DEFAULT 'straight_line', -- straight_line, declining_balance
    useful_life_years INTEGER NOT NULL CHECK (useful_life_years > 0),
    salvage_value DECIMAL(15,2) DEFAULT 0 CHECK (salvage_value >= 0),
    annual_depreciation DECIMAL(15,2) GENERATED ALWAYS AS (
        CASE 
            WHEN depreciation_method = 'straight_line' THEN (purchase_amount - salvage_value) / useful_life_years
            ELSE purchase_amount * 0.2 -- Simplified declining balance
        END
    ) STORED,
    accumulated_depreciation DECIMAL(15,2) DEFAULT 0,
    book_value DECIMAL(15,2) GENERATED ALWAYS AS (purchase_amount - accumulated_depreciation) STORED,
    disposal_date DATE,
    disposal_amount DECIMAL(15,2),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES T_User(user_id),
    updated_by UUID REFERENCES T_User(user_id)
);

-- T_Dat_Tax_Calculations: Tax calculation results table
CREATE TABLE T_Dat_Tax_Calculations (
    calculation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES T_User(user_id) ON DELETE CASCADE,
    calculation_year INTEGER NOT NULL,
    calculation_period_start DATE NOT NULL,
    calculation_period_end DATE NOT NULL,
    total_income DECIMAL(15,2) NOT NULL DEFAULT 0,
    total_expenses DECIMAL(15,2) NOT NULL DEFAULT 0,
    total_deductible_expenses DECIMAL(15,2) NOT NULL DEFAULT 0,
    net_income DECIMAL(15,2) GENERATED ALWAYS AS (total_income - total_deductible_expenses) STORED,
    basic_deduction DECIMAL(15,2) DEFAULT 480000, -- 基礎控除
    blue_form_deduction DECIMAL(15,2) DEFAULT 0, -- 青色申告特別控除
    other_deductions DECIMAL(15,2) DEFAULT 0,
    total_deductions DECIMAL(15,2) GENERATED ALWAYS AS (basic_deduction + blue_form_deduction + other_deductions) STORED,
    taxable_income DECIMAL(15,2) GENERATED ALWAYS AS (GREATEST(net_income - total_deductions, 0)) STORED,
    income_tax DECIMAL(15,2) DEFAULT 0,
    resident_tax DECIMAL(15,2) DEFAULT 0,
    business_tax DECIMAL(15,2) DEFAULT 0,
    total_tax DECIMAL(15,2) GENERATED ALWAYS AS (income_tax + resident_tax + business_tax) STORED,
    calculation_notes TEXT,
    is_final BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES T_User(user_id),
    updated_by UUID REFERENCES T_User(user_id)
);

-- T_Dat_File_Uploads: File upload tracking table
CREATE TABLE T_Dat_File_Uploads (
    upload_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES T_User(user_id) ON DELETE CASCADE,
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    file_type VARCHAR(100) NOT NULL,
    mime_type VARCHAR(100),
    upload_type VARCHAR(50) NOT NULL, -- 'income_receipt', 'expense_receipt', 'document', etc.
    related_record_id UUID, -- Can reference income_id, expense_id, etc.
    related_table VARCHAR(100),
    ocr_status VARCHAR(20) DEFAULT 'pending', -- pending, processing, completed, failed
    ocr_result JSONB,
    is_processed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES T_User(user_id),
    updated_by UUID REFERENCES T_User(user_id)
);

-- ============================================================================
-- Create Indexes for Business Tables
-- ============================================================================

-- Income table indexes
CREATE INDEX idx_t_dat_incomes_user_id ON T_Dat_Incomes(user_id);
CREATE INDEX idx_t_dat_incomes_category_id ON T_Dat_Incomes(category_id);
CREATE INDEX idx_t_dat_incomes_income_date ON T_Dat_Incomes(income_date);
CREATE INDEX idx_t_dat_incomes_amount ON T_Dat_Incomes(amount);
CREATE INDEX idx_t_dat_incomes_is_paid ON T_Dat_Incomes(is_paid);
CREATE INDEX idx_t_dat_incomes_created_at ON T_Dat_Incomes(created_at);
CREATE INDEX idx_t_dat_incomes_user_date ON T_Dat_Incomes(user_id, income_date);

-- Expense table indexes
CREATE INDEX idx_t_dat_expenses_user_id ON T_Dat_Expenses(user_id);
CREATE INDEX idx_t_dat_expenses_category_id ON T_Dat_Expenses(category_id);
CREATE INDEX idx_t_dat_expenses_expense_date ON T_Dat_Expenses(expense_date);
CREATE INDEX idx_t_dat_expenses_amount ON T_Dat_Expenses(amount);
CREATE INDEX idx_t_dat_expenses_is_paid ON T_Dat_Expenses(is_paid);
CREATE INDEX idx_t_dat_expenses_created_at ON T_Dat_Expenses(created_at);
CREATE INDEX idx_t_dat_expenses_user_date ON T_Dat_Expenses(user_id, expense_date);

-- Asset table indexes
CREATE INDEX idx_t_dat_assets_user_id ON T_Dat_Assets(user_id);
CREATE INDEX idx_t_dat_assets_purchase_date ON T_Dat_Assets(purchase_date);
CREATE INDEX idx_t_dat_assets_is_active ON T_Dat_Assets(is_active);

-- Tax calculation indexes
CREATE INDEX idx_t_dat_tax_calculations_user_id ON T_Dat_Tax_Calculations(user_id);
CREATE INDEX idx_t_dat_tax_calculations_year ON T_Dat_Tax_Calculations(calculation_year);
CREATE INDEX idx_t_dat_tax_calculations_period ON T_Dat_Tax_Calculations(calculation_period_start, calculation_period_end);

-- File upload indexes
CREATE INDEX idx_t_dat_file_uploads_user_id ON T_Dat_File_Uploads(user_id);
CREATE INDEX idx_t_dat_file_uploads_type ON T_Dat_File_Uploads(upload_type);
CREATE INDEX idx_t_dat_file_uploads_related ON T_Dat_File_Uploads(related_table, related_record_id);
CREATE INDEX idx_t_dat_file_uploads_ocr_status ON T_Dat_File_Uploads(ocr_status);

-- Category indexes
CREATE INDEX idx_t_master_income_categories_active ON T_Master_Income_Categories(is_active);
CREATE INDEX idx_t_master_income_categories_code ON T_Master_Income_Categories(category_code);
CREATE INDEX idx_t_master_expense_categories_active ON T_Master_Expense_Categories(is_active);
CREATE INDEX idx_t_master_expense_categories_code ON T_Master_Expense_Categories(category_code);

-- ============================================================================
-- Apply timestamp update triggers to business tables
-- ============================================================================

CREATE TRIGGER update_t_master_income_categories_updated_at BEFORE UPDATE ON T_Master_Income_Categories FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_t_master_expense_categories_updated_at BEFORE UPDATE ON T_Master_Expense_Categories FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_t_dat_incomes_updated_at BEFORE UPDATE ON T_Dat_Incomes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_t_dat_expenses_updated_at BEFORE UPDATE ON T_Dat_Expenses FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_t_dat_assets_updated_at BEFORE UPDATE ON T_Dat_Assets FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_t_dat_tax_calculations_updated_at BEFORE UPDATE ON T_Dat_Tax_Calculations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_t_dat_file_uploads_updated_at BEFORE UPDATE ON T_Dat_File_Uploads FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Create Views for Common Queries
-- ============================================================================

-- View for income summary by category
CREATE VIEW V_Income_Summary_By_Category AS
SELECT 
    ic.category_name,
    ic.category_code,
    COUNT(i.income_id) as record_count,
    SUM(i.amount) as total_amount,
    SUM(i.tax_amount) as total_tax,
    SUM(i.net_amount) as total_net_amount,
    AVG(i.amount) as average_amount
FROM T_Master_Income_Categories ic
LEFT JOIN T_Dat_Incomes i ON ic.category_id = i.category_id
WHERE ic.is_active = TRUE
GROUP BY ic.category_id, ic.category_name, ic.category_code
ORDER BY ic.sort_order, ic.category_name;

-- View for expense summary by category
CREATE VIEW V_Expense_Summary_By_Category AS
SELECT 
    ec.category_name,
    ec.category_code,
    COUNT(e.expense_id) as record_count,
    SUM(e.amount) as total_amount,
    SUM(e.tax_amount) as total_tax,
    SUM(e.net_amount) as total_net_amount,
    SUM(e.deductible_amount) as total_deductible_amount,
    AVG(e.amount) as average_amount
FROM T_Master_Expense_Categories ec
LEFT JOIN T_Dat_Expenses e ON ec.category_id = e.category_id
WHERE ec.is_active = TRUE
GROUP BY ec.category_id, ec.category_name, ec.category_code
ORDER BY ec.sort_order, ec.category_name;

-- View for monthly financial summary
CREATE VIEW V_Monthly_Financial_Summary AS
SELECT 
    user_id,
    DATE_TRUNC('month', income_date) as month,
    'income' as type,
    SUM(amount) as total_amount,
    SUM(net_amount) as total_net_amount,
    COUNT(*) as record_count
FROM T_Dat_Incomes
GROUP BY user_id, DATE_TRUNC('month', income_date)
UNION ALL
SELECT 
    user_id,
    DATE_TRUNC('month', expense_date) as month,
    'expense' as type,
    SUM(amount) as total_amount,
    SUM(deductible_amount) as total_net_amount,
    COUNT(*) as record_count
FROM T_Dat_Expenses
GROUP BY user_id, DATE_TRUNC('month', expense_date)
ORDER BY month DESC, type;

-- ============================================================================
-- Grant permissions on business tables
-- ============================================================================

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO postgres;

COMMENT ON TABLE T_Master_Income_Categories IS 'Master table for income categories';
COMMENT ON TABLE T_Master_Expense_Categories IS 'Master table for expense categories';
COMMENT ON TABLE T_Dat_Incomes IS 'Income transaction records';
COMMENT ON TABLE T_Dat_Expenses IS 'Expense transaction records';
COMMENT ON TABLE T_Dat_Assets IS 'Asset management for depreciation calculations';
COMMENT ON TABLE T_Dat_Tax_Calculations IS 'Tax calculation results';
COMMENT ON TABLE T_Dat_File_Uploads IS 'File upload tracking and OCR processing';