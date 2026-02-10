import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

function MedicalRecordsDashboard() {
  const [records, setRecords] = useState([]);
  const [formData, setFormData] = useState({
    patient_id: '',
    diagnosis: '',
    treatment: '',
    notes: ''
  });
  const [selectedPatient, setSelectedPatient] = useState('');
  const [patients, setPatients] = useState([]);

  useEffect(() => {
    fetchPatients();
  }, []);

  const fetchPatients = async () => {
    try {
      const response = await axios.get(`${API_BASE}/patients`);
      setPatients(response.data.patients || []);
    } catch (error) {
      console.error('Error fetching patients:', error);
    }
  };

  const fetchRecords = async (patientId) => {
    if (!patientId) return;
    try {
      const response = await axios.get(`${API_BASE}/medical-records/patient/${patientId}`);
      setRecords(response.data.records || []);
    } catch (error) {
      console.error('Error fetching records:', error);
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
    fetchRecords(patientId);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.patient_id || !formData.diagnosis || !formData.treatment) {
      alert('Please fill in all required fields');
      return;
    }

    try {
      await axios.post(`${API_BASE}/medical-records`, formData);
      setFormData({
        patient_id: formData.patient_id,
        diagnosis: '',
        treatment: '',
        notes: ''
      });
      fetchRecords(formData.patient_id);
    } catch (error) {
      console.error('Error creating record:', error);
      alert('Failed to create medical record');
    }
  };

  return (
    <div className="dashboard">
      <div className="dashboard-section">
        <h2>📋 Medical Records Management</h2>
        
        <form onSubmit={handleSubmit} className="form">
          <div className="form-group">
            <label>Select Patient *</label>
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
            <label>Diagnosis *</label>
            <input 
              type="text" 
              name="diagnosis" 
              value={formData.diagnosis}
              onChange={handleInputChange}
              placeholder="e.g., Hypertension"
              required
            />
          </div>

          <div className="form-group">
            <label>Treatment *</label>
            <input 
              type="text" 
              name="treatment" 
              value={formData.treatment}
              onChange={handleInputChange}
              placeholder="e.g., Medication therapy"
              required
            />
          </div>

          <div className="form-group">
            <label>Clinical Notes</label>
            <textarea 
              name="notes" 
              value={formData.notes}
              onChange={handleInputChange}
              placeholder="Additional clinical notes..."
              rows="3"
            />
          </div>

          <button type="submit" className="btn-primary">Add Medical Record</button>
        </form>
      </div>

      <div className="dashboard-section">
        <h3>Patient Medical History</h3>
        {selectedPatient ? (
          records.length > 0 ? (
            <div className="records-list">
              {records.map(record => (
                <div key={record.id} className="record-card">
                  <div className="record-header">
                    <strong>Record ID: {record.id}</strong>
                    <span className="record-date">
                      {new Date(record.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="record-content">
                    <p><strong>Diagnosis:</strong> {record.diagnosis}</p>
                    <p><strong>Treatment:</strong> {record.treatment}</p>
                    {record.notes && <p><strong>Notes:</strong> {record.notes}</p>}
                    <p className="record-version">Version: {record.version}</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="empty-state">No medical records found for this patient</p>
          )
        ) : (
          <p className="empty-state">Select a patient to view their medical records</p>
        )}
      </div>
    </div>
  );
}

export default MedicalRecordsDashboard;
