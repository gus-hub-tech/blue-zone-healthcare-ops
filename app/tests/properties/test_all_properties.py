"""Comprehensive property-based tests for hospital management system"""
import pytest
from hypothesis import given, strategies as st, settings
from datetime import date, datetime, timedelta
from decimal import Decimal
from services.patient_service import PatientService
from services.appointment_service import AppointmentService
from services.medical_record_service import MedicalRecordService
from services.billing_service import BillingService
from services.inventory_service import InventoryService
from services.staff_service import StaffService
from services.department_service import DepartmentService
from services.prescription_service import PrescriptionService
from services.access_control_service import AccessControlService
from models.patient import PatientStatus
from models.appointment import AppointmentStatus
from models.prescription import PrescriptionStatus
from models.inventory import InventoryTransactionType
from database import SessionLocal
import logging

logger = logging.getLogger(__name__)

# Strategies
patient_name_strategy = st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cc', 'Cs')))
contact_info_strategy = st.emails()
insurance_id_strategy = st.text(min_size=5, max_size=20, alphabet=st.characters(min_codepoint=48, max_codepoint=122))
staff_name_strategy = st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cc', 'Cs')))
department_name_strategy = st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cc', 'Cs')))
inventory_name_strategy = st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cc', 'Cs')))
quantity_strategy = st.integers(min_value=1, max_value=1000)
price_strategy = st.decimals(min_value=Decimal('0.01'), max_value=Decimal('10000'), places=2)

def valid_date_of_birth():
    """Generate valid date of birth"""
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
    @settings(max_examples=50)
    def test_patient_registration_idempotence(self, name, contact_info, insurance_id, dob):
        """**Validates: Requirements 1.1**"""
        db = SessionLocal()
        try:
            service = PatientService(db)
            patient_data = {
                'name': name,
                'date_of_birth': dob,
                'contact_info': contact_info,
                'insurance_id': insurance_id
            }
            
            patient1 = service.register_patient(patient_data)
            assert patient1 is not None
            
            with pytest.raises(ValueError):
                service.register_patient(patient_data)
            
        finally:
            db.close()
    
    @given(
        name=patient_name_strategy,
        contact_info=contact_info_strategy,
        insurance_id=insurance_id_strategy,
        dob=valid_date_of_birth()
    )
    @settings(max_examples=50)
    def test_patient_data_persistence(self, name, contact_info, insurance_id, dob):
        """**Validates: Requirements 1.4**"""
        db = SessionLocal()
        try:
            service = PatientService(db)
            patient_data = {
                'name': name,
                'date_of_birth': dob,
                'contact_info': contact_info,
                'insurance_id': insurance_id
            }
            
            patient1 = service.register_patient(patient_data)
            patient2 = service.get_patient(patient1.id)
            
            assert patient2 is not None
            assert patient2.id == patient1.id
            assert patient2.name == name
            assert patient2.date_of_birth == dob
            assert patient2.contact_info == contact_info
            assert patient2.insurance_id == insurance_id
            
        finally:
            db.close()

@pytest.mark.properties
class TestAppointmentProperties:
    """Property-based tests for appointment scheduling"""
    
    @given(
        patient_name=patient_name_strategy,
        doctor_name=staff_name_strategy,
        contact_info=contact_info_strategy,
        insurance_id=insurance_id_strategy,
        dob=valid_date_of_birth()
    )
    @settings(max_examples=30)
    def test_appointment_double_booking_prevention(self, patient_name, doctor_name, contact_info, insurance_id, dob):
        """**Validates: Requirements 3.2**"""
        db = SessionLocal()
        try:
            patient_service = PatientService(db)
            staff_service = StaffService(db)
            appointment_service = AppointmentService(db)
            
            # Create patient
            patient = patient_service.register_patient({
                'name': patient_name,
                'date_of_birth': dob,
                'contact_info': contact_info,
                'insurance_id': insurance_id
            })
            
            # Create doctor
            doctor = staff_service.add_staff({
                'name': doctor_name,
                'role': 'doctor'
            })
            
            # Schedule appointment
            scheduled_time = datetime.utcnow() + timedelta(days=1)
            app1 = appointment_service.schedule_appointment(patient.id, doctor.id, scheduled_time)
            assert app1 is not None
            
            # Try to schedule at same time - should fail
            with pytest.raises(ValueError):
                appointment_service.schedule_appointment(patient.id, doctor.id, scheduled_time)
            
        finally:
            db.close()

@pytest.mark.properties
class TestBillingProperties:
    """Property-based tests for billing"""
    
    @given(
        amount=price_strategy,
        quantity=quantity_strategy
    )
    @settings(max_examples=50)
    def test_billing_amount_calculation_consistency(self, amount, quantity):
        """**Validates: Requirements 6.2**"""
        db = SessionLocal()
        try:
            service = BillingService(db)
            
            services = [
                {
                    'service_type': 'consultation',
                    'quantity': quantity,
                    'unit_price': amount,
                    'total_price': amount * quantity
                }
            ]
            
            # Calculate charges multiple times
            result1 = service.calculate_charges(services)
            result2 = service.calculate_charges(services)
            
            # Results should be identical
            assert result1['total_amount'] == result2['total_amount']
            assert result1['insurance_coverage'] == result2['insurance_coverage']
            assert result1['patient_responsibility'] == result2['patient_responsibility']
            
        finally:
            db.close()

@pytest.mark.properties
class TestInventoryProperties:
    """Property-based tests for inventory"""
    
    @given(
        name=inventory_name_strategy,
        initial_qty=quantity_strategy,
        consume_qty=quantity_strategy,
        unit_cost=price_strategy
    )
    @settings(max_examples=50)
    def test_inventory_consumption_decrements_stock(self, name, initial_qty, consume_qty, unit_cost):
        """**Validates: Requirements 7.2**"""
        db = SessionLocal()
        try:
            service = InventoryService(db)
            
            # Add inventory
            item = service.add_inventory_item({
                'name': name,
                'quantity': initial_qty,
                'unit_cost': unit_cost,
                'storage_location': 'warehouse'
            })
            
            # Only test if we have enough to consume
            if initial_qty >= consume_qty:
                # Consume inventory
                updated = service.consume_inventory(item.id, consume_qty)
                
                # Verify quantity decreased by exactly the consumed amount
                assert updated.quantity == initial_qty - consume_qty
            
        finally:
            db.close()

@pytest.mark.properties
class TestAppointmentCancellationProperties:
    """Property-based tests for appointment cancellation"""
    
    @given(
        patient_name=patient_name_strategy,
        doctor_name=staff_name_strategy,
        contact_info=contact_info_strategy,
        insurance_id=insurance_id_strategy,
        dob=valid_date_of_birth()
    )
    @settings(max_examples=30)
    def test_appointment_cancellation_frees_slot(self, patient_name, doctor_name, contact_info, insurance_id, dob):
        """**Validates: Requirements 3.4**"""
        db = SessionLocal()
        try:
            patient_service = PatientService(db)
            staff_service = StaffService(db)
            appointment_service = AppointmentService(db)
            
            # Create patient
            patient = patient_service.register_patient({
                'name': patient_name,
                'date_of_birth': dob,
                'contact_info': contact_info,
                'insurance_id': insurance_id
            })
            
            # Create doctor
            doctor = staff_service.add_staff({
                'name': doctor_name,
                'role': 'doctor'
            })
            
            # Schedule appointment
            scheduled_time = datetime.utcnow() + timedelta(days=1)
            app1 = appointment_service.schedule_appointment(patient.id, doctor.id, scheduled_time)
            
            # Cancel appointment
            appointment_service.cancel_appointment(app1.id)
            
            # Try to schedule at same time - should succeed now
            app2 = appointment_service.schedule_appointment(patient.id, doctor.id, scheduled_time)
            assert app2 is not None
            assert app2.id != app1.id
            
        finally:
            db.close()

@pytest.mark.properties
class TestMedicalRecordProperties:
    """Property-based tests for medical records"""
    
    @given(
        patient_name=patient_name_strategy,
        contact_info=contact_info_strategy,
        insurance_id=insurance_id_strategy,
        dob=valid_date_of_birth()
    )
    @settings(max_examples=30)
    def test_medical_record_version_history(self, patient_name, contact_info, insurance_id, dob):
        """**Validates: Requirements 2.4**"""
        db = SessionLocal()
        try:
            patient_service = PatientService(db)
            medical_service = MedicalRecordService(db)
            
            # Create patient
            patient = patient_service.register_patient({
                'name': patient_name,
                'date_of_birth': dob,
                'contact_info': contact_info,
                'insurance_id': insurance_id
            })
            
            # Create medical record
            record = medical_service.create_record(patient.id, 'doctor1')
            assert record is not None
            assert record.version == 1
            
            # Add diagnosis
            diagnosis = medical_service.add_diagnosis(patient.id, 'ICD-001', 'Test Diagnosis')
            assert diagnosis is not None
            
            # Retrieve record
            retrieved = medical_service.get_record(patient.id)
            assert retrieved is not None
            assert retrieved.id == record.id
            
        finally:
            db.close()

@pytest.mark.properties
class TestPrescriptionProperties:
    """Property-based tests for prescriptions"""
    
    @given(
        patient_name=patient_name_strategy,
        doctor_name=staff_name_strategy,
        contact_info=contact_info_strategy,
        insurance_id=insurance_id_strategy,
        dob=valid_date_of_birth(),
        medication_name=inventory_name_strategy
    )
    @settings(max_examples=30)
    def test_prescription_medication_validation(self, patient_name, doctor_name, contact_info, insurance_id, dob, medication_name):
        """**Validates: Requirements 5.2**"""
        db = SessionLocal()
        try:
            patient_service = PatientService(db)
            staff_service = StaffService(db)
            prescription_service = PrescriptionService(db)
            inventory_service = InventoryService(db)
            
            # Create patient
            patient = patient_service.register_patient({
                'name': patient_name,
                'date_of_birth': dob,
                'contact_info': contact_info,
                'insurance_id': insurance_id
            })
            
            # Create doctor
            doctor = staff_service.add_staff({
                'name': doctor_name,
                'role': 'doctor'
            })
            
            # Create medication in inventory
            medication = inventory_service.add_inventory_item({
                'name': medication_name,
                'quantity': 100,
                'unit_cost': Decimal('10.00'),
                'storage_location': 'pharmacy'
            })
            
            # Create prescription with valid medication
            prescription = prescription_service.create_prescription({
                'patient_id': patient.id,
                'doctor_id': doctor.id,
                'medication_id': medication.id,
                'dosage': '500mg',
                'frequency': 'twice daily',
                'duration': '7 days'
            })
            
            assert prescription is not None
            assert prescription.medication_id == medication.id
            
            # Try to create prescription with invalid medication - should fail
            with pytest.raises(ValueError):
                prescription_service.create_prescription({
                    'patient_id': patient.id,
                    'doctor_id': doctor.id,
                    'medication_id': 'invalid-med-id',
                    'dosage': '500mg',
                    'frequency': 'twice daily',
                    'duration': '7 days'
                })
            
        finally:
            db.close()

@pytest.mark.properties
class TestInventoryExpirationProperties:
    """Property-based tests for inventory expiration"""
    
    @given(
        name=inventory_name_strategy,
        quantity=quantity_strategy,
        unit_cost=price_strategy
    )
    @settings(max_examples=30)
    def test_expired_item_prevention(self, name, quantity, unit_cost):
        """**Validates: Requirements 7.5**"""
        db = SessionLocal()
        try:
            inventory_service = InventoryService(db)
            
            # Create expired item
            expired_date = date.today() - timedelta(days=1)
            item = inventory_service.add_inventory_item({
                'name': name,
                'quantity': quantity,
                'unit_cost': unit_cost,
                'expiration_date': expired_date,
                'storage_location': 'warehouse'
            })
            
            # Try to consume expired item - should fail
            with pytest.raises(ValueError):
                inventory_service.consume_inventory(item.id, 1)
            
        finally:
            db.close()

@pytest.mark.properties
class TestAccessControlProperties:
    """Property-based tests for access control"""
    
    @given(
        username=st.text(min_size=3, max_size=20, alphabet=st.characters(min_codepoint=97, max_codepoint=122)),
        password=st.text(min_size=8, max_size=20)
    )
    @settings(max_examples=30)
    def test_access_control_enforcement(self, username, password):
        """**Validates: Requirements 9.2**"""
        db = SessionLocal()
        try:
            access_service = AccessControlService(db)
            
            # Create user
            user = access_service.create_user(username, password, 'doctor')
            assert user is not None
            
            # Authenticate with correct password
            token_data = access_service.authenticate_user(username, password)
            assert token_data is not None
            assert 'access_token' in token_data
            
            # Try to authenticate with wrong password - should fail
            with pytest.raises(ValueError):
                access_service.authenticate_user(username, 'wrong_password')
            
        finally:
            db.close()

@pytest.mark.properties
class TestBillingImmutabilityProperties:
    """Property-based tests for billing immutability"""
    
    @given(
        patient_name=patient_name_strategy,
        contact_info=contact_info_strategy,
        insurance_id=insurance_id_strategy,
        dob=valid_date_of_birth(),
        amount=price_strategy
    )
    @settings(max_examples=30)
    def test_audit_trail_immutability(self, patient_name, contact_info, insurance_id, dob, amount):
        """**Validates: Requirements 6.5**"""
        db = SessionLocal()
        try:
            patient_service = PatientService(db)
            billing_service = BillingService(db)
            
            # Create patient
            patient = patient_service.register_patient({
                'name': patient_name,
                'date_of_birth': dob,
                'contact_info': contact_info,
                'insurance_id': insurance_id
            })
            
            # Create billing record
            billing = billing_service.create_billing_record(patient.id, [
                {
                    'service_type': 'consultation',
                    'quantity': 1,
                    'unit_price': amount,
                    'total_price': amount
                }
            ])
            
            # Finalize billing record
            finalized = billing_service.finalize_billing_record(billing.id)
            assert finalized.is_finalized
            
            # Try to process payment on finalized record - should fail
            with pytest.raises(ValueError):
                billing_service.process_payment(billing.id, amount, 'credit_card')
            
        finally:
            db.close()

@pytest.mark.properties
class TestTransactionConsistencyProperties:
    """Property-based tests for transaction consistency"""
    
    @given(
        patient_name=patient_name_strategy,
        contact_info=contact_info_strategy,
        insurance_id=insurance_id_strategy,
        dob=valid_date_of_birth(),
        amount=price_strategy
    )
    @settings(max_examples=30)
    def test_transaction_consistency(self, patient_name, contact_info, insurance_id, dob, amount):
        """**Validates: Requirements 10.4**"""
        db = SessionLocal()
        try:
            patient_service = PatientService(db)
            billing_service = BillingService(db)
            
            # Create patient
            patient = patient_service.register_patient({
                'name': patient_name,
                'date_of_birth': dob,
                'contact_info': contact_info,
                'insurance_id': insurance_id
            })
            
            # Create billing record
            billing = billing_service.create_billing_record(patient.id, [
                {
                    'service_type': 'consultation',
                    'quantity': 1,
                    'unit_price': amount,
                    'total_price': amount
                }
            ])
            
            # Verify billing record exists and has correct data
            retrieved = billing_service.get_billing_record(billing.id)
            assert retrieved is not None
            assert retrieved.patient_id == patient.id
            assert retrieved.total_amount == billing.total_amount
            
            # Verify patient balance is updated
            balance = billing_service.get_patient_balance(patient.id)
            assert balance['patient_id'] == patient.id
            assert balance['total_due'] > 0
            
        finally:
            db.close()

@pytest.mark.properties
class TestDepartmentProperties:
    """Property-based tests for departments"""
    
    @given(
        dept_name=department_name_strategy,
        staff_name=staff_name_strategy,
        budget=price_strategy
    )
    @settings(max_examples=30)
    def test_department_staff_assignment_consistency(self, dept_name, staff_name, budget):
        """**Validates: Requirements 8.2**"""
        db = SessionLocal()
        try:
            dept_service = DepartmentService(db)
            staff_service = StaffService(db)
            
            # Create department
            dept = dept_service.create_department({
                'name': dept_name,
                'budget_allocation': budget
            })
            
            # Create staff
            staff = staff_service.add_staff({
                'name': staff_name,
                'role': 'nurse'
            })
            
            # Assign to department
            dept_service.assign_staff_to_department(staff.id, dept.id)
            
            # Verify staff is in department
            dept_staff = dept_service.get_department_staff(dept.id)
            staff_ids = [s.id for s in dept_staff]
            assert staff.id in staff_ids
            
        finally:
            db.close()
