import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

function AppointmentDashboard() {
  const [appointments, setAppointments] = useState([]);
  const [formData, setFormData] = useState({
    patient_id: '',
    doctor_id: '',
    scheduled_time: ''
  });
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchAppointments();
  }, []);

  const fetchAppointments = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/appointments`);
      setAppointments(response.data.appointments || []);
    } catch (error) {
      setMessage('Error fetching appointments');
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
      const response = await axios.post(`${API_URL}/appointments`, formData);
      setAppointments([...appointments, response.data]);
      setFormData({ patient_id: '', doctor_id: '', scheduled_time: '' });
      setMessage('Appointment scheduled successfully!');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('Error scheduling appointment');
    }
  };

  const handleCancel = async (appointmentId) => {
    try {
      await axios.delete(`${API_URL}/appointments/${appointmentId}`);
      setAppointments(appointments.map(apt => 
        apt.id === appointmentId ? { ...apt, status: 'cancelled' } : apt
      ));
      setMessage('Appointment cancelled');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('Error cancelling appointment');
    }
  };

  return (
    <div className="dashboard">
      <h2>📅 Appointment Scheduling</h2>

      {message && (
        <div className={`alert ${message.includes('Error') ? 'alert-error' : 'alert-success'}`}>
          {message}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label>Patient ID</label>
            <input
              type="text"
              name="patient_id"
              value={formData.patient_id}
              onChange={handleInputChange}
              required
              placeholder="P001"
            />
          </div>
          <div className="form-group">
            <label>Doctor ID</label>
            <input
              type="text"
              name="doctor_id"
              value={formData.doctor_id}
              onChange={handleInputChange}
              required
              placeholder="D001"
            />
          </div>
        </div>

        <div className="form-group">
          <label>Appointment Date & Time</label>
          <input
            type="datetime-local"
            name="scheduled_time"
            value={formData.scheduled_time}
            onChange={handleInputChange}
            required
          />
        </div>

        <div className="button-group">
          <button type="submit" className="btn btn-primary">Schedule Appointment</button>
          <button type="reset" className="btn btn-secondary">Clear</button>
        </div>
      </form>

      <h3 style={{ marginTop: '2rem' }}>Scheduled Appointments</h3>
      {loading ? (
        <div className="loading">Loading appointments...</div>
      ) : appointments.length === 0 ? (
        <div className="empty-state">
          <p>No appointments scheduled yet</p>
        </div>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Patient ID</th>
              <th>Doctor ID</th>
              <th>Date & Time</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {appointments.map(apt => (
              <tr key={apt.id}>
                <td>{apt.id}</td>
                <td>{apt.patient_id}</td>
                <td>{apt.doctor_id}</td>
                <td>{apt.scheduled_time}</td>
                <td>
                  <span style={{ color: apt.status === 'scheduled' ? 'green' : 'red' }}>
                    ● {apt.status}
                  </span>
                </td>
                <td>
                  {apt.status === 'scheduled' && (
                    <button 
                      className="btn btn-danger" 
                      onClick={() => handleCancel(apt.id)}
                      style={{ padding: '0.5rem 1rem', fontSize: '0.9rem' }}
                    >
                      Cancel
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default AppointmentDashboard;
