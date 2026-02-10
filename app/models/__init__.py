"""Models package"""
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from app.models.patient import Patient, PatientStatus
from app.models.audit import PatientAuditLog
from app.models.medical_record import MedicalRecord, Diagnosis, Treatment, ClinicalNote
from app.models.appointment import Appointment, AppointmentSlot, AppointmentStatus
from app.models.staff import Staff, StaffRole, StaffStatus, StaffCredential, StaffAvailability
from app.models.prescription import Prescription, PrescriptionItem, PrescriptionStatus
from app.models.billing import BillingRecord, BillingItem, Payment, BillingStatus, PaymentStatus
from app.models.inventory import InventoryItem, InventoryTransaction, InventoryTransactionType
from app.models.department import Department, DepartmentStaff
from app.models.access_control import User, Role, AccessLog, UserRole, AccessLogAction

__all__ = [
    'Base',
    'Patient', 'PatientStatus', 'PatientAuditLog',
    'MedicalRecord', 'Diagnosis', 'Treatment', 'ClinicalNote',
    'Appointment', 'AppointmentSlot', 'AppointmentStatus',
    'Staff', 'StaffRole', 'StaffStatus', 'StaffCredential', 'StaffAvailability',
    'Prescription', 'PrescriptionItem', 'PrescriptionStatus',
    'BillingRecord', 'BillingItem', 'Payment', 'BillingStatus', 'PaymentStatus',
    'InventoryItem', 'InventoryTransaction', 'InventoryTransactionType',
    'Department', 'DepartmentStaff',
    'User', 'Role', 'AccessLog', 'UserRole', 'AccessLogAction'
]
