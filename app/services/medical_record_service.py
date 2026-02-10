"""Medical record management service"""
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.medical_record import MedicalRecord, Diagnosis, Treatment, ClinicalNote
import logging

logger = logging.getLogger(__name__)

class MedicalRecordService:
    """Service for medical record management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_record(self, patient_id: str, created_by: str) -> MedicalRecord:
        """Create a new medical record"""
        record_id = str(uuid.uuid4())
        record = MedicalRecord(
            id=record_id,
            patient_id=patient_id,
            created_by=created_by,
            version=1
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        logger.info(f"Medical record created: {record_id}")
        return record
    
    def get_record(self, patient_id: str, version: int = None) -> Optional[MedicalRecord]:
        """Get patient's medical record"""
        query = self.db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient_id)
        if version:
            query = query.filter(MedicalRecord.version == version)
        return query.first()
    
    def add_diagnosis(self, patient_id: str, diagnosis_code: str, description: str) -> Diagnosis:
        """Add diagnosis to medical record"""
        record = self.get_record(patient_id)
        if not record:
            raise ValueError(f"Medical record not found for patient: {patient_id}")
        
        diagnosis_id = str(uuid.uuid4())
        diagnosis = Diagnosis(
            id=diagnosis_id,
            record_id=record.id,
            diagnosis_code=diagnosis_code,
            description=description
        )
        self.db.add(diagnosis)
        self.db.commit()
        self.db.refresh(diagnosis)
        logger.info(f"Diagnosis added: {diagnosis_id}")
        return diagnosis
    
    def add_treatment(self, patient_id: str, treatment_type: str, description: str, 
                     date_started: datetime, date_ended: datetime = None) -> Treatment:
        """Add treatment to medical record"""
        record = self.get_record(patient_id)
        if not record:
            raise ValueError(f"Medical record not found for patient: {patient_id}")
        
        treatment_id = str(uuid.uuid4())
        treatment = Treatment(
            id=treatment_id,
            record_id=record.id,
            treatment_type=treatment_type,
            description=description,
            date_started=date_started,
            date_ended=date_ended
        )
        self.db.add(treatment)
        self.db.commit()
        self.db.refresh(treatment)
        logger.info(f"Treatment added: {treatment_id}")
        return treatment
    
    def add_clinical_note(self, patient_id: str, note_text: str, created_by: str) -> ClinicalNote:
        """Add clinical note to medical record"""
        record = self.get_record(patient_id)
        if not record:
            raise ValueError(f"Medical record not found for patient: {patient_id}")
        
        note_id = str(uuid.uuid4())
        note = ClinicalNote(
            id=note_id,
            record_id=record.id,
            note_text=note_text,
            created_by=created_by
        )
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        logger.info(f"Clinical note added: {note_id}")
        return note
    
    def get_record_history(self, patient_id: str) -> List[MedicalRecord]:
        """Get medical record version history"""
        return self.db.query(MedicalRecord).filter(
            MedicalRecord.patient_id == patient_id
        ).order_by(MedicalRecord.version.desc()).all()
    
    def verify_access(self, user_id: str, patient_id: str) -> bool:
        """Verify user has access to patient's medical record"""
        # TODO: Implement access control logic
        return True
