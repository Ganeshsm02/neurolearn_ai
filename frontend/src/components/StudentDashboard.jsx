import React, { useEffect, useState } from 'react';
import { fetchStudentDashboard } from '../services/api';
import { TopicHistogramChart } from './AnalyticsChart';
import QuizModal from './QuizModal';

export default function StudentDashboard({ studentId, subject, selectedSubject, setSelectedSubject, subjects }) {
  const [selectedIa, setSelectedIa] = useState('Internal Assessment 1');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showQuiz, setShowQuiz] = useState(false);

  const activeSubject = selectedSubject || subject || 'Deep Learning';

  useEffect(() => {
    loadDashboard();
  }, [studentId, activeSubject, selectedIa]);

  const loadDashboard = async () => {
    setLoading(true);
    try {
      const res = await fetchStudentDashboard(studentId, activeSubject, selectedIa);
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubjectChange = (e) => {
    const newSub = e.target.value;
    if (setSelectedSubject) {
      setSelectedSubject(newSub);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '60px', color: 'var(--text-muted)' }}>
        <div style={{ fontSize: '2rem', marginBottom: '12px' }}>🔄</div>
        <div>Loading Student Dashboard & Topic Performance Histogram for {activeSubject} ({selectedIa})...</div>
      </div>
    );
  }

  const histogramData = data?.histogram_data || [];
  const iaLackingTopics = data?.ia_lacking_topics || [];
  const recs = data?.recommendations || {};
  const youtubeResources = data?.youtube_resources || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Subject & IA Filter Selector Bar */}
      <div className="glass-card" style={{
        background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%)',
        border: '1px solid var(--primary)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '16px',
        padding: '20px 24px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{ width: '42px', height: '42px', borderRadius: '12px', background: 'var(--primary-gradient)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '22px' }}>
            🎓
          </div>
          <div>
            <h1 style={{ fontSize: '1.4rem', fontWeight: '800', color: '#fff' }}>
              {data?.student_name} ({data?.student_id})
            </h1>
            <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              Subject & Assessment Topic Analysis Platform
            </div>
          </div>
        </div>

        {/* Dropdowns for Subject and IA */}
        <div style={{ display: 'flex', gap: '14px', alignItems: 'center', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <label style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: '700', textTransform: 'uppercase' }}>SELECT SUBJECT</label>
            <select
              value={activeSubject}
              onChange={handleSubjectChange}
              className="form-control"
              style={{ width: '220px', fontSize: '0.85rem', padding: '8px 12px', border: '1px solid var(--primary)' }}
            >
              {subjects?.map((sub, i) => (
                <option key={i} value={sub}>{sub}</option>
              ))}
            </select>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <label style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: '700', textTransform: 'uppercase' }}>SELECT ASSESSMENT (IA)</label>
            <select
              value={selectedIa}
              onChange={(e) => setSelectedIa(e.target.value)}
              className="form-control"
              style={{ width: '230px', fontSize: '0.85rem', padding: '8px 12px', border: '1px solid var(--primary)' }}
            >
              <option value="Internal Assessment 1">Internal Assessment 1 (IA 1)</option>
              <option value="Internal Assessment 2">Internal Assessment 2 (IA 2)</option>
              <option value="Internal Assessment 3">Internal Assessment 3 (IA 3)</option>
            </select>
          </div>

          <button onClick={() => setShowQuiz(true)} className="btn-primary" style={{ padding: '10px 18px', background: 'var(--secondary-gradient)', marginTop: '16px' }}>
            ⚡ Launch PDF Topic Quiz
          </button>
        </div>
      </div>

      {/* Topic Performance Histogram Chart */}
      <div className="grid-2">
        <div className="glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 style={{ fontSize: '1.05rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
              📊 Topic Performance Histogram ({selectedIa})
            </h3>
            <span className="badge badge-weak" style={{ fontSize: '0.7rem' }}>
              🔴 Red Bars = Lacking Topics (&lt;50%)
            </span>
          </div>

          <TopicHistogramChart histogramData={histogramData} />
        </div>

        {/* Lacking Topics Analysis & Quiz Launcher Card */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <h3 style={{ fontSize: '1.05rem', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              ⚠️ Weak / Lacking Topics Analysis
            </h3>

            {iaLackingTopics.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <div style={{ background: 'rgba(239, 68, 68, 0.12)', border: '1px solid rgba(239, 68, 68, 0.3)', padding: '12px 14px', borderRadius: '10px', color: '#f87171', fontSize: '0.9rem' }}>
                  <strong>Lacking Topics in {selectedIa}:</strong>
                  <ul style={{ paddingLeft: '18px', marginTop: '6px', color: '#fff' }}>
                    {iaLackingTopics.map((t, idx) => <li key={idx}>{t}</li>)}
                  </ul>
                </div>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                  YouTube video lectures have been retrieved below specifically for these lacking topics.
                </p>
              </div>
            ) : (
              <div style={{ background: 'rgba(16, 185, 129, 0.12)', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '16px', borderRadius: '10px', color: '#34d399', fontSize: '0.9rem' }}>
                🟢 Great performance! You met or exceeded passing criteria across all tested topics in {selectedIa}.
              </div>
            )}
          </div>

          <button onClick={() => setShowQuiz(true)} className="btn-primary" style={{ width: '100%', justifyContent: 'center', marginTop: '16px' }}>
            ⚡ Take Adaptive Quiz on {iaLackingTopics.length > 0 ? 'Lacking Topics' : 'Unit PDF Concepts'}
          </button>
        </div>
      </div>

      {/* 📺 YouTube Video Lectures for Lacking Topics */}
      <div className="glass-card">
        <h3 style={{ fontSize: '1.1rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          📺 YouTube Video Lectures (Specifically for Lacking Topics)
        </h3>

        {youtubeResources.length > 0 ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
            {youtubeResources.map((res, idx) => (
              <a key={idx} href={res.url} target="_blank" rel="noopener noreferrer" style={{ textDecoration: 'none' }}>
                <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '10px', border: '1px solid rgba(239, 68, 68, 0.3)', transition: 'all 0.2s', height: '100%' }}>
                  <div style={{ fontSize: '0.75rem', color: '#f87171', fontWeight: '800', textTransform: 'uppercase', marginBottom: '6px' }}>
                    TOPIC: {res.topic}
                  </div>
                  <div style={{ fontWeight: '700', color: '#fff', fontSize: '0.95rem', marginBottom: '6px' }}>
                    {res.title}
                  </div>
                  <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
                    {res.description}
                  </div>
                </div>
              </a>
            ))}
          </div>
        ) : (
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            No video lectures required for current topics.
          </p>
        )}
      </div>

      {/* Quiz Modal Render */}
      {showQuiz && recs.quiz_questions && (
        <QuizModal
          quizQuestions={recs.quiz_questions}
          studentId={studentId}
          onClose={() => setShowQuiz(false)}
        />
      )}
    </div>
  );
}
