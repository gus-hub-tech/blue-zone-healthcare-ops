import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

function BillingDashboard() {
  const [bills, setBills] = useState([]);
  const [formData, setFormData] = useState({
    patient_id: '',
    amount: '',
    description: ''
  });
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchBills();
  }, []);

  const fetchBills = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/billing`);
      setBills(response.data.bills || []);
    } catch (error) {
      setMessage('Error fetching bills');
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
      const response = await axios.post(`${API_URL}/billing`, {
        ...formData,
        amount: parseFloat(formData.amount)
      });
      setBills([...bills, response.data]);
      setFormData({ patient_id: '', amount: '', description: '' });
      setMessage('Bill created successfully!');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('Error creating bill');
    }
  };

  const totalAmount = bills.reduce((sum, bill) => sum + (bill.amount || 0), 0);

  return (
    <div className="dashboard">
      <h2>💰 Billing Management</h2>

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
            <label>Amount ($)</label>
            <input
              type="number"
              name="amount"
              value={formData.amount}
              onChange={handleInputChange}
              required
              step="0.01"
              placeholder="0.00"
            />
          </div>
        </div>

        <div className="form-group">
          <label>Description</label>
          <input
            type="text"
            name="description"
            value={formData.description}
            onChange={handleInputChange}
            required
            placeholder="e.g., Consultation, Surgery, Lab Tests"
          />
        </div>

        <div className="button-group">
          <button type="submit" className="btn btn-primary">Create Bill</button>
          <button type="reset" className="btn btn-secondary">Clear</button>
        </div>
      </form>

      <h3 style={{ marginTop: '2rem' }}>Billing Records</h3>
      <div style={{ 
        background: '#f0f0f0', 
        padding: '1rem', 
        borderRadius: '5px', 
        marginBottom: '1rem',
        fontSize: '1.2rem',
        fontWeight: 'bold'
      }}>
        Total Amount: ${totalAmount.toFixed(2)}
      </div>

      {loading ? (
        <div className="loading">Loading bills...</div>
      ) : bills.length === 0 ? (
        <div className="empty-state">
          <p>No billing records yet</p>
        </div>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Patient ID</th>
              <th>Amount</th>
              <th>Description</th>
              <th>Status</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            {bills.map(bill => (
              <tr key={bill.id}>
                <td>{bill.id}</td>
                <td>{bill.patient_id}</td>
                <td>${bill.amount.toFixed(2)}</td>
                <td>{bill.description}</td>
                <td>
                  <span style={{ color: bill.status === 'pending' ? 'orange' : 'green' }}>
                    ● {bill.status}
                  </span>
                </td>
                <td>{new Date(bill.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default BillingDashboard;
