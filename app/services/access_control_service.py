"""Access control and security service"""
import uuid
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.access_control import User, Role, AccessLog, UserRole, AccessLogAction
from config import settings
from passlib.context import CryptContext
from jose import JWTError, jwt
import logging

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AccessControlService:
    """Service for access control and security"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def authenticate_user(self, username: str, password: str) -> dict:
        """Authenticate user and return JWT token"""
        user = self.db.query(User).filter(User.username == username).first()
        
        if not user or not pwd_context.verify(password, user.password_hash):
            self.log_access(username, "authentication", "authentication", "denied", "Invalid credentials")
            raise ValueError("Invalid credentials")
        
        # Update last login
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        # Generate JWT token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.utcnow() + access_token_expires
        
        to_encode = {
            "sub": user.id,
            "username": user.username,
            "role": user.role.value,
            "exp": expire
        }
        
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        self.log_access(user.id, "authentication", "authentication", "success", "User authenticated")
        
        return {
            "access_token": encoded_jwt,
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username,
            "role": user.role.value
        }
    
    def verify_permission(self, user_id: str, resource: str, action: str) -> bool:
        """Verify user has permission for resource action"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        role = self.db.query(Role).filter(Role.name == user.role.value).first()
        if not role:
            return False
        
        # Check permissions
        permissions = role.permissions or {}
        resource_perms = permissions.get(resource, [])
        
        has_permission = action in resource_perms
        
        if not has_permission:
            self.log_access(user_id, resource, action, "denied", f"Permission denied for {action} on {resource}")
        
        return has_permission
    
    def log_access(self, user_id: str, resource: str, action: str, status: str, details: str = None):
        """Log access to resources"""
        log_id = str(uuid.uuid4())
        access_log = AccessLog(
            id=log_id,
            user_id=user_id,
            resource=resource,
            action=AccessLogAction(action) if action in [a.value for a in AccessLogAction] else AccessLogAction.VIEW,
            status=status,
            details=details
        )
        
        self.db.add(access_log)
        self.db.commit()
        logger.info(f"Access logged: {user_id} - {resource} - {action} - {status}")
    
    def get_user_role(self, user_id: str) -> Optional[str]:
        """Get user's role"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            return user.role.value
        return None
    
    def update_user_role(self, user_id: str, new_role: str) -> User:
        """Update user's role"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User not found: {user_id}")
        
        old_role = user.role.value
        user.role = UserRole(new_role)
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(user)
        
        self.log_access(user_id, "user_role", "update", "success", f"Role changed from {old_role} to {new_role}")
        logger.info(f"User role updated: {user_id} - {old_role} -> {new_role}")
        return user
    
    def check_data_access(self, user_id: str, patient_id: str) -> bool:
        """Check if user can access patient data"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        # Admins and doctors can access patient data
        if user.role in [UserRole.ADMIN, UserRole.DOCTOR, UserRole.NURSE]:
            return True
        
        # Patients can only access their own data
        if user.role == UserRole.PATIENT and user.id == patient_id:
            return True
        
        return False
    
    def create_user(self, username: str, password: str, role: str) -> User:
        """Create a new user"""
        # Check if user already exists
        existing = self.db.query(User).filter(User.username == username).first()
        if existing:
            raise ValueError(f"User already exists: {username}")
        
        user_id = str(uuid.uuid4())
        password_hash = pwd_context.hash(password)
        
        user = User(
            id=user_id,
            username=username,
            password_hash=password_hash,
            role=UserRole(role)
        )
        
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            logger.info(f"User created: {user_id}")
            return user
        except IntegrityError:
            self.db.rollback()
            raise ValueError(f"Error creating user: {username}")
    
    def create_role(self, name: str, permissions: dict) -> Role:
        """Create a new role"""
        role_id = str(uuid.uuid4())
        role = Role(
            id=role_id,
            name=name,
            permissions=permissions
        )
        
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        logger.info(f"Role created: {role_id}")
        return role
