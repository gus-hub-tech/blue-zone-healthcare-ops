"""Medical record models"""
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, Enum
from sqlalchemy.sql import func
from datetime import datetime
import enum
from models import Base

class MedicalRecord(Base):
    """Medical record model"""
    __tablename__ = "medical_records"
    
    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False, index=True)
    created_by = Column(String, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

class Diagnosis(Base):
    """Diagnosis model"""
    __tablename__ = "diagnoses"
    
    id = Column(String, primary_key=True, index=True)
    record_id = Column(String, ForeignKey("medical_records.id"), nullable=False, index=True)
    diagnosis_code = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    date_recorded = Column(DateTime, server_default=func.now(), nullable=False)

class Treatment(Base):
    """Treatment model"""
    __tablename__ = "treatments"
    
    id = Column(String, primary_key=True, index=True)
    record_id = Column(String, ForeignKey("medical_records.id"), nullable=False, index=True)
    treatment_type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    date_started = Column(DateTime, nullable=False)
    date_ended = Column(DateTime, nullable=True)

class ClinicalNote(Base):
    """Clinical note model"""
    __tablename__ = "clinical_notes"
    
    id = Column(String, primary_key=True, index=True)
    record_id = Column(String, ForeignKey("medical_records.id"), nullable=False, index=True)
    note_text = Column(Text, nullable=False)
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
