import React, { useState } from 'react';
import { loginUser } from '../services/api';

export default function LoginModal({ initialRole = 'student', onClose, onLoginSuccess }) {
  const [role, setRole] = useState(initialRole === 'teacher' ? 'teacher' : 'student');
  const [username, setUsername] = useState(initialRole === 'teacher' ? 'teacher' : 'STU101');
  const [password, setPassword] = useState('password123');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleRoleSwitch = (newRole) => {
    setRole(newRole);
    if (newRole === 'student') {
      setUsername('STU101');
      setPassword('password123');
    } else {
      setUsername('teacher');
      setPassword('password123');
    }
    setErrorMsg('');
  };

  const handleQuickFill = (targetRole, defaultUser, defaultPass) => {
    setRole(targetRole);
    setUsername(defaultUser);
    setPassword(defaultPass);
    setErrorMsg('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg('');
    try {
      const res = await loginUser(role, username, password);
      if (res.status === 'success') {
        onLoginSuccess(res.user, res.role || role);
        onClose();
      } else {
        setErrorMsg(res.message || 'Login failed.');
      }
    } catch (err) {
      setErrorMsg('Server error. Please ensure backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(15, 23, 42, 0.85)',
      backdropFilter: 'blur(12px)',
      zIndex: 1000,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px'
    }}>
      <div className="glass-card" style={{ maxWidth: '440px', width: '100%', border: '1px solid var(--primary)', boxShadow: '0 20px 40px rgba(0,0,0,0.5)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
          <div>
            <h2 style={{ fontSize: '1.3rem', fontWeight: '800', color: '#fff', margin: 0 }}>
              {role === 'teacher' ? '👨‍🏫 Teacher Login' : '🎓 Student Login'}
            </h2>
            <p style={{ margin: '4px 0 0 0', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Enter credentials to access {role === 'teacher' ? 'Teacher Management' : 'Student Dashboard'}
            </p>
          </div>
          <button onClick={onClose} className="btn-secondary" style={{ padding: '6px 12px', fontSize: '0.85rem' }}>✕</button>
        </div>

        {/* Demo Credentials Quick-Select */}
        <div style={{ marginBottom: '16px', padding: '10px', background: 'rgba(59, 130, 246, 0.08)', borderRadius: '8px', border: '1px dashed rgba(59, 130, 246, 0.3)' }}>
          <div style={{ fontSize: '0.75rem', color: '#93c5fd', fontWeight: 600, marginBottom: '6px' }}>⚡ Demo One-Click Fill:</div>
          <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
            {role === 'student' ? (
              <button
                type="button"
                onClick={() => handleQuickFill('student', 'STU101', 'password123')}
                style={{ fontSize: '0.75rem', padding: '4px 8px', background: 'rgba(16, 185, 129, 0.2)', border: '1px solid rgba(16, 185, 129, 0.4)', borderRadius: '6px', color: '#34d399', cursor: 'pointer' }}
              >
                🎓 STU101
              </button>
            ) : (
              <button
                type="button"
                onClick={() => handleQuickFill('teacher', 'teacher', 'password123')}
                style={{ fontSize: '0.75rem', padding: '4px 8px', background: 'rgba(168, 85, 247, 0.2)', border: '1px solid rgba(168, 85, 247, 0.4)', borderRadius: '6px', color: '#c084fc', cursor: 'pointer' }}
              >
                👨‍🏫 teacher
              </button>
            )}
          </div>
        </div>

        {errorMsg && (
          <div style={{ background: 'rgba(239, 68, 68, 0.15)', border: '1px solid #f87171', color: '#f87171', padding: '10px', borderRadius: '8px', fontSize: '0.85rem', marginBottom: '16px' }}>
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group" style={{ marginBottom: '16px' }}>
            <label>
              {role === 'student' ? 'Student ID (e.g. STU101)' : 'Teacher Username'}
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="form-control"
              placeholder={role === 'student' ? 'STU101' : 'teacher'}
              required
            />
          </div>

          <div className="form-group" style={{ marginBottom: '20px' }}>
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="form-control"
              required
            />
          </div>

          <button type="submit" className="btn-primary" style={{ width: '100%', justifyContent: 'center' }} disabled={loading}>
            {loading ? 'Authenticating...' : `Login as ${role === 'student' ? 'Student' : 'Teacher'}`}
          </button>
        </form>
      </div>
    </div>
  );
}
