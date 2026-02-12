"""Patient management routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from database import get_db
from services.patient_service import PatientService
from models.patient import PatientStatus

router = APIRouter(prefix="/patients", tags=["patients"])

# Pydantic models
class PatientCreate(BaseModel):
    """Patient creation schema"""
    name: str
    date_of_birth: date
    contact_info: str
    insurance_id: str

class PatientUpdate(BaseModel):
    """Patient update schema"""
    name: Optional[str] = None
    contact_info: Optional[str] = None
    insurance_id: Optional[str] = None

class PatientResponse(BaseModel):
    """Patient response schema"""
    id: str
    name: str
    date_of_birth: date
    contact_info: str
    insurance_id: str
    status: str
    
    class Config:
        from_attributes = True

@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def register_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    """Register a new patient"""
    try:
        service = PatientService(db)
        created = service.register_patient(patient.dict())
        return created
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: str, db: Session = Depends(get_db)):
    """Get patient by ID"""
    service = PatientService(db)
    patient = service.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return patient

@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(patient_id: str, updates: PatientUpdate, db: Session = Depends(get_db)):
    """Update patient information"""
    try:
        service = PatientService(db)
        updated = service.update_patient(patient_id, updates.dict(exclude_unset=True))
        return updated
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("", response_model=List[PatientResponse])
def list_patients(status_filter: Optional[str] = None, name: Optional[str] = None, db: Session = Depends(get_db)):
    """List patients with optional filtering"""
    service = PatientService(db)
    filters = {}
    if status_filter:
        filters['status'] = status_filter
    if name:
        filters['name'] = name
    
    patients = service.list_patients(filters if filters else None)
    return patients

@router.patch("/{patient_id}/status")
def change_patient_status(patient_id: str, new_status: str, db: Session = Depends(get_db)):
    """Change patient status"""
    try:
        service = PatientService(db)
        if new_status == "inactive":
            patient = service.deactivate_patient(patient_id)
        else:
            patient = service.update_patient(patient_id, {'status': new_status})
        return patient
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
