"""Appointment models"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.models import Base

class AppointmentStatus(str, enum.Enum):
    """Appointment status enumeration"""
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Appointment(Base):
    """Appointment model"""
    __tablename__ = "appointments"
    
    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(String, ForeignKey("staff.id"), nullable=False, index=True)
    scheduled_time = Column(DateTime, nullable=False, index=True)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

class AppointmentSlot(Base):
    """Appointment slot model"""
    __tablename__ = "appointment_slots"
    
    id = Column(String, primary_key=True, index=True)
    doctor_id = Column(String, ForeignKey("staff.id"), nullable=False, index=True)
    slot_date = Column(DateTime, nullable=False, index=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
