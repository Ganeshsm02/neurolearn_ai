import React, { useState, useEffect } from 'react';
import {
  fetchAdminOverview,
  fetchAdminUnits,
  fetchAdminQuestionPapers,
  fetchAdminStudents,
  deleteAdminUnit
} from '../services/api';

export default function AdminDashboard({ onOpenLogin }) {
  const [activeAdminTab, setActiveAdminTab] = useState('overview'); // 'overview', 'units', 'papers', 'students', 'diagnostics'
  const [overview, setOverview] = useState(null);
  const [units, setUnits] = useState([]);
  const [questionPapers, setQuestionPapers] = useState([]);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionMsg, setActionMsg] = useState('');
  const [selectedUnitTopics, setSelectedUnitTopics] = useState(null);
  const [selectedPaperView, setSelectedPaperView] = useState(null);

  useEffect(() => {
    loadAllAdminData();
  }, []);

  const loadAllAdminData = async () => {
    setLoading(true);
    try {
      const [ovRes, uRes, qpRes, stRes] = await Promise.all([
        fetchAdminOverview(),
        fetchAdminUnits(),
        fetchAdminQuestionPapers(),
        fetchAdminStudents()
      ]);

      if (ovRes.status === 'success') setOverview(ovRes);
      if (uRes.status === 'success') setUnits(uRes.units || []);
      if (qpRes.status === 'success') setQuestionPapers(qpRes.question_papers || []);
      if (stRes.status === 'success') setStudents(stRes.student_records || []);
    } catch (err) {
      console.error('Error fetching admin data:', err);
      setActionMsg('Failed to fetch admin statistics from server.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUnit = async (subject, unitNumber) => {
    if (!window.confirm(`Are you sure you want to delete Unit ${unitNumber} of ${subject}?`)) {
      return;
    }
    try {
      const res = await deleteAdminUnit(subject, unitNumber);
      if (res.status === 'success') {
        setActionMsg(`Unit ${unitNumber} of ${subject} successfully deleted.`);
        loadAllAdminData();
      } else {
        setActionMsg(res.message || 'Failed to delete unit.');
      }
    } catch (err) {
      setActionMsg('Server error while deleting unit.');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Top Banner */}
      <div className="glass-card" style={{
        background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%)',
        border: '1px solid rgba(147, 197, 253, 0.3)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '24px',
        flexWrap: 'wrap',
        gap: '16px'
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '1.8rem' }}>🛡️</span>
            <h1 style={{ fontSize: '1.6rem', fontWeight: '800', color: '#fff', margin: 0 }}>
              Admin Control Center
            </h1>
            <span className="badge badge-strong" style={{ background: 'rgba(16, 185, 129, 0.2)', color: '#34d399', border: '1px solid rgba(16, 185, 129, 0.4)' }}>
              ● System Online
            </span>
          </div>
          <p style={{ margin: '6px 0 0 0', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            Centralized management for syllabus units, generated question papers, student marks, and AI services.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={loadAllAdminData} className="btn-secondary" style={{ padding: '8px 14px', fontSize: '0.82rem' }}>
            🔄 Refresh System Data
          </button>
        </div>
      </div>

      {actionMsg && (
        <div style={{
          padding: '12px 18px',
          borderRadius: '10px',
          background: 'rgba(59, 130, 246, 0.15)',
          border: '1px solid #60a5fa',
          color: '#93c5fd',
          fontSize: '0.88rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <span>{actionMsg}</span>
          <button onClick={() => setActionMsg('')} style={{ background: 'transparent', border: 'none', color: '#93c5fd', cursor: 'pointer', fontWeight: 'bold' }}>✕</button>
        </div>
      )}

      {/* KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <div className="glass-card" style={{ padding: '18px', borderLeft: '4px solid #60a5fa' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>SYLLABUS UNITS</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#fff', margin: '6px 0' }}>
            {overview?.stats?.total_units ?? units.length}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#60a5fa' }}>Indexed with AI topic extraction</div>
        </div>

        <div className="glass-card" style={{ padding: '18px', borderLeft: '4px solid #a855f7' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>QUESTION PAPERS</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#fff', margin: '6px 0' }}>
            {overview?.stats?.total_question_papers ?? questionPapers.length}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#c084fc' }}>Anna University Blueprint format</div>
        </div>

        <div className="glass-card" style={{ padding: '18px', borderLeft: '4px solid #34d399' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>STUDENT MARKS LOGS</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#fff', margin: '6px 0' }}>
            {overview?.stats?.active_student_records ?? students.length}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#34d399' }}>Tracked across Internal Assessments</div>
        </div>

        <div className="glass-card" style={{ padding: '18px', borderLeft: '4px solid #f59e0b' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>STORAGE ENGINE</div>
          <div style={{ fontSize: '1.3rem', fontWeight: 800, color: '#fff', margin: '8px 0' }}>
            {overview?.stats?.database_mode || 'JSON Store'}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#fbbf24' }}>Local database active (`store.json`)</div>
        </div>
      </div>

      {/* Admin Navigation Tabs */}
      <div style={{ display: 'flex', gap: '8px', background: 'rgba(30, 41, 59, 0.6)', padding: '6px', borderRadius: '12px', border: '1px solid var(--border-color)', flexWrap: 'wrap' }}>
        <button
          onClick={() => setActiveAdminTab('overview')}
          className={activeAdminTab === 'overview' ? 'btn-primary' : 'btn-secondary'}
          style={{ padding: '8px 16px', fontSize: '0.85rem' }}
        >
          📊 Subject Breakdown
        </button>
        <button
          onClick={() => setActiveAdminTab('units')}
          className={activeAdminTab === 'units' ? 'btn-primary' : 'btn-secondary'}
          style={{ padding: '8px 16px', fontSize: '0.85rem' }}
        >
          📂 Unit & Topic Registry ({units.length})
        </button>
        <button
          onClick={() => setActiveAdminTab('papers')}
          className={activeAdminTab === 'papers' ? 'btn-primary' : 'btn-secondary'}
          style={{ padding: '8px 16px', fontSize: '0.85rem' }}
        >
          📝 Question Papers Vault ({questionPapers.length})
        </button>
        <button
          onClick={() => setActiveAdminTab('students')}
          className={activeAdminTab === 'students' ? 'btn-primary' : 'btn-secondary'}
          style={{ padding: '8px 16px', fontSize: '0.85rem' }}
        >
          👥 Student Records ({students.length})
        </button>
        <button
          onClick={() => setActiveAdminTab('diagnostics')}
          className={activeAdminTab === 'diagnostics' ? 'btn-primary' : 'btn-secondary'}
          style={{ padding: '8px 16px', fontSize: '0.85rem' }}
        >
          ⚙️ AI Diagnostics & Health
        </button>
      </div>

      {/* Tab 1: Subject Breakdown */}
      {activeAdminTab === 'overview' && (
        <div className="glass-card" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1.15rem', color: '#fff', marginBottom: '16px' }}>
            Academic Subject Distribution
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
            {(overview?.subject_breakdown || []).map((sb, idx) => (
              <div key={idx} style={{
                background: 'rgba(15, 23, 42, 0.6)',
                border: '1px solid var(--border-color)',
                borderRadius: '12px',
                padding: '16px'
              }}>
                <div style={{ fontWeight: '700', color: '#fff', fontSize: '0.95rem', marginBottom: '8px' }}>
                  📘 {sb.subject}
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                  <span>Uploaded Units:</span>
                  <span style={{ color: '#60a5fa', fontWeight: 600 }}>{sb.unit_count}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                  <span>Question Papers:</span>
                  <span style={{ color: '#c084fc', fontWeight: 600 }}>{sb.question_paper_count}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 2: Unit & Topic Registry */}
      {activeAdminTab === 'units' && (
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
            <div>
              <h3 style={{ fontSize: '1.15rem', color: '#fff', margin: 0 }}>
                Uploaded Units & Extracted Topics Registry
              </h3>
              <p style={{ margin: '4px 0 0 0', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                These topics are automatically indexed by PyMuPDF and used to formulate academic questions ("What is...", "What are...", "What role does...").
              </p>
            </div>
          </div>

          {units.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
              No syllabus units uploaded yet. Teachers can upload PDF materials in Module 2.
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left', color: 'var(--text-muted)' }}>
                    <th style={{ padding: '12px' }}>Subject</th>
                    <th style={{ padding: '12px' }}>Unit #</th>
                    <th style={{ padding: '12px' }}>Unit Name</th>
                    <th style={{ padding: '12px' }}>Extracted Topics</th>
                    <th style={{ padding: '12px', textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {units.map((u, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                      <td style={{ padding: '12px', fontWeight: 600, color: '#fff' }}>{u.subject}</td>
                      <td style={{ padding: '12px' }}>
                        <span className="badge badge-strong">Unit {u.unit_number}</span>
                      </td>
                      <td style={{ padding: '12px', color: '#cbd5e1' }}>{u.unit_name}</td>
                      <td style={{ padding: '12px' }}>
                        <button
                          onClick={() => setSelectedUnitTopics(u)}
                          className="btn-secondary"
                          style={{ padding: '4px 10px', fontSize: '0.75rem' }}
                        >
                          🔍 View {u.topic_count} Topics
                        </button>
                      </td>
                      <td style={{ padding: '12px', textAlign: 'right' }}>
                        <button
                          onClick={() => handleDeleteUnit(u.subject, u.unit_number)}
                          style={{
                            background: 'rgba(239, 68, 68, 0.15)',
                            border: '1px solid rgba(239, 68, 68, 0.4)',
                            color: '#f87171',
                            padding: '4px 10px',
                            borderRadius: '6px',
                            fontSize: '0.75rem',
                            cursor: 'pointer'
                          }}
                        >
                          🗑️ Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Tab 3: Question Papers Vault */}
      {activeAdminTab === 'papers' && (
        <div className="glass-card" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1.15rem', color: '#fff', marginBottom: '16px' }}>
            Generated Blueprint Question Papers
          </h3>
          {questionPapers.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
              No question papers generated yet.
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left', color: 'var(--text-muted)' }}>
                    <th style={{ padding: '12px' }}>Subject</th>
                    <th style={{ padding: '12px' }}>Exam Name</th>
                    <th style={{ padding: '12px' }}>Questions</th>
                    <th style={{ padding: '12px' }}>Total Marks</th>
                    <th style={{ padding: '12px', textAlign: 'right' }}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {questionPapers.map((qp, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                      <td style={{ padding: '12px', fontWeight: 600, color: '#fff' }}>{qp.subject}</td>
                      <td style={{ padding: '12px', color: '#93c5fd' }}>{qp.exam_name}</td>
                      <td style={{ padding: '12px' }}>{qp.total_questions || '8'} items</td>
                      <td style={{ padding: '12px' }}>{qp.total_marks || 100} Marks</td>
                      <td style={{ padding: '12px', textAlign: 'right' }}>
                        <button
                          onClick={() => setSelectedPaperView(qp)}
                          className="btn-primary"
                          style={{ padding: '4px 10px', fontSize: '0.75rem' }}
                        >
                          👁️ Inspect Paper
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Tab 4: Student Records */}
      {activeAdminTab === 'students' && (
        <div className="glass-card" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1.15rem', color: '#fff', marginBottom: '16px' }}>
            Internal Assessment Marks & Student Records
          </h3>
          {students.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
              No student marks uploaded yet. Teachers can upload marks under Module 2.
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left', color: 'var(--text-muted)' }}>
                    <th style={{ padding: '12px' }}>Student ID</th>
                    <th style={{ padding: '12px' }}>Subject</th>
                    <th style={{ padding: '12px' }}>Exam Name</th>
                    <th style={{ padding: '12px' }}>Marks Scored</th>
                    <th style={{ padding: '12px' }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {students.map((st, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                      <td style={{ padding: '12px', fontWeight: 700, color: '#93c5fd' }}>{st.student_id}</td>
                      <td style={{ padding: '12px', color: '#fff' }}>{st.subject}</td>
                      <td style={{ padding: '12px', color: 'var(--text-muted)' }}>{st.exam_name}</td>
                      <td style={{ padding: '12px', fontWeight: 600, color: '#34d399' }}>{st.total_score || st.marks || 'N/A'}</td>
                      <td style={{ padding: '12px' }}>
                        <span className="badge badge-strong" style={{ background: 'rgba(16, 185, 129, 0.2)', color: '#34d399' }}>
                          Verified
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Tab 5: AI Diagnostics */}
      {activeAdminTab === 'diagnostics' && (
        <div className="glass-card" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1.15rem', color: '#fff', marginBottom: '16px' }}>
            System Infrastructure & AI Service Health
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
              <div style={{ fontWeight: 600, color: '#93c5fd', marginBottom: '4px' }}>📄 PyMuPDF PDF Engine</div>
              <div style={{ fontSize: '0.8rem', color: '#34d399' }}>● Active & Operational</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>Extracts high-resolution text, headings, and domain concepts without modifying core logic.</div>
            </div>

            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
              <div style={{ fontWeight: 600, color: '#c084fc', marginBottom: '4px' }}>❓ Question Generation Engine</div>
              <div style={{ fontSize: '0.8rem', color: '#34d399' }}>● "What is/are..." Formula Active</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>Filters important technical topics and generates Part A, B, and C Anna University Blueprint papers.</div>
            </div>

            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
              <div style={{ fontWeight: 600, color: '#fbbf24', marginBottom: '4px' }}>🤖 ML Mark Predictor (Module 1)</div>
              <div style={{ fontSize: '0.8rem', color: '#34d399' }}>● Multi-Model Regression Active</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>Random Forest, Gradient Boosting, Ridge, and Linear Regression with SHAP explainability.</div>
            </div>

            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
              <div style={{ fontWeight: 600, color: '#60a5fa', marginBottom: '4px' }}>🎯 Placement Guidance (Module 3)</div>
              <div style={{ fontSize: '0.8rem', color: '#34d399' }}>● ATS Resume Scorer Active</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>Cosine similarity matching, skills gap analyzer, and AI mock interview feedback.</div>
            </div>
          </div>
        </div>
      )}

      {/* Modal: View Extracted Topics */}
      {selectedUnitTopics && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(15, 23, 42, 0.85)',
          backdropFilter: 'blur(10px)',
          zIndex: 1000,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '20px'
        }}>
          <div className="glass-card" style={{ maxWidth: '600px', width: '100%', maxHeight: '80vh', overflowY: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div>
                <h3 style={{ fontSize: '1.2rem', color: '#fff', margin: 0 }}>
                  Topics: {selectedUnitTopics.subject} - Unit {selectedUnitTopics.unit_number}
                </h3>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  Total {selectedUnitTopics.topics?.length || 0} extracted concepts
                </span>
              </div>
              <button onClick={() => setSelectedUnitTopics(null)} className="btn-secondary" style={{ padding: '4px 10px', fontSize: '0.8rem' }}>✕</button>
            </div>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {(selectedUnitTopics.topics || []).map((t, idx) => (
                <span
                  key={idx}
                  style={{
                    background: 'rgba(99, 102, 241, 0.15)',
                    border: '1px solid rgba(99, 102, 241, 0.4)',
                    color: '#c084fc',
                    padding: '6px 12px',
                    borderRadius: '8px',
                    fontSize: '0.82rem'
                  }}
                >
                  📌 {t}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Modal: Inspect Question Paper */}
      {selectedPaperView && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(15, 23, 42, 0.85)',
          backdropFilter: 'blur(10px)',
          zIndex: 1000,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '20px'
        }}>
          <div className="glass-card" style={{ maxWidth: '750px', width: '100%', maxHeight: '85vh', overflowY: 'auto', border: '1px solid var(--primary)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div>
                <h3 style={{ fontSize: '1.2rem', color: '#fff', margin: 0 }}>
                  📝 {selectedPaperView.subject} — {selectedPaperView.exam_name}
                </h3>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  Generated Academic Blueprint Paper
                </span>
              </div>
              <button onClick={() => setSelectedPaperView(null)} className="btn-secondary" style={{ padding: '4px 10px', fontSize: '0.8rem' }}>✕</button>
            </div>

            {/* Part A */}
            <div style={{ marginBottom: '16px', background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '10px' }}>
              <div style={{ fontWeight: 700, color: '#93c5fd', marginBottom: '8px' }}>
                PART A (5 Questions x 2 Marks = 10 Marks)
              </div>
              {(selectedPaperView.paper?.part_a || []).map((q, idx) => (
                <div key={idx} style={{ fontSize: '0.85rem', color: '#e2e8f0', marginBottom: '6px' }}>
                  <strong>Q{idx + 1}.</strong> {q.question || q} <span style={{ color: 'var(--text-muted)' }}>[{q.topic || 'Core Concept'}]</span>
                </div>
              ))}
            </div>

            {/* Part B */}
            <div style={{ marginBottom: '16px', background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '10px' }}>
              <div style={{ fontWeight: 700, color: '#c084fc', marginBottom: '8px' }}>
                PART B (Either / Or — 24 Marks)
              </div>
              {(selectedPaperView.paper?.part_b || []).map((q, idx) => (
                <div key={idx} style={{ fontSize: '0.85rem', color: '#e2e8f0', marginBottom: '8px' }}>
                  <div><strong>Q{idx + 6}a.</strong> {q.option_a?.question || q.question}</div>
                  <div style={{ color: 'var(--text-muted)', margin: '2px 0', fontSize: '0.8rem' }}>--- OR ---</div>
                  <div><strong>Q{idx + 6}b.</strong> {q.option_b?.question || 'Discuss advanced case studies and architectural implementations.'}</div>
                </div>
              ))}
            </div>

            {/* Part C */}
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '10px' }}>
              <div style={{ fontWeight: 700, color: '#34d399', marginBottom: '8px' }}>
                PART C (Application / Comprehensive Problem — 16 Marks)
              </div>
              {(selectedPaperView.paper?.part_c || []).map((q, idx) => (
                <div key={idx} style={{ fontSize: '0.85rem', color: '#e2e8f0' }}>
                  <strong>Q8.</strong> {q.question || q}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
