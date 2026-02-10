"""Prescription management routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.prescription_service import PrescriptionService

router = APIRouter(prefix="/prescriptions", tags=["prescriptions"])

class PrescriptionCreate(BaseModel):
    """Prescription creation schema"""
    patient_id: str
    doctor_id: str
    medication_id: str
    dosage: str
    frequency: str
    duration: str

class PrescriptionResponse(BaseModel):
    """Prescription response schema"""
    id: str
    patient_id: str
    doctor_id: str
    medication_id: str
    dosage: str
    frequency: str
    duration: str
    status: str
    
    class Config:
        from_attributes = True

@router.post("", response_model=PrescriptionResponse, status_code=status.HTTP_201_CREATED)
def create_prescription(prescription: PrescriptionCreate, db: Session = Depends(get_db)):
    """Create a prescription"""
    try:
        service = PrescriptionService(db)
        created = service.create_prescription(prescription.dict())
        return created
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{prescription_id}", response_model=PrescriptionResponse)
def get_prescription(prescription_id: str, db: Session = Depends(get_db)):
    """Get prescription by ID"""
    service = PrescriptionService(db)
    prescription = service.get_prescription(prescription_id)
    if not prescription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prescription not found")
    return prescription

@router.get("/patient/{patient_id}/prescriptions", response_model=List[PrescriptionResponse])
def get_patient_prescriptions(patient_id: str, db: Session = Depends(get_db)):
    """Get patient's prescriptions"""
    service = PrescriptionService(db)
    prescriptions = service.get_patient_prescriptions(patient_id)
    return prescriptions

@router.patch("/{prescription_id}/status")
def update_prescription_status(prescription_id: str, status: str, db: Session = Depends(get_db)):
    """Update prescription status"""
    try:
        service = PrescriptionService(db)
        updated = service.update_prescription_status(prescription_id, status)
        return updated
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
