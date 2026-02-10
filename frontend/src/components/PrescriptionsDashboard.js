import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

function PrescriptionsDashboard() {
  const [prescriptions, setPrescriptions] = useState([]);
  const [formData, setFormData] = useState({
    patient_id: '',
    doctor_id: '',
    medication: '',
    dosage: '',
    frequency: '',
    duration: ''
  });
  const [selectedPatient, setSelectedPatient] = useState('');
  const [patients, setPatients] = useState([]);
  const [staff, setStaff] = useState([]);

  useEffect(() => {
    fetchPatients();
    fetchStaff();
  }, []);

  const fetchPatients = async () => {
    try {
      const response = await axios.get(`${API_BASE}/patients`);
      setPatients(response.data.patients || []);
    } catch (error) {
      console.error('Error fetching patients:', error);
    }
  };

  const fetchStaff = async () => {
    try {
      const response = await axios.get(`${API_BASE}/staff`);
      setStaff(response.data.staff || []);
    } catch (error) {
      console.error('Error fetching staff:', error);
    }
  };

  const fetchPrescriptions = async (patientId) => {
    if (!patientId) return;
    try {
      const response = await axios.get(`${API_BASE}/prescriptions/patient/${patientId}`);
      setPrescriptions(response.data.prescriptions || []);
    } catch (error) {
      console.error('Error fetching prescriptions:', error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handlePatientSelect = (e) => {
    const patientId = e.target.value;
    setSelectedPatient(patientId);
    setFormData(prev => ({
      ...prev,
      patient_id: patientId
    }));
    fetchPrescriptions(patientId);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.patient_id || !formData.doctor_id || !formData.medication || 
        !formData.dosage || !formData.frequency || !formData.duration) {
      alert('Please fill in all required fields');
      return;
    }

    try {
      await axios.post(`${API_BASE}/prescriptions`, formData);
      setFormData({
        patient_id: formData.patient_id,
        doctor_id: '',
        medication: '',
        dosage: '',
        frequency: '',
        duration: ''
      });
      fetchPrescriptions(formData.patient_id);
    } catch (error) {
      console.error('Error creating prescription:', error);
      alert('Failed to create prescription');
    }
  };

  const updateStatus = async (prescriptionId, newStatus) => {
    try {
      await axios.patch(`${API_BASE}/prescriptions/${prescriptionId}/status`, { status: newStatus });
      fetchPrescriptions(selectedPatient);
    } catch (error) {
      console.error('Error updating prescription status:', error);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'active': '#10b981',
      'filled': '#3b82f6',
      'expired': '#ef4444',
      'cancelled': '#6b7280'
    };
    return colors[status] || '#6b7280';
  };

  return (
    <div className="dashboard">
      <div className="dashboard-section">
        <h2>💊 Prescription Management</h2>
        
        <form onSubmit={handleSubmit} className="form">
          <div className="form-row">
            <div className="form-group">
              <label>Patient *</label>
              <select 
                value={selectedPatient} 
                onChange={handlePatientSelect}
                required
              >
                <option value="">-- Choose a patient --</option>
                {patients.map(patient => (
                  <option key={patient.id} value={patient.id}>
                    {patient.name} ({patient.id})
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Prescribing Doctor *</label>
              <select 
                name="doctor_id" 
                value={formData.doctor_id}
                onChange={handleInputChange}
                required
              >
                <option value="">-- Select doctor --</option>
                {staff.filter(s => s.role === 'doctor').map(doctor => (
                  <option key={doctor.id} value={doctor.id}>
                    {doctor.name} ({doctor.specialization})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Medication *</label>
              <input 
                type="text" 
                name="medication" 
                value={formData.medication}
                onChange={handleInputChange}
                placeholder="e.g., Aspirin"
                required
              />
            </div>

            <div className="form-group">
              <label>Dosage *</label>
              <input 
                type="text" 
                name="dosage" 
                value={formData.dosage}
                onChange={handleInputChange}
                placeholder="e.g., 500mg"
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Frequency *</label>
              <input 
                type="text" 
                name="frequency" 
                value={formData.frequency}
                onChange={handleInputChange}
                placeholder="e.g., Twice daily"
                required
              />
            </div>

            <div className="form-group">
              <label>Duration *</label>
              <input 
                type="text" 
                name="duration" 
                value={formData.duration}
                onChange={handleInputChange}
                placeholder="e.g., 7 days"
                required
              />
            </div>
          </div>

          <button type="submit" className="btn-primary">Create Prescription</button>
        </form>
      </div>

      <div className="dashboard-section">
        <h3>Patient Prescriptions</h3>
        {selectedPatient ? (
          prescriptions.length > 0 ? (
            <div className="prescriptions-list">
              {prescriptions.map(rx => (
                <div key={rx.id} className="prescription-card">
                  <div className="prescription-header">
                    <strong>{rx.medication}</strong>
                    <span 
                      className="status-badge" 
                      style={{ backgroundColor: getStatusColor(rx.status) }}
                    >
                      {rx.status}
                    </span>
                  </div>
                  <div className="prescription-details">
                    <p><strong>Dosage:</strong> {rx.dosage}</p>
                    <p><strong>Frequency:</strong> {rx.frequency}</p>
                    <p><strong>Duration:</strong> {rx.duration}</p>
                    <p><strong>Doctor:</strong> {rx.doctor_id}</p>
                    <p className="prescription-date">
                      Created: {new Date(rx.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="prescription-actions">
                    {rx.status === 'active' && (
                      <>
                        <button 
                          className="btn-small btn-success"
                          onClick={() => updateStatus(rx.id, 'filled')}
                        >
                          Mark Filled
                        </button>
                        <button 
                          className="btn-small btn-danger"
                          onClick={() => updateStatus(rx.id, 'cancelled')}
                        >
                          Cancel
                        </button>
                      </>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="empty-state">No prescriptions found for this patient</p>
          )
        ) : (
          <p className="empty-state">Select a patient to view their prescriptions</p>
        )}
      </div>
    </div>
  );
}

export default PrescriptionsDashboard;
