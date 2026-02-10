"""Prescription management service"""
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.prescription import Prescription, PrescriptionItem, PrescriptionStatus
from app.models.inventory import InventoryItem
import logging

logger = logging.getLogger(__name__)

class PrescriptionService:
    """Service for prescription management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_prescription(self, prescription_data: dict) -> Prescription:
        """Create a new prescription"""
        required_fields = ['patient_id', 'doctor_id', 'medication_id', 'dosage', 'frequency', 'duration']
        for field in required_fields:
            if field not in prescription_data or not prescription_data[field]:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate medication exists
        medication = self.db.query(InventoryItem).filter(
            InventoryItem.id == prescription_data['medication_id']
        ).first()
        
        if not medication:
            raise ValueError(f"Medication not found: {prescription_data['medication_id']}")
        
        prescription_id = str(uuid.uuid4())
        prescription = Prescription(
            id=prescription_id,
            patient_id=prescription_data['patient_id'],
            doctor_id=prescription_data['doctor_id'],
            medication_id=prescription_data['medication_id'],
            dosage=prescription_data['dosage'],
            frequency=prescription_data['frequency'],
            duration=prescription_data['duration'],
            status=PrescriptionStatus.ACTIVE
        )
        
        self.db.add(prescription)
        self.db.commit()
        self.db.refresh(prescription)
        logger.info(f"Prescription created: {prescription_id}")
        return prescription
    
    def get_prescription(self, prescription_id: str) -> Optional[Prescription]:
        """Get prescription by ID"""
        return self.db.query(Prescription).filter(Prescription.id == prescription_id).first()
    
    def get_patient_prescriptions(self, patient_id: str) -> List[Prescription]:
        """Get all prescriptions for a patient"""
        return self.db.query(Prescription).filter(
            Prescription.patient_id == patient_id
        ).order_by(Prescription.created_at.desc()).all()
    
    def update_prescription_status(self, prescription_id: str, status: str) -> Prescription:
        """Update prescription status"""
        prescription = self.get_prescription(prescription_id)
        if not prescription:
            raise ValueError(f"Prescription not found: {prescription_id}")
        
        prescription.status = PrescriptionStatus(status)
        prescription.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(prescription)
        logger.info(f"Prescription status updated: {prescription_id} -> {status}")
        return prescription
    
    def validate_medication(self, medication_id: str) -> bool:
        """Validate medication exists in inventory"""
        medication = self.db.query(InventoryItem).filter(
            InventoryItem.id == medication_id
        ).first()
        return medication is not None
    
    def get_prescription_history(self, patient_id: str) -> List[Prescription]:
        """Get prescription history for a patient"""
        return self.db.query(Prescription).filter(
            Prescription.patient_id == patient_id
        ).order_by(Prescription.created_at.desc()).all()
