import React from 'react';

export default function Navbar({
  activeTab,
  setActiveTab,
  selectedSubject,
  setSelectedSubject,
  subjects
}) {
  return (
    <nav style={{
      background: 'rgba(15, 23, 42, 0.9)',
      backdropFilter: 'blur(16px)',
      borderBottom: '1px solid var(--border-color)',
      position: 'sticky',
      top: 0,
      zIndex: 100,
      padding: '12px 24px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      gap: '16px',
      flexWrap: 'wrap'
    }}>
      {/* Brand / Logo */}
      <div
        style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }}
        onClick={() => setActiveTab('prediction')}
      >
        <div style={{
          width: '38px',
          height: '38px',
          borderRadius: '10px',
          background: 'var(--primary-gradient)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '19px',
          boxShadow: '0 0 20px rgba(99, 102, 241, 0.5)'
        }}>
          🧠
        </div>
        <div>
          <div style={{ fontSize: '1.15rem', fontWeight: '800', background: 'linear-gradient(135deg, #fff 0%, #cbd5e1 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            NeuroLearn AI
          </div>
          <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', fontWeight: '600', letterSpacing: '0.05em' }}>
            INTELLIGENT LEARNING & PLACEMENT PLATFORM
          </div>
        </div>
      </div>

      {/* Primary Navigation Tabs - Module 1, 2, 3 (Admin removed completely) */}
      <div style={{ display: 'flex', gap: '6px', background: 'rgba(30, 41, 59, 0.6)', padding: '4px', borderRadius: '10px', border: '1px solid var(--border-color)', flexWrap: 'wrap' }}>
        <button
          onClick={() => setActiveTab('prediction')}
          className={activeTab === 'prediction' ? 'btn-primary' : 'btn-secondary'}
          style={{ padding: '7px 12px', fontSize: '0.8rem', borderRadius: '8px' }}
        >
          📊 Module 1: Prediction
        </button>

        <button
          onClick={() => setActiveTab('collaboration')}
          className={activeTab === 'collaboration' ? 'btn-primary' : 'btn-secondary'}
          style={{ padding: '7px 12px', fontSize: '0.8rem', borderRadius: '8px' }}
        >
          🤝 Module 2: Collaboration
        </button>

        <button
          onClick={() => setActiveTab('placement')}
          className={activeTab === 'placement' ? 'btn-primary' : 'btn-secondary'}
          style={{ padding: '7px 12px', fontSize: '0.8rem', borderRadius: '8px' }}
        >
          🎯 Module 3: Placement
        </button>
      </div>

      {/* Subject Selector Only (Profession, Switch, and Logout removed) */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: '700' }}>SUBJECT:</span>
        <select
          value={selectedSubject}
          onChange={(e) => setSelectedSubject(e.target.value)}
          className="form-control"
          style={{ padding: '6px 12px', fontSize: '0.82rem', width: '200px', background: 'rgba(30, 41, 59, 0.9)' }}
        >
          {subjects.map((sub, i) => (
            <option key={i} value={sub}>{sub}</option>
          ))}
        </select>
      </div>
    </nav>
  );
}
