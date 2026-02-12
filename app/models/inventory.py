"""Inventory models"""
from sqlalchemy import Column, String, DateTime, Integer, Numeric, Date, Enum
from sqlalchemy.sql import func
from datetime import datetime
import enum
from models import Base

class InventoryTransactionType(str, enum.Enum):
    """Inventory transaction type enumeration"""
    ADD = "add"
    CONSUME = "consume"
    ADJUST = "adjust"
    RETURN = "return"

class InventoryItem(Base):
    """Inventory item model"""
    __tablename__ = "inventory_items"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=0)
    unit_cost = Column(Numeric(10, 2), nullable=False)
    expiration_date = Column(Date, nullable=True)
    storage_location = Column(String, nullable=False)
    min_threshold = Column(Integer, default=10, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

class InventoryTransaction(Base):
    """Inventory transaction model"""
    __tablename__ = "inventory_transactions"
    
    id = Column(String, primary_key=True, index=True)
    item_id = Column(String, nullable=False, index=True)
    transaction_type = Column(Enum(InventoryTransactionType), nullable=False)
    quantity = Column(Integer, nullable=False)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False)
    user_id = Column(String, nullable=True)
    notes = Column(String, nullable=True)
