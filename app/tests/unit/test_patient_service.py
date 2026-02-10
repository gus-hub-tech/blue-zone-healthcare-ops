"""Unit tests for patient service"""
import pytest
from datetime import date
from app.services.patient_service import PatientService
from app.models.patient import PatientStatus
from app.database import SessionLocal
import uuid

@pytest.fixture
def db():
    """Database session fixture"""
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture
def patient_service(db):
    """Patient service fixture"""
    return PatientService(db)

class TestPatientService:
    """Unit tests for PatientService"""
    
    def test_register_patient_success(self, patient_service):
        """Test successful patient registration"""
        unique_id = str(uuid.uuid4())[:8]
        patient_data = {
            'name': f'John Doe {unique_id}',
            'date_of_birth': date(1990, 1, 1),
            'contact_info': f'john{unique_id}@example.com',
            'insurance_id': 'INS123456'
        }
        
        patient = patient_service.register_patient(patient_data)
        
        assert patient is not None
        assert patient.name == patient_data['name']
        assert patient.status == PatientStatus.ACTIVE
    
    def test_register_patient_missing_field(self, patient_service):
        """Test patient registration with missing field"""
        patient_data = {
            'name': 'John Doe',
            'date_of_birth': date(1990, 1, 1),
            # Missing contact_info
            'insurance_id': 'INS123456'
        }
        
        with pytest.raises(ValueError):
            patient_service.register_patient(patient_data)
    
    def test_get_patient(self, patient_service):
        """Test retrieving patient"""
        unique_id = str(uuid.uuid4())[:8]
        patient_data = {
            'name': f'Jane Doe {unique_id}',
            'date_of_birth': date(1985, 5, 15),
            'contact_info': f'jane{unique_id}@example.com',
            'insurance_id': 'INS789012'
        }
        
        created = patient_service.register_patient(patient_data)
        retrieved = patient_service.get_patient(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == patient_data['name']
    
    def test_update_patient(self, patient_service):
        """Test updating patient"""
        unique_id = str(uuid.uuid4())[:8]
        patient_data = {
            'name': f'Bob Smith {unique_id}',
            'date_of_birth': date(1980, 3, 20),
            'contact_info': f'bob{unique_id}@example.com',
            'insurance_id': 'INS345678'
        }
        
        patient = patient_service.register_patient(patient_data)
        
        updates = {
            'contact_info': f'bob.smith{unique_id}@example.com'
        }
        
        updated = patient_service.update_patient(patient.id, updates)
        
        assert updated.contact_info == updates['contact_info']
    
    def test_deactivate_patient(self, patient_service):
        """Test deactivating patient"""
        unique_id = str(uuid.uuid4())[:8]
        patient_data = {
            'name': f'Alice Johnson {unique_id}',
            'date_of_birth': date(1992, 7, 10),
            'contact_info': f'alice{unique_id}@example.com',
            'insurance_id': 'INS901234'
        }
        
        patient = patient_service.register_patient(patient_data)
        deactivated = patient_service.deactivate_patient(patient.id)
        
        assert deactivated.status == PatientStatus.INACTIVE
    
    def test_list_patients(self, patient_service):
        """Test listing patients"""
        # Register multiple patients with unique data
        for i in range(3):
            unique_id = str(uuid.uuid4())[:8]
            patient_service.register_patient({
                'name': f'Patient {i} {unique_id}',
                'date_of_birth': date(1990, 1, 1),
                'contact_info': f'patient{i}{unique_id}@example.com',
                'insurance_id': f'INS{i:06d}'
            })
        
        patients = patient_service.list_patients()
        assert len(patients) >= 3
