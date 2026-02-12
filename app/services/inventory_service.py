"""Inventory management service"""
import uuid
from datetime import datetime, date
from typing import List, Optional
from sqlalchemy.orm import Session
from models.inventory import InventoryItem, InventoryTransaction, InventoryTransactionType
import logging

logger = logging.getLogger(__name__)

class InventoryService:
    """Service for inventory management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def add_inventory_item(self, item_data: dict) -> InventoryItem:
        """Add a new inventory item"""
        required_fields = ['name', 'quantity', 'unit_cost', 'storage_location']
        for field in required_fields:
            if field not in item_data or item_data[field] is None:
                raise ValueError(f"Missing required field: {field}")
        
        item_id = str(uuid.uuid4())
        item = InventoryItem(
            id=item_id,
            name=item_data['name'],
            quantity=item_data['quantity'],
            unit_cost=item_data['unit_cost'],
            expiration_date=item_data.get('expiration_date'),
            storage_location=item_data['storage_location'],
            min_threshold=item_data.get('min_threshold', 10)
        )
        
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        
        # Log transaction
        self._log_transaction(item_id, InventoryTransactionType.ADD, item_data['quantity'])
        
        logger.info(f"Inventory item added: {item_id}")
        return item
    
    def get_inventory_item(self, item_id: str) -> Optional[InventoryItem]:
        """Get inventory item by ID"""
        return self.db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    
    def consume_inventory(self, item_id: str, quantity: int, user_id: str = None) -> InventoryItem:
        """Consume inventory"""
        item = self.get_inventory_item(item_id)
        if not item:
            raise ValueError(f"Inventory item not found: {item_id}")
        
        if item.quantity < quantity:
            raise ValueError(f"Insufficient inventory: {item_id}")
        
        # Check if item is expired
        if item.expiration_date and item.expiration_date < date.today():
            raise ValueError(f"Item is expired: {item_id}")
        
        item.quantity -= quantity
        item.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(item)
        
        # Log transaction
        self._log_transaction(item_id, InventoryTransactionType.CONSUME, quantity, user_id)
        
        logger.info(f"Inventory consumed: {item_id} - {quantity} units")
        return item
    
    def get_low_stock_items(self, threshold: int = None) -> List[InventoryItem]:
        """Get items with low stock"""
        query = self.db.query(InventoryItem)
        
        if threshold:
            query = query.filter(InventoryItem.quantity <= threshold)
        else:
            query = query.filter(InventoryItem.quantity <= InventoryItem.min_threshold)
        
        return query.all()
    
    def get_expired_items(self) -> List[InventoryItem]:
        """Get expired items"""
        today = date.today()
        return self.db.query(InventoryItem).filter(
            InventoryItem.expiration_date < today
        ).all()
    
    def update_stock_level(self, item_id: str, quantity: int, user_id: str = None) -> InventoryItem:
        """Update stock level"""
        item = self.get_inventory_item(item_id)
        if not item:
            raise ValueError(f"Inventory item not found: {item_id}")
        
        old_quantity = item.quantity
        item.quantity = quantity
        item.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(item)
        
        # Log transaction
        adjustment = quantity - old_quantity
        self._log_transaction(item_id, InventoryTransactionType.ADJUST, adjustment, user_id)
        
        logger.info(f"Stock level updated: {item_id} - {old_quantity} -> {quantity}")
        return item
    
    def get_inventory_report(self) -> dict:
        """Get inventory report"""
        items = self.db.query(InventoryItem).all()
        
        total_value = sum(item.quantity * item.unit_cost for item in items)
        low_stock_items = self.get_low_stock_items()
        expired_items = self.get_expired_items()
        
        return {
            'total_items': len(items),
            'total_value': total_value,
            'low_stock_count': len(low_stock_items),
            'expired_count': len(expired_items),
            'items': [
                {
                    'id': item.id,
                    'name': item.name,
                    'quantity': item.quantity,
                    'unit_cost': item.unit_cost,
                    'expiration_date': item.expiration_date
                }
                for item in items
            ]
        }
    
    def _log_transaction(self, item_id: str, transaction_type: InventoryTransactionType, 
                        quantity: int, user_id: str = None):
        """Log inventory transaction"""
        transaction_id = str(uuid.uuid4())
        transaction = InventoryTransaction(
            id=transaction_id,
            item_id=item_id,
            transaction_type=transaction_type,
            quantity=quantity,
            user_id=user_id
        )
        self.db.add(transaction)
        self.db.commit()
