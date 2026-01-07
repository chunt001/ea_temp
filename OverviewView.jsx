import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const OverviewView = () => {
  const stats = [
    { label: 'Total Applications', value: '156', change: '+12 this quarter', positive: true },
    { label: 'Business Capabilities', value: '42', change: '8 new mappings', positive: true },
    { label: 'Architecture Reviews', value: '23', change: 'This quarter', positive: null },
    { label: 'Tech Debt Items', value: '34', change: '-8 resolved', positive: true }
  ];

  const applicationsByType = [
    { name: 'Core Business', value: 45, color: '#0ea5e9' },
    { name: 'Support', value: 32, color: '#f59e0b' },
    { name: 'Infrastructure', value: 28, color: '#10b981' },
    { name: 'Analytics', value: 18, color: '#8b5cf6' },
    { name: 'Legacy', value: 33, color: '#ef4444' }
  ];

  return (
    <div className="view-container">
      <div className="view-header">
        <h1 className="view-title">Enterprise Architecture Overview</h1>
        <p className="view-description">
          Comprehensive view of your enterprise architecture landscape, application portfolio, 
          and business capability mappings.
        </p>
      </div>

      <div className="stats-grid">
        {stats.map((stat, index) => (
          <div key={index} className="stat-card">
            <div className="stat-label">{stat.label}</div>
            <div className="stat-value">{stat.value}</div>
            {stat.change && (
              <div className={`stat-change ${stat.positive ? 'positive' : ''}`}>
                {stat.change}
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="card-grid">
        <div className="card">
          <h2 className="card-title">Applications by Type</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={applicationsByType}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {applicationsByType.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card" style={{ marginTop: '1.5rem' }}>
        <h2 className="card-title">Recent Architecture Reviews</h2>
        <div className="data-table">
          <table>
            <thead>
              <tr>
                <th>Project</th>
                <th>Date</th>
                <th>Status</th>
                <th>Decision</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>SharePoint Migration</td>
                <td>Jan 2026</td>
                <td><span className="badge badge-success">Approved</span></td>
                <td>Proceed with Phase 2</td>
              </tr>
              <tr>
                <td>API Gateway Implementation</td>
                <td>Dec 2025</td>
                <td><span className="badge badge-warning">In Review</span></td>
                <td>Pending security assessment</td>
              </tr>
              <tr>
                <td>Legacy System Decommission</td>
                <td>Dec 2025</td>
                <td><span className="badge badge-success">Approved</span></td>
                <td>Q2 2026 timeline</td>
              </tr>
              <tr>
                <td>Cloud Data Platform</td>
                <td>Nov 2025</td>
                <td><span className="badge badge-primary">Completed</span></td>
                <td>Approved with conditions</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default OverviewView;
