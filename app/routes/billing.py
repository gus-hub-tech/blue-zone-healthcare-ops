"""Billing and payment routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from decimal import Decimal
from typing import List
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.billing_service import BillingService

router = APIRouter(prefix="/billing", tags=["billing"])

class BillingItemCreate(BaseModel):
    """Billing item creation schema"""
    service_type: str
    quantity: Decimal
    unit_price: Decimal
    total_price: Decimal

class BillingRecordCreate(BaseModel):
    """Billing record creation schema"""
    patient_id: str
    items: List[BillingItemCreate]

class PaymentCreate(BaseModel):
    """Payment creation schema"""
    billing_id: str
    amount: Decimal
    payment_method: str

@router.post("")
def create_billing_record(billing: BillingRecordCreate, db: Session = Depends(get_db)):
    """Create a billing record"""
    try:
        service = BillingService(db)
        items = [item.dict() for item in billing.items]
        created = service.create_billing_record(billing.patient_id, items)
        return created
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{billing_id}")
def get_billing_record(billing_id: str, db: Session = Depends(get_db)):
    """Get billing record by ID"""
    service = BillingService(db)
    record = service.get_billing_record(billing_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Billing record not found")
    return record

@router.get("/patient/{patient_id}/billing")
def get_patient_billing(patient_id: str, db: Session = Depends(get_db)):
    """Get patient's billing records"""
    from app.models.billing import BillingRecord
    db_records = db.query(BillingRecord).filter(BillingRecord.patient_id == patient_id).all()
    return db_records

@router.post("/payments")
def process_payment(payment: PaymentCreate, db: Session = Depends(get_db)):
    """Process a payment"""
    try:
        service = BillingService(db)
        created = service.process_payment(payment.billing_id, payment.amount, payment.payment_method)
        return created
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/patient/{patient_id}/balance")
def get_patient_balance(patient_id: str, db: Session = Depends(get_db)):
    """Get patient's account balance"""
    service = BillingService(db)
    balance = service.get_patient_balance(patient_id)
    return balance

@router.patch("/{billing_id}/finalize")
def finalize_billing_record(billing_id: str, db: Session = Depends(get_db)):
    """Finalize a billing record"""
    try:
        service = BillingService(db)
        finalized = service.finalize_billing_record(billing_id)
        return finalized
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
