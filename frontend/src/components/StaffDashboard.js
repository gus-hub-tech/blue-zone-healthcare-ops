import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

function StaffDashboard() {
  const [staff, setStaff] = useState([]);
  const [formData, setFormData] = useState({
    name: '',
    role: 'doctor',
    specialization: '',
    license_number: '',
    department: ''
  });
  const [departments, setDepartments] = useState([]);

  useEffect(() => {
    fetchStaff();
    fetchDepartments();
  }, []);

  const fetchStaff = async () => {
    try {
      const response = await axios.get(`${API_BASE}/staff`);
      setStaff(response.data.staff || []);
    } catch (error) {
      console.error('Error fetching staff:', error);
    }
  };

  const fetchDepartments = async () => {
    try {
      const response = await axios.get(`${API_BASE}/departments`);
      setDepartments(response.data.departments || []);
    } catch (error) {
      console.error('Error fetching departments:', error);
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
    if (!formData.name || !formData.specialization || !formData.license_number) {
      alert('Please fill in all required fields');
      return;
    }

    try {
      await axios.post(`${API_BASE}/staff`, formData);
      setFormData({
        name: '',
        role: 'doctor',
        specialization: '',
        license_number: '',
        department: ''
      });
      fetchStaff();
    } catch (error) {
      console.error('Error adding staff:', error);
      alert('Failed to add staff member');
    }
  };

  const getRoleIcon = (role) => {
    const icons = {
      'doctor': '👨‍⚕️',
      'nurse': '👩‍⚕️',
      'technician': '🔧',
      'admin': '👔'
    };
    return icons[role] || '👤';
  };

  return (
    <div className="dashboard">
      <div className="dashboard-section">
        <h2>👨‍⚕️ Staff Management</h2>
        
        <form onSubmit={handleSubmit} className="form">
          <div className="form-row">
            <div className="form-group">
              <label>Name *</label>
              <input 
                type="text" 
                name="name" 
                value={formData.name}
                onChange={handleInputChange}
                placeholder="Full name"
                required
              />
            </div>

            <div className="form-group">
              <label>Role *</label>
              <select 
                name="role" 
                value={formData.role}
                onChange={handleInputChange}
              >
                <option value="doctor">Doctor</option>
                <option value="nurse">Nurse</option>
                <option value="technician">Technician</option>
                <option value="admin">Admin</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Specialization *</label>
              <input 
                type="text" 
                name="specialization" 
                value={formData.specialization}
                onChange={handleInputChange}
                placeholder="e.g., Cardiology"
                required
              />
            </div>

            <div className="form-group">
              <label>License Number *</label>
              <input 
                type="text" 
                name="license_number" 
                value={formData.license_number}
                onChange={handleInputChange}
                placeholder="License #"
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label>Department</label>
            <select 
              name="department" 
              value={formData.department}
              onChange={handleInputChange}
            >
              <option value="">-- Select department --</option>
              {departments.map(dept => (
                <option key={dept.id} value={dept.id}>
                  {dept.name}
                </option>
              ))}
            </select>
          </div>

          <button type="submit" className="btn-primary">Add Staff Member</button>
        </form>
      </div>

      <div className="dashboard-section">
        <h3>Staff Directory</h3>
        {staff.length > 0 ? (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Role</th>
                  <th>Specialization</th>
                  <th>License</th>
                  <th>Department</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {staff.map(member => (
                  <tr key={member.id}>
                    <td>{member.id}</td>
                    <td>{getRoleIcon(member.role)} {member.name}</td>
                    <td>{member.role}</td>
                    <td>{member.specialization}</td>
                    <td>{member.license_number}</td>
                    <td>{member.department || 'Unassigned'}</td>
                    <td>
                      <span className={`status-badge status-${member.status}`}>
                        {member.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="empty-state">No staff members registered yet</p>
        )}
      </div>
    </div>
  );
}

export default StaffDashboard;
