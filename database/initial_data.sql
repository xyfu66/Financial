-- Personal Financial Management System - Initial Data
-- PostgreSQL 14+ Initial Data Script

-- Connect to the database
\c financial_system;

-- ============================================================================
-- Insert Default Income Categories (Japanese Tax Law Compliant)
-- ============================================================================

INSERT INTO T_Master_Income_Categories (category_code, category_name, category_name_en, description, tax_deductible, is_business_income, sort_order) VALUES
-- 事業所得 (Business Income)
('INC001', '売上高', 'Sales Revenue', '商品・サービスの売上', FALSE, TRUE, 1),
('INC002', '業務委託収入', 'Contract Income', '業務委託による収入', FALSE, TRUE, 2),
('INC003', 'コンサルティング収入', 'Consulting Income', 'コンサルティング業務による収入', FALSE, TRUE, 3),
('INC004', 'システム開発収入', 'System Development Income', 'システム開発業務による収入', FALSE, TRUE, 4),
('INC005', 'デザイン収入', 'Design Income', 'デザイン業務による収入', FALSE, TRUE, 5),
('INC006', '講師料', 'Teaching Fee', '講師・研修による収入', FALSE, TRUE, 6),
('INC007', '原稿料', 'Writing Fee', '執筆・原稿による収入', FALSE, TRUE, 7),
('INC008', 'ライセンス収入', 'License Income', 'ライセンス・特許による収入', FALSE, TRUE, 8),

-- 雑所得 (Miscellaneous Income)
('INC009', '雑所得', 'Miscellaneous Income', 'その他の雑所得', FALSE, FALSE, 9),
('INC010', '利息収入', 'Interest Income', '預金利息等', FALSE, FALSE, 10),
('INC011', '配当収入', 'Dividend Income', '株式配当等', FALSE, FALSE, 11),
('INC012', '不動産収入', 'Real Estate Income', '不動産賃貸収入', FALSE, TRUE, 12),

-- その他
('INC013', '補助金・助成金', 'Subsidies/Grants', '政府・自治体からの補助金', FALSE, TRUE, 13),
('INC014', '返金・返還', 'Refunds', '経費の返金等', FALSE, TRUE, 14),
('INC015', 'その他収入', 'Other Income', 'その他の収入', FALSE, TRUE, 15);

-- ============================================================================
-- Insert Default Expense Categories (Japanese Tax Law Compliant)
-- ============================================================================

INSERT INTO T_Master_Expense_Categories (category_code, category_name, category_name_en, description, tax_deductible, is_business_expense, depreciation_years, sort_order) VALUES
-- 売上原価 (Cost of Goods Sold)
('EXP001', '仕入高', 'Purchases', '商品・材料の仕入', TRUE, TRUE, NULL, 1),
('EXP002', '外注費', 'Subcontracting Costs', '外部委託費用', TRUE, TRUE, NULL, 2),

-- 販売費及び一般管理費 (Selling, General & Administrative Expenses)
('EXP003', '広告宣伝費', 'Advertising Expenses', '広告・宣伝に関する費用', TRUE, TRUE, NULL, 3),
('EXP004', '接待交際費', 'Entertainment Expenses', '接待・交際に関する費用', TRUE, TRUE, NULL, 4),
('EXP005', '旅費交通費', 'Travel Expenses', '出張・交通に関する費用', TRUE, TRUE, NULL, 5),
('EXP006', '通信費', 'Communication Expenses', '電話・インターネット等', TRUE, TRUE, NULL, 6),
('EXP007', '水道光熱費', 'Utilities', '電気・ガス・水道代', TRUE, TRUE, NULL, 7),
('EXP008', '消耗品費', 'Office Supplies', '事務用品・消耗品', TRUE, TRUE, NULL, 8),
('EXP009', '修繕費', 'Repair Expenses', '設備・機器の修理費', TRUE, TRUE, NULL, 9),

-- 人件費 (Personnel Expenses)
('EXP010', '給料賃金', 'Salaries', '従業員給与', TRUE, TRUE, NULL, 10),
('EXP011', '法定福利費', 'Statutory Welfare', '社会保険料等', TRUE, TRUE, NULL, 11),
('EXP012', '福利厚生費', 'Employee Benefits', '福利厚生に関する費用', TRUE, TRUE, NULL, 12),

-- 地代家賃 (Rent)
('EXP013', '地代家賃', 'Rent', '事務所・店舗の賃料', TRUE, TRUE, NULL, 13),
('EXP014', '駐車場代', 'Parking Fees', '駐車場利用料', TRUE, TRUE, NULL, 14),

-- 減価償却費 (Depreciation)
('EXP015', '減価償却費', 'Depreciation', '固定資産の減価償却', TRUE, TRUE, NULL, 15),

-- 租税公課 (Taxes and Dues)
('EXP016', '租税公課', 'Taxes and Dues', '事業税・固定資産税等', TRUE, TRUE, NULL, 16),
('EXP017', '印紙税', 'Stamp Tax', '契約書等の印紙税', TRUE, TRUE, NULL, 17),

-- 保険料 (Insurance)
('EXP018', '損害保険料', 'Insurance Premiums', '事業用保険料', TRUE, TRUE, NULL, 18),

-- 金融関係 (Financial)
('EXP019', '支払利息', 'Interest Expenses', '借入金利息', TRUE, TRUE, NULL, 19),
('EXP020', '支払手数料', 'Bank Charges', '銀行手数料等', TRUE, TRUE, NULL, 20),

-- 専門サービス (Professional Services)
('EXP021', '支払報酬', 'Professional Fees', '税理士・弁護士等への報酬', TRUE, TRUE, NULL, 21),
('EXP022', '会議費', 'Meeting Expenses', '会議・研修費用', TRUE, TRUE, NULL, 22),
('EXP023', '研修費', 'Training Expenses', '研修・セミナー費用', TRUE, TRUE, NULL, 23),

-- IT関係 (IT Related)
('EXP024', 'ソフトウェア費', 'Software Expenses', 'ソフトウェア購入・利用料', TRUE, TRUE, NULL, 24),
('EXP025', 'システム利用料', 'System Usage Fees', 'クラウドサービス等', TRUE, TRUE, NULL, 25),
('EXP026', 'ドメイン・サーバー費', 'Domain/Server Fees', 'ドメイン・サーバー利用料', TRUE, TRUE, NULL, 26),

-- 固定資産 (Fixed Assets)
('EXP027', '建物', 'Buildings', '建物の購入・建設', TRUE, TRUE, 47, 27),
('EXP028', '建物附属設備', 'Building Fixtures', '建物附属設備', TRUE, TRUE, 15, 28),
('EXP029', '機械装置', 'Machinery', '機械・装置', TRUE, TRUE, 10, 29),
('EXP030', '車両運搬具', 'Vehicles', '自動車・運搬具', TRUE, TRUE, 6, 30),
('EXP031', '工具器具備品', 'Tools and Equipment', '工具・器具・備品', TRUE, TRUE, 6, 31),
('EXP032', 'パソコン・IT機器', 'Computer Equipment', 'パソコン・IT関連機器', TRUE, TRUE, 4, 32),

-- その他 (Others)
('EXP033', '新聞図書費', 'Books and Publications', '新聞・書籍・雑誌', TRUE, TRUE, NULL, 33),
('EXP034', '諸会費', 'Membership Fees', '組合費・会費等', TRUE, TRUE, NULL, 34),
('EXP035', '寄付金', 'Donations', '寄付金', FALSE, TRUE, NULL, 35),
('EXP036', '雑費', 'Miscellaneous Expenses', 'その他の経費', TRUE, TRUE, NULL, 36),

-- 個人事業主特有 (Sole Proprietor Specific)
('EXP037', '青色申告会費', 'Blue Form Association Fee', '青色申告会の会費', TRUE, TRUE, NULL, 37),
('EXP038', '帳簿作成費', 'Bookkeeping Expenses', '帳簿作成に関する費用', TRUE, TRUE, NULL, 38),

-- 家事按分対象 (Home Office Deductible)
('EXP039', '家事按分_通信費', 'Home Office Communication', '自宅兼事務所の通信費', TRUE, TRUE, NULL, 39),
('EXP040', '家事按分_光熱費', 'Home Office Utilities', '自宅兼事務所の光熱費', TRUE, TRUE, NULL, 40);

-- ============================================================================
-- Insert Default User Roles
-- ============================================================================

INSERT INTO T_User_Role (role_name, role_description, permissions) VALUES
('super_admin', 'システム管理者', '{"all": true}'),
('admin', '管理者', '{"users": ["view", "create", "edit"], "financial": ["view", "create", "edit", "delete"], "reports": ["view", "export"], "system": ["view"]}'),
('user', '一般ユーザー', '{"financial": ["view", "create", "edit"], "reports": ["view"], "profile": ["view", "edit"]}');

-- ============================================================================
-- Insert Default Permissions
-- ============================================================================

INSERT INTO T_User_Permission (permission_name, permission_description, resource, action) VALUES
-- User Management
('user_view', 'ユーザー情報の閲覧', 'user', 'view'),
('user_create', 'ユーザーの作成', 'user', 'create'),
('user_edit', 'ユーザー情報の編集', 'user', 'edit'),
('user_delete', 'ユーザーの削除', 'user', 'delete'),

-- Financial Data
('income_view', '収入データの閲覧', 'income', 'view'),
('income_create', '収入データの作成', 'income', 'create'),
('income_edit', '収入データの編集', 'income', 'edit'),
('income_delete', '収入データの削除', 'income', 'delete'),
('income_import', '収入データのインポート', 'income', 'import'),
('income_export', '収入データのエクスポート', 'income', 'export'),

('expense_view', '支出データの閲覧', 'expense', 'view'),
('expense_create', '支出データの作成', 'expense', 'create'),
('expense_edit', '支出データの編集', 'expense', 'edit'),
('expense_delete', '支出データの削除', 'expense', 'delete'),
('expense_import', '支出データのインポート', 'expense', 'import'),
('expense_export', '支出データのエクスポート', 'expense', 'export'),

-- Reports
('report_view', 'レポートの閲覧', 'report', 'view'),
('report_export', 'レポートのエクスポート', 'report', 'export'),
('tax_calculation', '税務計算の実行', 'tax', 'calculate'),

-- System
('system_view', 'システム情報の閲覧', 'system', 'view'),
('audit_view', '監査ログの閲覧', 'audit', 'view'),
('notification_manage', '通知の管理', 'notification', 'manage'),

-- File Operations
('file_upload', 'ファイルのアップロード', 'file', 'upload'),
('ocr_process', 'OCR処理の実行', 'ocr', 'process');

-- ============================================================================
-- Insert Default Notifications
-- ============================================================================

INSERT INTO T_Notification (title, message, notification_type, is_active, target_roles, priority) VALUES
('システム開始', 'Personal Financial Management Systemへようこそ！', 'INFO', TRUE, ARRAY['super_admin', 'admin', 'user']::user_role_type[], 1),
('青色申告について', '青色申告の特別控除を受けるためには、複式簿記による記帳が必要です。', 'INFO', TRUE, ARRAY['user']::user_role_type[], 2),
('データバックアップ', '重要なデータは定期的にバックアップを取ることをお勧めします。', 'WARNING', TRUE, ARRAY['super_admin', 'admin', 'user']::user_role_type[], 3);

-- ============================================================================
-- Create sample admin user (password: admin123)
-- Note: This should be changed in production
-- ============================================================================

-- Insert admin user (password hash for 'admin123')
INSERT INTO T_User (username, email, password_hash, role, is_active, is_staff, is_superuser) VALUES
('admin', 'admin@example.com', 'pbkdf2_sha256$600000$dummy$hash', 'super_admin', TRUE, TRUE, TRUE);

-- Get the admin user ID for the detail record
DO $$
DECLARE
    admin_user_id UUID;
BEGIN
    SELECT user_id INTO admin_user_id FROM T_User WHERE username = 'admin';
    
    -- Insert admin user details
    INSERT INTO T_User_Detail (user_id, first_name, last_name, first_name_kana, last_name_kana) VALUES
    (admin_user_id, '管理者', 'システム', 'カンリシャ', 'システム');
END $$;

-- ============================================================================
-- Update sequences to start from appropriate values
-- ============================================================================

-- This ensures that auto-generated IDs don't conflict with manually inserted data
SELECT setval(pg_get_serial_sequence('T_Master_Income_Categories', 'category_id'), (SELECT MAX(category_id::text)::bigint FROM T_Master_Income_Categories) + 1, false);
SELECT setval(pg_get_serial_sequence('T_Master_Expense_Categories', 'category_id'), (SELECT MAX(category_id::text)::bigint FROM T_Master_Expense_Categories) + 1, false);

-- ============================================================================
-- Create sample data for testing (optional - can be removed in production)
-- ============================================================================

-- Sample income data
DO $$
DECLARE
    admin_user_id UUID;
    sales_category_id UUID;
    consulting_category_id UUID;
BEGIN
    SELECT user_id INTO admin_user_id FROM T_User WHERE username = 'admin';
    SELECT category_id INTO sales_category_id FROM T_Master_Income_Categories WHERE category_code = 'INC001';
    SELECT category_id INTO consulting_category_id FROM T_Master_Income_Categories WHERE category_code = 'INC003';
    
    -- Sample income records
    INSERT INTO T_Dat_Incomes (user_id, category_id, income_date, description, client_name, amount, tax_amount, created_by) VALUES
    (admin_user_id, sales_category_id, '2024-01-15', 'Webサイト制作', '株式会社サンプル', 550000, 50000, admin_user_id),
    (admin_user_id, consulting_category_id, '2024-01-20', 'ITコンサルティング', '有限会社テスト', 220000, 20000, admin_user_id),
    (admin_user_id, sales_category_id, '2024-02-10', 'システム開発', '株式会社デモ', 880000, 80000, admin_user_id);
END $$;

-- Sample expense data
DO $$
DECLARE
    admin_user_id UUID;
    office_supplies_id UUID;
    communication_id UUID;
    software_id UUID;
BEGIN
    SELECT user_id INTO admin_user_id FROM T_User WHERE username = 'admin';
    SELECT category_id INTO office_supplies_id FROM T_Master_Expense_Categories WHERE category_code = 'EXP008';
    SELECT category_id INTO communication_id FROM T_Master_Expense_Categories WHERE category_code = 'EXP006';
    SELECT category_id INTO software_id FROM T_Master_Expense_Categories WHERE category_code = 'EXP024';
    
    -- Sample expense records
    INSERT INTO T_Dat_Expenses (user_id, category_id, expense_date, description, vendor_name, amount, tax_amount, business_use_percentage, created_by) VALUES
    (admin_user_id, office_supplies_id, '2024-01-05', '事務用品購入', 'オフィス用品店', 15400, 1400, 100.00, admin_user_id),
    (admin_user_id, communication_id, '2024-01-31', 'インターネット料金', 'NTT', 6600, 600, 80.00, admin_user_id),
    (admin_user_id, software_id, '2024-02-01', 'Adobe Creative Suite', 'Adobe', 7678, 698, 100.00, admin_user_id);
END $$;

-- ============================================================================
-- Final verification queries (commented out for production)
-- ============================================================================

/*
-- Verify data insertion
SELECT 'Income Categories' as table_name, COUNT(*) as record_count FROM T_Master_Income_Categories
UNION ALL
SELECT 'Expense Categories', COUNT(*) FROM T_Master_Expense_Categories
UNION ALL
SELECT 'User Roles', COUNT(*) FROM T_User_Role
UNION ALL
SELECT 'User Permissions', COUNT(*) FROM T_User_Permission
UNION ALL
SELECT 'Users', COUNT(*) FROM T_User
UNION ALL
SELECT 'Notifications', COUNT(*) FROM T_Notification;
*/

COMMENT ON SCHEMA public IS 'Personal Financial Management System - Initial data loaded successfully';