"""Department management service"""
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from models.department import Department, DepartmentStaff
from models.staff import Staff
import logging

logger = logging.getLogger(__name__)

class DepartmentService:
    """Service for department management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_department(self, dept_data: dict) -> Department:
        """Create a new department"""
        required_fields = ['name', 'budget_allocation']
        for field in required_fields:
            if field not in dept_data or dept_data[field] is None:
                raise ValueError(f"Missing required field: {field}")
        
        # Check if department already exists
        existing = self.db.query(Department).filter(Department.name == dept_data['name']).first()
        if existing:
            raise ValueError(f"Department already exists: {dept_data['name']}")
        
        dept_id = str(uuid.uuid4())
        department = Department(
            id=dept_id,
            name=dept_data['name'],
            head_of_dept_id=dept_data.get('head_of_dept_id'),
            budget_allocation=dept_data['budget_allocation']
        )
        
        self.db.add(department)
        self.db.commit()
        self.db.refresh(department)
        logger.info(f"Department created: {dept_id}")
        return department
    
    def get_department(self, dept_id: str) -> Optional[Department]:
        """Get department by ID"""
        return self.db.query(Department).filter(Department.id == dept_id).first()
    
    def update_department(self, dept_id: str, updates: dict) -> Department:
        """Update department information"""
        department = self.get_department(dept_id)
        if not department:
            raise ValueError(f"Department not found: {dept_id}")
        
        allowed_fields = ['name', 'head_of_dept_id', 'budget_allocation']
        for field in allowed_fields:
            if field in updates:
                setattr(department, field, updates[field])
        
        department.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(department)
        logger.info(f"Department updated: {dept_id}")
        return department
    
    def assign_staff_to_department(self, staff_id: str, dept_id: str) -> DepartmentStaff:
        """Assign staff member to department"""
        department = self.get_department(dept_id)
        if not department:
            raise ValueError(f"Department not found: {dept_id}")
        
        staff = self.db.query(Staff).filter(Staff.id == staff_id).first()
        if not staff:
            raise ValueError(f"Staff member not found: {staff_id}")
        
        # Check if already assigned
        existing = self.db.query(DepartmentStaff).filter(
            DepartmentStaff.staff_id == staff_id,
            DepartmentStaff.end_date == None
        ).first()
        
        if existing:
            # End previous assignment
            existing.end_date = datetime.utcnow()
            self.db.commit()
        
        assignment_id = str(uuid.uuid4())
        assignment = DepartmentStaff(
            id=assignment_id,
            department_id=dept_id,
            staff_id=staff_id
        )
        
        # Update staff department
        staff.department_id = dept_id
        
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        logger.info(f"Staff assigned to department: {staff_id} -> {dept_id}")
        return assignment
    
    def get_department_staff(self, dept_id: str) -> List[Staff]:
        """Get all staff members in a department"""
        return self.db.query(Staff).filter(Staff.department_id == dept_id).all()
    
    def get_department_metrics(self, dept_id: str) -> dict:
        """Get department metrics"""
        department = self.get_department(dept_id)
        if not department:
            raise ValueError(f"Department not found: {dept_id}")
        
        staff_list = self.get_department_staff(dept_id)
        
        # Count appointments (would need appointment service)
        # Count patients served (would need medical records service)
        
        return {
            'department_id': dept_id,
            'department_name': department.name,
            'staff_count': len(staff_list),
            'budget_allocation': department.budget_allocation,
            'head_of_dept_id': department.head_of_dept_id,
            'staff': [
                {
                    'id': staff.id,
                    'name': staff.name,
                    'role': staff.role.value,
                    'specialization': staff.specialization
                }
                for staff in staff_list
            ]
        }
