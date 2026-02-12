"""Appointment scheduling routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from database import get_db
from services.appointment_service import AppointmentService

router = APIRouter(prefix="/appointments", tags=["appointments"])

class AppointmentCreate(BaseModel):
    """Appointment creation schema"""
    patient_id: str
    doctor_id: str
    scheduled_time: datetime

class AppointmentResponse(BaseModel):
    """Appointment response schema"""
    id: str
    patient_id: str
    doctor_id: str
    scheduled_time: datetime
    status: str
    
    class Config:
        from_attributes = True

@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def schedule_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    """Schedule an appointment"""
    try:
        service = AppointmentService(db)
        created = service.schedule_appointment(
            appointment.patient_id,
            appointment.doctor_id,
            appointment.scheduled_time
        )
        return created
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(appointment_id: str, db: Session = Depends(get_db)):
    """Get appointment by ID"""
    service = AppointmentService(db)
    from models.appointment import Appointment
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    return appointment

@router.delete("/{appointment_id}")
def cancel_appointment(appointment_id: str, db: Session = Depends(get_db)):
    """Cancel an appointment"""
    try:
        service = AppointmentService(db)
        cancelled = service.cancel_appointment(appointment_id)
        return cancelled
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/doctor/{doctor_id}/available-slots")
def get_available_slots(doctor_id: str, start_date: datetime, end_date: datetime, db: Session = Depends(get_db)):
    """Get available appointment slots for a doctor"""
    service = AppointmentService(db)
    slots = service.get_available_slots(doctor_id, (start_date, end_date))
    return {"available_slots": slots}

@router.get("/patient/{patient_id}/appointments", response_model=List[AppointmentResponse])
def get_patient_appointments(patient_id: str, db: Session = Depends(get_db)):
    """Get patient's appointments"""
    service = AppointmentService(db)
    appointments = service.get_appointments(patient_id=patient_id)
    return appointments
