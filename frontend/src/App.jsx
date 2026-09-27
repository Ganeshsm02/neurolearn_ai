import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Module1Predictor from './components/Module1Predictor';
import StudentDashboard from './components/StudentDashboard';
import TeacherDashboard from './components/TeacherDashboard';
import PlacementModule from './components/PlacementModule';
import { fetchSubjects, loginUser } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('prediction'); // 'prediction', 'collaboration', 'placement'
  const [module2Role, setModule2Role] = useState(null); // 'student' or 'teacher'
  const [module2AuthIntent, setModule2AuthIntent] = useState(null); // 'student' or 'teacher'

  const [subjects, setSubjects] = useState([
    'Deep Learning',
    'Machine Learning',
    'MLOps',
    'Cloud Computing & Application Development (CCAD)',
    'Natural Language Processing (NLP)',
    'Generative AI',
    'Reinforcement Learning'
  ]);
  const [selectedSubject, setSelectedSubject] = useState('Deep Learning');

  // Auth State
  const [user, setUser] = useState(null);

  // Student Login Form State
  const [studentIdInput, setStudentIdInput] = useState('STU101');
  const [studentPasswordInput, setStudentPasswordInput] = useState('password123');
  const [studentError, setStudentError] = useState('');
  const [studentLoading, setStudentLoading] = useState(false);

  // Teacher Login Form State
  const [teacherUsernameInput, setTeacherUsernameInput] = useState('teacher');
  const [teacherPasswordInput, setTeacherPasswordInput] = useState('password123');
  const [teacherError, setTeacherError] = useState('');
  const [teacherLoading, setTeacherLoading] = useState(false);

  useEffect(() => {
    loadSubjects();
  }, []);

  const loadSubjects = async () => {
    try {
      const res = await fetchSubjects();
      if (res.subjects && res.subjects.length > 0) {
        setSubjects(res.subjects);
      }
    } catch (err) {
      console.log('Using default subjects list');
    }
  };

  const handleStudentLogin = async (e) => {
    e.preventDefault();
    setStudentLoading(true);
    setStudentError('');
    try {
      const res = await loginUser('student', studentIdInput, studentPasswordInput);
      if (res.status === 'success') {
        setUser({ ...res.user, role: 'student', student_id: studentIdInput.trim().toUpperCase() });
        setModule2Role('student');
        setModule2AuthIntent(null);
      } else {
        setStudentError(res.message || 'Invalid Student ID or password.');
      }
    } catch (err) {
      setStudentError('Server connection error. Please ensure backend is running.');
    } finally {
      setStudentLoading(false);
    }
  };

  const handleTeacherLogin = async (e) => {
    e.preventDefault();
    setTeacherLoading(true);
    setTeacherError('');
    try {
      const res = await loginUser('teacher', teacherUsernameInput, teacherPasswordInput);
      if (res.status === 'success') {
        setUser({ ...res.user, role: 'teacher', username: teacherUsernameInput.trim() });
        setModule2Role('teacher');
        setModule2AuthIntent(null);
      } else {
        setTeacherError(res.message || 'Invalid Teacher username or password.');
      }
    } catch (err) {
      setTeacherError('Server connection error. Please ensure backend is running.');
    } finally {
      setTeacherLoading(false);
    }
  };

  const handleLogout = () => {
    setUser(null);
    setModule2Role(null);
    setModule2AuthIntent(null);
    setStudentError('');
    setTeacherError('');
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar
        activeTab={activeTab}
        setActiveTab={(tab) => {
          setActiveTab(tab);
        }}
        selectedSubject={selectedSubject}
        setSelectedSubject={setSelectedSubject}
        subjects={subjects}
      />

      <main style={{ flex: 1, padding: '32px 24px', maxWidth: '1280px', margin: '0 auto', width: '100%' }}>
        {/* Module 1: Prediction Engine */}
        {activeTab === 'prediction' && (
          <Module1Predictor subject={selectedSubject} />
        )}

        {/* Module 2: Student & Teacher Collaboration Gate */}
        {activeTab === 'collaboration' && (
          <div>
            {/* Step 1: Not logged in and no role intent -> Ask Student or Teacher */}
            {!module2Role && !module2AuthIntent && (
              <div className="glass-card" style={{ maxWidth: '800px', margin: '30px auto', textAlign: 'center', padding: '40px' }}>
                <div style={{ fontSize: '3rem', marginBottom: '14px' }}>🤝</div>
                <h2 style={{ fontSize: '1.6rem', color: '#fff', marginBottom: '10px' }}>
                  Module 2: Academic Collaboration Portal
                </h2>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', marginBottom: '32px' }}>
                  Select whether you are a Student or Teacher to access your dedicated dashboard:
                </p>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '24px' }}>
                  {/* Student Option Card */}
                  <div
                    onClick={() => {
                      setStudentError('');
                      setModule2AuthIntent('student');
                    }}
                    className="glass-card"
                    style={{
                      cursor: 'pointer',
                      border: '1px solid rgba(16, 185, 129, 0.4)',
                      padding: '28px 24px',
                      transition: 'all 0.3s ease',
                      textAlign: 'center'
                    }}
                  >
                    <div style={{ fontSize: '2.8rem', marginBottom: '12px' }}>🎓</div>
                    <div style={{ fontWeight: '800', fontSize: '1.2rem', color: '#fff' }}>Student</div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '8px', lineHeight: 1.5 }}>
                      Topic Performance Histogram, Lacking Topics Analysis, Video Lectures & Adaptive Quizzes
                    </div>
                    <button className="btn-primary" style={{ marginTop: '20px', width: '100%', justifyContent: 'center', background: 'rgba(16, 185, 129, 0.85)' }}>
                      Student Login →
                    </button>
                  </div>

                  {/* Teacher Option Card */}
                  <div
                    onClick={() => {
                      setTeacherError('');
                      setModule2AuthIntent('teacher');
                    }}
                    className="glass-card"
                    style={{
                      cursor: 'pointer',
                      border: '1px solid rgba(168, 85, 247, 0.4)',
                      padding: '28px 24px',
                      transition: 'all 0.3s ease',
                      textAlign: 'center'
                    }}
                  >
                    <div style={{ fontSize: '2.8rem', marginBottom: '12px' }}>👨‍🏫</div>
                    <div style={{ fontWeight: '800', fontSize: '1.2rem', color: '#fff' }}>Teacher</div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '8px', lineHeight: 1.5 }}>
                      Upload Syllabus PDFs, AI Topic Extraction, Question Paper Generator & Student Marks Analytics
                    </div>
                    <button className="btn-primary" style={{ marginTop: '20px', width: '100%', justifyContent: 'center', background: 'rgba(168, 85, 247, 0.85)' }}>
                      Teacher Login →
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Step 2A: Student Login Form - Only student details asked, NO teacher directions */}
            {!module2Role && module2AuthIntent === 'student' && (
              <div className="glass-card" style={{ maxWidth: '440px', margin: '40px auto', padding: '36px' }}>
                <div style={{ textAlign: 'center', marginBottom: '24px' }}>
                  <div style={{ fontSize: '2.8rem', marginBottom: '8px' }}>🎓</div>
                  <h2 style={{ fontSize: '1.4rem', fontWeight: '800', color: '#fff', margin: 0 }}>
                    Student Login
                  </h2>
                  <p style={{ margin: '6px 0 0 0', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                    Enter your student credentials to view your performance dashboard
                  </p>
                </div>

                {/* Quick Demo Fill for Student Only */}
                <div style={{ marginBottom: '16px', padding: '10px 14px', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '8px', border: '1px dashed rgba(16, 185, 129, 0.3)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.78rem', color: '#34d399' }}>Demo Student: <strong>STU101</strong></span>
                  <button
                    type="button"
                    onClick={() => {
                      setStudentIdInput('STU101');
                      setStudentPasswordInput('password123');
                      setStudentError('');
                    }}
                    style={{ fontSize: '0.75rem', padding: '4px 8px', background: 'rgba(16, 185, 129, 0.2)', border: '1px solid rgba(16, 185, 129, 0.4)', borderRadius: '6px', color: '#34d399', cursor: 'pointer' }}
                  >
                    ⚡ Quick Fill
                  </button>
                </div>

                {studentError && (
                  <div style={{ background: 'rgba(239, 68, 68, 0.15)', border: '1px solid #f87171', color: '#f87171', padding: '10px', borderRadius: '8px', fontSize: '0.85rem', marginBottom: '16px' }}>
                    {studentError}
                  </div>
                )}

                <form onSubmit={handleStudentLogin}>
                  <div className="form-group" style={{ marginBottom: '16px' }}>
                    <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#e2e8f0', display: 'block', marginBottom: '6px' }}>
                      Student ID
                    </label>
                    <input
                      type="text"
                      value={studentIdInput}
                      onChange={(e) => setStudentIdInput(e.target.value)}
                      className="form-control"
                      placeholder="e.g. STU101"
                      required
                    />
                  </div>

                  <div className="form-group" style={{ marginBottom: '22px' }}>
                    <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#e2e8f0', display: 'block', marginBottom: '6px' }}>
                      Password
                    </label>
                    <input
                      type="password"
                      value={studentPasswordInput}
                      onChange={(e) => setStudentPasswordInput(e.target.value)}
                      className="form-control"
                      placeholder="••••••••"
                      required
                    />
                  </div>

                  <button
                    type="submit"
                    className="btn-primary"
                    style={{ width: '100%', justifyContent: 'center', padding: '11px', background: 'rgba(16, 185, 129, 0.85)' }}
                    disabled={studentLoading}
                  >
                    {studentLoading ? 'Authenticating...' : 'Login as Student →'}
                  </button>

                  <button
                    type="button"
                    onClick={() => {
                      setModule2AuthIntent(null);
                      setStudentError('');
                    }}
                    className="btn-secondary"
                    style={{ width: '100%', justifyContent: 'center', marginTop: '10px', padding: '9px', fontSize: '0.82rem' }}
                  >
                    ← Back to Student or Teacher selection
                  </button>
                </form>
              </div>
            )}

            {/* Step 2B: Teacher Login Form - Only teacher details asked, NO student directions */}
            {!module2Role && module2AuthIntent === 'teacher' && (
              <div className="glass-card" style={{ maxWidth: '440px', margin: '40px auto', padding: '36px' }}>
                <div style={{ textAlign: 'center', marginBottom: '24px' }}>
                  <div style={{ fontSize: '2.8rem', marginBottom: '8px' }}>👨‍🏫</div>
                  <h2 style={{ fontSize: '1.4rem', fontWeight: '800', color: '#fff', margin: 0 }}>
                    Teacher Login
                  </h2>
                  <p style={{ margin: '6px 0 0 0', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                    Enter your faculty credentials to manage syllabus, question papers & marks
                  </p>
                </div>

                {/* Quick Demo Fill for Teacher Only */}
                <div style={{ marginBottom: '16px', padding: '10px 14px', background: 'rgba(168, 85, 247, 0.1)', borderRadius: '8px', border: '1px dashed rgba(168, 85, 247, 0.3)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.78rem', color: '#c084fc' }}>Demo Faculty: <strong>teacher</strong></span>
                  <button
                    type="button"
                    onClick={() => {
                      setTeacherUsernameInput('teacher');
                      setTeacherPasswordInput('password123');
                      setTeacherError('');
                    }}
                    style={{ fontSize: '0.75rem', padding: '4px 8px', background: 'rgba(168, 85, 247, 0.2)', border: '1px solid rgba(168, 85, 247, 0.4)', borderRadius: '6px', color: '#c084fc', cursor: 'pointer' }}
                  >
                    ⚡ Quick Fill
                  </button>
                </div>

                {teacherError && (
                  <div style={{ background: 'rgba(239, 68, 68, 0.15)', border: '1px solid #f87171', color: '#f87171', padding: '10px', borderRadius: '8px', fontSize: '0.85rem', marginBottom: '16px' }}>
                    {teacherError}
                  </div>
                )}

                <form onSubmit={handleTeacherLogin}>
                  <div className="form-group" style={{ marginBottom: '16px' }}>
                    <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#e2e8f0', display: 'block', marginBottom: '6px' }}>
                      Teacher Username
                    </label>
                    <input
                      type="text"
                      value={teacherUsernameInput}
                      onChange={(e) => setTeacherUsernameInput(e.target.value)}
                      className="form-control"
                      placeholder="e.g. teacher"
                      required
                    />
                  </div>

                  <div className="form-group" style={{ marginBottom: '22px' }}>
                    <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#e2e8f0', display: 'block', marginBottom: '6px' }}>
                      Password
                    </label>
                    <input
                      type="password"
                      value={teacherPasswordInput}
                      onChange={(e) => setTeacherPasswordInput(e.target.value)}
                      className="form-control"
                      placeholder="••••••••"
                      required
                    />
                  </div>

                  <button
                    type="submit"
                    className="btn-primary"
                    style={{ width: '100%', justifyContent: 'center', padding: '11px', background: 'rgba(168, 85, 247, 0.85)' }}
                    disabled={teacherLoading}
                  >
                    {teacherLoading ? 'Authenticating...' : 'Login as Teacher →'}
                  </button>

                  <button
                    type="button"
                    onClick={() => {
                      setModule2AuthIntent(null);
                      setTeacherError('');
                    }}
                    className="btn-secondary"
                    style={{ width: '100%', justifyContent: 'center', marginTop: '10px', padding: '9px', fontSize: '0.82rem' }}
                  >
                    ← Back to Student or Teacher selection
                  </button>
                </form>
              </div>
            )}

            {/* Step 3: Authenticated State - Displays Dashboard with Logout button (instead of Change Role) */}
            {module2Role && (
              <div>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '20px',
                  background: 'rgba(30, 41, 59, 0.6)',
                  padding: '12px 20px',
                  borderRadius: '12px',
                  border: '1px solid var(--border-color)',
                  flexWrap: 'wrap',
                  gap: '10px'
                }}>
                  <div style={{ fontWeight: '700', color: '#fff', fontSize: '0.9rem' }}>
                    PORTAL MODE:{' '}
                    <span style={{ color: module2Role === 'student' ? '#34d399' : '#c084fc' }}>
                      {module2Role === 'student'
                        ? `🎓 Student Learning Dashboard (${user?.student_id || 'STU101'})`
                        : `👨‍🏫 Teacher Management Dashboard (${user?.name || user?.username || 'Teacher'})`}
                    </span>
                  </div>
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button
                      onClick={handleLogout}
                      className="btn-secondary"
                      style={{
                        padding: '6px 16px',
                        fontSize: '0.82rem',
                        color: '#f87171',
                        borderColor: 'rgba(239, 68, 68, 0.4)',
                        background: 'rgba(239, 68, 68, 0.1)',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px'
                      }}
                    >
                      🚪 Logout
                    </button>
                  </div>
                </div>

                {module2Role === 'student' && (
                  <StudentDashboard
                    studentId={user?.student_id || 'STU101'}
                    subject={selectedSubject}
                    selectedSubject={selectedSubject}
                    setSelectedSubject={setSelectedSubject}
                    subjects={subjects}
                  />
                )}

                {module2Role === 'teacher' && (
                  <TeacherDashboard
                    subject={selectedSubject}
                    user={user}
                    onOpenLogin={() => {
                      setModule2Role(null);
                      setModule2AuthIntent('teacher');
                    }}
                  />
                )}
              </div>
            )}
          </div>
        )}

        {/* Module 3: AI Placement & Career Guidance System */}
        {activeTab === 'placement' && (
          <PlacementModule />
        )}
      </main>

      <footer style={{
        textAlign: 'center',
        padding: '20px',
        borderTop: '1px solid var(--border-color)',
        color: 'var(--text-muted)',
        fontSize: '0.85rem'
      }}>
        NeuroLearn AI © 2026 — Module 1: Prediction | Module 2: Collaboration | Module 3: Placement System
      </footer>
    </div>
  );
}
