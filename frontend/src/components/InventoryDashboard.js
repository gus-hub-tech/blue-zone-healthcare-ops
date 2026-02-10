import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

function InventoryDashboard() {
  const [inventory, setInventory] = useState([]);
  const [formData, setFormData] = useState({
    name: '',
    quantity: '',
    unit_cost: '',
    expiration_date: ''
  });
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchInventory();
  }, []);

  const fetchInventory = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/inventory`);
      setInventory(response.data.inventory || []);
    } catch (error) {
      setMessage('Error fetching inventory');
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
      const response = await axios.post(`${API_URL}/inventory`, {
        ...formData,
        quantity: parseInt(formData.quantity),
        unit_cost: parseFloat(formData.unit_cost)
      });
      setInventory([...inventory, response.data]);
      setFormData({ name: '', quantity: '', unit_cost: '', expiration_date: '' });
      setMessage('Item added to inventory!');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('Error adding item');
    }
  };

  const totalValue = inventory.reduce((sum, item) => 
    sum + (item.quantity * item.unit_cost), 0
  );

  return (
    <div className="dashboard">
      <h2>📦 Inventory Management</h2>

      {message && (
        <div className={`alert ${message.includes('Error') ? 'alert-error' : 'alert-success'}`}>
          {message}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label>Item Name</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              required
              placeholder="e.g., Aspirin, Bandages"
            />
          </div>
          <div className="form-group">
            <label>Quantity</label>
            <input
              type="number"
              name="quantity"
              value={formData.quantity}
              onChange={handleInputChange}
              required
              placeholder="100"
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Unit Cost ($)</label>
            <input
              type="number"
              name="unit_cost"
              value={formData.unit_cost}
              onChange={handleInputChange}
              required
              step="0.01"
              placeholder="0.00"
            />
          </div>
          <div className="form-group">
            <label>Expiration Date</label>
            <input
              type="date"
              name="expiration_date"
              value={formData.expiration_date}
              onChange={handleInputChange}
              required
            />
          </div>
        </div>

        <div className="button-group">
          <button type="submit" className="btn btn-primary">Add Item</button>
          <button type="reset" className="btn btn-secondary">Clear</button>
        </div>
      </form>

      <h3 style={{ marginTop: '2rem' }}>Inventory Items</h3>
      <div style={{ 
        background: '#f0f0f0', 
        padding: '1rem', 
        borderRadius: '5px', 
        marginBottom: '1rem',
        fontSize: '1.2rem',
        fontWeight: 'bold'
      }}>
        Total Inventory Value: ${totalValue.toFixed(2)}
      </div>

      {loading ? (
        <div className="loading">Loading inventory...</div>
      ) : inventory.length === 0 ? (
        <div className="empty-state">
          <p>No items in inventory</p>
        </div>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Item Name</th>
              <th>Quantity</th>
              <th>Unit Cost</th>
              <th>Total Value</th>
              <th>Expiration Date</th>
            </tr>
          </thead>
          <tbody>
            {inventory.map(item => (
              <tr key={item.id}>
                <td>{item.id}</td>
                <td>{item.name}</td>
                <td>{item.quantity}</td>
                <td>${item.unit_cost.toFixed(2)}</td>
                <td>${(item.quantity * item.unit_cost).toFixed(2)}</td>
                <td>{item.expiration_date}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default InventoryDashboard;
