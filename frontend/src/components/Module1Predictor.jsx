import React, { useState } from 'react';
import { predictPerformance } from '../services/api';

export default function Module1Predictor({ subject }) {
  const [formData, setFormData] = useState({
    ia1_marks: 38,
    ia2_marks: 40,
    ia3_marks: 42,
    assignment_marks: 18,
    attendance_pct: 88,
    previous_gpa: 8.5
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: parseFloat(e.target.value) || 0 });
  };

  const handlePredict = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await predictPerformance(formData);
      setResult(res.prediction);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '1.8rem', fontWeight: '700', marginBottom: '8px' }}>
          Module 1: Student Performance Prediction
        </h1>
        <p style={{ color: 'var(--text-muted)' }}>
          Powered by Feed Forward Neural Network (FFNN) model predicting semester performance from IA1, IA2, IA3, assignments, attendance, and GPA for <strong style={{ color: 'var(--primary)' }}>{subject}</strong>.
        </p>
      </div>

      <div className="grid-2">
        {/* Form Input Card */}
        <div className="glass-card">
          <h3 style={{ fontSize: '1.1rem', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            📝 Internal Assessment Inputs
          </h3>

          <form onSubmit={handlePredict}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <div className="form-group">
                <label>IA 1 Marks (Max 50)</label>
                <input
                  type="number"
                  name="ia1_marks"
                  max="50"
                  min="0"
                  value={formData.ia1_marks}
                  onChange={handleChange}
                  className="form-control"
                  required
                />
              </div>

              <div className="form-group">
                <label>IA 2 Marks (Max 50)</label>
                <input
                  type="number"
                  name="ia2_marks"
                  max="50"
                  min="0"
                  value={formData.ia2_marks}
                  onChange={handleChange}
                  className="form-control"
                  required
                />
              </div>

              <div className="form-group">
                <label>IA 3 Marks (Max 50)</label>
                <input
                  type="number"
                  name="ia3_marks"
                  max="50"
                  min="0"
                  value={formData.ia3_marks}
                  onChange={handleChange}
                  className="form-control"
                  required
                />
              </div>

              <div className="form-group">
                <label>Assignment Marks (Max 20)</label>
                <input
                  type="number"
                  name="assignment_marks"
                  max="20"
                  min="0"
                  value={formData.assignment_marks}
                  onChange={handleChange}
                  className="form-control"
                  required
                />
              </div>

              <div className="form-group">
                <label>Attendance % (0-100)</label>
                <input
                  type="number"
                  name="attendance_pct"
                  max="100"
                  min="0"
                  value={formData.attendance_pct}
                  onChange={handleChange}
                  className="form-control"
                  required
                />
              </div>

              <div className="form-group">
                <label>Previous GPA (0-10)</label>
                <input
                  type="number"
                  name="previous_gpa"
                  step="0.1"
                  max="10"
                  min="0"
                  value={formData.previous_gpa}
                  onChange={handleChange}
                  className="form-control"
                  required
                />
              </div>
            </div>

            <button type="submit" className="btn-primary" style={{ width: '100%', marginTop: '16px', justifyContent: 'center' }} disabled={loading}>
              {loading ? 'Analyzing Neural Network...' : '⚡ Predict Semester Performance'}
            </button>
          </form>
        </div>

        {/* Prediction Results Display */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', textAlign: 'center', minHeight: '350px' }}>
          {result ? (
            <div style={{ animation: 'fadeIn 0.5s ease-in' }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '8px' }}>
                EXPECTED SEMESTER SCORE
              </div>
              <div style={{ fontSize: '3.5rem', fontWeight: '800', background: 'var(--primary-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', lineHeight: 1 }}>
                {result.expected_semester_marks} <span style={{ fontSize: '1.5rem', color: 'var(--text-muted)' }}>/ 100</span>
              </div>

              <div style={{ display: 'flex', justifyContent: 'center', gap: '12px', margin: '20px 0' }}>
                <span className={`badge badge-${result.performance_category.toLowerCase() === 'excellent' || result.performance_category.toLowerCase() === 'good' ? 'strong' : result.performance_category.toLowerCase() === 'average' ? 'moderate' : 'weak'}`} style={{ padding: '8px 16px', fontSize: '0.85rem' }}>
                  Category: {result.performance_category}
                </span>
                <span className="badge badge-strong" style={{ padding: '8px 16px', fontSize: '0.85rem', background: 'rgba(139, 92, 246, 0.2)', border: '1px solid rgba(139, 92, 246, 0.4)', color: '#c084fc' }}>
                  Grade: {result.expected_grade}
                </span>
              </div>

              <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-color)', textAlign: 'left' }}>
                <div style={{ fontSize: '0.8rem', fontWeight: '700', color: 'var(--primary)', marginBottom: '4px' }}>
                  💡 PERFORMANCE INSIGHTS:
                </div>
                <div style={{ fontSize: '0.9rem', color: 'var(--text-sub)' }}>
                  {result.performance_insights}
                </div>
              </div>
            </div>
          ) : (
            <div style={{ color: 'var(--text-muted)' }}>
              <div style={{ fontSize: '3rem', marginBottom: '12px' }}>🎯</div>
              <p style={{ fontWeight: '500' }}>Enter your IA1, IA2, IA3, assignment marks and GPA to view your predicted semester score.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
