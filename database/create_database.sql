-- Personal Financial Management System Database Schema
-- PostgreSQL 14+ Database Creation Script

-- Create database (run this separately if needed)
-- CREATE DATABASE financial_system WITH ENCODING 'UTF8' LC_COLLATE='C' LC_CTYPE='C';

-- Connect to the database
\c financial_system;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create custom types
CREATE TYPE user_role_type AS ENUM ('super_admin', 'admin', 'user');
CREATE TYPE notification_type AS ENUM ('INFO', 'WARNING', 'MAINTENANCE', 'URGENT');
CREATE TYPE audit_action_type AS ENUM ('CREATE', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT', 'IMPORT', 'EXPORT');
CREATE TYPE gender_type AS ENUM ('male', 'female', 'other');

-- ============================================================================
-- User Management Tables
-- ============================================================================

-- T_User: Main user information table
CREATE TABLE T_User (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    role user_role_type NOT NULL DEFAULT 'user',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    date_joined TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES T_User(user_id),
    updated_by UUID REFERENCES T_User(user_id)
);

-- T_User_History: User information history table
CREATE TABLE T_User_History (
    history_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    username VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    role user_role_type NOT NULL,
    is_active BOOLEAN NOT NULL,
    is_staff BOOLEAN NOT NULL,
    is_superuser BOOLEAN NOT NULL,
    date_joined TIMESTAMP WITH TIME ZONE NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_by UUID,
    updated_by UUID,
    history_created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    history_action VARCHAR(10) NOT NULL -- INSERT, UPDATE, DELETE
);

-- T_User_Detail: Detailed user information table
CREATE TABLE T_User_Detail (
    detail_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL REFERENCES T_User(user_id) ON DELETE CASCADE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    first_name_kana VARCHAR(100),
    last_name_kana VARCHAR(100),
    addr TEXT,
    room_name VARCHAR(200),
    sex gender_type,
    birth_day DATE,
    phone_number VARCHAR(20),
    is_disabled BOOLEAN NOT NULL DEFAULT FALSE,
    is_widow BOOLEAN NOT NULL DEFAULT FALSE,
    is_household_head BOOLEAN NOT NULL DEFAULT FALSE,
    occupation VARCHAR(200),
    occupation_category VARCHAR(100),
    primary_income_source VARCHAR(200),
    tax_number VARCHAR(50), -- マイナンバー (encrypted)
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES T_User(user_id),
    updated_by UUID REFERENCES T_User(user_id)
);

-- T_User_Detail_History: User detail history table
CREATE TABLE T_User_Detail_History (
    history_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    detail_id UUID NOT NULL,
    user_id UUID NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    first_name_kana VARCHAR(100),
    last_name_kana VARCHAR(100),
    addr TEXT,
    room_name VARCHAR(200),
    sex gender_type,
    birth_day DATE,
    phone_number VARCHAR(20),
    is_disabled BOOLEAN NOT NULL,
    is_widow BOOLEAN NOT NULL,
    is_household_head BOOLEAN NOT NULL,
    occupation VARCHAR(200),
    occupation_category VARCHAR(100),
    primary_income_source VARCHAR(200),
    tax_number VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_by UUID,
    updated_by UUID,
    history_created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    history_action VARCHAR(10) NOT NULL
);

-- T_User_Role: Role management table
CREATE TABLE T_User_Role (
    role_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    role_name VARCHAR(50) UNIQUE NOT NULL,
    role_description TEXT,
    permissions JSONB,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES T_User(user_id),
    updated_by UUID REFERENCES T_User(user_id)
);

-- T_User_Permission: Permission management table
CREATE TABLE T_User_Permission (
    permission_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    permission_name VARCHAR(100) UNIQUE NOT NULL,
    permission_description TEXT,
    resource VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES T_User(user_id),
    updated_by UUID REFERENCES T_User(user_id)
);

-- ============================================================================
-- System Management Tables
-- ============================================================================

-- T_Notification: Notification management table
CREATE TABLE T_Notification (
    notification_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    notification_type notification_type NOT NULL DEFAULT 'INFO',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    target_roles user_role_type[],
    priority INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES T_User(user_id),
    updated_by UUID REFERENCES T_User(user_id)
);

-- T_Audit_Log: Audit log table
CREATE TABLE T_Audit_Log (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES T_User(user_id),
    table_name VARCHAR(100) NOT NULL,
    record_id UUID,
    action audit_action_type NOT NULL,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- Create Indexes
-- ============================================================================

-- User table indexes
CREATE INDEX idx_t_user_username ON T_User(username);
CREATE INDEX idx_t_user_email ON T_User(email);
CREATE INDEX idx_t_user_role ON T_User(role);
CREATE INDEX idx_t_user_is_active ON T_User(is_active);
CREATE INDEX idx_t_user_created_at ON T_User(created_at);

-- User detail indexes
CREATE INDEX idx_t_user_detail_user_id ON T_User_Detail(user_id);
CREATE INDEX idx_t_user_detail_name ON T_User_Detail(last_name, first_name);

-- Notification indexes
CREATE INDEX idx_t_notification_is_active ON T_Notification(is_active);
CREATE INDEX idx_t_notification_type ON T_Notification(notification_type);
CREATE INDEX idx_t_notification_dates ON T_Notification(start_date, end_date);

-- Audit log indexes
CREATE INDEX idx_t_audit_log_user_id ON T_Audit_Log(user_id);
CREATE INDEX idx_t_audit_log_table_name ON T_Audit_Log(table_name);
CREATE INDEX idx_t_audit_log_action ON T_Audit_Log(action);
CREATE INDEX idx_t_audit_log_created_at ON T_Audit_Log(created_at);
CREATE INDEX idx_t_audit_log_record_id ON T_Audit_Log(record_id);

-- ============================================================================
-- Create Functions and Triggers for automatic timestamp updates
-- ============================================================================

-- Function to update timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to tables
CREATE TRIGGER update_t_user_updated_at BEFORE UPDATE ON T_User FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_t_user_detail_updated_at BEFORE UPDATE ON T_User_Detail FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_t_user_role_updated_at BEFORE UPDATE ON T_User_Role FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_t_user_permission_updated_at BEFORE UPDATE ON T_User_Permission FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_t_notification_updated_at BEFORE UPDATE ON T_Notification FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Create Functions for History Tables
-- ============================================================================

-- Function to create user history record
CREATE OR REPLACE FUNCTION create_user_history()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO T_User_History (
            user_id, username, email, password_hash, role, is_active, is_staff, is_superuser,
            date_joined, last_login, created_at, updated_at, created_by, updated_by, history_action
        ) VALUES (
            OLD.user_id, OLD.username, OLD.email, OLD.password_hash, OLD.role, OLD.is_active, OLD.is_staff, OLD.is_superuser,
            OLD.date_joined, OLD.last_login, OLD.created_at, OLD.updated_at, OLD.created_by, OLD.updated_by, 'DELETE'
        );
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO T_User_History (
            user_id, username, email, password_hash, role, is_active, is_staff, is_superuser,
            date_joined, last_login, created_at, updated_at, created_by, updated_by, history_action
        ) VALUES (
            NEW.user_id, NEW.username, NEW.email, NEW.password_hash, NEW.role, NEW.is_active, NEW.is_staff, NEW.is_superuser,
            NEW.date_joined, NEW.last_login, NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, 'UPDATE'
        );
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO T_User_History (
            user_id, username, email, password_hash, role, is_active, is_staff, is_superuser,
            date_joined, last_login, created_at, updated_at, created_by, updated_by, history_action
        ) VALUES (
            NEW.user_id, NEW.username, NEW.email, NEW.password_hash, NEW.role, NEW.is_active, NEW.is_staff, NEW.is_superuser,
            NEW.date_joined, NEW.last_login, NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, 'INSERT'
        );
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Function to create user detail history record
CREATE OR REPLACE FUNCTION create_user_detail_history()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO T_User_Detail_History (
            detail_id, user_id, first_name, last_name, first_name_kana, last_name_kana,
            addr, room_name, sex, birth_day, phone_number, is_disabled, is_widow, is_household_head,
            occupation, occupation_category, primary_income_source, tax_number,
            created_at, updated_at, created_by, updated_by, history_action
        ) VALUES (
            OLD.detail_id, OLD.user_id, OLD.first_name, OLD.last_name, OLD.first_name_kana, OLD.last_name_kana,
            OLD.addr, OLD.room_name, OLD.sex, OLD.birth_day, OLD.phone_number, OLD.is_disabled, OLD.is_widow, OLD.is_household_head,
            OLD.occupation, OLD.occupation_category, OLD.primary_income_source, OLD.tax_number,
            OLD.created_at, OLD.updated_at, OLD.created_by, OLD.updated_by, 'DELETE'
        );
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO T_User_Detail_History (
            detail_id, user_id, first_name, last_name, first_name_kana, last_name_kana,
            addr, room_name, sex, birth_day, phone_number, is_disabled, is_widow, is_household_head,
            occupation, occupation_category, primary_income_source, tax_number,
            created_at, updated_at, created_by, updated_by, history_action
        ) VALUES (
            NEW.detail_id, NEW.user_id, NEW.first_name, NEW.last_name, NEW.first_name_kana, NEW.last_name_kana,
            NEW.addr, NEW.room_name, NEW.sex, NEW.birth_day, NEW.phone_number, NEW.is_disabled, NEW.is_widow, NEW.is_household_head,
            NEW.occupation, NEW.occupation_category, NEW.primary_income_source, NEW.tax_number,
            NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, 'UPDATE'
        );
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO T_User_Detail_History (
            detail_id, user_id, first_name, last_name, first_name_kana, last_name_kana,
            addr, room_name, sex, birth_day, phone_number, is_disabled, is_widow, is_household_head,
            occupation, occupation_category, primary_income_source, tax_number,
            created_at, updated_at, created_by, updated_by, history_action
        ) VALUES (
            NEW.detail_id, NEW.user_id, NEW.first_name, NEW.last_name, NEW.first_name_kana, NEW.last_name_kana,
            NEW.addr, NEW.room_name, NEW.sex, NEW.birth_day, NEW.phone_number, NEW.is_disabled, NEW.is_widow, NEW.is_household_head,
            NEW.occupation, NEW.occupation_category, NEW.primary_income_source, NEW.tax_number,
            NEW.created_at, NEW.updated_at, NEW.created_by, NEW.updated_by, 'INSERT'
        );
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Apply history triggers
CREATE TRIGGER t_user_history_trigger
    AFTER INSERT OR UPDATE OR DELETE ON T_User
    FOR EACH ROW EXECUTE FUNCTION create_user_history();

CREATE TRIGGER t_user_detail_history_trigger
    AFTER INSERT OR UPDATE OR DELETE ON T_User_Detail
    FOR EACH ROW EXECUTE FUNCTION create_user_detail_history();

-- ============================================================================
-- Grant permissions
-- ============================================================================

-- Grant usage on sequences
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Grant permissions on tables
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;

COMMENT ON DATABASE financial_system IS 'Personal Financial Management System Database';