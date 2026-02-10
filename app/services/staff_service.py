"""Staff management service"""
import uuid
from datetime import datetime, date
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.staff import Staff, StaffRole, StaffStatus, StaffCredential, StaffAvailability
import logging

logger = logging.getLogger(__name__)

class StaffService:
    """Service for staff management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def add_staff(self, staff_data: dict) -> Staff:
        """Add a new staff member"""
        required_fields = ['name', 'role']
        for field in required_fields:
            if field not in staff_data or not staff_data[field]:
                raise ValueError(f"Missing required field: {field}")
        
        staff_id = str(uuid.uuid4())
        staff = Staff(
            id=staff_id,
            name=staff_data['name'],
            role=StaffRole(staff_data['role']),
            specialization=staff_data.get('specialization'),
            license_number=staff_data.get('license_number'),
            department_id=staff_data.get('department_id'),
            status=StaffStatus.ACTIVE
        )
        
        self.db.add(staff)
        self.db.commit()
        self.db.refresh(staff)
        logger.info(f"Staff member added: {staff_id}")
        return staff
    
    def get_staff(self, staff_id: str) -> Optional[Staff]:
        """Get staff member by ID"""
        return self.db.query(Staff).filter(Staff.id == staff_id).first()
    
    def update_staff(self, staff_id: str, updates: dict) -> Staff:
        """Update staff information"""
        staff = self.get_staff(staff_id)
        if not staff:
            raise ValueError(f"Staff member not found: {staff_id}")
        
        allowed_fields = ['name', 'specialization', 'license_number', 'status']
        for field in allowed_fields:
            if field in updates:
                if field == 'status':
                    setattr(staff, field, StaffStatus(updates[field]))
                else:
                    setattr(staff, field, updates[field])
        
        staff.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(staff)
        logger.info(f"Staff member updated: {staff_id}")
        return staff
    
    def assign_to_department(self, staff_id: str, department_id: str) -> Staff:
        """Assign staff member to department"""
        staff = self.get_staff(staff_id)
        if not staff:
            raise ValueError(f"Staff member not found: {staff_id}")
        
        staff.department_id = department_id
        staff.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(staff)
        logger.info(f"Staff member assigned to department: {staff_id} -> {department_id}")
        return staff
    
    def get_staff_by_department(self, department_id: str) -> List[Staff]:
        """Get all staff members in a department"""
        return self.db.query(Staff).filter(Staff.department_id == department_id).all()
    
    def verify_credentials(self, staff_id: str) -> dict:
        """Verify staff credentials"""
        staff = self.get_staff(staff_id)
        if not staff:
            raise ValueError(f"Staff member not found: {staff_id}")
        
        credentials = self.db.query(StaffCredential).filter(
            StaffCredential.staff_id == staff_id
        ).all()
        
        return {
            'staff_id': staff_id,
            'name': staff.name,
            'license_number': staff.license_number,
            'credentials': [
                {
                    'type': cred.credential_type,
                    'number': cred.credential_number,
                    'expiry_date': cred.expiry_date
                }
                for cred in credentials
            ]
        }
    
    def get_availability(self, staff_id: str) -> List[StaffAvailability]:
        """Get staff member's availability"""
        return self.db.query(StaffAvailability).filter(
            StaffAvailability.staff_id == staff_id
        ).all()
    
    def add_credential(self, staff_id: str, credential_type: str, credential_number: str,
                      expiry_date: date = None) -> StaffCredential:
        """Add credential to staff member"""
        staff = self.get_staff(staff_id)
        if not staff:
            raise ValueError(f"Staff member not found: {staff_id}")
        
        credential_id = str(uuid.uuid4())
        credential = StaffCredential(
            id=credential_id,
            staff_id=staff_id,
            credential_type=credential_type,
            credential_number=credential_number,
            expiry_date=expiry_date
        )
        
        self.db.add(credential)
        self.db.commit()
        self.db.refresh(credential)
        logger.info(f"Credential added: {credential_id}")
        return credential
    
    def set_availability(self, staff_id: str, day_of_week: str, start_time: str, end_time: str) -> StaffAvailability:
        """Set staff member's availability"""
        staff = self.get_staff(staff_id)
        if not staff:
            raise ValueError(f"Staff member not found: {staff_id}")
        
        availability_id = str(uuid.uuid4())
        availability = StaffAvailability(
            id=availability_id,
            staff_id=staff_id,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time
        )
        
        self.db.add(availability)
        self.db.commit()
        self.db.refresh(availability)
        logger.info(f"Availability set: {availability_id}")
        return availability
