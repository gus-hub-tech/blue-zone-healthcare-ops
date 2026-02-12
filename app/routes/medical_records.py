"""Medical records routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from database import get_db
from services.medical_record_service import MedicalRecordService

router = APIRouter(prefix="/medical-records", tags=["medical-records"])

class DiagnosisCreate(BaseModel):
    """Diagnosis creation schema"""
    diagnosis_code: str
    description: str

class TreatmentCreate(BaseModel):
    """Treatment creation schema"""
    treatment_type: str
    description: str
    date_started: datetime
    date_ended: datetime = None

class ClinicalNoteCreate(BaseModel):
    """Clinical note creation schema"""
    note_text: str

@router.get("/patient/{patient_id}")
def get_patient_medical_record(patient_id: str, db: Session = Depends(get_db)):
    """Get patient's medical record"""
    service = MedicalRecordService(db)
    record = service.get_record(patient_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medical record not found")
    return record

@router.post("/patient/{patient_id}/diagnoses")
def add_diagnosis(patient_id: str, diagnosis: DiagnosisCreate, db: Session = Depends(get_db)):
    """Add diagnosis to medical record"""
    try:
        service = MedicalRecordService(db)
        created = service.add_diagnosis(patient_id, diagnosis.diagnosis_code, diagnosis.description)
        return created
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/patient/{patient_id}/treatments")
def add_treatment(patient_id: str, treatment: TreatmentCreate, db: Session = Depends(get_db)):
    """Add treatment to medical record"""
    try:
        service = MedicalRecordService(db)
        created = service.add_treatment(
            patient_id,
            treatment.treatment_type,
            treatment.description,
            treatment.date_started,
            treatment.date_ended
        )
        return created
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/patient/{patient_id}/notes")
def add_clinical_note(patient_id: str, note: ClinicalNoteCreate, user_id: str, db: Session = Depends(get_db)):
    """Add clinical note to medical record"""
    try:
        service = MedicalRecordService(db)
        created = service.add_clinical_note(patient_id, note.note_text, user_id)
        return created
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/patient/{patient_id}/history")
def get_medical_record_history(patient_id: str, db: Session = Depends(get_db)):
    """Get medical record version history"""
    service = MedicalRecordService(db)
    history = service.get_record_history(patient_id)
    return history
