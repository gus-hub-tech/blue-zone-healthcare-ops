"""Models package"""
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from models.patient import Patient, PatientStatus
from models.audit import PatientAuditLog
from models.medical_record import MedicalRecord, Diagnosis, Treatment, ClinicalNote
from models.appointment import Appointment, AppointmentSlot, AppointmentStatus
from models.staff import Staff, StaffRole, StaffStatus, StaffCredential, StaffAvailability
from models.prescription import Prescription, PrescriptionItem, PrescriptionStatus
from models.billing import BillingRecord, BillingItem, Payment, BillingStatus, PaymentStatus
from models.inventory import InventoryItem, InventoryTransaction, InventoryTransactionType
from models.department import Department, DepartmentStaff
from models.access_control import User, Role, AccessLog, UserRole, AccessLogAction

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
