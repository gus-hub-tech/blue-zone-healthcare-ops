"""Unit tests for prescription service"""
import pytest
from datetime import datetime
from services.prescription_service import PrescriptionService
from services.inventory_service import InventoryService
from models.prescription import PrescriptionStatus
from database import SessionLocal

@pytest.fixture
def db():
    """Database session fixture"""
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture
def prescription_service(db):
    """Prescription service fixture"""
    return PrescriptionService(db)

@pytest.fixture
def inventory_service(db):
    """Inventory service fixture"""
    return InventoryService(db)

class TestPrescriptionService:
    """Unit tests for PrescriptionService"""
    
    def test_create_prescription_success(self, prescription_service, inventory_service):
        """Test successful prescription creation"""
        # First create a medication in inventory
        medication = inventory_service.add_inventory_item({
            'name': 'Aspirin',
            'quantity': 100,
            'unit_cost': 0.50,
            'storage_location': 'Pharmacy A'
        })
        
        prescription_data = {
            'patient_id': 'patient-123',
            'doctor_id': 'doctor-456',
            'medication_id': medication.id,
            'dosage': '100mg',
            'frequency': 'twice daily',
            'duration': '30 days'
        }
        
        prescription = prescription_service.create_prescription(prescription_data)
        
        assert prescription is not None
        assert prescription.patient_id == 'patient-123'
        assert prescription.doctor_id == 'doctor-456'
        assert prescription.status == PrescriptionStatus.ACTIVE
    
    def test_create_prescription_missing_field(self, prescription_service):
        """Test prescription creation with missing field"""
        prescription_data = {
            'patient_id': 'patient-123',
            'doctor_id': 'doctor-456',
            # Missing medication_id
            'dosage': '100mg',
            'frequency': 'twice daily',
            'duration': '30 days'
        }
        
        with pytest.raises(ValueError, match="Missing required field"):
            prescription_service.create_prescription(prescription_data)
    
    def test_create_prescription_invalid_medication(self, prescription_service):
        """Test prescription creation with invalid medication"""
        prescription_data = {
            'patient_id': 'patient-123',
            'doctor_id': 'doctor-456',
            'medication_id': 'nonexistent-med',
            'dosage': '100mg',
            'frequency': 'twice daily',
            'duration': '30 days'
        }
        
        with pytest.raises(ValueError, match="Medication not found"):
            prescription_service.create_prescription(prescription_data)
    
    def test_get_prescription(self, prescription_service, inventory_service):
        """Test retrieving prescription"""
        medication = inventory_service.add_inventory_item({
            'name': 'Ibuprofen',
            'quantity': 100,
            'unit_cost': 0.75,
            'storage_location': 'Pharmacy B'
        })
        
        prescription_data = {
            'patient_id': 'patient-789',
            'doctor_id': 'doctor-101',
            'medication_id': medication.id,
            'dosage': '200mg',
            'frequency': 'three times daily',
            'duration': '7 days'
        }
        
        created = prescription_service.create_prescription(prescription_data)
        retrieved = prescription_service.get_prescription(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
    
    def test_get_patient_prescriptions(self, prescription_service, inventory_service):
        """Test getting all prescriptions for a patient"""
        patient_id = 'patient-202'
        
        # Create multiple medications
        medications = []
        for i in range(2):
            med = inventory_service.add_inventory_item({
                'name': f'Medication {i}',
                'quantity': 100,
                'unit_cost': 1.00,
                'storage_location': 'Pharmacy C'
            })
            medications.append(med)
        
        # Create prescriptions
        for med in medications:
            prescription_data = {
                'patient_id': patient_id,
                'doctor_id': 'doctor-303',
                'medication_id': med.id,
                'dosage': '100mg',
                'frequency': 'daily',
                'duration': '30 days'
            }
            prescription_service.create_prescription(prescription_data)
        
        prescriptions = prescription_service.get_patient_prescriptions(patient_id)
        
        assert len(prescriptions) >= 2
        assert all(p.patient_id == patient_id for p in prescriptions)
    
    def test_update_prescription_status(self, prescription_service, inventory_service):
        """Test updating prescription status"""
        medication = inventory_service.add_inventory_item({
            'name': 'Metformin',
            'quantity': 100,
            'unit_cost': 0.25,
            'storage_location': 'Pharmacy D'
        })
        
        prescription_data = {
            'patient_id': 'patient-404',
            'doctor_id': 'doctor-505',
            'medication_id': medication.id,
            'dosage': '500mg',
            'frequency': 'twice daily',
            'duration': '90 days'
        }
        
        prescription = prescription_service.create_prescription(prescription_data)
        
        updated = prescription_service.update_prescription_status(
            prescription.id,
            'filled'
        )
        
        assert updated.status == PrescriptionStatus.FILLED
    
    def test_validate_medication(self, prescription_service, inventory_service):
        """Test medication validation"""
        medication = inventory_service.add_inventory_item({
            'name': 'Lisinopril',
            'quantity': 100,
            'unit_cost': 0.50,
            'storage_location': 'Pharmacy E'
        })
        
        # Valid medication
        is_valid = prescription_service.validate_medication(medication.id)
        assert is_valid is True
        
        # Invalid medication
        is_valid = prescription_service.validate_medication('nonexistent-med')
        assert is_valid is False
    
    def test_get_prescription_history(self, prescription_service, inventory_service):
        """Test getting prescription history"""
        patient_id = 'patient-606'
        
        medication = inventory_service.add_inventory_item({
            'name': 'Atorvastatin',
            'quantity': 100,
            'unit_cost': 0.60,
            'storage_location': 'Pharmacy F'
        })
        
        prescription_data = {
            'patient_id': patient_id,
            'doctor_id': 'doctor-707',
            'medication_id': medication.id,
            'dosage': '20mg',
            'frequency': 'daily',
            'duration': '180 days'
        }
        
        prescription_service.create_prescription(prescription_data)
        
        history = prescription_service.get_prescription_history(patient_id)
        
        assert history is not None
        assert len(history) >= 1
