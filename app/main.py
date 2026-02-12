"""FastAPI application factory and configuration"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Pydantic models
class PatientCreate(BaseModel):
    name: str
    dob: str
    contact: str
    insurance_id: str

class PatientResponse(BaseModel):
    id: str
    name: str
    dob: str
    contact: str
    insurance_id: str
    status: str

class MedicalRecordCreate(BaseModel):
    patient_id: str
    diagnosis: str
    treatment: str
    notes: str = ""

class PrescriptionCreate(BaseModel):
    patient_id: str
    doctor_id: str
    medication: str
    dosage: str
    frequency: str
    duration: str

class StaffCreate(BaseModel):
    name: str
    role: str
    specialization: str
    license_number: str
    department: str = ""

class DepartmentCreate(BaseModel):
    name: str
    head_of_dept_id: str
    budget_allocation: float

class AppointmentCreate(BaseModel):
    patient_id: str
    doctor_id: str
    scheduled_time: str

class AppointmentResponse(BaseModel):
    id: str
    patient_id: str
    doctor_id: str
    scheduled_time: str
    status: str

class BillingCreate(BaseModel):
    patient_id: str
    amount: float
    description: str

class InventoryCreate(BaseModel):
    name: str
    quantity: int
    unit_cost: float
    expiration_date: str

# In-memory storage for demo
patients_db = {}
medical_records_db = {}
prescriptions_db = {}
appointments_db = {}
staff_db = {}
departments_db = {}
billing_db = {}
inventory_db = {}

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        description="Comprehensive Hospital Management System"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Health check endpoint
    @app.get("/health")
    def health_check():
        return {"status": "healthy", "service": "hospital-management-system"}
    
    @app.get("/")
    def root():
        return {"message": "Hospital Management System API", "version": "1.0.0"}
    
    # ===== PATIENT ENDPOINTS =====
    @app.post("/patients", response_model=PatientResponse)
    def create_patient(patient: PatientCreate):
        patient_id = f"P{len(patients_db) + 1:03d}"
        patients_db[patient_id] = {
            "id": patient_id,
            "name": patient.name,
            "dob": patient.dob,
            "contact": patient.contact,
            "insurance_id": patient.insurance_id,
            "status": "active"
        }
        return patients_db[patient_id]
    
    @app.get("/patients/{patient_id}", response_model=PatientResponse)
    def get_patient(patient_id: str):
        if patient_id not in patients_db:
            return {"error": "Patient not found"}
        return patients_db[patient_id]
    
    @app.get("/patients")
    def list_patients():
        return {"patients": list(patients_db.values())}
    
    # ===== MEDICAL RECORDS ENDPOINTS =====
    @app.post("/medical-records")
    def create_medical_record(record: MedicalRecordCreate):
        record_id = f"MR{len(medical_records_db) + 1:03d}"
        medical_records_db[record_id] = {
            "id": record_id,
            "patient_id": record.patient_id,
            "diagnosis": record.diagnosis,
            "treatment": record.treatment,
            "notes": record.notes,
            "created_at": datetime.now().isoformat(),
            "version": 1
        }
        return medical_records_db[record_id]
    
    @app.get("/medical-records/patient/{patient_id}")
    def get_patient_medical_records(patient_id: str):
        records = [r for r in medical_records_db.values() if r["patient_id"] == patient_id]
        return {"records": records}
    
    @app.get("/medical-records/{record_id}")
    def get_medical_record(record_id: str):
        if record_id not in medical_records_db:
            return {"error": "Record not found"}
        return medical_records_db[record_id]
    
    # ===== PRESCRIPTION ENDPOINTS =====
    @app.post("/prescriptions")
    def create_prescription(prescription: PrescriptionCreate):
        prescription_id = f"RX{len(prescriptions_db) + 1:03d}"
        prescriptions_db[prescription_id] = {
            "id": prescription_id,
            "patient_id": prescription.patient_id,
            "doctor_id": prescription.doctor_id,
            "medication": prescription.medication,
            "dosage": prescription.dosage,
            "frequency": prescription.frequency,
            "duration": prescription.duration,
            "status": "active",
            "created_at": datetime.now().isoformat()
        }
        return prescriptions_db[prescription_id]
    
    @app.get("/prescriptions/patient/{patient_id}")
    def get_patient_prescriptions(patient_id: str):
        prescriptions = [p for p in prescriptions_db.values() if p["patient_id"] == patient_id]
        return {"prescriptions": prescriptions}
    
    @app.get("/prescriptions/{prescription_id}")
    def get_prescription(prescription_id: str):
        if prescription_id not in prescriptions_db:
            return {"error": "Prescription not found"}
        return prescriptions_db[prescription_id]
    
    @app.patch("/prescriptions/{prescription_id}/status")
    def update_prescription_status(prescription_id: str, status: str):
        if prescription_id not in prescriptions_db:
            return {"error": "Prescription not found"}
        prescriptions_db[prescription_id]["status"] = status
        return prescriptions_db[prescription_id]
    
    # ===== STAFF ENDPOINTS =====
    @app.post("/staff")
    def add_staff(staff: StaffCreate):
        staff_id = f"S{len(staff_db) + 1:03d}"
        staff_db[staff_id] = {
            "id": staff_id,
            "name": staff.name,
            "role": staff.role,
            "specialization": staff.specialization,
            "license_number": staff.license_number,
            "department": staff.department,
            "status": "active"
        }
        return staff_db[staff_id]
    
    @app.get("/staff")
    def list_staff():
        return {"staff": list(staff_db.values())}
    
    @app.get("/staff/{staff_id}")
    def get_staff(staff_id: str):
        if staff_id not in staff_db:
            return {"error": "Staff not found"}
        return staff_db[staff_id]
    
    @app.put("/staff/{staff_id}")
    def update_staff(staff_id: str, staff: StaffCreate):
        if staff_id not in staff_db:
            return {"error": "Staff not found"}
        staff_db[staff_id].update(staff.dict())
        return staff_db[staff_id]
    
    # ===== DEPARTMENT ENDPOINTS =====
    @app.post("/departments")
    def create_department(dept: DepartmentCreate):
        dept_id = f"D{len(departments_db) + 1:03d}"
        departments_db[dept_id] = {
            "id": dept_id,
            "name": dept.name,
            "head_of_dept_id": dept.head_of_dept_id,
            "budget_allocation": dept.budget_allocation,
            "staff_count": 0
        }
        return departments_db[dept_id]
    
    @app.get("/departments")
    def list_departments():
        return {"departments": list(departments_db.values())}
    
    @app.get("/departments/{dept_id}")
    def get_department(dept_id: str):
        if dept_id not in departments_db:
            return {"error": "Department not found"}
        dept = departments_db[dept_id]
        dept["staff_count"] = len([s for s in staff_db.values() if s["department"] == dept_id])
        return dept
    
    @app.get("/departments/{dept_id}/staff")
    def get_department_staff(dept_id: str):
        staff = [s for s in staff_db.values() if s["department"] == dept_id]
        return {"staff": staff}
    
    # ===== APPOINTMENT ENDPOINTS =====
    @app.post("/appointments", response_model=AppointmentResponse)
    def create_appointment(appointment: AppointmentCreate):
        # Check for double-booking
        for apt in appointments_db.values():
            if (apt["doctor_id"] == appointment.doctor_id and 
                apt["scheduled_time"] == appointment.scheduled_time and
                apt["status"] == "scheduled"):
                return {"error": "Doctor already has appointment at this time"}
        
        appointment_id = f"A{len(appointments_db) + 1:03d}"
        appointments_db[appointment_id] = {
            "id": appointment_id,
            "patient_id": appointment.patient_id,
            "doctor_id": appointment.doctor_id,
            "scheduled_time": appointment.scheduled_time,
            "status": "scheduled"
        }
        return appointments_db[appointment_id]
    
    @app.get("/appointments/{appointment_id}", response_model=AppointmentResponse)
    def get_appointment(appointment_id: str):
        if appointment_id not in appointments_db:
            return {"error": "Appointment not found"}
        return appointments_db[appointment_id]
    
    @app.get("/appointments")
    def list_appointments():
        return {"appointments": list(appointments_db.values())}
    
    @app.delete("/appointments/{appointment_id}")
    def cancel_appointment(appointment_id: str):
        if appointment_id not in appointments_db:
            return {"error": "Appointment not found"}
        appointments_db[appointment_id]["status"] = "cancelled"
        return {"status": "cancelled"}
    
    @app.get("/appointments/doctor/{doctor_id}/available-slots")
    def get_available_slots(doctor_id: str):
        booked_times = [apt["scheduled_time"] for apt in appointments_db.values() 
                       if apt["doctor_id"] == doctor_id and apt["status"] == "scheduled"]
        return {"doctor_id": doctor_id, "booked_times": booked_times}
    
    # ===== BILLING ENDPOINTS =====
    @app.post("/billing")
    def create_billing(billing: BillingCreate):
        billing_id = f"B{len(billing_db) + 1:03d}"
        billing_db[billing_id] = {
            "id": billing_id,
            "patient_id": billing.patient_id,
            "amount": billing.amount,
            "description": billing.description,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        return billing_db[billing_id]
    
    @app.get("/billing/{billing_id}")
    def get_billing(billing_id: str):
        if billing_id not in billing_db:
            return {"error": "Billing record not found"}
        return billing_db[billing_id]
    
    @app.get("/billing/patient/{patient_id}/billing")
    def get_patient_billing(patient_id: str):
        bills = [b for b in billing_db.values() if b["patient_id"] == patient_id]
        total = sum(b["amount"] for b in bills)
        return {"bills": bills, "total": total}
    
    @app.get("/billing/patient/{patient_id}/balance")
    def get_patient_balance(patient_id: str):
        bills = [b for b in billing_db.values() if b["patient_id"] == patient_id]
        total = sum(b["amount"] for b in bills)
        return {"patient_id": patient_id, "balance": total}
    
    @app.patch("/billing/{billing_id}/finalize")
    def finalize_billing(billing_id: str):
        if billing_id not in billing_db:
            return {"error": "Billing record not found"}
        billing_db[billing_id]["status"] = "finalized"
        return billing_db[billing_id]
    
    # ===== INVENTORY ENDPOINTS =====
    @app.post("/inventory")
    def add_inventory(item: InventoryCreate):
        item_id = f"INV{len(inventory_db) + 1:03d}"
        inventory_db[item_id] = {
            "id": item_id,
            "name": item.name,
            "quantity": item.quantity,
            "unit_cost": item.unit_cost,
            "expiration_date": item.expiration_date
        }
        return inventory_db[item_id]
    
    @app.get("/inventory")
    def list_inventory():
        return {"inventory": list(inventory_db.values())}
    
    @app.get("/inventory/{item_id}")
    def get_inventory_item(item_id: str):
        if item_id not in inventory_db:
            return {"error": "Item not found"}
        return inventory_db[item_id]
    
    @app.patch("/inventory/{item_id}/consume")
    def consume_inventory(item_id: str, quantity: int):
        if item_id not in inventory_db:
            return {"error": "Item not found"}
        if inventory_db[item_id]["quantity"] < quantity:
            return {"error": "Insufficient quantity"}
        inventory_db[item_id]["quantity"] -= quantity
        return inventory_db[item_id]
    
    @app.get("/inventory/low-stock")
    def get_low_stock_items(threshold: int = 10):
        low_stock = [item for item in inventory_db.values() if item["quantity"] < threshold]
        return {"low_stock_items": low_stock}
    
    @app.get("/inventory/expired")
    def get_expired_items():
        today = datetime.now().date()
        expired = [item for item in inventory_db.values() 
                  if datetime.fromisoformat(item["expiration_date"]).date() < today]
        return {"expired_items": expired}
    
    return app

# Create app instance
app = create_app()
