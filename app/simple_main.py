"""Minimal working FastAPI application"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Hospital Management System",
    version="1.0.0",
    description="A comprehensive hospital management system"
)

@app.get("/")
def read_root():
    return {"message": "Hospital Management System API"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "hospital-management-system"}

@app.get("/docs")
def docs():
    return {"message": "API documentation available at /docs"}

@app.post("/patients")
def create_patient(name: str, dob: str, contact: str):
    return {
        "id": "P001",
        "name": name,
        "dob": dob,
        "contact": contact,
        "status": "active"
    }

@app.get("/patients/{patient_id}")
def get_patient(patient_id: str):
    return {
        "id": patient_id,
        "name": "John Doe",
        "dob": "1990-01-01",
        "contact": "555-1234",
        "status": "active"
    }

@app.get("/appointments")
def list_appointments():
    return {
        "appointments": [
            {"id": "A001", "patient_id": "P001", "doctor_id": "D001", "time": "2026-01-24 10:00"}
        ]
    }

@app.post("/appointments")
def create_appointment(patient_id: str, doctor_id: str, time: str):
    return {
        "id": "A001",
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "time": time,
        "status": "scheduled"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
