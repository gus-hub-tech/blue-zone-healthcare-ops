"""Access control models"""
from sqlalchemy import Column, String, DateTime, Enum, JSON
from sqlalchemy.sql import func
from datetime import datetime
import enum
from models import Base

class UserRole(str, enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    DOCTOR = "doctor"
    NURSE = "nurse"
    STAFF = "staff"
    PATIENT = "patient"

class AccessLogAction(str, enum.Enum):
    """Access log action enumeration"""
    VIEW = "view"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    DOWNLOAD = "download"

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime, nullable=True)

class Role(Base):
    """Role model"""
    __tablename__ = "roles"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    permissions = Column(JSON, nullable=False, default={})
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

class AccessLog(Base):
    """Access log model"""
    __tablename__ = "access_logs"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    resource = Column(String, nullable=False)
    action = Column(Enum(AccessLogAction), nullable=False)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    status = Column(String, nullable=False)  # success, denied, error
    details = Column(String, nullable=True)
