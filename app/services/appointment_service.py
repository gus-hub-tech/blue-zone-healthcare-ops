"""Appointment scheduling service"""
import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from models.appointment import Appointment, AppointmentSlot, AppointmentStatus
import logging

logger = logging.getLogger(__name__)

class AppointmentService:
    """Service for appointment scheduling"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def schedule_appointment(self, patient_id: str, doctor_id: str, scheduled_time: datetime) -> Appointment:
        """Schedule an appointment"""
        # Check if doctor is available
        if not self.check_doctor_availability(doctor_id, scheduled_time):
            raise ValueError("Doctor is not available at the requested time")
        
        # Check for double-booking
        existing = self.db.query(Appointment).filter(
            and_(
                Appointment.doctor_id == doctor_id,
                Appointment.scheduled_time == scheduled_time,
                Appointment.status == AppointmentStatus.SCHEDULED
            )
        ).first()
        
        if existing:
            raise ValueError("Time slot is already booked")
        
        appointment_id = str(uuid.uuid4())
        appointment = Appointment(
            id=appointment_id,
            patient_id=patient_id,
            doctor_id=doctor_id,
            scheduled_time=scheduled_time,
            status=AppointmentStatus.SCHEDULED
        )
        
        self.db.add(appointment)
        self.db.commit()
        self.db.refresh(appointment)
        logger.info(f"Appointment scheduled: {appointment_id}")
        return appointment
    
    def get_available_slots(self, doctor_id: str, date_range: tuple) -> List[datetime]:
        """Get available appointment slots for a doctor"""
        start_date, end_date = date_range
        
        # Get all booked appointments
        booked = self.db.query(Appointment).filter(
            and_(
                Appointment.doctor_id == doctor_id,
                Appointment.scheduled_time >= start_date,
                Appointment.scheduled_time <= end_date,
                Appointment.status == AppointmentStatus.SCHEDULED
            )
        ).all()
        
        booked_times = {app.scheduled_time for app in booked}
        
        # Generate available slots (30-minute intervals)
        available_slots = []
        current = start_date
        while current <= end_date:
            if current not in booked_times:
                available_slots.append(current)
            current += timedelta(minutes=30)
        
        return available_slots
    
    def cancel_appointment(self, appointment_id: str) -> Appointment:
        """Cancel an appointment"""
        appointment = self.db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise ValueError(f"Appointment not found: {appointment_id}")
        
        appointment.status = AppointmentStatus.CANCELLED
        appointment.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(appointment)
        logger.info(f"Appointment cancelled: {appointment_id}")
        return appointment
    
    def reschedule_appointment(self, appointment_id: str, new_time: datetime) -> Appointment:
        """Reschedule an appointment"""
        appointment = self.db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise ValueError(f"Appointment not found: {appointment_id}")
        
        # Check if new time is available
        if not self.check_doctor_availability(appointment.doctor_id, new_time):
            raise ValueError("Doctor is not available at the new time")
        
        appointment.scheduled_time = new_time
        appointment.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(appointment)
        logger.info(f"Appointment rescheduled: {appointment_id}")
        return appointment
    
    def get_appointments(self, patient_id: str = None, doctor_id: str = None) -> List[Appointment]:
        """Get appointments by patient or doctor"""
        query = self.db.query(Appointment)
        
        if patient_id:
            query = query.filter(Appointment.patient_id == patient_id)
        if doctor_id:
            query = query.filter(Appointment.doctor_id == doctor_id)
        
        return query.all()
    
    def check_doctor_availability(self, doctor_id: str, time_slot: datetime) -> bool:
        """Check if doctor is available at the given time"""
        # Check for conflicting appointments
        conflict = self.db.query(Appointment).filter(
            and_(
                Appointment.doctor_id == doctor_id,
                Appointment.scheduled_time == time_slot,
                Appointment.status == AppointmentStatus.SCHEDULED
            )
        ).first()
        
        return conflict is None
