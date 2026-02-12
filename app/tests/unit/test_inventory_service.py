"""Unit tests for inventory service"""
import pytest
from datetime import date, timedelta
from decimal import Decimal
from services.inventory_service import InventoryService
from models.inventory import InventoryTransactionType
from database import SessionLocal

@pytest.fixture
def db():
    """Database session fixture"""
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture
def inventory_service(db):
    """Inventory service fixture"""
    return InventoryService(db)

class TestInventoryService:
    """Unit tests for InventoryService"""
    
    def test_add_inventory_item_success(self, inventory_service):
        """Test successful inventory item addition"""
        item_data = {
            'name': 'Aspirin',
            'quantity': 100,
            'unit_cost': Decimal('0.50'),
            'storage_location': 'Pharmacy A',
            'min_threshold': 20
        }
        
        item = inventory_service.add_inventory_item(item_data)
        
        assert item is not None
        assert item.name == 'Aspirin'
        assert item.quantity == 100
    
    def test_add_inventory_item_missing_field(self, inventory_service):
        """Test inventory item addition with missing field"""
        item_data = {
            'name': 'Ibuprofen',
            'quantity': 100,
            # Missing unit_cost
            'storage_location': 'Pharmacy B'
        }
        
        with pytest.raises(ValueError, match="Missing required field"):
            inventory_service.add_inventory_item(item_data)
    
    def test_get_inventory_item(self, inventory_service):
        """Test retrieving inventory item"""
        item_data = {
            'name': 'Metformin',
            'quantity': 50,
            'unit_cost': Decimal('0.25'),
            'storage_location': 'Pharmacy C'
        }
        
        created = inventory_service.add_inventory_item(item_data)
        retrieved = inventory_service.get_inventory_item(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == 'Metformin'
    
    def test_consume_inventory(self, inventory_service):
        """Test consuming inventory"""
        item_data = {
            'name': 'Lisinopril',
            'quantity': 100,
            'unit_cost': Decimal('0.50'),
            'storage_location': 'Pharmacy D'
        }
        
        item = inventory_service.add_inventory_item(item_data)
        
        consumed = inventory_service.consume_inventory(item.id, 10)
        
        assert consumed.quantity == 90
    
    def test_inventory_consumption_decrements_stock(self, inventory_service):
        """Test that consuming inventory decrements stock correctly"""
        item_data = {
            'name': 'Atorvastatin',
            'quantity': 100,
            'unit_cost': Decimal('0.60'),
            'storage_location': 'Pharmacy E'
        }
        
        item = inventory_service.add_inventory_item(item_data)
        initial_quantity = item.quantity
        
        consumed_qty = 25
        inventory_service.consume_inventory(item.id, consumed_qty)
        
        updated = inventory_service.get_inventory_item(item.id)
        assert updated.quantity == initial_quantity - consumed_qty
    
    def test_consume_inventory_insufficient_stock(self, inventory_service):
        """Test consuming more than available"""
        item_data = {
            'name': 'Amlodipine',
            'quantity': 10,
            'unit_cost': Decimal('0.75'),
            'storage_location': 'Pharmacy F'
        }
        
        item = inventory_service.add_inventory_item(item_data)
        
        with pytest.raises(ValueError, match="Insufficient inventory"):
            inventory_service.consume_inventory(item.id, 20)
    
    def test_consume_expired_item_prevention(self, inventory_service):
        """Test that expired items cannot be consumed"""
        yesterday = date.today() - timedelta(days=1)
        
        item_data = {
            'name': 'Expired Medicine',
            'quantity': 100,
            'unit_cost': Decimal('1.00'),
            'storage_location': 'Pharmacy G',
            'expiration_date': yesterday
        }
        
        item = inventory_service.add_inventory_item(item_data)
        
        with pytest.raises(ValueError, match="Item is expired"):
            inventory_service.consume_inventory(item.id, 10)
    
    def test_get_low_stock_items(self, inventory_service):
        """Test getting low stock items"""
        # Add item with low stock
        item_data = {
            'name': 'Low Stock Item',
            'quantity': 5,
            'unit_cost': Decimal('1.00'),
            'storage_location': 'Pharmacy H',
            'min_threshold': 10
        }
        
        inventory_service.add_inventory_item(item_data)
        
        low_stock = inventory_service.get_low_stock_items()
        
        assert len(low_stock) >= 1
    
    def test_get_expired_items(self, inventory_service):
        """Test getting expired items"""
        yesterday = date.today() - timedelta(days=1)
        
        item_data = {
            'name': 'Expired Item',
            'quantity': 50,
            'unit_cost': Decimal('1.00'),
            'storage_location': 'Pharmacy I',
            'expiration_date': yesterday
        }
        
        inventory_service.add_inventory_item(item_data)
        
        expired = inventory_service.get_expired_items()
        
        assert len(expired) >= 1
    
    def test_update_stock_level(self, inventory_service):
        """Test updating stock level"""
        item_data = {
            'name': 'Stock Update Item',
            'quantity': 100,
            'unit_cost': Decimal('0.50'),
            'storage_location': 'Pharmacy J'
        }
        
        item = inventory_service.add_inventory_item(item_data)
        
        updated = inventory_service.update_stock_level(item.id, 150)
        
        assert updated.quantity == 150
    
    def test_get_inventory_report(self, inventory_service):
        """Test getting inventory report"""
        # Add multiple items
        for i in range(3):
            item_data = {
                'name': f'Item {i}',
                'quantity': 100 + i * 10,
                'unit_cost': Decimal('1.00'),
                'storage_location': f'Pharmacy {i}'
            }
            inventory_service.add_inventory_item(item_data)
        
        report = inventory_service.get_inventory_report()
        
        assert report is not None
        assert 'total_items' in report
        assert 'total_value' in report
        assert 'low_stock_count' in report
        assert 'expired_count' in report
        assert len(report['items']) >= 3
