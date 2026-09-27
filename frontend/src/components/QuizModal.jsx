import React, { useState } from 'react';
import { submitAdaptiveQuiz } from '../services/api';

export default function QuizModal({ quizQuestions, studentId, onClose }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const currentQ = quizQuestions[currentIndex];

  const handleSelectOption = (optIndex) => {
    setUserAnswers({
      ...userAnswers,
      [currentIndex]: optIndex
    });
  };

  const handleSubmit = async () => {
    setLoading(true);
    const answersPayload = quizQuestions.map((q, idx) => ({
      question: q.question,
      selected: userAnswers[idx] !== undefined ? userAnswers[idx] : -1,
      correct: q.correct,
      explanation: q.explanation
    }));

    try {
      const res = await submitAdaptiveQuiz({
        student_id: studentId,
        answers: answersPayload
      });
      setResult(res);
      setSubmitted(true);
    } catch (err) {
      console.error(err);
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
      <div className="glass-card" style={{ maxWidth: '680px', width: '100%', maxHeight: '90vh', overflowY: 'auto', border: '1px solid var(--primary)' }}>
        
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px' }}>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '700', color: '#fff' }}>
              🧠 Adaptive AI Self-Assessment Quiz
            </h2>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Targeted Focus on Weak & Moderate Topics</div>
          </div>
          <button onClick={onClose} className="btn-secondary" style={{ padding: '6px 12px', fontSize: '0.85rem' }}>✕ Close</button>
        </div>

        {!submitted ? (
          <div>
            {/* Progress Bar */}
            <div style={{ background: 'rgba(255, 255, 255, 0.1)', height: '6px', borderRadius: '4px', marginBottom: '20px', overflow: 'hidden' }}>
              <div style={{ background: 'var(--primary-gradient)', height: '100%', width: `${((currentIndex + 1) / quizQuestions.length) * 100}%`, transition: 'width 0.3s' }}></div>
            </div>

            <div style={{ fontSize: '0.8rem', color: 'var(--primary)', fontWeight: '700', marginBottom: '8px' }}>
              QUESTION {currentIndex + 1} OF {quizQuestions.length}
            </div>

            <h3 style={{ fontSize: '1.1rem', marginBottom: '20px', lineHeight: 1.4 }}>
              {currentQ?.question}
            </h3>

            {/* Options */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '24px' }}>
              {currentQ?.options.map((opt, optIdx) => {
                const isSelected = userAnswers[currentIndex] === optIdx;
                return (
                  <button
                    key={optIdx}
                    onClick={() => handleSelectOption(optIdx)}
                    style={{
                      padding: '14px 18px',
                      borderRadius: '10px',
                      textAlign: 'left',
                      background: isSelected ? 'rgba(99, 102, 241, 0.25)' : 'rgba(30, 41, 59, 0.6)',
                      border: isSelected ? '2px solid var(--primary)' : '1px solid var(--border-color)',
                      color: isSelected ? '#fff' : 'var(--text-sub)',
                      fontSize: '0.95rem',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                      transition: 'all 0.2s'
                    }}
                  >
                    <span style={{
                      width: '24px',
                      height: '24px',
                      borderRadius: '50%',
                      background: isSelected ? 'var(--primary)' : 'rgba(255,255,255,0.1)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '0.75rem',
                      fontWeight: '700'
                    }}>
                      {String.fromCharCode(65 + optIdx)}
                    </span>
                    {opt}
                  </button>
                );
              })}
            </div>

            {/* Navigation buttons */}
            <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid var(--border-color)', paddingTop: '16px' }}>
              <button
                disabled={currentIndex === 0}
                onClick={() => setCurrentIndex(currentIndex - 1)}
                className="btn-secondary"
                style={{ padding: '8px 16px', fontSize: '0.85rem' }}
              >
                ← Previous
              </button>

              {currentIndex < quizQuestions.length - 1 ? (
                <button
                  onClick={() => setCurrentIndex(currentIndex + 1)}
                  className="btn-primary"
                  style={{ padding: '8px 20px', fontSize: '0.85rem' }}
                >
                  Next Question →
                </button>
              ) : (
                <button
                  onClick={handleSubmit}
                  className="btn-primary"
                  style={{ padding: '8px 20px', fontSize: '0.85rem', background: 'var(--success-gradient)' }}
                  disabled={loading}
                >
                  {loading ? 'Evaluating...' : '✓ Finish & Submit Quiz'}
                </button>
              )}
            </div>
          </div>
        ) : (
          /* Quiz Results View */
          <div style={{ textAlign: 'center', padding: '10px 0' }}>
            <div style={{ fontSize: '3.5rem', fontWeight: '800', color: result?.score_percentage >= 70 ? '#34d399' : '#fbbf24', marginBottom: '8px' }}>
              {result?.score_percentage}%
            </div>
            <h3 style={{ fontSize: '1.2rem', marginBottom: '4px' }}>
              {result?.grade_feedback}
            </h3>
            <p style={{ color: 'var(--text-muted)', marginBottom: '20px', fontSize: '0.9rem' }}>
              You answered {result?.correct_answers} out of {result?.total_questions} questions correctly.
            </p>

            {/* Explanations List */}
            <div style={{ textAlign: 'left', display: 'flex', flexDirection: 'column', gap: '12px', maxHeight: '300px', overflowY: 'auto', marginBottom: '20px', paddingRight: '6px' }}>
              {result?.detailed_results.map((item, idx) => (
                <div key={idx} style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '12px 16px', borderRadius: '10px', borderLeft: item.is_correct ? '4px solid #10b981' : '4px solid #ef4444' }}>
                  <div style={{ fontSize: '0.85rem', fontWeight: '700', color: item.is_correct ? '#34d399' : '#f87171', marginBottom: '4px' }}>
                    {item.is_correct ? '✓ Correct' : '✕ Incorrect'} — Q{idx + 1}: {item.question}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    💡 Explanation: {item.explanation}
                  </div>
                </div>
              ))}
            </div>

            <button onClick={onClose} className="btn-primary" style={{ width: '100%', justifyContent: 'center' }}>
              Done & Return to Dashboard
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
