#!/usr/bin/env python3
"""Run property-based tests and report results"""
import subprocess
import sys

# List of all property tests to run
tests = [
    "app/tests/properties/test_all_properties.py::TestPatientProperties::test_patient_registration_idempotence",
    "app/tests/properties/test_all_properties.py::TestPatientProperties::test_patient_data_persistence",
    "app/tests/properties/test_all_properties.py::TestAppointmentProperties::test_appointment_double_booking_prevention",
    "app/tests/properties/test_all_properties.py::TestAppointmentCancellationProperties::test_appointment_cancellation_frees_slot",
    "app/tests/properties/test_all_properties.py::TestMedicalRecordProperties::test_medical_record_version_history",
    "app/tests/properties/test_all_properties.py::TestPrescriptionProperties::test_prescription_medication_validation",
    "app/tests/properties/test_all_properties.py::TestBillingProperties::test_billing_amount_calculation_consistency",
    "app/tests/properties/test_all_properties.py::TestInventoryProperties::test_inventory_consumption_decrements_stock",
    "app/tests/properties/test_all_properties.py::TestInventoryExpirationProperties::test_expired_item_prevention",
    "app/tests/properties/test_all_properties.py::TestDepartmentProperties::test_department_staff_assignment_consistency",
    "app/tests/properties/test_all_properties.py::TestAccessControlProperties::test_access_control_enforcement",
    "app/tests/properties/test_all_properties.py::TestBillingImmutabilityProperties::test_audit_trail_immutability",
    "app/tests/properties/test_all_properties.py::TestTransactionConsistencyProperties::test_transaction_consistency",
]

print("Running property-based tests...")
for test in tests:
    print(f"\nRunning: {test}")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test, "-v", "--tb=short", "--hypothesis-seed=0"],
        timeout=60
    )
    if result.returncode != 0:
        print(f"FAILED: {test}")
    else:
        print(f"PASSED: {test}")

print("\nAll tests completed!")
