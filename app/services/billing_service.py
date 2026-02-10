"""Billing and payment processing service"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.billing import BillingRecord, BillingItem, Payment, BillingStatus, PaymentStatus
import logging

logger = logging.getLogger(__name__)

class BillingService:
    """Service for billing and payment processing"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_billing_record(self, patient_id: str, items: List[dict]) -> BillingRecord:
        """Create a billing record"""
        if not items:
            raise ValueError("Billing record must have at least one item")
        
        # Calculate totals
        total_amount = Decimal('0')
        for item in items:
            total_amount += Decimal(str(item.get('total_price', 0)))
        
        # Calculate insurance coverage and patient responsibility
        insurance_coverage = total_amount * Decimal('0.8')  # 80% coverage
        patient_responsibility = total_amount - insurance_coverage
        
        billing_id = str(uuid.uuid4())
        billing_record = BillingRecord(
            id=billing_id,
            patient_id=patient_id,
            total_amount=total_amount,
            insurance_coverage=insurance_coverage,
            patient_responsibility=patient_responsibility,
            status=BillingStatus.PENDING
        )
        
        self.db.add(billing_record)
        self.db.flush()
        
        # Add billing items
        for item in items:
            item_id = str(uuid.uuid4())
            billing_item = BillingItem(
                id=item_id,
                billing_id=billing_id,
                service_type=item['service_type'],
                quantity=Decimal(str(item['quantity'])),
                unit_price=Decimal(str(item['unit_price'])),
                total_price=Decimal(str(item['total_price']))
            )
            self.db.add(billing_item)
        
        self.db.commit()
        self.db.refresh(billing_record)
        logger.info(f"Billing record created: {billing_id}")
        return billing_record
    
    def get_billing_record(self, billing_id: str) -> Optional[BillingRecord]:
        """Get billing record by ID"""
        return self.db.query(BillingRecord).filter(BillingRecord.id == billing_id).first()
    
    def get_patient_balance(self, patient_id: str) -> dict:
        """Get patient's account balance"""
        records = self.db.query(BillingRecord).filter(
            BillingRecord.patient_id == patient_id
        ).all()
        
        total_due = Decimal('0')
        total_paid = Decimal('0')
        
        for record in records:
            if record.status != BillingStatus.PAID:
                total_due += record.patient_responsibility
            else:
                total_paid += record.patient_responsibility
        
        return {
            'patient_id': patient_id,
            'total_due': total_due,
            'total_paid': total_paid,
            'balance': total_due
        }
    
    def process_payment(self, billing_id: str, amount: Decimal, payment_method: str) -> Payment:
        """Process a payment"""
        billing_record = self.get_billing_record(billing_id)
        if not billing_record:
            raise ValueError(f"Billing record not found: {billing_id}")
        
        if billing_record.is_finalized:
            raise ValueError("Cannot process payment for finalized billing record")
        
        payment_id = str(uuid.uuid4())
        payment = Payment(
            id=payment_id,
            billing_id=billing_id,
            amount=amount,
            payment_method=payment_method,
            status=PaymentStatus.COMPLETED
        )
        
        self.db.add(payment)
        
        # Update billing record status if fully paid
        if amount >= billing_record.patient_responsibility:
            billing_record.status = BillingStatus.PAID
        
        self.db.commit()
        self.db.refresh(payment)
        logger.info(f"Payment processed: {payment_id}")
        return payment
    
    def get_payment_history(self, patient_id: str) -> List[Payment]:
        """Get payment history for a patient"""
        payments = self.db.query(Payment).join(BillingRecord).filter(
            BillingRecord.patient_id == patient_id
        ).order_by(Payment.created_at.desc()).all()
        return payments
    
    def calculate_charges(self, services: List[dict]) -> dict:
        """Calculate charges for services"""
        total_amount = Decimal('0')
        for service in services:
            total_amount += Decimal(str(service.get('total_price', 0)))
        
        insurance_coverage = total_amount * Decimal('0.8')
        patient_responsibility = total_amount - insurance_coverage
        
        return {
            'total_amount': total_amount,
            'insurance_coverage': insurance_coverage,
            'patient_responsibility': patient_responsibility
        }
    
    def finalize_billing_record(self, billing_id: str) -> BillingRecord:
        """Finalize a billing record (make it immutable)"""
        billing_record = self.get_billing_record(billing_id)
        if not billing_record:
            raise ValueError(f"Billing record not found: {billing_id}")
        
        billing_record.is_finalized = True
        billing_record.status = BillingStatus.FINALIZED
        billing_record.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(billing_record)
        logger.info(f"Billing record finalized: {billing_id}")
        return billing_record
