from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class PatientAuditLog(Base):
    __tablename__ = "patient_audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(String, index=True)      # Who accessed it
    patient_id = Column(String, index=True)     # Whose record it is
    action = Column(String)                     # View, Update, Delete
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)