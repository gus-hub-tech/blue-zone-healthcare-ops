"""Staff models"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Date
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.models import Base

class StaffRole(str, enum.Enum):
    """Staff role enumeration"""
    DOCTOR = "doctor"
    NURSE = "nurse"
    TECHNICIAN = "technician"
    ADMIN = "admin"

class StaffStatus(str, enum.Enum):
    """Staff status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"

class Staff(Base):
    """Staff model"""
    __tablename__ = "staff"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    role = Column(Enum(StaffRole), nullable=False)
    specialization = Column(String, nullable=True)
    license_number = Column(String, nullable=True, unique=True)
    department_id = Column(String, ForeignKey("departments.id"), nullable=True)
    status = Column(Enum(StaffStatus), default=StaffStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

class StaffCredential(Base):
    """Staff credential model"""
    __tablename__ = "staff_credentials"
    
    id = Column(String, primary_key=True, index=True)
    staff_id = Column(String, ForeignKey("staff.id"), nullable=False, index=True)
    credential_type = Column(String, nullable=False)
    credential_number = Column(String, nullable=False)
    expiry_date = Column(Date, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

class StaffAvailability(Base):
    """Staff availability model"""
    __tablename__ = "staff_availability"
    
    id = Column(String, primary_key=True, index=True)
    staff_id = Column(String, ForeignKey("staff.id"), nullable=False, index=True)
    day_of_week = Column(String, nullable=False)  # Monday, Tuesday, etc.
    start_time = Column(String, nullable=False)  # HH:MM format
    end_time = Column(String, nullable=False)    # HH:MM format
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
