-- Initial Data and Triggers for Personal Financial Management System
-- SQL Server 2019 Compatible

USE FinancialManagement;
GO

-- Insert default income categories (Japanese tax-compliant)
INSERT INTO T_Master_Income_Categories (category_code, category_name, category_name_en, description, tax_category, is_business_income, sort_order) VALUES
('INC001', '事業所得', 'Business Income', '個人事業による収入', '事業所得', 1, 1),
('INC002', '給与所得', 'Salary Income', '給与・賞与による収入', '給与所得', 0, 2),
('INC003', '雑所得', 'Miscellaneous Income', 'その他の収入', '雑所得', 1, 3),
('INC004', '不動産所得', 'Real Estate Income', '不動産賃貸による収入', '不動産所得', 1, 4),
('INC005', '配当所得', 'Dividend Income', '株式配当による収入', '配当所得', 0, 5),
('INC006', '利子所得', 'Interest Income', '預金利子による収入', '利子所得', 0, 6),
('INC007', 'フリーランス収入', 'Freelance Income', 'フリーランス業務による収入', '事業所得', 1, 7),
('INC008', 'コンサルティング収入', 'Consulting Income', 'コンサルティング業務による収入', '事業所得', 1, 8);
GO

-- Insert default expense categories (Japanese tax-deductible expenses)
INSERT INTO T_Master_Expense_Categories (category_code, category_name, category_name_en, description, tax_deductible, deduction_rate, requires_receipt, sort_order) VALUES
('EXP001', '旅費交通費', 'Travel Expenses', '出張・交通費', 1, 100.00, 1, 1),
('EXP002', '通信費', 'Communication Expenses', '電話・インターネット費用', 1, 100.00, 1, 2),
('EXP003', '消耗品費', 'Office Supplies', '事務用品・消耗品', 1, 100.00, 1, 3),
('EXP004', '会議費', 'Meeting Expenses', '会議・打合せ費用', 1, 100.00, 1, 4),
('EXP005', '接待交際費', 'Entertainment Expenses', '接待・交際費', 1, 100.00, 1, 5),
('EXP006', '広告宣伝費', 'Advertising Expenses', '広告・宣伝費用', 1, 100.00, 1, 6),
('EXP007', '外注費', 'Outsourcing Expenses', '外部委託費用', 1, 100.00, 1, 7),
('EXP008', '地代家賃', 'Rent Expenses', '事務所賃料', 1, 100.00, 1, 8),
('EXP009', '水道光熱費', 'Utilities', '電気・ガス・水道代', 1, 50.00, 1, 9),
('EXP010', '損害保険料', 'Insurance Premiums', '事業用保険料', 1, 100.00, 1, 10),
('EXP011', '修繕費', 'Repair Expenses', '設備・備品修繕費', 1, 100.00, 1, 11),
('EXP012', '減価償却費', 'Depreciation', '固定資産減価償却', 1, 100.00, 0, 12),
('EXP013', '福利厚生費', 'Welfare Expenses', '従業員福利厚生費', 1, 100.00, 1, 13),
('EXP014', '研修費', 'Training Expenses', '研修・教育費用', 1, 100.00, 1, 14),
('EXP015', '図書費', 'Books and Materials', '書籍・資料費', 1, 100.00, 1, 15),
('EXP016', 'ソフトウェア費', 'Software Expenses', 'ソフトウェア・ライセンス費', 1, 100.00, 1, 16),
('EXP017', '支払手数料', 'Service Fees', '銀行手数料・各種手数料', 1, 100.00, 1, 17),
('EXP018', '租税公課', 'Taxes and Dues', '事業税・印紙税等', 1, 100.00, 1, 18),
('EXP019', '雑費', 'Miscellaneous Expenses', 'その他の経費', 1, 100.00, 1, 19),
('EXP020', '食費', 'Meal Expenses', '食事代（事業関連）', 1, 50.00, 1, 20);
GO

-- Insert default user roles
INSERT INTO T_User_Role (role_name, role_description) VALUES
('super_admin', 'システム全体の管理権限を持つスーパー管理者'),
('admin', '一般的な管理権限を持つ管理者'),
('user', '一般ユーザー');
GO

-- Insert default permissions
INSERT INTO T_User_Permission (permission_name, permission_description, resource, action) VALUES
-- Income permissions
('income_create', '収入データの作成', 'income', 'create'),
('income_read', '収入データの閲覧', 'income', 'read'),
('income_update', '収入データの更新', 'income', 'update'),
('income_delete', '収入データの削除', 'income', 'delete'),
('income_import', '収入データのインポート', 'income', 'import'),
('income_export', '収入データのエクスポート', 'income', 'export'),

-- Expense permissions
('expense_create', '支出データの作成', 'expense', 'create'),
('expense_read', '支出データの閲覧', 'expense', 'read'),
('expense_update', '支出データの更新', 'expense', 'update'),
('expense_delete', '支出データの削除', 'expense', 'delete'),
('expense_import', '支出データのインポート', 'expense', 'import'),
('expense_export', '支出データのエクスポート', 'expense', 'export'),

-- User management permissions
('user_create', 'ユーザーの作成', 'user', 'create'),
('user_read', 'ユーザー情報の閲覧', 'user', 'read'),
('user_update', 'ユーザー情報の更新', 'user', 'update'),
('user_delete', 'ユーザーの削除', 'user', 'delete'),

-- System permissions
('system_read', 'システム情報の閲覧', 'system', 'read'),
('system_update', 'システム設定の更新', 'system', 'update'),

-- Report permissions
('report_read', 'レポートの閲覧', 'report', 'read'),
('report_export', 'レポートのエクスポート', 'report', 'export');
GO

-- Insert default system configurations
INSERT INTO T_System_Config (config_key, config_value, config_type, description, is_system) VALUES
('system_name', 'Personal Financial Management System', 'STRING', 'システム名', 1),
('system_version', '1.0.0', 'STRING', 'システムバージョン', 1),
('max_file_size_mb', '10', 'INTEGER', 'アップロードファイルの最大サイズ（MB）', 0),
('session_timeout_minutes', '30', 'INTEGER', 'セッションタイムアウト時間（分）', 0),
('password_min_length', '8', 'INTEGER', 'パスワード最小文字数', 0),
('backup_retention_days', '30', 'INTEGER', 'バックアップ保持日数', 0),
('audit_log_retention_days', '365', 'INTEGER', '監査ログ保持日数', 0),
('ocr_confidence_threshold', '80', 'INTEGER', 'OCR信頼度閾値（%）', 0),
('default_currency', 'JPY', 'STRING', 'デフォルト通貨', 0),
('tax_year_start_month', '1', 'INTEGER', '税務年度開始月', 0);
GO

-- Create triggers for audit logging
-- Trigger for T_User table
CREATE TRIGGER TR_T_User_Audit
ON T_User
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @operation NVARCHAR(10);
    DECLARE @user_id INT = ISNULL(CAST(SESSION_CONTEXT(N'current_user_id') AS INT), 0);
    
    IF EXISTS(SELECT * FROM inserted) AND EXISTS(SELECT * FROM deleted)
        SET @operation = 'UPDATE';
    ELSE IF EXISTS(SELECT * FROM inserted)
        SET @operation = 'INSERT';
    ELSE
        SET @operation = 'DELETE';
    
    -- Insert into history table
    IF @operation = 'INSERT'
    BEGIN
        INSERT INTO T_User_History (user_id, username, email, role, is_active, operation_type, operation_user_id)
        SELECT user_id, username, email, role, is_active, @operation, @user_id
        FROM inserted;
    END
    ELSE IF @operation = 'UPDATE'
    BEGIN
        INSERT INTO T_User_History (user_id, username, email, role, is_active, operation_type, operation_user_id)
        SELECT user_id, username, email, role, is_active, @operation, @user_id
        FROM inserted;
    END
    ELSE IF @operation = 'DELETE'
    BEGIN
        INSERT INTO T_User_History (user_id, username, email, role, is_active, operation_type, operation_user_id)
        SELECT user_id, username, email, role, is_active, @operation, @user_id
        FROM deleted;
    END
END;
GO

-- Trigger for T_User_Detail table
CREATE TRIGGER TR_T_User_Detail_Audit
ON T_User_Detail
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @operation NVARCHAR(10);
    DECLARE @user_id INT = ISNULL(CAST(SESSION_CONTEXT(N'current_user_id') AS INT), 0);
    
    IF EXISTS(SELECT * FROM inserted) AND EXISTS(SELECT * FROM deleted)
        SET @operation = 'UPDATE';
    ELSE IF EXISTS(SELECT * FROM inserted)
        SET @operation = 'INSERT';
    ELSE
        SET @operation = 'DELETE';
    
    -- Insert into history table
    IF @operation = 'INSERT'
    BEGIN
        INSERT INTO T_User_Detail_History (
            detail_id, user_id, first_name, last_name, first_name_kana, last_name_kana,
            addr, room_name, sex, birth_day, is_disabled, is_widow, is_household_head,
            occupation, occupation_category, primary_income_source, phone_number,
            postal_code, prefecture, city, operation_type, operation_user_id
        )
        SELECT 
            detail_id, user_id, first_name, last_name, first_name_kana, last_name_kana,
            addr, room_name, sex, birth_day, is_disabled, is_widow, is_household_head,
            occupation, occupation_category, primary_income_source, phone_number,
            postal_code, prefecture, city, @operation, @user_id
        FROM inserted;
    END
    ELSE IF @operation = 'UPDATE'
    BEGIN
        INSERT INTO T_User_Detail_History (
            detail_id, user_id, first_name, last_name, first_name_kana, last_name_kana,
            addr, room_name, sex, birth_day, is_disabled, is_widow, is_household_head,
            occupation, occupation_category, primary_income_source, phone_number,
            postal_code, prefecture, city, operation_type, operation_user_id
        )
        SELECT 
            detail_id, user_id, first_name, last_name, first_name_kana, last_name_kana,
            addr, room_name, sex, birth_day, is_disabled, is_widow, is_household_head,
            occupation, occupation_category, primary_income_source, phone_number,
            postal_code, prefecture, city, @operation, @user_id
        FROM inserted;
    END
    ELSE IF @operation = 'DELETE'
    BEGIN
        INSERT INTO T_User_Detail_History (
            detail_id, user_id, first_name, last_name, first_name_kana, last_name_kana,
            addr, room_name, sex, birth_day, is_disabled, is_widow, is_household_head,
            occupation, occupation_category, primary_income_source, phone_number,
            postal_code, prefecture, city, operation_type, operation_user_id
        )
        SELECT 
            detail_id, user_id, first_name, last_name, first_name_kana, last_name_kana,
            addr, room_name, sex, birth_day, is_disabled, is_widow, is_household_head,
            occupation, occupation_category, primary_income_source, phone_number,
            postal_code, prefecture, city, @operation, @user_id
        FROM deleted;
    END
END;
GO

-- Create stored procedures for financial calculations
CREATE PROCEDURE SP_CalculateFinancialSummary
    @user_id INT,
    @period_type NVARCHAR(20),
    @period_year INT,
    @period_month INT = NULL,
    @period_quarter INT = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @start_date DATE, @end_date DATE;
    
    -- Calculate period dates
    IF @period_type = 'MONTHLY'
    BEGIN
        SET @start_date = DATEFROMPARTS(@period_year, @period_month, 1);
        SET @end_date = EOMONTH(@start_date);
    END
    ELSE IF @period_type = 'QUARTERLY'
    BEGIN
        SET @start_date = DATEFROMPARTS(@period_year, (@period_quarter - 1) * 3 + 1, 1);
        SET @end_date = EOMONTH(DATEADD(MONTH, 2, @start_date));
    END
    ELSE IF @period_type = 'YEARLY'
    BEGIN
        SET @start_date = DATEFROMPARTS(@period_year, 1, 1);
        SET @end_date = DATEFROMPARTS(@period_year, 12, 31);
    END
    
    -- Calculate income totals
    DECLARE @total_income DECIMAL(15,2) = 0;
    DECLARE @total_income_tax DECIMAL(15,2) = 0;
    DECLARE @net_income DECIMAL(15,2) = 0;
    
    SELECT 
        @total_income = ISNULL(SUM(amount), 0),
        @total_income_tax = ISNULL(SUM(tax_amount), 0),
        @net_income = ISNULL(SUM(net_amount), 0)
    FROM T_Dat_Incomes
    WHERE user_id = @user_id 
        AND income_date BETWEEN @start_date AND @end_date
        AND status = 'CONFIRMED';
    
    -- Calculate expense totals
    DECLARE @total_expenses DECIMAL(15,2) = 0;
    DECLARE @total_deductible_expenses DECIMAL(15,2) = 0;
    DECLARE @total_expense_tax DECIMAL(15,2) = 0;
    
    SELECT 
        @total_expenses = ISNULL(SUM(amount), 0),
        @total_deductible_expenses = ISNULL(SUM(deductible_amount), 0),
        @total_expense_tax = ISNULL(SUM(tax_amount), 0)
    FROM T_Dat_Expenses
    WHERE user_id = @user_id 
        AND expense_date BETWEEN @start_date AND @end_date
        AND status = 'CONFIRMED';
    
    -- Insert or update summary
    MERGE T_Financial_Summary AS target
    USING (SELECT @user_id AS user_id, @period_type AS period_type, 
                  @period_year AS period_year, @period_month AS period_month, 
                  @period_quarter AS period_quarter) AS source
    ON (target.user_id = source.user_id 
        AND target.period_type = source.period_type 
        AND target.period_year = source.period_year
        AND ISNULL(target.period_month, 0) = ISNULL(source.period_month, 0)
        AND ISNULL(target.period_quarter, 0) = ISNULL(source.period_quarter, 0))
    WHEN MATCHED THEN
        UPDATE SET 
            total_income = @total_income,
            total_income_tax = @total_income_tax,
            net_income = @net_income,
            total_expenses = @total_expenses,
            total_deductible_expenses = @total_deductible_expenses,
            total_expense_tax = @total_expense_tax,
            updated_at = GETUTCDATE()
    WHEN NOT MATCHED THEN
        INSERT (user_id, period_type, period_year, period_month, period_quarter,
                total_income, total_income_tax, net_income,
                total_expenses, total_deductible_expenses, total_expense_tax)
        VALUES (@user_id, @period_type, @period_year, @period_month, @period_quarter,
                @total_income, @total_income_tax, @net_income,
                @total_expenses, @total_deductible_expenses, @total_expense_tax);
END;
GO

PRINT 'Initial data and triggers created successfully!';