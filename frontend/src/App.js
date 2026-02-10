import React, { useState } from 'react';
import './App.css';
import PatientDashboard from './components/PatientDashboard';
import AppointmentDashboard from './components/AppointmentDashboard';
import BillingDashboard from './components/BillingDashboard';
import InventoryDashboard from './components/InventoryDashboard';
import MedicalRecordsDashboard from './components/MedicalRecordsDashboard';
import StaffDashboard from './components/StaffDashboard';
import PrescriptionsDashboard from './components/PrescriptionsDashboard';
import DepartmentsDashboard from './components/DepartmentsDashboard';

function App() {
  const [activeTab, setActiveTab] = useState('patients');

  return (
    <div className="App">
      <header className="header">
        <h1>🏥 Hospital Management System</h1>
        <p>Comprehensive Healthcare Operations Platform</p>
      </header>

      <nav className="navbar">
        <button 
          className={activeTab === 'patients' ? 'active' : ''} 
          onClick={() => setActiveTab('patients')}
        >
          👥 Patients
        </button>
        <button 
          className={activeTab === 'appointments' ? 'active' : ''} 
          onClick={() => setActiveTab('appointments')}
        >
          📅 Appointments
        </button>
        <button 
          className={activeTab === 'medical' ? 'active' : ''} 
          onClick={() => setActiveTab('medical')}
        >
          📋 Medical Records
        </button>
        <button 
          className={activeTab === 'prescriptions' ? 'active' : ''} 
          onClick={() => setActiveTab('prescriptions')}
        >
          💊 Prescriptions
        </button>
        <button 
          className={activeTab === 'staff' ? 'active' : ''} 
          onClick={() => setActiveTab('staff')}
        >
          👨‍⚕️ Staff
        </button>
        <button 
          className={activeTab === 'departments' ? 'active' : ''} 
          onClick={() => setActiveTab('departments')}
        >
          🏢 Departments
        </button>
        <button 
          className={activeTab === 'billing' ? 'active' : ''} 
          onClick={() => setActiveTab('billing')}
        >
          💰 Billing
        </button>
        <button 
          className={activeTab === 'inventory' ? 'active' : ''} 
          onClick={() => setActiveTab('inventory')}
        >
          📦 Inventory
        </button>
      </nav>

      <main className="main-content">
        {activeTab === 'patients' && <PatientDashboard />}
        {activeTab === 'appointments' && <AppointmentDashboard />}
        {activeTab === 'medical' && <MedicalRecordsDashboard />}
        {activeTab === 'prescriptions' && <PrescriptionsDashboard />}
        {activeTab === 'staff' && <StaffDashboard />}
        {activeTab === 'departments' && <DepartmentsDashboard />}
        {activeTab === 'billing' && <BillingDashboard />}
        {activeTab === 'inventory' && <InventoryDashboard />}
      </main>
    </div>
  );
}

export default App;
