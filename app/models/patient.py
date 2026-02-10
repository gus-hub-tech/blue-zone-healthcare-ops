"""Patient model"""
from sqlalchemy import Column, String, Date, DateTime, Enum
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.models import Base

class PatientStatus(str, enum.Enum):
    """Patient status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"

class Patient(Base):
    """Patient model"""
    __tablename__ = "patients"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    date_of_birth = Column(Date, nullable=False)
    contact_info = Column(String, nullable=False)
    insurance_id = Column(String, nullable=False)
    status = Column(Enum(PatientStatus), default=PatientStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
