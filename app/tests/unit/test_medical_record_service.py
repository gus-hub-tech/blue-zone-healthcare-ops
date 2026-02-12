"""Unit tests for medical record service"""
import pytest
from datetime import datetime, date
from services.medical_record_service import MedicalRecordService
from models.medical_record import MedicalRecord
from database import SessionLocal
import uuid

@pytest.fixture
def db():
    """Database session fixture"""
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture
def medical_record_service(db):
    """Medical record service fixture"""
    return MedicalRecordService(db)

class TestMedicalRecordService:
    """Unit tests for MedicalRecordService"""
    
    def test_create_record_success(self, medical_record_service):
        """Test successful medical record creation"""
        patient_id = "patient-123"
        created_by = "doctor-456"
        
        record = medical_record_service.create_record(patient_id, created_by)
        
        assert record is not None
        assert record.patient_id == patient_id
        assert record.created_by == created_by
        assert record.version == 1
    
    def test_get_record(self, medical_record_service):
        """Test retrieving medical record"""
        patient_id = f"patient-{str(uuid.uuid4())[:8]}"
        created_by = "doctor-101"
        
        created = medical_record_service.create_record(patient_id, created_by)
        retrieved = medical_record_service.get_record(patient_id)
        
        assert retrieved is not None
        assert retrieved.patient_id == patient_id
    
    def test_add_diagnosis(self, medical_record_service):
        """Test adding diagnosis to medical record"""
        patient_id = "patient-202"
        created_by = "doctor-303"
        
        medical_record_service.create_record(patient_id, created_by)
        
        diagnosis = medical_record_service.add_diagnosis(
            patient_id,
            "ICD-10-001",
            "Hypertension"
        )
        
        assert diagnosis is not None
        assert diagnosis.diagnosis_code == "ICD-10-001"
        assert diagnosis.description == "Hypertension"
    
    def test_add_diagnosis_no_record(self, medical_record_service):
        """Test adding diagnosis when record doesn't exist"""
        with pytest.raises(ValueError):
            medical_record_service.add_diagnosis(
                "nonexistent-patient",
                "ICD-10-001",
                "Hypertension"
            )
    
    def test_add_treatment(self, medical_record_service):
        """Test adding treatment to medical record"""
        patient_id = "patient-404"
        created_by = "doctor-505"
        
        medical_record_service.create_record(patient_id, created_by)
        
        start_date = datetime.utcnow()
        treatment = medical_record_service.add_treatment(
            patient_id,
            "medication",
            "Aspirin 100mg daily",
            start_date
        )
        
        assert treatment is not None
        assert treatment.treatment_type == "medication"
        assert treatment.description == "Aspirin 100mg daily"
    
    def test_add_clinical_note(self, medical_record_service):
        """Test adding clinical note to medical record"""
        patient_id = "patient-606"
        created_by = "doctor-707"
        
        medical_record_service.create_record(patient_id, created_by)
        
        note = medical_record_service.add_clinical_note(
            patient_id,
            "Patient shows improvement",
            created_by
        )
        
        assert note is not None
        assert note.note_text == "Patient shows improvement"
        assert note.created_by == created_by
    
    def test_get_record_history(self, medical_record_service):
        """Test retrieving medical record version history"""
        patient_id = "patient-808"
        created_by = "doctor-909"
        
        medical_record_service.create_record(patient_id, created_by)
        medical_record_service.add_diagnosis(patient_id, "ICD-10-001", "Hypertension")
        
        history = medical_record_service.get_record_history(patient_id)
        
        assert history is not None
        assert len(history) >= 1
    
    def test_verify_access(self, medical_record_service):
        """Test access verification"""
        patient_id = "patient-1010"
        user_id = "user-1111"
        
        # Currently returns True for all users (TODO in service)
        result = medical_record_service.verify_access(user_id, patient_id)
        assert result is True
