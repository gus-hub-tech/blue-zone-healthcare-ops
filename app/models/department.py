"""Department models"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric
from sqlalchemy.sql import func
from datetime import datetime
from app.models import Base

class Department(Base):
    """Department model"""
    __tablename__ = "departments"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    head_of_dept_id = Column(String, ForeignKey("staff.id"), nullable=True)
    budget_allocation = Column(Numeric(12, 2), nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

class DepartmentStaff(Base):
    """Department staff assignment model"""
    __tablename__ = "department_staff"
    
    id = Column(String, primary_key=True, index=True)
    department_id = Column(String, ForeignKey("departments.id"), nullable=False, index=True)
    staff_id = Column(String, ForeignKey("staff.id"), nullable=False, index=True)
    assignment_date = Column(DateTime, server_default=func.now(), nullable=False)
    end_date = Column(DateTime, nullable=True)
