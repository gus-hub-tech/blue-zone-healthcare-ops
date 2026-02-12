"""Inventory management routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from decimal import Decimal
from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from database import get_db
from services.inventory_service import InventoryService

router = APIRouter(prefix="/inventory", tags=["inventory"])

class InventoryItemCreate(BaseModel):
    """Inventory item creation schema"""
    name: str
    quantity: int
    unit_cost: Decimal
    expiration_date: Optional[date] = None
    storage_location: str
    min_threshold: Optional[int] = 10

class InventoryItemResponse(BaseModel):
    """Inventory item response schema"""
    id: str
    name: str
    quantity: int
    unit_cost: Decimal
    expiration_date: Optional[date]
    storage_location: str
    min_threshold: int
    
    class Config:
        from_attributes = True

@router.post("", response_model=InventoryItemResponse, status_code=status.HTTP_201_CREATED)
def add_inventory_item(item: InventoryItemCreate, db: Session = Depends(get_db)):
    """Add inventory item"""
    try:
        service = InventoryService(db)
        created = service.add_inventory_item(item.dict())
        return created
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{item_id}", response_model=InventoryItemResponse)
def get_inventory_item(item_id: str, db: Session = Depends(get_db)):
    """Get inventory item by ID"""
    service = InventoryService(db)
    item = service.get_inventory_item(item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")
    return item

@router.patch("/{item_id}/consume")
def consume_inventory(item_id: str, quantity: int, db: Session = Depends(get_db)):
    """Consume inventory"""
    try:
        service = InventoryService(db)
        updated = service.consume_inventory(item_id, quantity)
        return updated
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/low-stock", response_model=List[InventoryItemResponse])
def get_low_stock_items(threshold: Optional[int] = None, db: Session = Depends(get_db)):
    """Get low stock items"""
    service = InventoryService(db)
    items = service.get_low_stock_items(threshold)
    return items

@router.get("/expired", response_model=List[InventoryItemResponse])
def get_expired_items(db: Session = Depends(get_db)):
    """Get expired items"""
    service = InventoryService(db)
    items = service.get_expired_items()
    return items

@router.get("", response_model=List[InventoryItemResponse])
def list_inventory(db: Session = Depends(get_db)):
    """List all inventory items"""
    from models.inventory import InventoryItem
    items = db.query(InventoryItem).all()
    return items
