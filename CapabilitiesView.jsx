import React, { useState } from 'react';

const CapabilitiesView = () => {
  const [expanded, setExpanded] = useState(new Set());

  const capabilities = [
    { id: 1, name: 'Investment Management', desc: 'Core investment decision-making', maturity: 4, apps: 8,
      children: [{ id: 11, name: 'Portfolio Construction', maturity: 4, apps: 3 }, { id: 12, name: 'Asset Allocation', maturity: 4, apps: 2 }]
    },
    { id: 2, name: 'Financial Management', desc: 'Financial planning and accounting', maturity: 4, apps: 5,
      children: [{ id: 31, name: 'Accounting & Control', maturity: 4, apps: 2 }, { id: 32, name: 'Financial Planning', maturity: 3, apps: 2 }]
    },
    { id: 3, name: 'Data & Analytics', desc: 'Data management and analytics', maturity: 3, apps: 7,
      children: [{ id: 51, name: 'Data Management', maturity: 3, apps: 3 }, { id: 52, name: 'Business Intelligence', maturity: 4, apps: 2 }]
    }
  ];

  const matColors = ['', '#ef4444', '#f59e0b', '#0ea5e9', '#10b981', '#10b981'];

  const toggleExpand = (id) => {
    const newExp = new Set(expanded);
    newExp.has(id) ? newExp.delete(id) : newExp.add(id);
    setExpanded(newExp);
  };

  return (
    <div className="view-container">
      <div className="view-header">
        <h1 className="view-title">Business Capability Model</h1>
        <p className="view-description">Hierarchical capabilities with maturity assessments</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Level 1 Capabilities</div>
          <div className="stat-value">{capabilities.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Average Maturity</div>
          <div className="stat-value">{(capabilities.reduce((sum, cap) => sum + cap.maturity, 0) / capabilities.length).toFixed(1)}</div>
        </div>
      </div>

      <div className="card">
        {capabilities.map(cap => (
          <div key={cap.id} style={{ marginBottom: '0.5rem', border: '1px solid #e2e8f0', borderRadius: '8px', overflow: 'hidden' }}>
            <div onClick={() => toggleExpand(cap.id)} style={{ padding: '1rem 1.5rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <span style={{ fontSize: '1.2rem' }}>{expanded.has(cap.id) ? '▼' : '▶'}</span>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600, fontSize: '1.05rem' }}>{cap.name}</div>
                <div style={{ fontSize: '0.875rem', color: '#64748b' }}>{cap.desc}</div>
              </div>
              <div style={{ width: '50px', height: '50px', borderRadius: '8px', background: matColors[cap.maturity], color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '1.2rem' }}>
                {cap.maturity}
              </div>
            </div>
            {expanded.has(cap.id) && cap.children && (
              <div style={{ background: '#f8fafc', padding: '0.5rem 1.5rem 1rem 3.5rem', borderTop: '1px solid #e2e8f0' }}>
                {cap.children.map(child => (
                  <div key={child.id} style={{ padding: '0.75rem 1rem', background: 'white', marginBottom: '0.5rem', borderRadius: '6px', display: 'flex', alignItems: 'center', gap: '1rem', border: '1px solid #e2e8f0' }}>
                    <div style={{ flex: 1, fontWeight: 500 }}>{child.name}</div>
                    <div style={{ padding: '0.25rem 0.75rem', borderRadius: '6px', background: matColors[child.maturity], color: 'white', fontSize: '0.875rem', fontWeight: 600 }}>M{child.maturity}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default CapabilitiesView;
