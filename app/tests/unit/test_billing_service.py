"""Unit tests for billing service"""
import pytest
from decimal import Decimal
from services.billing_service import BillingService
from models.billing import BillingStatus, PaymentStatus
from database import SessionLocal

@pytest.fixture
def db():
    """Database session fixture"""
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture
def billing_service(db):
    """Billing service fixture"""
    return BillingService(db)

class TestBillingService:
    """Unit tests for BillingService"""
    
    def test_create_billing_record_success(self, billing_service):
        """Test successful billing record creation"""
        patient_id = 'patient-123'
        items = [
            {
                'service_type': 'consultation',
                'quantity': 1,
                'unit_price': 100.00,
                'total_price': 100.00
            },
            {
                'service_type': 'lab_test',
                'quantity': 2,
                'unit_price': 50.00,
                'total_price': 100.00
            }
        ]
        
        billing_record = billing_service.create_billing_record(patient_id, items)
        
        assert billing_record is not None
        assert billing_record.patient_id == patient_id
        assert billing_record.total_amount == Decimal('200.00')
        assert billing_record.status == BillingStatus.PENDING
    
    def test_create_billing_record_no_items(self, billing_service):
        """Test billing record creation with no items"""
        with pytest.raises(ValueError, match="must have at least one item"):
            billing_service.create_billing_record('patient-123', [])
    
    def test_billing_amount_calculation(self, billing_service):
        """Test billing amount calculation"""
        patient_id = 'patient-456'
        items = [
            {
                'service_type': 'surgery',
                'quantity': 1,
                'unit_price': 1000.00,
                'total_price': 1000.00
            }
        ]
        
        billing_record = billing_service.create_billing_record(patient_id, items)
        
        # 80% insurance coverage, 20% patient responsibility
        assert billing_record.insurance_coverage == Decimal('800.00')
        assert billing_record.patient_responsibility == Decimal('200.00')
    
    def test_billing_amount_calculation_consistency(self, billing_service):
        """Test that billing calculation is consistent"""
        patient_id = 'patient-789'
        items = [
            {
                'service_type': 'consultation',
                'quantity': 1,
                'unit_price': 150.00,
                'total_price': 150.00
            }
        ]
        
        # Create same billing twice
        billing1 = billing_service.create_billing_record(patient_id, items)
        billing2 = billing_service.create_billing_record(patient_id, items)
        
        # Amounts should be identical
        assert billing1.total_amount == billing2.total_amount
        assert billing1.insurance_coverage == billing2.insurance_coverage
        assert billing1.patient_responsibility == billing2.patient_responsibility
    
    def test_get_billing_record(self, billing_service):
        """Test retrieving billing record"""
        patient_id = 'patient-101'
        items = [
            {
                'service_type': 'xray',
                'quantity': 1,
                'unit_price': 75.00,
                'total_price': 75.00
            }
        ]
        
        created = billing_service.create_billing_record(patient_id, items)
        retrieved = billing_service.get_billing_record(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
    
    def test_get_patient_balance(self, billing_service):
        """Test getting patient account balance"""
        patient_id = 'patient-202'
        items = [
            {
                'service_type': 'consultation',
                'quantity': 1,
                'unit_price': 100.00,
                'total_price': 100.00
            }
        ]
        
        billing_service.create_billing_record(patient_id, items)
        
        balance = billing_service.get_patient_balance(patient_id)
        
        assert balance is not None
        assert balance['patient_id'] == patient_id
        assert balance['total_due'] > 0
    
    def test_process_payment(self, billing_service):
        """Test processing payment"""
        patient_id = 'patient-303'
        items = [
            {
                'service_type': 'consultation',
                'quantity': 1,
                'unit_price': 100.00,
                'total_price': 100.00
            }
        ]
        
        billing_record = billing_service.create_billing_record(patient_id, items)
        
        payment = billing_service.process_payment(
            billing_record.id,
            Decimal('20.00'),
            'credit_card'
        )
        
        assert payment is not None
        assert payment.amount == Decimal('20.00')
        assert payment.status == PaymentStatus.COMPLETED
    
    def test_process_payment_full_amount(self, billing_service):
        """Test processing full payment"""
        patient_id = 'patient-404'
        items = [
            {
                'service_type': 'consultation',
                'quantity': 1,
                'unit_price': 100.00,
                'total_price': 100.00
            }
        ]
        
        billing_record = billing_service.create_billing_record(patient_id, items)
        
        payment = billing_service.process_payment(
            billing_record.id,
            billing_record.patient_responsibility,
            'credit_card'
        )
        
        # Verify billing record is marked as paid
        updated_record = billing_service.get_billing_record(billing_record.id)
        assert updated_record.status == BillingStatus.PAID
    
    def test_get_payment_history(self, billing_service):
        """Test getting payment history"""
        patient_id = 'patient-505'
        items = [
            {
                'service_type': 'consultation',
                'quantity': 1,
                'unit_price': 100.00,
                'total_price': 100.00
            }
        ]
        
        billing_record = billing_service.create_billing_record(patient_id, items)
        billing_service.process_payment(
            billing_record.id,
            Decimal('20.00'),
            'credit_card'
        )
        
        history = billing_service.get_payment_history(patient_id)
        
        assert history is not None
        assert len(history) >= 1
    
    def test_calculate_charges(self, billing_service):
        """Test charge calculation"""
        services = [
            {
                'service_type': 'consultation',
                'quantity': 1,
                'unit_price': 100.00,
                'total_price': 100.00
            },
            {
                'service_type': 'lab_test',
                'quantity': 1,
                'unit_price': 50.00,
                'total_price': 50.00
            }
        ]
        
        charges = billing_service.calculate_charges(services)
        
        assert charges['total_amount'] == Decimal('150.00')
        assert charges['insurance_coverage'] == Decimal('120.00')
        assert charges['patient_responsibility'] == Decimal('30.00')
    
    def test_finalize_billing_record(self, billing_service):
        """Test finalizing billing record (immutability)"""
        patient_id = 'patient-606'
        items = [
            {
                'service_type': 'consultation',
                'quantity': 1,
                'unit_price': 100.00,
                'total_price': 100.00
            }
        ]
        
        billing_record = billing_service.create_billing_record(patient_id, items)
        
        finalized = billing_service.finalize_billing_record(billing_record.id)
        
        assert finalized.is_finalized is True
        assert finalized.status == BillingStatus.FINALIZED
    
    def test_cannot_process_payment_on_finalized_record(self, billing_service):
        """Test that payment cannot be processed on finalized record"""
        patient_id = 'patient-707'
        items = [
            {
                'service_type': 'consultation',
                'quantity': 1,
                'unit_price': 100.00,
                'total_price': 100.00
            }
        ]
        
        billing_record = billing_service.create_billing_record(patient_id, items)
        billing_service.finalize_billing_record(billing_record.id)
        
        with pytest.raises(ValueError, match="Cannot process payment for finalized"):
            billing_service.process_payment(
                billing_record.id,
                Decimal('20.00'),
                'credit_card'
            )
