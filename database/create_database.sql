-- Personal Financial Management System Database Creation Script
-- SQL Server 2019 Compatible

-- Create database if it doesn't exist
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'FinancialManagement')
BEGIN
    CREATE DATABASE FinancialManagement
    COLLATE Japanese_CI_AS;
END
GO

USE FinancialManagement;
GO

-- Enable snapshot isolation for better concurrency
ALTER DATABASE FinancialManagement SET ALLOW_SNAPSHOT_ISOLATION ON;
ALTER DATABASE FinancialManagement SET READ_COMMITTED_SNAPSHOT ON;
GO

-- Create schemas for better organization
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'audit')
    EXEC('CREATE SCHEMA audit');
GO

IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'master')
    EXEC('CREATE SCHEMA master');
GO

-- User Management Tables
-- T_User: Main user information table
CREATE TABLE T_User (
    user_id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(50) NOT NULL UNIQUE,
    email NVARCHAR(255) NOT NULL UNIQUE,
    password_hash NVARCHAR(255) NOT NULL,
    role NVARCHAR(20) NOT NULL DEFAULT 'user' CHECK (role IN ('super_admin', 'admin', 'user')),
    is_active BIT NOT NULL DEFAULT 1,
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    last_login DATETIME2 NULL,
    failed_login_attempts INT NOT NULL DEFAULT 0,
    locked_until DATETIME2 NULL,
    
    INDEX IX_T_User_username (username),
    INDEX IX_T_User_email (email),
    INDEX IX_T_User_role (role),
    INDEX IX_T_User_is_active (is_active)
);
GO

-- T_User_History: User information history table
CREATE TABLE T_User_History (
    history_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    username NVARCHAR(50) NOT NULL,
    email NVARCHAR(255) NOT NULL,
    role NVARCHAR(20) NOT NULL,
    is_active BIT NOT NULL,
    operation_type NVARCHAR(10) NOT NULL CHECK (operation_type IN ('INSERT', 'UPDATE', 'DELETE')),
    operation_timestamp DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    operation_user_id INT NOT NULL,
    
    INDEX IX_T_User_History_user_id (user_id),
    INDEX IX_T_User_History_operation_timestamp (operation_timestamp)
);
GO

-- T_User_Detail: Detailed user information table
CREATE TABLE T_User_Detail (
    detail_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    first_name NVARCHAR(50) NOT NULL,
    last_name NVARCHAR(50) NOT NULL,
    first_name_kana NVARCHAR(50) NULL,
    last_name_kana NVARCHAR(50) NULL,
    addr NVARCHAR(MAX) NULL,
    room_name NVARCHAR(100) NULL,
    sex NCHAR(1) NULL CHECK (sex IN ('M', 'F')),
    birth_day DATE NULL,
    is_disabled BIT NOT NULL DEFAULT 0,
    is_widow BIT NOT NULL DEFAULT 0,
    is_household_head BIT NOT NULL DEFAULT 0,
    occupation NVARCHAR(100) NULL,
    occupation_category NVARCHAR(50) NULL,
    primary_income_source NVARCHAR(100) NULL,
    phone_number NVARCHAR(20) NULL,
    postal_code NVARCHAR(10) NULL,
    prefecture NVARCHAR(20) NULL,
    city NVARCHAR(50) NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    
    FOREIGN KEY (user_id) REFERENCES T_User(user_id) ON DELETE CASCADE,
    INDEX IX_T_User_Detail_user_id (user_id)
);
GO

-- T_User_Detail_History: User detail information history table
CREATE TABLE T_User_Detail_History (
    history_id INT IDENTITY(1,1) PRIMARY KEY,
    detail_id INT NOT NULL,
    user_id INT NOT NULL,
    first_name NVARCHAR(50) NOT NULL,
    last_name NVARCHAR(50) NOT NULL,
    first_name_kana NVARCHAR(50) NULL,
    last_name_kana NVARCHAR(50) NULL,
    addr NVARCHAR(MAX) NULL,
    room_name NVARCHAR(100) NULL,
    sex NCHAR(1) NULL,
    birth_day DATE NULL,
    is_disabled BIT NULL,
    is_widow BIT NULL,
    is_household_head BIT NULL,
    occupation NVARCHAR(100) NULL,
    occupation_category NVARCHAR(50) NULL,
    primary_income_source NVARCHAR(100) NULL,
    phone_number NVARCHAR(20) NULL,
    postal_code NVARCHAR(10) NULL,
    prefecture NVARCHAR(20) NULL,
    city NVARCHAR(50) NULL,
    operation_type NVARCHAR(10) NOT NULL CHECK (operation_type IN ('INSERT', 'UPDATE', 'DELETE')),
    operation_timestamp DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    operation_user_id INT NOT NULL,
    
    INDEX IX_T_User_Detail_History_user_id (user_id),
    INDEX IX_T_User_Detail_History_operation_timestamp (operation_timestamp)
);
GO

-- T_User_Role: Role management table
CREATE TABLE T_User_Role (
    role_id INT IDENTITY(1,1) PRIMARY KEY,
    role_name NVARCHAR(50) NOT NULL UNIQUE,
    role_description NVARCHAR(MAX) NULL,
    is_active BIT NOT NULL DEFAULT 1,
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    
    INDEX IX_T_User_Role_role_name (role_name),
    INDEX IX_T_User_Role_is_active (is_active)
);
GO

-- T_User_Permission: Permission management table
CREATE TABLE T_User_Permission (
    permission_id INT IDENTITY(1,1) PRIMARY KEY,
    permission_name NVARCHAR(50) NOT NULL UNIQUE,
    permission_description NVARCHAR(MAX) NULL,
    resource NVARCHAR(50) NOT NULL CHECK (resource IN ('income', 'expense', 'user', 'system', 'report')),
    action NVARCHAR(20) NOT NULL CHECK (action IN ('create', 'read', 'update', 'delete', 'import', 'export')),
    is_active BIT NOT NULL DEFAULT 1,
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    
    INDEX IX_T_User_Permission_resource_action (resource, action),
    INDEX IX_T_User_Permission_is_active (is_active)
);
GO

-- System Management Tables
-- T_Notification: System notification management table
CREATE TABLE T_Notification (
    notification_id INT IDENTITY(1,1) PRIMARY KEY,
    title NVARCHAR(200) NOT NULL,
    message NVARCHAR(MAX) NOT NULL,
    notification_type NVARCHAR(20) NOT NULL DEFAULT 'INFO' CHECK (notification_type IN ('INFO', 'WARNING', 'MAINTENANCE', 'URGENT')),
    is_active BIT NOT NULL DEFAULT 1,
    start_date DATETIME2 NOT NULL,
    end_date DATETIME2 NOT NULL,
    target_roles NVARCHAR(100) NULL,
    priority INT NOT NULL DEFAULT 1 CHECK (priority BETWEEN 1 AND 4),
    created_by INT NOT NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    
    FOREIGN KEY (created_by) REFERENCES T_User(user_id),
    INDEX IX_T_Notification_is_active_dates (is_active, start_date, end_date),
    INDEX IX_T_Notification_type_priority (notification_type, priority)
);
GO

-- T_Audit_Log: Comprehensive audit logging table
CREATE TABLE T_Audit_Log (
    log_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NULL,
    table_name NVARCHAR(50) NOT NULL,
    record_id NVARCHAR(50) NULL,
    action NVARCHAR(20) NOT NULL CHECK (action IN ('CREATE', 'READ', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT', 'IMPORT', 'EXPORT')),
    old_values NVARCHAR(MAX) NULL,
    new_values NVARCHAR(MAX) NULL,
    ip_address NVARCHAR(45) NULL,
    user_agent NVARCHAR(MAX) NULL,
    session_id NVARCHAR(255) NULL,
    request_method NVARCHAR(10) NULL,
    request_url NVARCHAR(500) NULL,
    response_status INT NULL,
    execution_time_ms INT NULL,
    error_message NVARCHAR(MAX) NULL,
    additional_data NVARCHAR(MAX) NULL,
    timestamp DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    
    FOREIGN KEY (user_id) REFERENCES T_User(user_id),
    INDEX IX_T_Audit_Log_timestamp (timestamp),
    INDEX IX_T_Audit_Log_user_id_timestamp (user_id, timestamp),
    INDEX IX_T_Audit_Log_table_action (table_name, action)
);
GO

PRINT 'Database schema created successfully!';