#!/usr/bin/env python3
"""Test a single property"""
import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try to import and run a simple test
try:
    from app.database import SessionLocal
    from app.services.patient_service import PatientService
    from datetime import date, timedelta
    
    print("Imports successful!")
    
    # Try to create a database session
    db = SessionLocal()
    print("Database session created!")
    
    # Try to create a patient service
    service = PatientService(db)
    print("PatientService created!")
    
    # Try to register a patient
    patient_data = {
        'name': 'Test Patient',
        'date_of_birth': date.today() - timedelta(days=365*30),
        'contact_info': 'test@example.com',
        'insurance_id': 'INS123456'
    }
    
    patient = service.register_patient(patient_data)
    print(f"Patient registered: {patient.id}")
    
    # Try to retrieve the patient
    retrieved = service.get_patient(patient.id)
    print(f"Patient retrieved: {retrieved.name}")
    
    db.close()
    print("Test completed successfully!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
