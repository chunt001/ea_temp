import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import OverviewView from './views/OverviewView';
import ApplicationsView from './views/ApplicationsView';
import CapabilitiesView from './views/CapabilitiesView';
import TIMEMatrixView from './views/TIMEMatrixView';
import HeatMapView from './views/HeatMapView';
import './App.css';

function App() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [currentView, setCurrentView] = useState('overview');

  const views = [
    { id: 'overview', path: '/', label: 'Overview', icon: '◈', component: OverviewView },
    { id: 'applications', path: '/applications', label: 'Applications', icon: '▣', component: ApplicationsView },
    { id: 'capabilities', path: '/capabilities', label: 'Capabilities', icon: '◉', component: CapabilitiesView },
    { id: 'time', path: '/time-matrix', label: 'TIME Matrix', icon: '▦', component: TIMEMatrixView },
    { id: 'heatmap', path: '/heatmap', label: 'Heat Maps', icon: '▨', component: HeatMapView }
  ];

  const ViewNavigation = () => (
    <div className="view-nav">
      <div className="view-nav-label">Navigate:</div>
      {views.map(view => (
        <button
          key={view.id}
          onClick={() => setCurrentView(view.id)}
          className={`view-nav-btn ${currentView === view.id ? 'active' : ''}`}
        >
          <span style={{ fontSize: '1.1rem' }}>{view.icon}</span>
          <span>{view.label}</span>
        </button>
      ))}
    </div>
  );

  return (
    <Router>
      <div className="app-container">
        <aside className={`sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
          <div className="sidebar-header">
            <div className="logo-section">
              <div className="logo-icon">EA</div>
              {!sidebarCollapsed && <h1>Enterprise Architecture</h1>}
            </div>
            <button 
              className="collapse-btn"
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              aria-label={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
            >
              {sidebarCollapsed ? '→' : '←'}
            </button>
          </div>

          <nav className="nav-menu">
            {views.map(view => (
              <div
                key={view.id}
                onClick={() => setCurrentView(view.id)}
                className={`nav-link ${currentView === view.id ? 'active' : ''}`}
              >
                <span className="nav-icon">{view.icon}</span>
                {!sidebarCollapsed && <span>{view.label}</span>}
              </div>
            ))}
          </nav>

          {!sidebarCollapsed && (
            <div className="sidebar-footer">
              v1.0.0 - BCI EA Team
            </div>
          )}
        </aside>

        <main className="main-content">
          <div className="fade-in">
            <ViewNavigation />
            <Routes>
              <Route path="/" element={<OverviewView />} />
              <Route path="/applications" element={<ApplicationsView />} />
              <Route path="/capabilities" element={<CapabilitiesView />} />
              <Route path="/time-matrix" element={<TIMEMatrixView />} />
              <Route path="/heatmap" element={<HeatMapView />} />
            </Routes>
          </div>
        </main>
      </div>
    </Router>
  );
}

export default App;
