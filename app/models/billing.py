"""Billing models"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Enum, Boolean
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.models import Base

class BillingStatus(str, enum.Enum):
    """Billing status enumeration"""
    PENDING = "pending"
    FINALIZED = "finalized"
    PAID = "paid"
    CANCELLED = "cancelled"

class PaymentStatus(str, enum.Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class BillingRecord(Base):
    """Billing record model"""
    __tablename__ = "billing_records"
    
    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False, index=True)
    total_amount = Column(Numeric(10, 2), nullable=False)
    insurance_coverage = Column(Numeric(10, 2), default=0, nullable=False)
    patient_responsibility = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(BillingStatus), default=BillingStatus.PENDING, nullable=False)
    is_finalized = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

class BillingItem(Base):
    """Billing item model"""
    __tablename__ = "billing_items"
    
    id = Column(String, primary_key=True, index=True)
    billing_id = Column(String, ForeignKey("billing_records.id"), nullable=False, index=True)
    service_type = Column(String, nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

class Payment(Base):
    """Payment model"""
    __tablename__ = "payments"
    
    id = Column(String, primary_key=True, index=True)
    billing_id = Column(String, ForeignKey("billing_records.id"), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(String, nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
