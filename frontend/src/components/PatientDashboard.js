import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

function PatientDashboard() {
  const [patients, setPatients] = useState([]);
  const [formData, setFormData] = useState({
    name: '',
    dob: '',
    contact: '',
    insurance_id: ''
  });
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchPatients();
  }, []);

  const fetchPatients = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/patients`);
      setPatients(response.data.patients || []);
    } catch (error) {
      setMessage('Error fetching patients');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API_URL}/patients`, formData);
      setPatients([...patients, response.data]);
      setFormData({ name: '', dob: '', contact: '', insurance_id: '' });
      setMessage('Patient added successfully!');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('Error adding patient');
    }
  };

  return (
    <div className="dashboard">
      <h2>👥 Patient Management</h2>

      {message && (
        <div className={`alert ${message.includes('Error') ? 'alert-error' : 'alert-success'}`}>
          {message}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label>Full Name</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              required
              placeholder="John Doe"
            />
          </div>
          <div className="form-group">
            <label>Date of Birth</label>
            <input
              type="date"
              name="dob"
              value={formData.dob}
              onChange={handleInputChange}
              required
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Contact Number</label>
            <input
              type="tel"
              name="contact"
              value={formData.contact}
              onChange={handleInputChange}
              required
              placeholder="555-1234"
            />
          </div>
          <div className="form-group">
            <label>Insurance ID</label>
            <input
              type="text"
              name="insurance_id"
              value={formData.insurance_id}
              onChange={handleInputChange}
              required
              placeholder="INS-12345"
            />
          </div>
        </div>

        <div className="button-group">
          <button type="submit" className="btn btn-primary">Add Patient</button>
          <button type="reset" className="btn btn-secondary">Clear</button>
        </div>
      </form>

      <h3 style={{ marginTop: '2rem' }}>Registered Patients</h3>
      {loading ? (
        <div className="loading">Loading patients...</div>
      ) : patients.length === 0 ? (
        <div className="empty-state">
          <p>No patients registered yet</p>
        </div>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>DOB</th>
              <th>Contact</th>
              <th>Insurance ID</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {patients.map(patient => (
              <tr key={patient.id}>
                <td>{patient.id}</td>
                <td>{patient.name}</td>
                <td>{patient.dob}</td>
                <td>{patient.contact}</td>
                <td>{patient.insurance_id}</td>
                <td><span style={{ color: 'green' }}>●</span> {patient.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default PatientDashboard;
