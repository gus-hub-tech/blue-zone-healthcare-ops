"""Department management routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session
from database import get_db
from services.department_service import DepartmentService

router = APIRouter(prefix="/departments", tags=["departments"])

class DepartmentCreate(BaseModel):
    """Department creation schema"""
    name: str
    budget_allocation: Decimal
    head_of_dept_id: Optional[str] = None

class DepartmentUpdate(BaseModel):
    """Department update schema"""
    name: Optional[str] = None
    head_of_dept_id: Optional[str] = None
    budget_allocation: Optional[Decimal] = None

class DepartmentResponse(BaseModel):
    """Department response schema"""
    id: str
    name: str
    head_of_dept_id: Optional[str]
    budget_allocation: Decimal
    
    class Config:
        from_attributes = True

@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(dept: DepartmentCreate, db: Session = Depends(get_db)):
    """Create a department"""
    try:
        service = DepartmentService(db)
        created = service.create_department(dept.dict())
        return created
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{dept_id}", response_model=DepartmentResponse)
def get_department(dept_id: str, db: Session = Depends(get_db)):
    """Get department by ID"""
    service = DepartmentService(db)
    dept = service.get_department(dept_id)
    if not dept:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    return dept

@router.put("/{dept_id}", response_model=DepartmentResponse)
def update_department(dept_id: str, updates: DepartmentUpdate, db: Session = Depends(get_db)):
    """Update department"""
    try:
        service = DepartmentService(db)
        updated = service.update_department(dept_id, updates.dict(exclude_unset=True))
        return updated
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{dept_id}/staff")
def get_department_staff(dept_id: str, db: Session = Depends(get_db)):
    """Get department staff"""
    service = DepartmentService(db)
    staff = service.get_department_staff(dept_id)
    return staff

@router.get("/{dept_id}/metrics")
def get_department_metrics(dept_id: str, db: Session = Depends(get_db)):
    """Get department metrics"""
    try:
        service = DepartmentService(db)
        metrics = service.get_department_metrics(dept_id)
        return metrics
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("", response_model=List[DepartmentResponse])
def list_departments(db: Session = Depends(get_db)):
    """List all departments"""
    from models.department import Department
    depts = db.query(Department).all()
    return depts
