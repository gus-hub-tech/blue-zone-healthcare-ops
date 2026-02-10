import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

function DepartmentsDashboard() {
  const [departments, setDepartments] = useState([]);
  const [selectedDept, setSelectedDept] = useState(null);
  const [deptStaff, setDeptStaff] = useState([]);
  const [formData, setFormData] = useState({
    name: '',
    head_of_dept_id: '',
    budget_allocation: ''
  });
  const [staff, setStaff] = useState([]);

  useEffect(() => {
    fetchDepartments();
    fetchStaff();
  }, []);

  const fetchDepartments = async () => {
    try {
      const response = await axios.get(`${API_BASE}/departments`);
      setDepartments(response.data.departments || []);
    } catch (error) {
      console.error('Error fetching departments:', error);
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

  const fetchDeptStaff = async (deptId) => {
    try {
      const response = await axios.get(`${API_BASE}/departments/${deptId}/staff`);
      setDeptStaff(response.data.staff || []);
    } catch (error) {
      console.error('Error fetching department staff:', error);
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
    if (!formData.name || !formData.head_of_dept_id || !formData.budget_allocation) {
      alert('Please fill in all required fields');
      return;
    }

    try {
      await axios.post(`${API_BASE}/departments`, {
        ...formData,
        budget_allocation: parseFloat(formData.budget_allocation)
      });
      setFormData({
        name: '',
        head_of_dept_id: '',
        budget_allocation: ''
      });
      fetchDepartments();
    } catch (error) {
      console.error('Error creating department:', error);
      alert('Failed to create department');
    }
  };

  const selectDepartment = (dept) => {
    setSelectedDept(dept);
    fetchDeptStaff(dept.id);
  };

  return (
    <div className="dashboard">
      <div className="dashboard-section">
        <h2>🏢 Department Management</h2>
        
        <form onSubmit={handleSubmit} className="form">
          <div className="form-row">
            <div className="form-group">
              <label>Department Name *</label>
              <input 
                type="text" 
                name="name" 
                value={formData.name}
                onChange={handleInputChange}
                placeholder="e.g., Cardiology"
                required
              />
            </div>

            <div className="form-group">
              <label>Head of Department *</label>
              <select 
                name="head_of_dept_id" 
                value={formData.head_of_dept_id}
                onChange={handleInputChange}
                required
              >
                <option value="">-- Select staff member --</option>
                {staff.map(member => (
                  <option key={member.id} value={member.id}>
                    {member.name} ({member.specialization})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>Budget Allocation ($) *</label>
            <input 
              type="number" 
              name="budget_allocation" 
              value={formData.budget_allocation}
              onChange={handleInputChange}
              placeholder="e.g., 500000"
              step="0.01"
              required
            />
          </div>

          <button type="submit" className="btn-primary">Create Department</button>
        </form>
      </div>

      <div className="dashboard-section">
        <h3>Departments</h3>
        {departments.length > 0 ? (
          <div className="departments-grid">
            {departments.map(dept => (
              <div 
                key={dept.id} 
                className={`department-card ${selectedDept?.id === dept.id ? 'selected' : ''}`}
                onClick={() => selectDepartment(dept)}
              >
                <div className="dept-header">
                  <h4>{dept.name}</h4>
                  <span className="dept-id">{dept.id}</span>
                </div>
                <div className="dept-info">
                  <p><strong>Head:</strong> {dept.head_of_dept_id}</p>
                  <p><strong>Budget:</strong> ${dept.budget_allocation?.toLocaleString()}</p>
                  <p><strong>Staff Count:</strong> {dept.staff_count || 0}</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="empty-state">No departments created yet</p>
        )}
      </div>

      {selectedDept && (
        <div className="dashboard-section">
          <h3>Staff in {selectedDept.name}</h3>
          {deptStaff.length > 0 ? (
            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Role</th>
                    <th>Specialization</th>
                    <th>License</th>
                  </tr>
                </thead>
                <tbody>
                  {deptStaff.map(member => (
                    <tr key={member.id}>
                      <td>{member.id}</td>
                      <td>{member.name}</td>
                      <td>{member.role}</td>
                      <td>{member.specialization}</td>
                      <td>{member.license_number}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="empty-state">No staff assigned to this department</p>
          )}
        </div>
      )}
    </div>
  );
}

export default DepartmentsDashboard;
