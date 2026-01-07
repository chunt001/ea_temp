import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const ApplicationsView = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');

  const applications = [
    { id: 1, name: 'Investment Management System', type: 'Core Business', status: 'Production', vendor: 'Internal', risk: 'Low', lastReview: '2025-12' },
    { id: 2, name: 'Portfolio Analytics', type: 'Analytics', status: 'Production', vendor: 'Bloomberg', risk: 'Low', lastReview: '2025-11' },
    { id: 3, name: 'Risk Assessment Platform', type: 'Core Business', status: 'Production', vendor: 'MSCI', risk: 'Medium', lastReview: '2025-10' },
    { id: 4, name: 'HR Management System', type: 'Support', status: 'Production', vendor: 'Workday', risk: 'Low', lastReview: '2025-12' },
    { id: 5, name: 'Financial Reporting', type: 'Support', status: 'Production', vendor: 'Oracle', risk: 'Medium', lastReview: '2025-09' },
    { id: 6, name: 'Legacy Trading System', type: 'Legacy', status: 'Decommission Planned', vendor: 'Custom', risk: 'High', lastReview: '2025-08' },
    { id: 7, name: 'Active Directory', type: 'Infrastructure', status: 'Production', vendor: 'Microsoft', risk: 'Low', lastReview: '2025-12' },
    { id: 8, name: 'Business Intelligence', type: 'Analytics', status: 'Production', vendor: 'Tableau', risk: 'Low', lastReview: '2025-10' }
  ];

  const filtered = applications.filter(app => {
    const matchesSearch = app.name.toLowerCase().includes(searchTerm.toLowerCase()) || app.vendor.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = filterType === 'all' || app.type === filterType;
    return matchesSearch && matchesType;
  });

  const typeColors = { 'Core Business': '#0ea5e9', 'Support': '#f59e0b', 'Infrastructure': '#10b981', 'Analytics': '#8b5cf6', 'Legacy': '#ef4444' };
  const appsByType = applications.reduce((acc, app) => { acc[app.type] = (acc[app.type] || 0) + 1; return acc; }, {});

  const getRiskClass = (risk) => {
    return risk === 'Low' ? 'badge-success' : risk === 'Medium' ? 'badge-warning' : 'badge-danger';
  };

  return (
    <div className="view-container">
      <div className="view-header">
        <h1 className="view-title">Application Portfolio</h1>
        <p className="view-description">Comprehensive application inventory with search and filtering</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Applications</div>
          <div className="stat-value">{applications.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Core Business</div>
          <div className="stat-value">{appsByType['Core Business'] || 0}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">High Risk</div>
          <div className="stat-value">{applications.filter(a => a.risk === 'High').length}</div>
        </div>
      </div>

      <div className="card">
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
          <input
            type="text"
            placeholder="Search applications..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ padding: '0.5rem 1rem', borderRadius: '8px', border: '1px solid #e2e8f0', flex: 1, minWidth: '200px' }}
          />
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            style={{ padding: '0.5rem 1rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}
          >
            <option value="all">All Types</option>
            {Object.keys(typeColors).map(type => <option key={type} value={type}>{type}</option>)}
          </select>
        </div>

        <div className="data-table">
          <table>
            <thead>
              <tr>
                <th>Application Name</th>
                <th>Type</th>
                <th>Status</th>
                <th>Vendor</th>
                <th>Risk</th>
                <th>Last Review</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(app => (
                <tr key={app.id}>
                  <td style={{ fontWeight: 500 }}>{app.name}</td>
                  <td><span className="badge badge-primary">{app.type}</span></td>
                  <td><span className={`badge ${app.status === 'Production' ? 'badge-success' : 'badge-danger'}`}>{app.status}</span></td>
                  <td>{app.vendor}</td>
                  <td><span className={`badge ${getRiskClass(app.risk)}`}>{app.risk}</span></td>
                  <td>{app.lastReview}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ApplicationsView;
