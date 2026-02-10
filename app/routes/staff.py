"""Staff management routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.staff_service import StaffService

router = APIRouter(prefix="/staff", tags=["staff"])

class StaffCreate(BaseModel):
    """Staff creation schema"""
    name: str
    role: str
    specialization: Optional[str] = None
    license_number: Optional[str] = None
    department_id: Optional[str] = None

class StaffUpdate(BaseModel):
    """Staff update schema"""
    name: Optional[str] = None
    specialization: Optional[str] = None
    license_number: Optional[str] = None
    status: Optional[str] = None

class StaffResponse(BaseModel):
    """Staff response schema"""
    id: str
    name: str
    role: str
    specialization: Optional[str]
    license_number: Optional[str]
    department_id: Optional[str]
    status: str
    
    class Config:
        from_attributes = True

@router.post("", response_model=StaffResponse, status_code=status.HTTP_201_CREATED)
def add_staff(staff: StaffCreate, db: Session = Depends(get_db)):
    """Add new staff member"""
    try:
        service = StaffService(db)
        created = service.add_staff(staff.dict())
        return created
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{staff_id}", response_model=StaffResponse)
def get_staff(staff_id: str, db: Session = Depends(get_db)):
    """Get staff member by ID"""
    service = StaffService(db)
    staff = service.get_staff(staff_id)
    if not staff:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff member not found")
    return staff

@router.put("/{staff_id}", response_model=StaffResponse)
def update_staff(staff_id: str, updates: StaffUpdate, db: Session = Depends(get_db)):
    """Update staff information"""
    try:
        service = StaffService(db)
        updated = service.update_staff(staff_id, updates.dict(exclude_unset=True))
        return updated
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.patch("/{staff_id}/department")
def assign_to_department(staff_id: str, department_id: str, db: Session = Depends(get_db)):
    """Assign staff to department"""
    try:
        service = StaffService(db)
        updated = service.assign_to_department(staff_id, department_id)
        return updated
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{staff_id}/availability")
def get_availability(staff_id: str, db: Session = Depends(get_db)):
    """Get staff member's availability"""
    service = StaffService(db)
    availability = service.get_availability(staff_id)
    return availability

@router.get("/department/{dept_id}/staff", response_model=List[StaffResponse])
def get_department_staff(dept_id: str, db: Session = Depends(get_db)):
    """Get all staff in a department"""
    service = StaffService(db)
    staff = service.get_staff_by_department(dept_id)
    return staff
