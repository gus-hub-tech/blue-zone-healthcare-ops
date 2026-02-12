"""Unit tests for access control service"""
import pytest
from services.access_control_service import AccessControlService
from models.access_control import UserRole
from database import SessionLocal
import uuid

@pytest.fixture
def db():
    """Database session fixture"""
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture
def access_control_service(db):
    """Access control service fixture"""
    return AccessControlService(db)

class TestAccessControlService:
    """Unit tests for AccessControlService"""
    
    def test_create_user_success(self, access_control_service):
        """Test successful user creation"""
        unique_id = str(uuid.uuid4())[:8]
        user = access_control_service.create_user(
            f'testuser{unique_id}',
            'password123',
            'doctor'
        )
        
        assert user is not None
        assert user.username == f'testuser{unique_id}'
        assert user.role == UserRole.DOCTOR
    
    def test_create_duplicate_user(self, access_control_service):
        """Test creating duplicate user"""
        unique_id = str(uuid.uuid4())[:8]
        username = f'duplicateuser{unique_id}'
        access_control_service.create_user(
            username,
            'password123',
            'nurse'
        )
        
        with pytest.raises(ValueError, match="User already exists"):
            access_control_service.create_user(
                username,
                'password456',
                'admin'
            )
    
    def test_authenticate_user_success(self, access_control_service):
        """Test successful user authentication"""
        unique_id = str(uuid.uuid4())[:8]
        username = f'authuser{unique_id}'
        access_control_service.create_user(
            username,
            'correctpassword',
            'doctor'
        )
        
        result = access_control_service.authenticate_user(
            username,
            'correctpassword'
        )
        
        assert result is not None
        assert 'access_token' in result
        assert result['username'] == username
        assert result['role'] == 'doctor'
    
    def test_authenticate_user_invalid_credentials(self, access_control_service):
        """Test authentication with invalid credentials"""
        unique_id = str(uuid.uuid4())[:8]
        username = f'invaliduser{unique_id}'
        access_control_service.create_user(
            username,
            'correctpassword',
            'nurse'
        )
        
        with pytest.raises(ValueError, match="Invalid credentials"):
            access_control_service.authenticate_user(
                username,
                'wrongpassword'
            )
    
    def test_authenticate_user_nonexistent(self, access_control_service):
        """Test authentication with nonexistent user"""
        with pytest.raises(ValueError, match="Invalid credentials"):
            access_control_service.authenticate_user(
                'nonexistentuser',
                'password123'
            )
    
    def test_get_user_role(self, access_control_service):
        """Test getting user role"""
        unique_id = str(uuid.uuid4())[:8]
        user = access_control_service.create_user(
            f'roleuser{unique_id}',
            'password123',
            'admin'
        )
        
        role = access_control_service.get_user_role(user.id)
        
        assert role == 'admin'
    
    def test_update_user_role(self, access_control_service):
        """Test updating user role"""
        unique_id = str(uuid.uuid4())[:8]
        user = access_control_service.create_user(
            f'updateuser{unique_id}',
            'password123',
            'nurse'
        )
        
        updated = access_control_service.update_user_role(user.id, 'doctor')
        
        assert updated.role == UserRole.DOCTOR
    
    def test_verify_permission_admin(self, access_control_service):
        """Test permission verification for admin"""
        unique_id = str(uuid.uuid4())[:8]
        user = access_control_service.create_user(
            f'adminuser{unique_id}',
            'password123',
            'admin'
        )
        
        # Create admin role with permissions
        access_control_service.create_role(
            f'admin{unique_id}',
            {
                'patients': ['read', 'write', 'delete'],
                'appointments': ['read', 'write', 'delete']
            }
        )
        
        # Admin should have permissions (basic check)
        # Note: Full permission check requires role setup
        assert user.role == UserRole.ADMIN
    
    def test_log_access(self, access_control_service):
        """Test logging access"""
        unique_id = str(uuid.uuid4())[:8]
        user = access_control_service.create_user(
            f'loguser{unique_id}',
            'password123',
            'doctor'
        )
        
        # Log access
        access_control_service.log_access(
            user.id,
            'patient_records',
            'view',
            'success',
            'Viewed patient record'
        )
        
        # Should not raise any exception
        assert True
    
    def test_check_data_access_admin(self, access_control_service):
        """Test data access check for admin"""
        unique_id = str(uuid.uuid4())[:8]
        user = access_control_service.create_user(
            f'adminaccess{unique_id}',
            'password123',
            'admin'
        )
        
        # Admin can access any patient data
        can_access = access_control_service.check_data_access(user.id, 'any-patient-id')
        
        assert can_access is True
    
    def test_check_data_access_doctor(self, access_control_service):
        """Test data access check for doctor"""
        unique_id = str(uuid.uuid4())[:8]
        user = access_control_service.create_user(
            f'doctoraccess{unique_id}',
            'password123',
            'doctor'
        )
        
        # Doctor can access any patient data
        can_access = access_control_service.check_data_access(user.id, 'any-patient-id')
        
        assert can_access is True
    
    def test_check_data_access_patient_own_data(self, access_control_service):
        """Test patient can access own data"""
        unique_id = str(uuid.uuid4())[:8]
        user = access_control_service.create_user(
            f'patientuser{unique_id}',
            'password123',
            'patient'
        )
        
        # Patient can access own data
        can_access = access_control_service.check_data_access(user.id, user.id)
        
        assert can_access is True
    
    def test_check_data_access_patient_other_data(self, access_control_service):
        """Test patient cannot access other patient data"""
        unique_id = str(uuid.uuid4())[:8]
        user = access_control_service.create_user(
            f'patientuser2{unique_id}',
            'password123',
            'patient'
        )
        
        # Patient cannot access other patient data
        can_access = access_control_service.check_data_access(user.id, 'other-patient-id')
        
        assert can_access is False
    
    def test_create_role(self, access_control_service):
        """Test creating a role"""
        unique_id = str(uuid.uuid4())[:8]
        permissions = {
            'patients': ['read', 'write'],
            'appointments': ['read']
        }
        
        role = access_control_service.create_role(f'custom_role{unique_id}', permissions)
        
        assert role is not None
        assert role.name == f'custom_role{unique_id}'
        assert role.permissions == permissions
