"""Patient management service"""
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.patient import Patient, PatientStatus
from models.audit import PatientAuditLog
import logging

logger = logging.getLogger(__name__)

class PatientService:
    """Service for patient management operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def register_patient(self, patient_data: dict) -> Patient:
        """
        Register a new patient
        
        Args:
            patient_data: Dictionary with patient information
            
        Returns:
            Patient: Created patient record
            
        Raises:
            ValueError: If patient already exists or validation fails
        """
        # Validate required fields
        required_fields = ['name', 'date_of_birth', 'contact_info', 'insurance_id']
        for field in required_fields:
            if field not in patient_data or not patient_data[field]:
                raise ValueError(f"Missing required field: {field}")
        
        # Check if patient with same details already exists
        existing = self.db.query(Patient).filter(
            Patient.name == patient_data['name'],
            Patient.date_of_birth == patient_data['date_of_birth'],
            Patient.contact_info == patient_data['contact_info']
        ).first()
        
        if existing:
            raise ValueError("Patient with same details already exists")
        
        # Create new patient
        patient_id = str(uuid.uuid4())
        patient = Patient(
            id=patient_id,
            name=patient_data['name'],
            date_of_birth=patient_data['date_of_birth'],
            contact_info=patient_data['contact_info'],
            insurance_id=patient_data['insurance_id'],
            status=PatientStatus.ACTIVE
        )
        
        try:
            self.db.add(patient)
            self.db.commit()
            self.db.refresh(patient)
            logger.info(f"Patient registered: {patient_id}")
            return patient
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Error registering patient: {e}")
            raise ValueError("Error registering patient")
    
    def get_patient(self, patient_id: str) -> Optional[Patient]:
        """
        Get patient by ID
        
        Args:
            patient_id: Patient ID
            
        Returns:
            Patient: Patient record or None if not found
        """
        return self.db.query(Patient).filter(Patient.id == patient_id).first()
    
    def update_patient(self, patient_id: str, updates: dict, user_id: str = None) -> Patient:
        """
        Update patient information
        
        Args:
            patient_id: Patient ID
            updates: Dictionary with fields to update
            user_id: User ID for audit trail
            
        Returns:
            Patient: Updated patient record
            
        Raises:
            ValueError: If patient not found
        """
        patient = self.get_patient(patient_id)
        if not patient:
            raise ValueError(f"Patient not found: {patient_id}")
        
        # Update allowed fields
        allowed_fields = ['name', 'contact_info', 'insurance_id']
        for field in allowed_fields:
            if field in updates:
                setattr(patient, field, updates[field])
        
        patient.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(patient)
            
            # Log audit trail
            if user_id:
                audit_log = PatientAuditLog(
                    doctor_id=user_id,
                    patient_id=patient_id,
                    action="UPDATE"
                )
                self.db.add(audit_log)
                self.db.commit()
            
            logger.info(f"Patient updated: {patient_id}")
            return patient
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating patient: {e}")
            raise ValueError("Error updating patient")
    
    def list_patients(self, filters: dict = None) -> List[Patient]:
        """
        List patients with optional filtering
        
        Args:
            filters: Optional filter criteria
            
        Returns:
            List[Patient]: List of patient records
        """
        query = self.db.query(Patient)
        
        if filters:
            if 'status' in filters:
                query = query.filter(Patient.status == filters['status'])
            if 'name' in filters:
                query = query.filter(Patient.name.ilike(f"%{filters['name']}%"))
        
        return query.all()
    
    def deactivate_patient(self, patient_id: str, user_id: str = None) -> Patient:
        """
        Deactivate a patient
        
        Args:
            patient_id: Patient ID
            user_id: User ID for audit trail
            
        Returns:
            Patient: Updated patient record
            
        Raises:
            ValueError: If patient not found
        """
        patient = self.get_patient(patient_id)
        if not patient:
            raise ValueError(f"Patient not found: {patient_id}")
        
        patient.status = PatientStatus.INACTIVE
        patient.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(patient)
            
            # Log audit trail
            if user_id:
                audit_log = PatientAuditLog(
                    doctor_id=user_id,
                    patient_id=patient_id,
                    action="DEACTIVATE"
                )
                self.db.add(audit_log)
                self.db.commit()
            
            logger.info(f"Patient deactivated: {patient_id}")
            return patient
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deactivating patient: {e}")
            raise ValueError("Error deactivating patient")
    
    def get_patient_history(self, patient_id: str) -> List[PatientAuditLog]:
        """
        Get patient audit history
        
        Args:
            patient_id: Patient ID
            
        Returns:
            List[PatientAuditLog]: List of audit log entries
        """
        return self.db.query(PatientAuditLog).filter(
            PatientAuditLog.patient_id == patient_id
        ).order_by(PatientAuditLog.timestamp.desc()).all()
