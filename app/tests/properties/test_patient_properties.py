"""Property-based tests for patient management"""
import pytest
from hypothesis import given, strategies as st
from datetime import date, datetime, timedelta
from app.services.patient_service import PatientService
from app.models.patient import Patient, PatientStatus
from app.database import SessionLocal
import logging

logger = logging.getLogger(__name__)

# Strategies for generating test data
patient_name_strategy = st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cc', 'Cs')))
contact_info_strategy = st.emails()
insurance_id_strategy = st.text(min_size=5, max_size=20, alphabet=st.characters(min_codepoint=48, max_codepoint=122))

def valid_date_of_birth():
    """Generate valid date of birth (between 18 and 100 years ago)"""
    today = date.today()
    min_date = today - timedelta(days=365*100)
    max_date = today - timedelta(days=365*18)
    return st.dates(min_value=min_date, max_value=max_date)

@pytest.mark.properties
class TestPatientProperties:
    """Property-based tests for patient management"""
    
    @given(
        name=patient_name_strategy,
        contact_info=contact_info_strategy,
        insurance_id=insurance_id_strategy,
        dob=valid_date_of_birth()
    )
    def test_patient_registration_idempotence(self, name, contact_info, insurance_id, dob):
        """
        **Validates: Requirements 1.1**
        
        Property 1: Patient Registration Idempotence
        For any valid patient registration data, registering the same patient twice 
        should result in only one patient record in the system (or an error on the second attempt).
        """
        db = SessionLocal()
        try:
            service = PatientService(db)
            
            patient_data = {
                'name': name,
                'date_of_birth': dob,
                'contact_info': contact_info,
                'insurance_id': insurance_id
            }
            
            # First registration should succeed
            patient1 = service.register_patient(patient_data)
            assert patient1 is not None
            assert patient1.name == name
            assert patient1.status == PatientStatus.ACTIVE
            
            # Second registration with same data should fail
            with pytest.raises(ValueError):
                service.register_patient(patient_data)
            
            # Verify only one patient exists with this data
            patients = service.list_patients({'name': name})
            assert len(patients) == 1
            assert patients[0].id == patient1.id
            
        finally:
            db.close()
    
    @given(
        name=patient_name_strategy,
        contact_info=contact_info_strategy,
        insurance_id=insurance_id_strategy,
        dob=valid_date_of_birth()
    )
    def test_patient_data_persistence(self, name, contact_info, insurance_id, dob):
        """
        **Validates: Requirements 1.4**
        
        Property 2: Patient Data Persistence
        For any patient record created in the system, retrieving that patient by ID 
        should return the exact same data that was stored.
        """
        db = SessionLocal()
        try:
            service = PatientService(db)
            
            patient_data = {
                'name': name,
                'date_of_birth': dob,
                'contact_info': contact_info,
                'insurance_id': insurance_id
            }
            
            # Register patient
            patient1 = service.register_patient(patient_data)
            patient_id = patient1.id
            
            # Retrieve patient
            patient2 = service.get_patient(patient_id)
            
            # Verify all data matches
            assert patient2 is not None
            assert patient2.id == patient1.id
            assert patient2.name == name
            assert patient2.date_of_birth == dob
            assert patient2.contact_info == contact_info
            assert patient2.insurance_id == insurance_id
            assert patient2.status == PatientStatus.ACTIVE
            
        finally:
            db.close()
