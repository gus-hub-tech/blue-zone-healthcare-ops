"""Audit logging models"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from datetime import datetime
from models import Base

class PatientAuditLog(Base):
    """Patient audit log model"""
    __tablename__ = "patient_audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(String, index=True, nullable=False)
    patient_id = Column(String, index=True, nullable=False)
    action = Column(String, nullable=False)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False)
