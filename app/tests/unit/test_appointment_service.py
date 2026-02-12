"""Unit tests for appointment service"""
import pytest
from datetime import datetime, timedelta
from services.appointment_service import AppointmentService
from models.appointment import AppointmentStatus
from database import SessionLocal

@pytest.fixture
def db():
    """Database session fixture"""
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture
def appointment_service(db):
    """Appointment service fixture"""
    return AppointmentService(db)

class TestAppointmentService:
    """Unit tests for AppointmentService"""
    
    def test_schedule_appointment_success(self, appointment_service):
        """Test successful appointment scheduling"""
        patient_id = "patient-123"
        doctor_id = "doctor-456"
        scheduled_time = datetime.utcnow() + timedelta(days=1)
        
        appointment = appointment_service.schedule_appointment(
            patient_id,
            doctor_id,
            scheduled_time
        )
        
        assert appointment is not None
        assert appointment.patient_id == patient_id
        assert appointment.doctor_id == doctor_id
        assert appointment.status == AppointmentStatus.SCHEDULED
    
    def test_schedule_appointment_double_booking_prevention(self, appointment_service):
        """Test double-booking prevention"""
        patient_id_1 = "patient-123"
        patient_id_2 = "patient-789"
        doctor_id = "doctor-456"
        scheduled_time = datetime.utcnow() + timedelta(days=1)
        
        # Schedule first appointment
        appointment_service.schedule_appointment(
            patient_id_1,
            doctor_id,
            scheduled_time
        )
        
        # Try to schedule second appointment at same time
        with pytest.raises(ValueError, match="Time slot is already booked|Doctor is not available"):
            appointment_service.schedule_appointment(
                patient_id_2,
                doctor_id,
                scheduled_time
            )
    
    def test_get_available_slots(self, appointment_service):
        """Test getting available appointment slots"""
        doctor_id = "doctor-456"
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=7)
        
        slots = appointment_service.get_available_slots(
            doctor_id,
            (start_date, end_date)
        )
        
        assert slots is not None
        assert len(slots) > 0
    
    def test_cancel_appointment(self, appointment_service):
        """Test appointment cancellation"""
        patient_id = "patient-123"
        doctor_id = "doctor-456"
        scheduled_time = datetime.utcnow() + timedelta(days=1)
        
        appointment = appointment_service.schedule_appointment(
            patient_id,
            doctor_id,
            scheduled_time
        )
        
        cancelled = appointment_service.cancel_appointment(appointment.id)
        
        assert cancelled.status == AppointmentStatus.CANCELLED
    
    def test_cancel_appointment_frees_slot(self, appointment_service):
        """Test that cancelling appointment frees the slot"""
        patient_id_1 = "patient-123"
        patient_id_2 = "patient-789"
        doctor_id = "doctor-456"
        scheduled_time = datetime.utcnow() + timedelta(days=1)
        
        # Schedule first appointment
        appointment = appointment_service.schedule_appointment(
            patient_id_1,
            doctor_id,
            scheduled_time
        )
        
        # Cancel it
        appointment_service.cancel_appointment(appointment.id)
        
        # Now should be able to schedule another appointment at same time
        new_appointment = appointment_service.schedule_appointment(
            patient_id_2,
            doctor_id,
            scheduled_time
        )
        
        assert new_appointment is not None
        assert new_appointment.patient_id == patient_id_2
    
    def test_reschedule_appointment(self, appointment_service):
        """Test rescheduling appointment"""
        patient_id = "patient-123"
        doctor_id = "doctor-456"
        scheduled_time = datetime.utcnow() + timedelta(days=1)
        new_time = datetime.utcnow() + timedelta(days=2)
        
        appointment = appointment_service.schedule_appointment(
            patient_id,
            doctor_id,
            scheduled_time
        )
        
        rescheduled = appointment_service.reschedule_appointment(
            appointment.id,
            new_time
        )
        
        assert rescheduled.scheduled_time == new_time
    
    def test_get_appointments_by_patient(self, appointment_service):
        """Test getting appointments by patient"""
        patient_id = "patient-123"
        doctor_id = "doctor-456"
        scheduled_time = datetime.utcnow() + timedelta(days=1)
        
        appointment_service.schedule_appointment(
            patient_id,
            doctor_id,
            scheduled_time
        )
        
        appointments = appointment_service.get_appointments(patient_id=patient_id)
        
        assert len(appointments) >= 1
        assert all(app.patient_id == patient_id for app in appointments)
    
    def test_get_appointments_by_doctor(self, appointment_service):
        """Test getting appointments by doctor"""
        patient_id = "patient-123"
        doctor_id = "doctor-456"
        scheduled_time = datetime.utcnow() + timedelta(days=1)
        
        appointment_service.schedule_appointment(
            patient_id,
            doctor_id,
            scheduled_time
        )
        
        appointments = appointment_service.get_appointments(doctor_id=doctor_id)
        
        assert len(appointments) >= 1
        assert all(app.doctor_id == doctor_id for app in appointments)
    
    def test_check_doctor_availability(self, appointment_service):
        """Test checking doctor availability"""
        doctor_id = "doctor-456"
        scheduled_time = datetime.utcnow() + timedelta(days=1)
        
        # Should be available initially
        available = appointment_service.check_doctor_availability(doctor_id, scheduled_time)
        assert available is True
        
        # Schedule appointment
        appointment_service.schedule_appointment(
            "patient-123",
            doctor_id,
            scheduled_time
        )
        
        # Should not be available now
        available = appointment_service.check_doctor_availability(doctor_id, scheduled_time)
        assert available is False
