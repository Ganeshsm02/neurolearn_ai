import React, { useState, useEffect } from 'react';
import {
  analyzePlacementProfile,
  analyzeResume,
  uploadResumePDF,
  fetchJobMatch,
  fetchPlacementPrepQuestions,
  evaluateMockInterview
} from '../services/api';

export default function PlacementModule() {
  const [activeSubTab, setActiveSubTab] = useState('profile');

  // Student Profile State
  const [cgpa, setCgpa] = useState(8.2);
  const [targetRole, setTargetRole] = useState('ML Engineer');
  const [skillsInput, setSkillsInput] = useState('Python, Machine Learning, SQL, Deep Learning');
  const [languagesInput, setLanguagesInput] = useState('Python, C++, SQL');
  const [certifications, setCertifications] = useState('AWS Certified Cloud Practitioner, TensorFlow Developer');
  const [projectsInput, setProjectsInput] = useState('Brain Tumor Segmentation using CNN, MLOps Pipeline for Sentiment Analysis');
  
  // Resume Analysis State (Text or PDF File)
  const [resumeText, setResumeText] = useState(`John Doe
Computer Science & Engineering Student | CGPA: 8.2
Technical Skills: Python, Machine Learning, Deep Learning, SQL, Git, Linux
Projects: Built neural network classifier achieving 94% accuracy. Implemented SQL database queries for web app.
Certifications: AWS Cloud Practitioner`);
  const [resumeFile, setResumeFile] = useState(null);

  // AI Mock Interview State
  const [questionIdx, setQuestionIdx] = useState(0);
  const [interviewQuestion, setInterviewQuestion] = useState('Explain how you would deploy a Deep Learning model to production and monitor data drift.');
  const [studentInterviewAnswer, setStudentInterviewAnswer] = useState('');
  const [interviewResult, setInterviewResult] = useState(null);

  const [resumeResult, setResumeResult] = useState(null);
  const [profileAnalysis, setProfileAnalysis] = useState(null);
  const [matchedJobs, setMatchedJobs] = useState([]);
  const [roleQuestions, setRoleQuestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [expandedAnswerIndex, setExpandedAnswerIndex] = useState({});

  useEffect(() => {
    runProfileAnalysis();
    runJobMatch();
    runRolePrepQuestions(targetRole);
  }, [targetRole]);

  const runProfileAnalysis = async () => {
    setLoading(true);
    try {
      const skillsArray = skillsInput.split(',').map(s => s.trim()).filter(Boolean);
      const res = await analyzePlacementProfile({
        cgpa,
        skills: skillsArray,
        target_role: targetRole
      });
      setProfileAnalysis(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleTextResumeAnalysis = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await analyzeResume({
        resume_text: resumeText,
        target_role: targetRole
      });
      setResumeResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handlePdfResumeUpload = async (e) => {
    e.preventDefault();
    if (!resumeFile) return;
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('resume_file', resumeFile);
      formData.append('target_role', targetRole);

      const res = await uploadResumePDF(formData);
      setResumeResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const runJobMatch = async () => {
    try {
      const skillsArray = skillsInput.split(',').map(s => s.trim()).filter(Boolean);
      const res = await fetchJobMatch({ skills: skillsArray });
      setMatchedJobs(res.jobs || []);
    } catch (err) {
      console.error(err);
    }
  };

  const runRolePrepQuestions = async (role) => {
    try {
      const res = await fetchPlacementPrepQuestions(role);
      setRoleQuestions(res.questions || []);
    } catch (err) {
      console.error(err);
    }
  };

  const handleEvaluateInterview = async (e) => {
    e.preventDefault();
    if (!studentInterviewAnswer.trim()) return;
    setLoading(true);
    try {
      const res = await evaluateMockInterview({
        user_answer: studentInterviewAnswer,
        target_role: targetRole,
        question_idx: questionIdx
      });
      setInterviewResult(res);
      setStudentInterviewAnswer('');
      if (res.next_question) {
        setInterviewQuestion(res.next_question);
        setQuestionIdx(res.next_question_idx || 0);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const toggleAnswerVisibility = (idx) => {
    setExpandedAnswerIndex(prev => ({ ...prev, [idx]: !prev[idx] }));
  };

  const readinessScore = profileAnalysis?.readiness_score || 78.5;
  const targetGap = profileAnalysis?.target_skill_gap || {};

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Placement Module Header */}
      <div className="glass-card" style={{
        background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%)',
        border: '1px solid var(--primary)',
        padding: '24px'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{ width: '48px', height: '48px', borderRadius: '14px', background: 'var(--secondary-gradient)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '24px' }}>
              🎯
            </div>
            <div>
              <h1 style={{ fontSize: '1.5rem', fontWeight: '800', color: '#fff' }}>
                AI-Based Placement & Career Guidance System
              </h1>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                Target Role Fit, Skill Gap Analysis, ATS PDF Resume Parser, Role Question Bank & AI Mock Interviewer
              </div>
            </div>
          </div>

          <div style={{ background: 'rgba(15, 23, 42, 0.7)', border: '1px solid var(--primary)', padding: '12px 20px', borderRadius: '14px', textAlign: 'right' }}>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: '700', textTransform: 'uppercase' }}>
              PLACEMENT READINESS SCORE
            </div>
            <div style={{ fontSize: '2rem', fontWeight: '800', color: readinessScore >= 75 ? '#34d399' : (readinessScore >= 50 ? '#fbbf24' : '#f87171') }}>
              {readinessScore}%
            </div>
          </div>
        </div>

        {/* Sub-Navigation Bar */}
        <div style={{ display: 'flex', gap: '8px', marginTop: '20px', overflowX: 'auto', paddingBottom: '4px' }}>
          {[
            { id: 'profile', label: '👤 Profile & Career Fit' },
            { id: 'gap', label: '⚡ Skill Gap & Roadmap' },
            { id: 'resume', label: '📄 ATS Resume PDF Analyzer' },
            { id: 'jobs', label: '💼 Job Matching Engine' },
            { id: 'prep', label: `✍️ Question Bank (${targetRole})` },
            { id: 'interview', label: '🤖 AI Mock Interviewer' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveSubTab(tab.id)}
              className={activeSubTab === tab.id ? 'btn-primary' : 'btn-secondary'}
              style={{ padding: '8px 16px', fontSize: '0.82rem', whiteSpace: 'nowrap' }}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* SUB-TAB 1: Profile & Career Fit */}
      {activeSubTab === 'profile' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div className="glass-card">
            <h3 style={{ fontSize: '1.1rem', marginBottom: '16px', color: 'var(--primary)' }}>
              👤 Student Profile & Target Role Selection
            </h3>
            <div className="grid-2">
              <div className="form-group">
                <label>Academic CGPA (0.0 - 10.0)</label>
                <input type="number" step="0.1" max="10" min="0" value={cgpa} onChange={(e) => setCgpa(Number(e.target.value))} className="form-control" />
              </div>
              <div className="form-group">
                <label>Target Career Role</label>
                <select value={targetRole} onChange={(e) => setTargetRole(e.target.value)} className="form-control">
                  <option value="ML Engineer">ML Engineer</option>
                  <option value="Data Scientist">Data Scientist</option>
                  <option value="Software Developer">Software Developer</option>
                  <option value="Data Analyst">Data Analyst</option>
                  <option value="Cloud Engineer">Cloud Engineer</option>
                  <option value="DevOps Engineer">DevOps Engineer</option>
                </select>
              </div>

              <div className="form-group">
                <label>Technical Skills (Comma Separated)</label>
                <input type="text" value={skillsInput} onChange={(e) => setSkillsInput(e.target.value)} className="form-control" placeholder="Python, Machine Learning, SQL..." />
              </div>
              <div className="form-group">
                <label>Programming Languages</label>
                <input type="text" value={languagesInput} onChange={(e) => setLanguagesInput(e.target.value)} className="form-control" placeholder="Python, C++, Java, SQL..." />
              </div>

              <div className="form-group">
                <label>Certifications</label>
                <input type="text" value={certifications} onChange={(e) => setCertifications(e.target.value)} className="form-control" />
              </div>
              <div className="form-group">
                <label>Key Projects</label>
                <input type="text" value={projectsInput} onChange={(e) => setProjectsInput(e.target.value)} className="form-control" />
              </div>
            </div>

            <button onClick={runProfileAnalysis} className="btn-primary" style={{ marginTop: '16px' }} disabled={loading}>
              {loading ? 'Analyzing Profile...' : '🚀 Calculate Career Suitability & Skill Gap'}
            </button>
          </div>

          {profileAnalysis && (
            <div className="glass-card">
              <h3 style={{ fontSize: '1.1rem', marginBottom: '16px', color: '#fff' }}>
                🎯 Career Role Suitability Scores
              </h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '14px' }}>
                {profileAnalysis.suitability_scores?.map((role, idx) => (
                  <div key={idx} style={{
                    background: 'rgba(15, 23, 42, 0.6)',
                    padding: '16px',
                    borderRadius: '12px',
                    border: role.role === targetRole ? '2px solid var(--primary)' : '1px solid var(--border-color)',
                    position: 'relative'
                  }}>
                    {role.role === targetRole && (
                      <span className="badge badge-strong" style={{ position: 'absolute', top: '12px', right: '12px', fontSize: '0.68rem' }}>
                        TARGET ROLE
                      </span>
                    )}
                    <div style={{ fontSize: '0.95rem', fontWeight: '700', color: '#fff', marginBottom: '4px' }}>
                      {role.role}
                    </div>
                    <div style={{ fontSize: '1.8rem', fontWeight: '800', color: role.suitability_score >= 75 ? '#34d399' : (role.suitability_score >= 50 ? '#fbbf24' : '#f87171') }}>
                      {role.suitability_score}%
                    </div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '6px' }}>
                      Matched: <strong style={{ color: '#34d399' }}>{role.matched_skills.length}</strong> | Missing: <strong style={{ color: '#f87171' }}>{role.missing_skills.length}</strong>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* SUB-TAB 2: Skill Gap Analysis & Learning Roadmap */}
      {activeSubTab === 'gap' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div className="glass-card">
            <h3 style={{ fontSize: '1.1rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              ⚡ Skill Gap Analysis for Target Role: <strong style={{ color: 'var(--primary)' }}>{targetRole}</strong>
            </h3>

            <div className="grid-2">
              <div style={{ background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '16px', borderRadius: '12px' }}>
                <h4 style={{ fontSize: '0.92rem', color: '#34d399', marginBottom: '10px' }}>
                  ✅ Possessed Skills ({targetGap.matched?.length || 0}):
                </h4>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {targetGap.matched?.map((sk, i) => (
                    <span key={i} className="badge badge-strong" style={{ padding: '6px 12px', fontSize: '0.82rem' }}>
                      {sk} ✅
                    </span>
                  ))}
                </div>
              </div>

              <div style={{ background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.3)', padding: '16px', borderRadius: '12px' }}>
                <h4 style={{ fontSize: '0.92rem', color: '#f87171', marginBottom: '10px' }}>
                  ❌ Identified Skill Gaps ({targetGap.missing?.length || 0}):
                </h4>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {targetGap.missing?.map((sk, i) => (
                    <span key={i} className="badge badge-weak" style={{ padding: '6px 12px', fontSize: '0.82rem' }}>
                      {sk} ❌
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="glass-card">
            <h3 style={{ fontSize: '1.1rem', marginBottom: '16px', color: '#fff' }}>
              🗺️ Personalized Learning Roadmap for {targetRole}
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {targetGap.roadmap?.map((step, idx) => (
                <div key={idx} style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '16px',
                  background: 'rgba(15, 23, 42, 0.6)',
                  padding: '14px 18px',
                  borderRadius: '10px',
                  borderLeft: '4px solid var(--primary)'
                }}>
                  <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'var(--primary-gradient)', color: '#fff', fontWeight: '800', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.85rem' }}>
                    {idx + 1}
                  </div>
                  <div>
                    <div style={{ fontWeight: '700', color: '#fff', fontSize: '0.95rem' }}>
                      {step}
                    </div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      Recommended order step {idx + 1} in placement preparation path.
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* SUB-TAB 3: ATS Resume PDF Analyzer */}
      {activeSubTab === 'resume' && (
        <div className="glass-card">
          <h3 style={{ fontSize: '1.1rem', marginBottom: '16px', color: 'var(--primary)' }}>
            📄 ATS Resume PDF File Analyzer & Keyword Parser
          </h3>

          <div className="grid-2" style={{ marginBottom: '24px' }}>
            {/* Option A: PDF File Upload */}
            <form onSubmit={handlePdfResumeUpload} style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '20px', borderRadius: '12px', border: '1px solid var(--primary)' }}>
              <h4 style={{ color: '#fff', fontSize: '0.95rem', marginBottom: '10px' }}>📁 Option 1: Upload Resume PDF File</h4>
              <div className="form-group" style={{ marginBottom: '16px' }}>
                <input
                  type="file"
                  accept=".pdf"
                  onChange={(e) => setResumeFile(e.target.files[0])}
                  className="form-control"
                />
              </div>
              <button type="submit" className="btn-primary" disabled={loading || !resumeFile} style={{ width: '100%' }}>
                {loading ? 'Processing Resume PDF...' : '🚀 Analyze Uploaded Resume PDF'}
              </button>
            </form>

            {/* Option B: Plain Text Paste */}
            <form onSubmit={handleTextResumeAnalysis} style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '20px', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
              <h4 style={{ color: '#fff', fontSize: '0.95rem', marginBottom: '10px' }}>📝 Option 2: Paste Resume Text</h4>
              <div className="form-group" style={{ marginBottom: '16px' }}>
                <textarea
                  rows={4}
                  value={resumeText}
                  onChange={(e) => setResumeText(e.target.value)}
                  className="form-control"
                  style={{ fontFamily: 'monospace', fontSize: '0.8rem' }}
                />
              </div>
              <button type="submit" className="btn-secondary" disabled={loading} style={{ width: '100%' }}>
                {loading ? 'Analyzing Text...' : '🚀 Analyze Pasted Text'}
              </button>
            </form>
          </div>

          {resumeResult && (
            <div style={{ marginTop: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(15, 23, 42, 0.7)', padding: '18px', borderRadius: '12px', border: '1px solid var(--primary)' }}>
                <div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: '700', textTransform: 'uppercase' }}>ATS RESUME MATCH SCORE</div>
                  <div style={{ fontSize: '2.5rem', fontWeight: '800', color: resumeResult.ats_score >= 75 ? '#34d399' : '#fbbf24' }}>
                    {resumeResult.ats_score}%
                  </div>
                </div>
                <div>
                  <span className={`badge badge-${resumeResult.ats_score >= 70 ? 'strong' : 'weak'}`} style={{ padding: '8px 14px' }}>
                    {resumeResult.ats_score >= 70 ? 'High ATS Match' : 'Needs Optimization'}
                  </span>
                </div>
              </div>

              <div className="grid-2">
                <div style={{ background: 'rgba(16, 185, 129, 0.08)', padding: '14px', borderRadius: '10px' }}>
                  <strong style={{ color: '#34d399', fontSize: '0.88rem' }}>Keywords Found in Resume:</strong>
                  <div style={{ marginTop: '6px', fontSize: '0.85rem', color: '#fff' }}>
                    {resumeResult.found_skills?.join(', ') || 'None'}
                  </div>
                </div>

                <div style={{ background: 'rgba(239, 68, 68, 0.08)', padding: '14px', borderRadius: '10px' }}>
                  <strong style={{ color: '#f87171', fontSize: '0.88rem' }}>Missing Target Keywords:</strong>
                  <div style={{ marginTop: '6px', fontSize: '0.85rem', color: '#fff' }}>
                    {resumeResult.missing_skills?.join(', ') || 'None'}
                  </div>
                </div>
              </div>

              {resumeResult.improvements?.length > 0 && (
                <div style={{ background: 'rgba(99, 102, 241, 0.12)', border: '1px solid var(--primary)', padding: '14px', borderRadius: '10px' }}>
                  <strong style={{ color: '#fff', fontSize: '0.88rem' }}>Actionable Resume Improvements:</strong>
                  <ul style={{ paddingLeft: '18px', marginTop: '6px', fontSize: '0.84rem', color: 'var(--text-sub)' }}>
                    {resumeResult.improvements.map((imp, idx) => (
                      <li key={idx}>{imp}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* SUB-TAB 4: Job Matching Engine */}
      {activeSubTab === 'jobs' && (
        <div className="glass-card">
          <h3 style={{ fontSize: '1.1rem', marginBottom: '16px', color: '#fff' }}>
            💼 AI Job Recommendation & Skill Match Engine
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {matchedJobs.map((job, idx) => (
              <div key={idx} style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
                <div>
                  <div style={{ fontWeight: '800', fontSize: '1.05rem', color: '#fff' }}>
                    {job.job_title}
                  </div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--primary)' }}>
                    🏢 {job.company} • 📍 {job.location} • 💰 {job.stipend}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                    Missing Requirements: <span style={{ color: '#f87171' }}>{job.missing_skills.join(', ') || 'None!'}</span>
                  </div>
                </div>

                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: '700', textTransform: 'uppercase' }}>MATCH PERCENTAGE</div>
                  <div style={{ fontSize: '2rem', fontWeight: '800', color: job.match_percentage >= 80 ? '#34d399' : '#fbbf24' }}>
                    {job.match_percentage}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SUB-TAB 5: Role-Tailored Question Bank */}
      {activeSubTab === 'prep' && (
        <div className="glass-card">
          <h3 style={{ fontSize: '1.1rem', marginBottom: '16px', color: 'var(--primary)' }}>
            ✍️ Placement Preparation Questions Tailored for: <strong style={{ color: '#fbbf24' }}>{targetRole}</strong>
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {roleQuestions.map((item, idx) => {
              const isExpanded = expandedAnswerIndex[idx];
              return (
                <div key={idx} style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
                  <div style={{ fontWeight: '700', color: '#fff', fontSize: '0.92rem', marginBottom: '8px' }}>
                    Q{idx + 1}: {item.question}
                  </div>

                  <button
                    onClick={() => toggleAnswerVisibility(idx)}
                    className="btn-secondary"
                    style={{ padding: '6px 12px', fontSize: '0.78rem' }}
                  >
                    {isExpanded ? '🙈 Hide Solution & Explanation' : '💡 Reveal Solution & Explanation'}
                  </button>

                  {isExpanded && (
                    <div style={{ marginTop: '12px', background: 'rgba(30, 41, 59, 0.6)', padding: '14px', borderRadius: '8px', borderLeft: '3px solid #34d399' }}>
                      <div style={{ fontWeight: '700', color: '#34d399', fontSize: '0.88rem' }}>
                        Answer: {item.answer}
                      </div>
                      <div style={{ fontSize: '0.84rem', color: 'var(--text-sub)', marginTop: '6px' }}>
                        {item.explanation}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* SUB-TAB 6: Interactive AI Mock Interview Simulator */}
      {activeSubTab === 'interview' && (
        <div className="glass-card">
          <h3 style={{ fontSize: '1.1rem', marginBottom: '16px', color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            🤖 AI Technical Mock Interviewer ({targetRole})
          </h3>

          <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '12px', marginBottom: '20px', border: '1px solid var(--border-color)' }}>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: '700' }}>INTERVIEW QUESTION #{questionIdx + 1}:</div>
            <div style={{ fontSize: '1.05rem', fontWeight: '800', color: '#fff', marginTop: '6px' }}>
              "{interviewQuestion}"
            </div>
          </div>

          <form onSubmit={handleEvaluateInterview}>
            <div className="form-group" style={{ marginBottom: '16px' }}>
              <label>Your Response / Solution:</label>
              <textarea
                rows={5}
                value={studentInterviewAnswer}
                onChange={(e) => setStudentInterviewAnswer(e.target.value)}
                className="form-control"
                placeholder="Explain your approach, technical trade-offs, and architecture..."
              />
            </div>

            <button type="submit" className="btn-primary" disabled={loading || !studentInterviewAnswer.trim()}>
              {loading ? 'Evaluating Answer...' : '⚡ Submit Answer & Advance to Next Question'}
            </button>
          </form>

          {interviewResult && (
            <div style={{ marginTop: '24px', background: 'rgba(15, 23, 42, 0.7)', padding: '20px', borderRadius: '12px', border: '1px solid var(--primary)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>PREVIOUS QUESTION SCORE</div>
                  <div style={{ fontSize: '2.5rem', fontWeight: '800', color: interviewResult.score >= 80 ? '#34d399' : '#fbbf24' }}>
                    {interviewResult.score} / 100
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '0.85rem', color: '#fff' }}>Technical Depth: <strong>{interviewResult.technical_depth}</strong></div>
                  <div style={{ fontSize: '0.85rem', color: '#fff' }}>Communication: <strong>{interviewResult.communication_rating}</strong></div>
                </div>
              </div>

              <div style={{ marginTop: '14px' }}>
                <strong style={{ color: '#fff', fontSize: '0.9rem' }}>AI Feedback & Guidance:</strong>
                <ul style={{ paddingLeft: '18px', marginTop: '6px', color: 'var(--text-sub)', fontSize: '0.85rem' }}>
                  {interviewResult.feedback?.map((fb, i) => <li key={i}>{fb}</li>)}
                </ul>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
