"""Prescription models"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Numeric, Enum
from sqlalchemy.sql import func
from datetime import datetime
import enum
from models import Base

class PrescriptionStatus(str, enum.Enum):
    """Prescription status enumeration"""
    ACTIVE = "active"
    FILLED = "filled"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class Prescription(Base):
    """Prescription model"""
    __tablename__ = "prescriptions"
    
    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(String, ForeignKey("staff.id"), nullable=False, index=True)
    medication_id = Column(String, ForeignKey("inventory_items.id"), nullable=False)
    dosage = Column(String, nullable=False)
    frequency = Column(String, nullable=False)
    duration = Column(String, nullable=False)
    status = Column(Enum(PrescriptionStatus), default=PrescriptionStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

class PrescriptionItem(Base):
    """Prescription item model"""
    __tablename__ = "prescription_items"
    
    id = Column(String, primary_key=True, index=True)
    prescription_id = Column(String, ForeignKey("prescriptions.id"), nullable=False, index=True)
    medication_id = Column(String, ForeignKey("inventory_items.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
