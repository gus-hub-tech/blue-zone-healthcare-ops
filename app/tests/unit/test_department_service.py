"""Unit tests for department service"""
import pytest
from decimal import Decimal
from app.services.department_service import DepartmentService
from app.services.staff_service import StaffService
from app.database import SessionLocal
import uuid

@pytest.fixture
def db():
    """Database session fixture"""
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture
def department_service(db):
    """Department service fixture"""
    return DepartmentService(db)

@pytest.fixture
def staff_service(db):
    """Staff service fixture"""
    return StaffService(db)

class TestDepartmentService:
    """Unit tests for DepartmentService"""
    
    def test_create_department_success(self, department_service):
        """Test successful department creation"""
        unique_id = str(uuid.uuid4())[:8]
        dept_data = {
            'name': f'Cardiology{unique_id}',
            'budget_allocation': Decimal('100000.00')
        }
        
        department = department_service.create_department(dept_data)
        
        assert department is not None
        assert department.name == dept_data['name']
        assert department.budget_allocation == Decimal('100000.00')
    
    def test_create_department_missing_field(self, department_service):
        """Test department creation with missing field"""
        unique_id = str(uuid.uuid4())[:8]
        dept_data = {
            'name': f'Neurology{unique_id}',
            # Missing budget_allocation
        }
        
        with pytest.raises(ValueError, match="Missing required field"):
            department_service.create_department(dept_data)
    
    def test_create_duplicate_department(self, department_service):
        """Test creating duplicate department"""
        unique_id = str(uuid.uuid4())[:8]
        dept_name = f'Orthopedics{unique_id}'
        dept_data = {
            'name': dept_name,
            'budget_allocation': Decimal('80000.00')
        }
        
        department_service.create_department(dept_data)
        
        with pytest.raises(ValueError, match="Department already exists"):
            department_service.create_department(dept_data)
    
    def test_get_department(self, department_service):
        """Test retrieving department"""
        unique_id = str(uuid.uuid4())[:8]
        dept_data = {
            'name': f'Pediatrics{unique_id}',
            'budget_allocation': Decimal('60000.00')
        }
        
        created = department_service.create_department(dept_data)
        retrieved = department_service.get_department(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == dept_data['name']
    
    def test_update_department(self, department_service):
        """Test updating department"""
        unique_id = str(uuid.uuid4())[:8]
        dept_data = {
            'name': f'Emergency{unique_id}',
            'budget_allocation': Decimal('150000.00')
        }
        
        department = department_service.create_department(dept_data)
        
        updates = {
            'budget_allocation': Decimal('200000.00')
        }
        
        updated = department_service.update_department(department.id, updates)
        
        assert updated.budget_allocation == Decimal('200000.00')
    
    def test_assign_staff_to_department(self, department_service, staff_service):
        """Test assigning staff to department"""
        # Create department
        unique_id = str(uuid.uuid4())[:8]
        dept_data = {
            'name': f'Surgery{unique_id}',
            'budget_allocation': Decimal('250000.00')
        }
        department = department_service.create_department(dept_data)
        
        # Create staff
        staff_data = {
            'name': f'Dr. John Smith {unique_id}',
            'role': 'doctor',
            'specialization': 'General Surgery'
        }
        staff = staff_service.add_staff(staff_data)
        
        # Assign to department
        assignment = department_service.assign_staff_to_department(staff.id, department.id)
        
        assert assignment is not None
        assert assignment.staff_id == staff.id
        assert assignment.department_id == department.id
    
    def test_staff_department_assignment_consistency(self, department_service, staff_service):
        """Test that staff assignment is consistent in department"""
        # Create department
        unique_id = str(uuid.uuid4())[:8]
        dept_data = {
            'name': f'Radiology{unique_id}',
            'budget_allocation': Decimal('120000.00')
        }
        department = department_service.create_department(dept_data)
        
        # Create staff
        staff_data = {
            'name': f'Dr. Jane Doe {unique_id}',
            'role': 'doctor',
            'specialization': 'Radiology'
        }
        staff = staff_service.add_staff(staff_data)
        
        # Assign to department
        department_service.assign_staff_to_department(staff.id, department.id)
        
        # Verify staff is in department
        dept_staff = department_service.get_department_staff(department.id)
        
        assert len(dept_staff) >= 1
        assert any(s.id == staff.id for s in dept_staff)
    
    def test_get_department_staff(self, department_service, staff_service):
        """Test getting all staff in department"""
        # Create department
        unique_id = str(uuid.uuid4())[:8]
        dept_data = {
            'name': f'Oncology{unique_id}',
            'budget_allocation': Decimal('180000.00')
        }
        department = department_service.create_department(dept_data)
        
        # Add multiple staff
        for i in range(3):
            staff_data = {
                'name': f'Dr. Staff {i} {unique_id}',
                'role': 'doctor',
                'specialization': 'Oncology'
            }
            staff = staff_service.add_staff(staff_data)
            department_service.assign_staff_to_department(staff.id, department.id)
        
        staff_list = department_service.get_department_staff(department.id)
        
        assert len(staff_list) >= 3
    
    def test_get_department_metrics(self, department_service, staff_service):
        """Test getting department metrics"""
        # Create department
        unique_id = str(uuid.uuid4())[:8]
        dept_data = {
            'name': f'Psychiatry{unique_id}',
            'budget_allocation': Decimal('90000.00')
        }
        department = department_service.create_department(dept_data)
        
        # Add staff
        staff_data = {
            'name': f'Dr. Mental Health {unique_id}',
            'role': 'doctor',
            'specialization': 'Psychiatry'
        }
        staff = staff_service.add_staff(staff_data)
        department_service.assign_staff_to_department(staff.id, department.id)
        
        metrics = department_service.get_department_metrics(department.id)
        
        assert metrics is not None
        assert metrics['department_id'] == department.id
        assert metrics['department_name'] == dept_data['name']
        assert metrics['staff_count'] >= 1
        assert metrics['budget_allocation'] == Decimal('90000.00')
        assert 'staff' in metrics
