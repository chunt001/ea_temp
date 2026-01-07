import React, { useState } from 'react';

const HeatMapView = () => {
  const [metric, setMetric] = useState('coverage');
  const [cell, setCell] = useState(null);

  const heatData = [
    { cap: 'Investment Management', apps: { 'IMS Core': { coverage: 90, maturity: 4, risk: 1, usage: 95 }, 'Portfolio Analytics': { coverage: 85, maturity: 4, risk: 1, usage: 88 }}},
    { cap: 'Financial Management', apps: { 'Oracle Financials': { coverage: 85, maturity: 4, risk: 1, usage: 90 }, 'Treasury System': { coverage: 70, maturity: 4, risk: 1, usage: 85 }}},
    { cap: 'Data & Analytics', apps: { 'Data Warehouse': { coverage: 95, maturity: 4, risk: 1, usage: 92 }, 'Tableau': { coverage: 80, maturity: 4, risk: 1, usage: 88 }}}
  ];

  const allApps = [...new Set(heatData.flatMap(r => Object.keys(r.apps)))].sort();

  const getColor = (v, m) => {
    if (m === 'risk') return v <= 1 ? '#10b981' : v <= 2 ? '#84cc16' : '#f59e0b';
    return v >= 80 ? '#10b981' : v >= 60 ? '#84cc16' : '#f59e0b';
  };

  const getIntensity = (v, m) => {
    if (m === 'risk') return 1 - (v - 1) / 4;
    if (m === 'maturity') return (v - 1) / 4;
    return v / 100;
  };

  return (
    <div className="view-container">
      <div className="view-header">
        <h1 className="view-title">Capability Heat Map</h1>
        <p className="view-description">Application-to-capability mappings with metrics</p>
      </div>

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {['coverage', 'maturity', 'risk', 'usage'].map(m => (
            <button key={m} onClick={() => setMetric(m)} className={`btn ${metric === m ? 'btn-primary' : ''}`} style={{ padding: '0.5rem 1rem', borderRadius: '8px', border: metric === m ? 'none' : '1px solid #e2e8f0', background: metric === m ? '#0ea5e9' : 'white', color: metric === m ? 'white' : '#1e293b' }}>
              {m.charAt(0).toUpperCase() + m.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <div className="card" style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'separate', borderSpacing: '4px', minWidth: '600px' }}>
          <thead>
            <tr>
              <th style={{ padding: '1rem', background: '#1a2332', color: 'white', position: 'sticky', left: 0 }}>Capability</th>
              {allApps.map(app => (<th key={app} style={{ padding: '0.5rem', background: '#2d3748', color: 'white', minWidth: '120px' }}>{app}</th>))}
            </tr>
          </thead>
          <tbody>
            {heatData.map(row => (
              <tr key={row.cap}>
                <td style={{ padding: '1rem', background: '#f8fafc', fontWeight: 600, position: 'sticky', left: 0' }}>{row.cap}</td>
                {allApps.map(app => {
                  const data = row.apps[app];
                  const value = data ? data[metric] : null;
                  const intensity = value !== null ? getIntensity(value, metric) : 0;
                  return (
                    <td key={app} onClick={() => data && setCell({ cap: row.cap, app, ...data })} style={{ padding: '1rem', textAlign: 'center', background: value !== null ? `${getColor(value, metric)}${Math.round(intensity * 100).toString(16).padStart(2, '0')}` : '#f8fafc', cursor: value ? 'pointer' : 'default', fontWeight: 600, color: value !== null && intensity > 0.5 ? 'white' : '#1e293b' }}>
                      {value !== null ? (metric === 'maturity' || metric === 'risk' ? value : `${value}%`) : '—'}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {cell && (
        <div className="card" style={{ marginTop: '1.5rem', border: '2px solid #0ea5e9' }}>
          <h2 className="card-title">Selected Mapping</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem' }}>
            <div><div style={{ fontSize: '0.875rem', color: '#64748b' }}>Capability</div><div style={{ fontWeight: 600 }}>{cell.cap}</div></div>
            <div><div style={{ fontSize: '0.875rem', color: '#64748b' }}>Application</div><div style={{ fontWeight: 600 }}>{cell.app}</div></div>
            <div><div style={{ fontSize: '0.875rem', color: '#64748b' }}>Coverage</div><div style={{ fontWeight: 600 }}>{cell.coverage}%</div></div>
            <div><div style={{ fontSize: '0.875rem', color: '#64748b' }}>Maturity</div><div style={{ fontWeight: 600 }}>Level {cell.maturity}</div></div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HeatMapView;
