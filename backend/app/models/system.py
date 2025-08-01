"""
System management models
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Notification(Base):
    """
    T_Notification: System notification management table
    """
    __tablename__ = "T_Notification"
    
    notification_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(20), nullable=False, default="INFO")  # INFO, WARNING, MAINTENANCE, URGENT
    is_active = Column(Boolean, default=True, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    target_roles = Column(String(100))  # Comma-separated roles: admin,user or empty for all
    priority = Column(Integer, default=1)  # 1=Low, 2=Medium, 3=High, 4=Critical
    created_by = Column(Integer, ForeignKey("T_User.user_id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class AuditLog(Base):
    """
    T_Audit_Log: Comprehensive audit logging table
    """
    __tablename__ = "T_Audit_Log"
    
    log_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("T_User.user_id"), nullable=True)  # Nullable for system operations
    table_name = Column(String(50), nullable=False)
    record_id = Column(String(50), nullable=True)  # Can be composite key as string
    action = Column(String(20), nullable=False)  # CREATE, READ, UPDATE, DELETE, LOGIN, LOGOUT, IMPORT, EXPORT
    old_values = Column(JSON, nullable=True)  # Previous values for UPDATE operations
    new_values = Column(JSON, nullable=True)  # New values for CREATE/UPDATE operations
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)
    session_id = Column(String(255), nullable=True)
    request_method = Column(String(10), nullable=True)  # GET, POST, PUT, DELETE
    request_url = Column(String(500), nullable=True)
    response_status = Column(Integer, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)  # Request execution time in milliseconds
    error_message = Column(Text, nullable=True)
    additional_data = Column(JSON, nullable=True)  # Any additional context data
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")

class SystemConfig(Base):
    """
    T_System_Config: System configuration table
    """
    __tablename__ = "T_System_Config"
    
    config_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    config_key = Column(String(100), unique=True, nullable=False, index=True)
    config_value = Column(Text, nullable=False)
    config_type = Column(String(20), nullable=False, default="STRING")  # STRING, INTEGER, BOOLEAN, JSON
    description = Column(Text)
    is_system = Column(Boolean, default=False)  # System configs cannot be modified via UI
    is_encrypted = Column(Boolean, default=False)  # Whether the value is encrypted
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by = Column(Integer, ForeignKey("T_User.user_id"), nullable=True)

class FileUpload(Base):
    """
    T_File_Upload: File upload tracking table
    """
    __tablename__ = "T_File_Upload"
    
    file_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    file_type = Column(String(50), nullable=False)  # MIME type
    file_extension = Column(String(10), nullable=False)
    upload_purpose = Column(String(50), nullable=False)  # INCOME_IMPORT, EXPENSE_IMPORT, OCR_PROCESSING
    processing_status = Column(String(20), default="PENDING")  # PENDING, PROCESSING, COMPLETED, FAILED
    processing_result = Column(JSON, nullable=True)  # OCR results or import results
    error_message = Column(Text, nullable=True)
    uploaded_by = Column(Integer, ForeignKey("T_User.user_id"), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

class SystemHealth(Base):
    """
    T_System_Health: System health monitoring table
    """
    __tablename__ = "T_System_Health"
    
    health_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    component = Column(String(50), nullable=False)  # DATABASE, API, OCR_SERVICE, FILE_SYSTEM
    status = Column(String(20), nullable=False)  # HEALTHY, WARNING, CRITICAL, DOWN
    response_time_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    additional_info = Column(JSON, nullable=True)
    checked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)