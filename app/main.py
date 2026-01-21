from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from . import models
import os

app = FastAPI(title="Blue-Zone Audit Logger")

# Connect using the endpoint you got from Terraform
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/log-access")
def log_patient_access(doctor_id: str, patient_id: str, action: str, db: Session = Depends(get_db)):
    new_log = models.PatientAuditLog(doctor_id=doctor_id, patient_id=patient_id, action=action)
    db.add(new_log)
    db.commit()
    return {"status": "Securely Logged"}
