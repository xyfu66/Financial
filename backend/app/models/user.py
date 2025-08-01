"""
User management models
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    """
    T_User: Main user information table
    """
    __tablename__ = "T_User"
    
    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="user")  # super_admin, admin, user
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True))
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True))
    
    # Relationships
    user_detail = relationship("UserDetail", back_populates="user", uselist=False)
    audit_logs = relationship("AuditLog", back_populates="user")
    incomes = relationship("Income", back_populates="user")
    expenses = relationship("Expense", back_populates="user")

class UserHistory(Base):
    """
    T_User_History: User information history table
    """
    __tablename__ = "T_User_History"
    
    history_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    username = Column(String(50), nullable=False)
    email = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    is_active = Column(Boolean, nullable=False)
    operation_type = Column(String(10), nullable=False)  # INSERT, UPDATE, DELETE
    operation_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    operation_user_id = Column(Integer, nullable=False)

class UserDetail(Base):
    """
    T_User_Detail: Detailed user information table
    """
    __tablename__ = "T_User_Detail"
    
    detail_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("T_User.user_id"), unique=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    first_name_kana = Column(String(50))  # Japanese phonetic reading
    last_name_kana = Column(String(50))   # Japanese phonetic reading
    addr = Column(Text)  # Address
    room_name = Column(String(100))  # Room/apartment name
    sex = Column(String(1))  # M/F
    birth_day = Column(Date)
    is_disabled = Column(Boolean, default=False)
    is_widow = Column(Boolean, default=False)
    is_household_head = Column(Boolean, default=False)
    occupation = Column(String(100))
    occupation_category = Column(String(50))  # Business category for tax purposes
    primary_income_source = Column(String(100))
    phone_number = Column(String(20))
    postal_code = Column(String(10))
    prefecture = Column(String(20))  # Japanese prefecture
    city = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="user_detail")

class UserDetailHistory(Base):
    """
    T_User_Detail_History: User detail information history table
    """
    __tablename__ = "T_User_Detail_History"
    
    history_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    detail_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    first_name_kana = Column(String(50))
    last_name_kana = Column(String(50))
    addr = Column(Text)
    room_name = Column(String(100))
    sex = Column(String(1))
    birth_day = Column(Date)
    is_disabled = Column(Boolean)
    is_widow = Column(Boolean)
    is_household_head = Column(Boolean)
    occupation = Column(String(100))
    occupation_category = Column(String(50))
    primary_income_source = Column(String(100))
    phone_number = Column(String(20))
    postal_code = Column(String(10))
    prefecture = Column(String(20))
    city = Column(String(50))
    operation_type = Column(String(10), nullable=False)  # INSERT, UPDATE, DELETE
    operation_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    operation_user_id = Column(Integer, nullable=False)

class UserRole(Base):
    """
    T_User_Role: Role management table
    """
    __tablename__ = "T_User_Role"
    
    role_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role_name = Column(String(50), unique=True, nullable=False)
    role_description = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class UserPermission(Base):
    """
    T_User_Permission: Permission management table
    """
    __tablename__ = "T_User_Permission"
    
    permission_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    permission_name = Column(String(50), unique=True, nullable=False)
    permission_description = Column(Text)
    resource = Column(String(50), nullable=False)  # income, expense, user, system
    action = Column(String(20), nullable=False)    # create, read, update, delete, import, export
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)