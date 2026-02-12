"""Unit tests for staff service"""
import pytest
from datetime import date
from services.staff_service import StaffService
from models.staff import StaffRole, StaffStatus
from database import SessionLocal
import uuid

@pytest.fixture
def db():
    """Database session fixture"""
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture
def staff_service(db):
    """Staff service fixture"""
    return StaffService(db)

class TestStaffService:
    """Unit tests for StaffService"""
    
    def test_add_staff_success(self, staff_service):
        """Test successful staff member addition"""
        unique_id = str(uuid.uuid4())[:8]
        staff_data = {
            'name': f'Dr. John Smith {unique_id}',
            'role': 'doctor',
            'specialization': 'Cardiology',
            'license_number': f'LIC-{unique_id}'
        }
        
        staff = staff_service.add_staff(staff_data)
        
        assert staff is not None
        assert staff.name == staff_data['name']
        assert staff.role == StaffRole.DOCTOR
        assert staff.status == StaffStatus.ACTIVE
    
    def test_add_staff_missing_field(self, staff_service):
        """Test staff addition with missing required field"""
        unique_id = str(uuid.uuid4())[:8]
        staff_data = {
            'name': f'Dr. Jane Doe {unique_id}',
            # Missing role
            'specialization': 'Neurology'
        }
        
        with pytest.raises(ValueError, match="Missing required field"):
            staff_service.add_staff(staff_data)
    
    def test_get_staff(self, staff_service):
        """Test retrieving staff member"""
        unique_id = str(uuid.uuid4())[:8]
        staff_data = {
            'name': f'Dr. Bob Johnson {unique_id}',
            'role': 'doctor',
            'specialization': 'Orthopedics'
        }
        
        created = staff_service.add_staff(staff_data)
        retrieved = staff_service.get_staff(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == staff_data['name']
    
    def test_update_staff(self, staff_service):
        """Test updating staff information"""
        unique_id = str(uuid.uuid4())[:8]
        staff_data = {
            'name': f'Nurse Alice {unique_id}',
            'role': 'nurse'
        }
        
        staff = staff_service.add_staff(staff_data)
        
        updates = {
            'specialization': 'Emergency Care'
        }
        
        updated = staff_service.update_staff(staff.id, updates)
        
        assert updated.specialization == 'Emergency Care'
    
    def test_assign_to_department(self, staff_service):
        """Test assigning staff to department"""
        unique_id = str(uuid.uuid4())[:8]
        staff_data = {
            'name': f'Dr. Charlie Brown {unique_id}',
            'role': 'doctor'
        }
        
        staff = staff_service.add_staff(staff_data)
        department_id = f"dept-{unique_id}"
        
        assigned = staff_service.assign_to_department(staff.id, department_id)
        
        assert assigned.department_id == department_id
    
    def test_get_staff_by_department(self, staff_service):
        """Test getting staff by department"""
        unique_id = str(uuid.uuid4())[:8]
        department_id = f"dept-{unique_id}"
        
        # Add multiple staff to same department
        for i in range(3):
            staff_data = {
                'name': f'Staff Member {i} {unique_id}',
                'role': 'nurse',
                'department_id': department_id
            }
            staff = staff_service.add_staff(staff_data)
            staff_service.assign_to_department(staff.id, department_id)
        
        staff_list = staff_service.get_staff_by_department(department_id)
        
        assert len(staff_list) >= 3
        assert all(s.department_id == department_id for s in staff_list)
    
    def test_verify_credentials(self, staff_service):
        """Test verifying staff credentials"""
        unique_id = str(uuid.uuid4())[:8]
        staff_data = {
            'name': f'Dr. Diana Prince {unique_id}',
            'role': 'doctor',
            'license_number': f'LIC-{unique_id}'
        }
        
        staff = staff_service.add_staff(staff_data)
        
        verification = staff_service.verify_credentials(staff.id)
        
        assert verification is not None
        assert verification['staff_id'] == staff.id
        assert verification['name'] == staff_data['name']
        assert verification['license_number'] == staff_data['license_number']
    
    def test_get_availability(self, staff_service):
        """Test getting staff availability"""
        unique_id = str(uuid.uuid4())[:8]
        staff_data = {
            'name': f'Dr. Edward Norton {unique_id}',
            'role': 'doctor'
        }
        
        staff = staff_service.add_staff(staff_data)
        
        availability = staff_service.get_availability(staff.id)
        
        assert availability is not None
        assert isinstance(availability, list)
    
    def test_add_credential(self, staff_service):
        """Test adding credential to staff member"""
        unique_id = str(uuid.uuid4())[:8]
        staff_data = {
            'name': f'Dr. Fiona Green {unique_id}',
            'role': 'doctor'
        }
        
        staff = staff_service.add_staff(staff_data)
        
        credential = staff_service.add_credential(
            staff.id,
            'board_certification',
            f'CERT-{unique_id}',
            date(2025, 12, 31)
        )
        
        assert credential is not None
        assert credential.credential_type == 'board_certification'
        assert credential.credential_number == f'CERT-{unique_id}'
    
    def test_set_availability(self, staff_service):
        """Test setting staff availability"""
        unique_id = str(uuid.uuid4())[:8]
        staff_data = {
            'name': f'Dr. George Harris {unique_id}',
            'role': 'doctor'
        }
        
        staff = staff_service.add_staff(staff_data)
        
        availability = staff_service.set_availability(
            staff.id,
            'monday',
            '09:00',
            '17:00'
        )
        
        assert availability is not None
        assert availability.day_of_week == 'monday'
        assert availability.start_time == '09:00'
        assert availability.end_time == '17:00'
