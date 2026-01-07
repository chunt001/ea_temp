import React, { useState } from 'react';

const TIMEMatrixView = () => {
  const [selected, setSelected] = useState(null);

  const timeApps = {
    I: [{ name: 'Investment Management System', notes: 'Core business capability' }, { name: 'Risk Assessment Platform', notes: 'Recent upgrades planned' }],
    M: [{ name: 'HR Management System', notes: 'Upgrade to SaaS version' }, { name: 'Financial Reporting', notes: 'API modernization needed' }],
    T: [{ name: 'Legacy Trading System', notes: 'High maintenance costs' }],
    E: [{ name: 'Old Survey Tool', notes: 'Rarely used' }]
  };

  const timeColors = {
    T: { label: 'Tolerate', color: '#ef4444', desc: 'High cost, low value' },
    I: { label: 'Invest', color: '#10b981', desc: 'High value, strategic' },
    M: { label: 'Migrate', color: '#f59e0b', desc: 'Modernization needed' },
    E: { label: 'Eliminate', color: '#64748b', desc: 'Low value, retirement' }
  };

  return (
    <div className="view-container">
      <div className="view-header">
        <h1 className="view-title">TIME Matrix Analysis</h1>
        <p className="view-description">Strategic technology investment framework</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Investment Priorities</div>
          <div className="stat-value">{timeApps.I.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Modernization Needed</div>
          <div className="stat-value">{timeApps.M.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">High-Cost Legacy</div>
          <div className="stat-value">{timeApps.T.length + timeApps.E.length}</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
        {['I', 'M', 'T', 'E'].map(cat => {
          const apps = timeApps[cat];
          return (
            <div key={cat} onClick={() => setSelected(selected === cat ? null : cat)} style={{ background: 'white', border: `3px solid ${timeColors[cat].color}`, borderRadius: '12px', padding: '1.5rem', cursor: 'pointer', transition: 'all 0.3s', transform: selected === cat ? 'scale(1.02)' : 'scale(1)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                <h3 style={{ fontSize: '1.5rem', fontWeight: 700, color: timeColors[cat].color }}>{timeColors[cat].label}</h3>
                <div style={{ width: '50px', height: '50px', borderRadius: '10px', background: timeColors[cat].color, color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.8rem', fontWeight: 'bold' }}>{apps.length}</div>
              </div>
              <p style={{ fontSize: '0.95rem', color: '#64748b', marginBottom: '1rem' }}>{timeColors[cat].desc}</p>
              {selected === cat && apps.map((app, i) => (
                <div key={i} style={{ padding: '0.75rem', background: '#f8fafc', borderRadius: '6px', marginBottom: '0.5rem', border: '1px solid #e2e8f0' }}>
                  <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>{app.name}</div>
                  <div style={{ fontSize: '0.85rem', color: '#64748b' }}>{app.notes}</div>
                </div>
              ))}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default TIMEMatrixView;
