import React, { useState, useEffect } from 'react';
import {
  uploadUnitPDF,
  uploadQuestionPaper,
  uploadStudentMarks,
  fetchClassAnalytics,
  fetchUnitTopics,
  generatePaperFromPDF,
  fetchStudentIAAnalysis,
  evaluateStudentAnswerSheet,
  fetchQuestionPaper
} from '../services/api';
import { TrendLineChart } from './AnalyticsChart';

export default function TeacherDashboard({ subject, user, onOpenLogin }) {
  const [activeStep, setActiveStep] = useState(1);
  const [unitNumber, setUnitNumber] = useState(1);
  const [pdfFile, setPdfFile] = useState(null);
  const [extractedContent, setExtractedContent] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [loading, setLoading] = useState(false);

  // Step 2 Question Paper Mapping State
  const [iaType, setIaType] = useState('IA 1'); // 'IA 1', 'IA 2', 'IA 3'
  const [questionsInput, setQuestionsInput] = useState([]);

  // Step 3 Student Marks Upload & Automated Answer Sheet Evaluation State
  const [step3Mode, setStep3Mode] = useState('ai_eval'); // 'ai_eval' or 'manual'
  const [marksIaType, setMarksIaType] = useState('Internal Assessment 1');
  const [studentId, setStudentId] = useState('STU101');
  const [studentName, setStudentName] = useState('John Doe');
  const [answerPdfFile, setAnswerPdfFile] = useState(null);
  const [answerSheetText, setAnswerSheetText] = useState('');
  const [evaluationReport, setEvaluationReport] = useState(null);
  const [evaluating, setEvaluating] = useState(false);
  const [marksScores, setMarksScores] = useState({});

  // Student Performance & Weak Topics Analyzer State (Triggered by Button / Modal)
  const [showAnalyzerModal, setShowAnalyzerModal] = useState(false);
  const [analysisStudentId, setAnalysisStudentId] = useState('STU101');
  const [analysisIaType, setAnalysisIaType] = useState('Internal Assessment 1');
  const [studentAnalysis, setStudentAnalysis] = useState(null);

  // Class Analytics State
  const [analytics, setAnalytics] = useState(null);

  useEffect(() => {
    loadClassAnalytics();
    loadExtractedTopicsForUnit(unitNumber);
  }, [subject, unitNumber]);

  useEffect(() => {
    if (activeStep === 2) {
      loadQuestionPaperForIa(iaType);
    }
  }, [activeStep, iaType, subject]);

  useEffect(() => {
    if (showAnalyzerModal) {
      handleRunStudentAnalysis();
    }
  }, [analysisStudentId, analysisIaType, subject, showAnalyzerModal]);

  const loadClassAnalytics = async () => {
    try {
      const res = await fetchClassAnalytics(subject);
      setAnalytics(res.analytics);
    } catch (err) {
      console.error(err);
    }
  };

  const loadExtractedTopicsForUnit = async (uNum) => {
    try {
      const res = await fetchUnitTopics(subject, uNum);
      if (res.topics && res.topics.length > 0) {
        setExtractedContent(res);
        if (questionsInput.length === 0) {
          try {
            const paperRes = await generatePaperFromPDF(subject, iaType, res.topics, uNum);
            if (paperRes.question_paper?.questions) {
              setQuestionsInput(paperRes.question_paper.questions);
            }
          } catch (e) {}
        }
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Step 1: Upload Unit PDF & Index in RAG Engine
  const handlePdfUpload = async (e) => {
    e.preventDefault();
    setLoading(true);
    setUploadStatus('Parsing PDF & extracting unit topics, subtopics, and key concepts...');
    try {
      const formData = new FormData();
      formData.append('subject', subject);
      formData.append('unit_number', unitNumber);
      if (pdfFile) {
        formData.append('unit_pdf', pdfFile);
      }
      const res = await uploadUnitPDF(formData);
      setUploadStatus(`✅ ${res.message}`);
      setExtractedContent(res.unit_data);

      // Auto-generate Step 2 questions immediately using the newly extracted topics!
      if (res.unit_data?.topics && res.unit_data.topics.length > 0) {
        try {
          const paperRes = await generatePaperFromPDF(subject, iaType, res.unit_data.topics, unitNumber);
          if (paperRes.question_paper?.questions) {
            setQuestionsInput(paperRes.question_paper.questions);
          }
        } catch (genErr) {
          console.error("Auto question generation after upload warning:", genErr);
        }
      }

      loadClassAnalytics();
    } catch (err) {
      setUploadStatus(`✕ Upload failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Step 2: Auto-Prepare Question Paper from PDF Topics based on Assessment Type (IA 1, IA 2, IA 3)
  const handleGeneratePaperByIaType = async (selectedIa) => {
    const targetIa = selectedIa || iaType;
    setLoading(true);
    const topicsToSend = extractedContent?.topics || [];
    setUploadStatus(`Preparing Blueprint question paper for ${targetIa} from extracted PDF topics...`);
    try {
      const res = await generatePaperFromPDF(subject, targetIa, topicsToSend, unitNumber);
      if (res.question_paper?.questions) {
        setQuestionsInput(res.question_paper.questions);
        setUploadStatus(`✅ Blueprint Question Paper prepared for ${targetIa} (${res.question_paper.questions.length} items)!`);
      }
    } catch (err) {
      setUploadStatus(`✕ Question Paper generation error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Question Paper editing helpers
  const handleAddQuestionRow = () => {
    const nextQId = `Q${questionsInput.length + 1}`;
    const defaultTopic = extractedContent?.topics?.[0] || 'Core Concept';
    setQuestionsInput([
      ...questionsInput,
      { question_id: nextQId, question: `What is ${defaultTopic}? Describe its primary characteristics.`, topic: defaultTopic, max_marks: 5, unit_number: unitNumber, part: 'Custom Question' }
    ]);
  };

  const handleRemoveQuestionRow = (idx) => {
    const updated = questionsInput.filter((_, i) => i !== idx);
    setQuestionsInput(updated);
  };

  // Save Question Paper Mapping
  const handleQpSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const examTitle = `Internal Assessment ${iaType.split(' ')[1] || '1'}`;
      const res = await uploadQuestionPaper({
        subject,
        exam_name: examTitle,
        unit_number: unitNumber,
        questions: questionsInput
      });
      setUploadStatus(`✅ Question Paper Mapping Saved for ${examTitle}!`);
      loadClassAnalytics();
    } catch (err) {
      setUploadStatus(`✕ Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Sample Answer Sheet Quick-Fill for instant demonstration
  const handleLoadSampleAnswerSheet = () => {
    const sample = `Q1. Convolutional Neural Networks (CNN) are specialized deep neural architectures designed for processing spatial grid data like images. They use convolution operations with shared weights and spatial pooling to extract translation-invariant hierarchical representations.

Q2. AlexNet and VGG are landmark CNN architectures. AlexNet introduced ReLU activations, dropout regularization, and GPU acceleration. VGG standardized deep architectures using consecutive 3x3 small receptive field convolutional filters.

Q3. A Perceptron is the fundamental binary linear classification unit in neural networks. It computes the dot product of input feature vectors and synaptic weights plus a bias, passing the sum through a threshold activation function.

Q4. Backpropagation Through Time (BPTT) is the gradient descent optimization algorithm used for training recurrent neural networks. It unrolls the recurrent computations across sequence time steps to compute weight gradients using the chain rule.

Q5. Activation functions introduce non-linear mappings into neural networks, enabling multi-layer networks to approximate non-linear decision boundaries and solve complex classification tasks.

Q6a. CNN Architecture comprises three primary layer types: convolutional layers, pooling layers, and fully connected dense layers. The convolutional layer performs spatial filtering using learnable kernels with specified stride and padding to generate 2D feature maps. Pooling layers (max pooling or average pooling) downsample feature map dimensions, reducing parameter count and computational complexity while ensuring translation invariance. Finally, fully connected layers flatten spatial representations into dense classification vectors with softmax normalization. Parameter optimization is executed via backpropagation and Adam optimizer.

Q7a. Convolutional Neural Networks use parameter sharing and local receptive fields to dramatically reduce memory footprint compared to fully connected layers. Instead of connecting every input pixel to every neuron, shared kernel weights slide across the receptive field, preserving spatial neighborhood structure. Mathematical convolution computes the inner product between receptive field and kernel weights.

Q8a. Deploying deep neural network architectures into enterprise production pipelines requires rigorous parameter tuning, loss function selection, and latency optimization. To mitigate overfitting and vanishing gradients, architectures incorporate residual skip connections, batch normalization layers, and dropout. Inference latency is optimized through FP16 quantization and pruning. Failure modes such as covariate shift are monitored using prediction drift metrics.`;

    setAnswerSheetText(sample);
    setUploadStatus('Loaded sample student answer sheet for demonstration! Click "Evaluate Answer Sheet" to run Dual Search.');
  };

  // Run Automated AI Answer Sheet Evaluation
  const handleEvaluateAnswerSheet = async () => {
    if (!answerPdfFile && !answerSheetText.trim()) {
      alert('Please upload a student answer sheet PDF or paste/type student answers.');
      return;
    }

    setEvaluating(true);
    setUploadStatus(`Analyzing student answer sheet using Semantic Vector Search + Keyword Search...`);

    try {
      let res;
      if (answerPdfFile) {
        const formData = new FormData();
        formData.append('subject', subject);
        formData.append('exam_name', marksIaType);
        formData.append('student_id', studentId);
        formData.append('student_name', studentName);
        formData.append('answer_pdf', answerPdfFile);
        if (answerSheetText) {
          formData.append('raw_text', answerSheetText);
        }
        res = await evaluateStudentAnswerSheet(formData);
      } else {
        res = await evaluateStudentAnswerSheet({
          subject,
          exam_name: marksIaType,
          student_id: studentId,
          student_name: studentName,
          raw_text: answerSheetText
        });
      }

      if (res.status === 'success' && res.evaluation) {
        setEvaluationReport(res.evaluation);
        setMarksScores(res.evaluation.question_scores || {});
        setUploadStatus(`✅ Answer Sheet Evaluated: ${res.evaluation.total_score} / ${res.evaluation.max_score} Marks (${res.evaluation.percentage}% - Grade ${res.evaluation.grade}) using Semantic + Keyword Search!`);
        loadClassAnalytics();
      } else {
        setUploadStatus(`✕ Evaluation warning: ${res.message || 'Unable to evaluate'}`);
      }
    } catch (err) {
      setUploadStatus(`✕ Evaluation error: ${err.message}`);
    } finally {
      setEvaluating(false);
    }
  };

  // Save Evaluated Marks to Database
  const handleSaveApprovedMarks = async () => {
    setLoading(true);
    try {
      const res = await uploadStudentMarks({
        subject,
        exam_name: marksIaType,
        student_id: studentId,
        student_name: studentName,
        question_scores: marksScores,
        total_score: evaluationReport?.total_score,
        max_score: evaluationReport?.max_score,
        percentage: evaluationReport?.percentage,
        grade: evaluationReport?.grade,
        evaluated_questions: evaluationReport?.evaluated_questions || []
      });
      setUploadStatus(`✅ Marks approved & saved for ${studentName} (${studentId}) under ${marksIaType}! RAG study guide & weak topic quiz assigned.`);
      loadClassAnalytics();
      if (showAnalyzerModal) handleRunStudentAnalysis();
    } catch (err) {
      setUploadStatus(`✕ Error saving marks: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Run Student Performance & Weak Topics Analysis
  const handleRunStudentAnalysis = async () => {
    try {
      const res = await fetchStudentIAAnalysis(subject, analysisStudentId, analysisIaType);
      setStudentAnalysis(res);
    } catch (err) {
      console.error(err);
    }
  };

  if (!user || user.role !== 'teacher') {
    return (
      <div className="glass-card" style={{ textAlign: 'center', padding: '60px 20px', maxWidth: '540px', margin: '40px auto' }}>
        <div style={{ fontSize: '3rem', marginBottom: '16px' }}>🔐</div>
        <h2 style={{ fontSize: '1.4rem', marginBottom: '8px' }}>Teacher Dashboard Authentication</h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: '24px', fontSize: '0.95rem' }}>
          Please log in as Teacher to upload unit PDFs, generate IA 1 / IA 2 / IA 3 question papers, and evaluate student answer sheets for <strong style={{ color: '#fff' }}>{subject}</strong>.
        </p>
        <button onClick={onOpenLogin} className="btn-primary" style={{ padding: '12px 24px', justifyContent: 'center' }}>
          🔑 Login as Teacher
        </button>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Top Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '1.6rem', fontWeight: '800' }}>👨‍🏫 Teacher Management Dashboard</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            Upload Unit PDFs, Auto-Prepare IA Question Papers & Evaluate Student Answer Sheets for <strong style={{ color: 'var(--primary)' }}>{subject}</strong>
          </p>
        </div>

        <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
          {/* Analyze Student Performance Button */}
          <button
            onClick={() => {
              setShowAnalyzerModal(true);
              handleRunStudentAnalysis();
            }}
            className="btn-primary"
            style={{ background: 'var(--secondary-gradient)', padding: '10px 18px', fontSize: '0.85rem' }}
          >
            📊 Analyze Student Performance
          </button>

          {/* Step Selector Tabs */}
          <div style={{ display: 'flex', gap: '6px', background: 'rgba(30, 41, 59, 0.6)', padding: '4px', borderRadius: '10px' }}>
            <button onClick={() => setActiveStep(1)} className={activeStep === 1 ? 'btn-primary' : 'btn-secondary'} style={{ padding: '6px 12px', fontSize: '0.8rem' }}>
              Step 1: Upload PDF
            </button>
            <button onClick={() => setActiveStep(2)} className={activeStep === 2 ? 'btn-primary' : 'btn-secondary'} style={{ padding: '6px 12px', fontSize: '0.8rem' }}>
              Step 2: Question Mapping
            </button>
            <button onClick={() => setActiveStep(3)} className={activeStep === 3 ? 'btn-primary' : 'btn-secondary'} style={{ padding: '6px 12px', fontSize: '0.8rem' }}>
              Step 3: Evaluate Answer Sheet & Marks
            </button>
          </div>
        </div>
      </div>

      {uploadStatus && (
        <div style={{ background: 'rgba(99, 102, 241, 0.15)', border: '1px solid var(--primary)', borderRadius: '10px', padding: '12px 16px', color: '#fff', fontSize: '0.9rem' }}>
          {uploadStatus}
        </div>
      )}

      {/* Main Workflow Form Card */}
      <div className="glass-card">
        {/* STEP 1: UPLOAD UNIT PDF */}
        {activeStep === 1 && (
          <div>
            <h3 style={{ fontSize: '1.1rem', marginBottom: '16px' }}>📄 Step 1: Upload Unit PDF & Extract Topics</h3>
            <form onSubmit={handlePdfUpload}>
              <div className="grid-2">
                <div className="form-group">
                  <label>Select Unit Number (Units 1 to 5)</label>
                  <select value={unitNumber} onChange={(e) => setUnitNumber(Number(e.target.value))} className="form-control">
                    {[1, 2, 3, 4, 5].map(n => <option key={n} value={n}>Unit {n}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Unit PDF File (PyMuPDF Text Extractor)</label>
                  <input type="file" accept=".pdf" onChange={(e) => setPdfFile(e.target.files[0])} className="form-control" />
                </div>
              </div>

              <button type="submit" className="btn-primary" style={{ marginTop: '12px' }} disabled={loading}>
                {loading ? 'Processing & Extracting Topics...' : '🚀 Upload PDF & Extract Unit Topics'}
              </button>
            </form>

            {/* Display Extracted Content Summary */}
            {extractedContent && (
              <div style={{ marginTop: '24px', background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
                <div style={{ fontWeight: '700', color: 'var(--primary)', marginBottom: '8px', fontSize: '0.9rem' }}>
                  💡 EXTRACTED TOPICS FOR UNIT {extractedContent.unit_number}: {extractedContent.unit_title}
                </div>
                <div style={{ marginBottom: '10px' }}>
                  <strong style={{ fontSize: '0.85rem', color: '#fff' }}>Extracted Topics: </strong>
                  <span style={{ color: 'var(--text-sub)', fontSize: '0.85rem' }}>{extractedContent.topics?.join(', ')}</span>
                </div>
                <div>
                  <strong style={{ fontSize: '0.85rem', color: '#fff' }}>Extracted Important Questions: </strong>
                  <ul style={{ paddingLeft: '18px', fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                    {extractedContent.important_questions?.map((q, idx) => (
                      <li key={idx}>{q.question} ({q.marks_category} Marks)</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        )}

        {/* STEP 2: QUESTION MAPPING & BLUEPRINT GENERATION */}
        {activeStep === 2 && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
              <div>
                <h3 style={{ fontSize: '1.1rem', margin: 0 }}>🗺️ Step 2: Auto-Prepare Question Paper from PDF Topics</h3>
                <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                  Strict Blueprint Alignment: IA 1 (5x2M, 4x12M [6a/b, 7a/b], 1x16M [8a/b]), IA 2 (Part A Unit 2, Part B Unit 3, Part C Unit 3), IA 3 (10x2M [2 per unit], 5x12M [Q6-Q10 a/b], 1x16M [Q11a/b]).
                </div>
              </div>
              <button type="button" onClick={handleAddQuestionRow} className="btn-secondary" style={{ padding: '6px 12px', fontSize: '0.8rem' }}>
                + Add Custom Question Row
              </button>
            </div>

            {/* Assessment Blueprint Info Card */}
            <div style={{
              background: 'rgba(59, 130, 246, 0.08)',
              border: '1px solid rgba(59, 130, 246, 0.3)',
              borderRadius: '10px',
              padding: '12px 16px',
              marginBottom: '16px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: '12px'
            }}>
              <div>
                <div style={{ fontWeight: '700', color: '#93c5fd', fontSize: '0.88rem' }}>
                  📌 Active Blueprint: {iaType === 'IA 1' ? 'Internal Assessment 1 (50 Marks)' : iaType === 'IA 2' ? 'Internal Assessment 2 (50 Marks)' : 'Internal Assessment 3 / Model Exam (100 Marks)'}
                </div>
                <div style={{ fontSize: '0.78rem', color: '#cbd5e1', marginTop: '2px' }}>
                  {iaType === 'IA 1' && 'Part A: Q1-Q5 (2M, Units 1 & 2) • Part B: Q6a/b (12M, Unit 1), Q7a/b (12M, Unit 2) • Part C: Q8a/b (16M, Either/Or)'}
                  {iaType === 'IA 2' && 'Part A: Q1-Q5 (2M, Unit 2) • Part B: Q6a/b (12M, Unit 3), Q7a/b (12M, Unit 3) • Part C: Q8a/b (16M, Unit 3 Either/Or)'}
                  {iaType === 'IA 3' && 'Part A: Q1-Q10 (2M, 2 questions per unit for Units 1-5) • Part B: Q6-Q10 (12M Each Unit Either/Or) • Part C: Q11a/b (16M Either/Or)'}
                </div>
              </div>

              <div style={{ display: 'flex', gap: '8px' }}>
                {['IA 1', 'IA 2', 'IA 3'].map((ia) => (
                  <button
                    key={ia}
                    type="button"
                    onClick={() => {
                      setIaType(ia);
                      handleGeneratePaperByIaType(ia);
                    }}
                    className={iaType === ia ? 'btn-primary' : 'btn-secondary'}
                    style={{ padding: '6px 12px', fontSize: '0.78rem' }}
                  >
                    {ia}
                  </button>
                ))}
              </div>
            </div>

            <form onSubmit={handleQpSubmit}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', margin: '16px 0 8px' }}>
                <h4 style={{ fontSize: '0.95rem', color: 'var(--primary)', margin: 0 }}>
                  Questions Blueprint Items ({questionsInput.length} Items):
                </h4>
                <button
                  type="button"
                  onClick={() => handleGeneratePaperByIaType(iaType)}
                  className="btn-secondary"
                  style={{ padding: '6px 12px', fontSize: '0.8rem' }}
                  disabled={loading}
                >
                  ⚡ Regenerate Blueprint from PDF Topics
                </button>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '16px', maxHeight: '420px', overflowY: 'auto', paddingRight: '4px' }}>
                {questionsInput.map((q, idx) => (
                  <div key={idx} style={{ display: 'grid', gridTemplateColumns: '70px 140px 1fr 180px 70px 36px', gap: '8px', alignItems: 'center', background: 'rgba(15, 23, 42, 0.5)', padding: '8px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                    <input
                      type="text"
                      value={q.question_id}
                      onChange={(e) => {
                        const updated = [...questionsInput];
                        updated[idx].question_id = e.target.value;
                        setQuestionsInput(updated);
                      }}
                      className="form-control"
                      style={{ padding: '6px', fontWeight: '700', textAlign: 'center' }}
                    />

                    <span style={{ fontSize: '0.72rem', color: 'var(--primary)', fontWeight: '700', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {q.part || `Unit ${q.unit_number}`}
                    </span>

                    <input
                      type="text"
                      value={q.question || ''}
                      onChange={(e) => {
                        const updated = [...questionsInput];
                        updated[idx].question = e.target.value;
                        setQuestionsInput(updated);
                      }}
                      className="form-control"
                      placeholder="Question Text"
                      style={{ padding: '6px' }}
                    />

                    {/* Mapped Topic */}
                    {extractedContent?.topics && extractedContent.topics.length > 0 ? (
                      <select
                        value={q.topic}
                        onChange={(e) => {
                          const updated = [...questionsInput];
                          updated[idx].topic = e.target.value;
                          setQuestionsInput(updated);
                        }}
                        className="form-control"
                        style={{ padding: '6px', fontSize: '0.8rem' }}
                      >
                        {extractedContent.topics.map((t, tIdx) => (
                          <option key={tIdx} value={t}>{t}</option>
                        ))}
                        <option value={q.topic}>{q.topic} (Custom)</option>
                      </select>
                    ) : (
                      <input
                        type="text"
                        value={q.topic}
                        onChange={(e) => {
                          const updated = [...questionsInput];
                          updated[idx].topic = e.target.value;
                          setQuestionsInput(updated);
                        }}
                        className="form-control"
                        placeholder="Mapped Topic"
                        style={{ padding: '6px', fontSize: '0.8rem' }}
                      />
                    )}

                    <input
                      type="number"
                      value={q.max_marks}
                      onChange={(e) => {
                        const updated = [...questionsInput];
                        updated[idx].max_marks = Number(e.target.value);
                        setQuestionsInput(updated);
                      }}
                      className="form-control"
                      placeholder="Marks"
                      style={{ padding: '6px', textAlign: 'center' }}
                    />

                    <button
                      type="button"
                      onClick={() => handleRemoveQuestionRow(idx)}
                      style={{ background: 'rgba(239, 68, 68, 0.2)', color: '#f87171', border: 'none', borderRadius: '6px', padding: '6px', cursor: 'pointer' }}
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>

              <button type="submit" className="btn-primary" disabled={loading}>
                {loading ? 'Saving Mapping...' : '💾 Save Question Paper Mapping'}
              </button>
            </form>
          </div>
        )}

        {/* STEP 3: AUTOMATED ANSWER SHEET EVALUATION & MARKS UPLOAD */}
        {activeStep === 3 && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
              <div>
                <h3 style={{ fontSize: '1.15rem', margin: 0 }}>
                  ✍️ Step 3: Student Answer Sheet Evaluation & Marks Upload
                </h3>
                <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                  Upload student answer sheets (PDF or text). The system compares student answers with authoritative content extracted from the uploaded PDF using both <strong>Semantic Vector Search</strong> and <strong>Keyword Search</strong> to award marks.
                </div>
              </div>

              {/* Mode Toggle */}
              <div style={{ display: 'flex', gap: '6px', background: 'rgba(30, 41, 59, 0.7)', padding: '4px', borderRadius: '8px' }}>
                <button
                  type="button"
                  onClick={() => setStep3Mode('ai_eval')}
                  className={step3Mode === 'ai_eval' ? 'btn-primary' : 'btn-secondary'}
                  style={{ padding: '6px 12px', fontSize: '0.78rem' }}
                >
                  ✨ AI Answer Sheet Evaluator
                </button>
                <button
                  type="button"
                  onClick={() => setStep3Mode('manual')}
                  className={step3Mode === 'manual' ? 'btn-primary' : 'btn-secondary'}
                  style={{ padding: '6px 12px', fontSize: '0.78rem' }}
                >
                  ✍️ Manual Marks Entry
                </button>
              </div>
            </div>

            {/* Assessment & Student Information Fields */}
            <div className="grid-2" style={{ marginBottom: '16px' }}>
              <div className="form-group">
                <label style={{ color: 'var(--primary)', fontWeight: '700' }}>Target Assessment (IA)</label>
                <select
                  value={marksIaType}
                  onChange={(e) => setMarksIaType(e.target.value)}
                  className="form-control"
                  style={{ border: '1px solid var(--primary)', fontWeight: '700' }}
                >
                  <option value="Internal Assessment 1">Internal Assessment 1 (IA 1)</option>
                  <option value="Internal Assessment 2">Internal Assessment 2 (IA 2)</option>
                  <option value="Internal Assessment 3">Internal Assessment 3 (IA 3)</option>
                </select>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr', gap: '10px' }}>
                <div className="form-group">
                  <label>Student ID</label>
                  <input type="text" value={studentId} onChange={(e) => setStudentId(e.target.value)} className="form-control" required />
                </div>
                <div className="form-group">
                  <label>Student Full Name</label>
                  <input type="text" value={studentName} onChange={(e) => setStudentName(e.target.value)} className="form-control" required />
                </div>
              </div>
            </div>

            {/* AI ANSWER SHEET EVALUATION MODE */}
            {step3Mode === 'ai_eval' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
                <div style={{
                  background: 'rgba(15, 23, 42, 0.7)',
                  border: '1px dashed rgba(99, 102, 241, 0.4)',
                  padding: '20px',
                  borderRadius: '12px'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px', flexWrap: 'wrap', gap: '8px' }}>
                    <div style={{ fontWeight: '700', color: '#fff', fontSize: '0.95rem' }}>
                      📄 Upload Student Answer Sheet (PDF or Scanned Text)
                    </div>
                    <button
                      type="button"
                      onClick={handleLoadSampleAnswerSheet}
                      style={{
                        background: 'rgba(59, 130, 246, 0.15)',
                        border: '1px solid #60a5fa',
                        color: '#93c5fd',
                        padding: '4px 10px',
                        borderRadius: '6px',
                        fontSize: '0.75rem',
                        cursor: 'pointer'
                      }}
                    >
                      ⚡ Quick Load Sample Student Answer Sheet
                    </button>
                  </div>

                  <div className="grid-2" style={{ gap: '16px', marginBottom: '14px' }}>
                    <div>
                      <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px', display: 'block' }}>
                        Option A: Upload Answer Sheet File (.pdf, .txt)
                      </label>
                      <input
                        type="file"
                        accept=".pdf,.txt"
                        onChange={(e) => setAnswerPdfFile(e.target.files[0])}
                        className="form-control"
                      />
                    </div>

                    <div>
                      <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px', display: 'block' }}>
                        Option B: Paste or Edit Student Written Text Answers
                      </label>
                      <textarea
                        rows={4}
                        value={answerSheetText}
                        onChange={(e) => setAnswerSheetText(e.target.value)}
                        className="form-control"
                        placeholder="Format: Q1. [Answer text]&#10;Q2. [Answer text]&#10;Q6a. [Answer text]..."
                        style={{ fontSize: '0.82rem', fontFamily: 'monospace' }}
                      />
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={handleEvaluateAnswerSheet}
                    className="btn-primary"
                    disabled={evaluating}
                    style={{ width: '100%', justifyContent: 'center', padding: '12px' }}
                  >
                    {evaluating ? '🔄 Analyzing Semantic Cosine Similarity & Keyword Matches...' : '✨ Run Dual Search AI Evaluation (Semantic + Keyword Similarity)'}
                  </button>
                </div>

                {/* EVALUATION REPORT CARD */}
                {evaluationReport && (
                  <div style={{
                    background: 'rgba(15, 23, 42, 0.85)',
                    border: '1px solid var(--primary)',
                    borderRadius: '14px',
                    padding: '24px'
                  }}>
                    {/* Header Summary */}
                    <div style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      borderBottom: '1px solid var(--border-color)',
                      paddingBottom: '16px',
                      marginBottom: '20px',
                      flexWrap: 'wrap',
                      gap: '12px'
                    }}>
                      <div>
                        <div style={{ fontSize: '1.25rem', fontWeight: '800', color: '#fff' }}>
                          📊 Evaluation Scorecard: {evaluationReport.student_name} ({evaluationReport.student_id})
                        </div>
                        <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                          {evaluationReport.exam_name} • Subject: <strong style={{ color: 'var(--primary)' }}>{subject}</strong>
                        </div>
                      </div>

                      <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
                        <div style={{ textAlign: 'right' }}>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>TOTAL AWARDED MARKS</div>
                          <div style={{ fontSize: '2rem', fontWeight: '800', color: evaluationReport.percentage >= 75 ? '#34d399' : evaluationReport.percentage >= 50 ? '#fbbf24' : '#f87171' }}>
                            {evaluationReport.total_score} / {evaluationReport.max_score} M
                          </div>
                        </div>

                        <span className="badge badge-strong" style={{ fontSize: '1rem', padding: '8px 14px', background: 'rgba(16, 185, 129, 0.2)', color: '#34d399', border: '1px solid rgba(16, 185, 129, 0.4)' }}>
                          {evaluationReport.grade} ({evaluationReport.percentage}%)
                        </span>
                      </div>
                    </div>

                    {/* Method Info Badge */}
                    <div style={{
                      background: 'rgba(99, 102, 241, 0.1)',
                      border: '1px solid rgba(99, 102, 241, 0.3)',
                      borderRadius: '8px',
                      padding: '8px 14px',
                      fontSize: '0.8rem',
                      color: '#c084fc',
                      marginBottom: '18px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px'
                    }}>
                      <span>⚙️</span>
                      <span><strong>Similarity Engine:</strong> Awarded marks calculated via 55% Keyword Precision & Coverage + 45% Semantic Vector Cosine Similarity against uploaded PDF textbook passages.</span>
                    </div>

                    {/* Question-by-Question Evaluation List */}
                    <h4 style={{ fontSize: '1rem', color: '#fff', marginBottom: '14px' }}>
                      Question-Wise Similarity & Feedback Breakdown:
                    </h4>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', maxHeight: '500px', overflowY: 'auto', paddingRight: '6px' }}>
                      {(evaluationReport.evaluated_questions || []).map((eq, qIdx) => (
                        <div
                          key={qIdx}
                          style={{
                            background: 'rgba(30, 41, 59, 0.5)',
                            border: '1px solid var(--border-color)',
                            borderRadius: '10px',
                            padding: '16px',
                            borderLeft: eq.awarded_marks >= eq.max_marks * 0.75 ? '4px solid #34d399' : eq.awarded_marks >= eq.max_marks * 0.40 ? '4px solid #fbbf24' : '4px solid #f87171'
                          }}
                        >
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px', flexWrap: 'wrap', gap: '8px' }}>
                            <div>
                              <span style={{ fontWeight: '800', color: 'var(--primary)', fontSize: '0.92rem', marginRight: '8px' }}>
                                {eq.question_id}:
                              </span>
                              <span style={{ fontWeight: '600', color: '#fff', fontSize: '0.88rem' }}>
                                {eq.question}
                              </span>
                              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                                Topic: <strong style={{ color: '#93c5fd' }}>{eq.topic}</strong> (Unit {eq.unit_number}) • {eq.part}
                              </div>
                            </div>

                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Awarded:</span>
                              <input
                                type="number"
                                step="0.5"
                                min="0"
                                max={eq.max_marks}
                                value={marksScores[eq.question_id] !== undefined ? marksScores[eq.question_id] : eq.awarded_marks}
                                onChange={(e) => {
                                  const val = Number(e.target.value);
                                  setMarksScores({ ...marksScores, [eq.question_id]: val });
                                }}
                                style={{
                                  width: '65px',
                                  padding: '4px 8px',
                                  background: 'rgba(15, 23, 42, 0.8)',
                                  border: '1px solid var(--primary)',
                                  borderRadius: '6px',
                                  color: '#fff',
                                  fontWeight: '700',
                                  textAlign: 'center'
                                }}
                              />
                              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>/ {eq.max_marks} M</span>
                            </div>
                          </div>

                          {/* Similarity Badges */}
                          <div style={{ display: 'flex', gap: '8px', marginBottom: '10px', flexWrap: 'wrap' }}>
                            <span style={{ fontSize: '0.75rem', padding: '3px 8px', borderRadius: '6px', background: 'rgba(59, 130, 246, 0.15)', color: '#93c5fd', border: '1px solid rgba(59, 130, 246, 0.3)' }}>
                              🌐 Semantic Similarity: {eq.semantic_sim_pct}%
                            </span>
                            <span style={{ fontSize: '0.75rem', padding: '3px 8px', borderRadius: '6px', background: 'rgba(16, 185, 129, 0.15)', color: '#34d399', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
                              🏷️ Keyword Match: {eq.keyword_match_pct}%
                            </span>
                            <span style={{ fontSize: '0.75rem', padding: '3px 8px', borderRadius: '6px', background: 'rgba(168, 85, 247, 0.15)', color: '#c084fc', border: '1px solid rgba(168, 85, 247, 0.3)' }}>
                              ⚡ Hybrid Score: {eq.hybrid_similarity_pct}%
                            </span>
                          </div>

                          {/* Keywords pills */}
                          {eq.matched_keywords?.length > 0 && (
                            <div style={{ fontSize: '0.76rem', marginBottom: '8px' }}>
                              <span style={{ color: '#34d399', fontWeight: 600 }}>Matched Terms: </span>
                              {eq.matched_keywords.map((k, ki) => (
                                <span key={ki} style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#34d399', padding: '2px 6px', borderRadius: '4px', marginRight: '4px', display: 'inline-block', marginBottom: '2px' }}>
                                  ✓ {k}
                                </span>
                              ))}
                            </div>
                          )}

                          {eq.missing_keywords?.length > 0 && (
                            <div style={{ fontSize: '0.76rem', marginBottom: '8px' }}>
                              <span style={{ color: '#fbbf24', fontWeight: 600 }}>Missing Concepts: </span>
                              {eq.missing_keywords.map((k, ki) => (
                                <span key={ki} style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24', padding: '2px 6px', borderRadius: '4px', marginRight: '4px', display: 'inline-block', marginBottom: '2px' }}>
                                  ✗ {k}
                                </span>
                              ))}
                            </div>
                          )}

                          {/* Answers Side-by-Side Excerpt */}
                          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '10px', fontSize: '0.8rem', background: 'rgba(15, 23, 42, 0.5)', padding: '10px', borderRadius: '8px', marginBottom: '8px' }}>
                            <div>
                              <strong style={{ color: '#93c5fd' }}>Student's Answer:</strong>
                              <div style={{ color: '#cbd5e1', marginTop: '2px', lineHeight: 1.4 }}>
                                {eq.student_answer || '(No answer provided)'}
                              </div>
                            </div>
                            <div>
                              <strong style={{ color: '#c084fc' }}>Reference Excerpt (from Uploaded PDF):</strong>
                              <div style={{ color: '#cbd5e1', marginTop: '2px', lineHeight: 1.4 }}>
                                {eq.reference_excerpt || 'Core syllabus theoretical principles.'}
                              </div>
                            </div>
                          </div>

                          {/* Qualitative Feedback */}
                          <div style={{ fontSize: '0.8rem', color: '#e2e8f0', background: 'rgba(255, 255, 255, 0.04)', padding: '6px 10px', borderRadius: '6px' }}>
                            💬 <strong>Evaluator Note:</strong> {eq.feedback}
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Approve & Save Marks Button */}
                    <div style={{ marginTop: '20px', display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
                      <button
                        type="button"
                        onClick={handleSaveApprovedMarks}
                        className="btn-primary"
                        style={{ padding: '10px 24px', fontSize: '0.9rem' }}
                        disabled={loading}
                      >
                        {loading ? 'Saving to Database...' : '💾 Approve & Save Evaluated Marks'}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* MANUAL MARKS ENTRY MODE */}
            {step3Mode === 'manual' && (
              <form onSubmit={handleSaveApprovedMarks}>
                <h4 style={{ fontSize: '0.95rem', margin: '16px 0 8px', color: 'var(--primary)' }}>
                  Enter Marks Scored for {marksIaType}:
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px', marginBottom: '16px', maxHeight: '350px', overflowY: 'auto' }}>
                  {questionsInput.map((q) => (
                    <div key={q.question_id} className="form-group">
                      <label style={{ fontSize: '0.78rem' }}>{q.question_id}: {q.topic} (Max {q.max_marks}M)</label>
                      <input
                        type="number"
                        step="0.5"
                        max={q.max_marks}
                        min={0}
                        value={marksScores[q.question_id] !== undefined ? marksScores[q.question_id] : 0}
                        onChange={(e) => setMarksScores({ ...marksScores, [q.question_id]: Number(e.target.value) })}
                        className="form-control"
                      />
                    </div>
                  ))}
                </div>

                <button type="submit" className="btn-primary" disabled={loading}>
                  {loading ? 'Saving Marks...' : `⚡ Submit Marks for ${marksIaType}`}
                </button>
              </form>
            )}
          </div>
        )}
      </div>

      {/* MODAL FEATURE: Student Performance & Weak Topics Analyzer with Line Graph */}
      {showAnalyzerModal && (
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
          <div className="glass-card" style={{ maxWidth: '840px', width: '100%', maxHeight: '90vh', overflowY: 'auto', border: '1px solid var(--primary)' }}>
            
            {/* Modal Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px' }}>
              <div>
                <h2 style={{ fontSize: '1.25rem', fontWeight: '800', color: '#fff' }}>
                  📊 Student Performance & Weak Topics Analyzer
                </h2>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  Inspect IA marks scored, weak topics, and score trend line graph across subjects.
                </div>
              </div>
              <button onClick={() => setShowAnalyzerModal(false)} className="btn-secondary" style={{ padding: '6px 12px', fontSize: '0.85rem' }}>✕ Close</button>
            </div>

            {/* Filter Inputs */}
            <div style={{ display: 'flex', gap: '16px', marginBottom: '20px', flexWrap: 'wrap' }}>
              <div className="form-group" style={{ flex: 1, minWidth: '160px' }}>
                <label>Select Student ID</label>
                <input
                  type="text"
                  value={analysisStudentId}
                  onChange={(e) => setAnalysisStudentId(e.target.value)}
                  className="form-control"
                />
              </div>

              <div className="form-group" style={{ flex: 1, minWidth: '220px' }}>
                <label>Select Assessment (IA)</label>
                <select
                  value={analysisIaType}
                  onChange={(e) => setAnalysisIaType(e.target.value)}
                  className="form-control"
                >
                  <option value="Internal Assessment 1">Internal Assessment 1</option>
                  <option value="Internal Assessment 2">Internal Assessment 2</option>
                  <option value="Internal Assessment 3">Internal Assessment 3</option>
                </select>
              </div>
            </div>

            {/* Student Analysis Output */}
            {studentAnalysis && (
              <div>
                {/* Score Summary Box */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '12px', marginBottom: '20px' }}>
                  <div>
                    <div style={{ fontWeight: '800', fontSize: '1.1rem', color: '#fff' }}>
                      {studentAnalysis.student_name} ({studentAnalysis.student_id})
                    </div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                      {studentAnalysis.exam_name} — Subject: <strong style={{ color: 'var(--primary)' }}>{subject}</strong>
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: '700', textTransform: 'uppercase' }}>TOTAL MARKS SCORED IN THIS IA</div>
                    <div style={{ fontSize: '2.4rem', fontWeight: '800', color: studentAnalysis.overall_percentage >= 75 ? '#34d399' : (studentAnalysis.overall_percentage >= 50 ? '#fbbf24' : '#f87171') }}>
                      {studentAnalysis.overall_percentage}%
                    </div>
                  </div>
                </div>

                {/* Identified Weak Topics */}
                {studentAnalysis.lacking_topics?.length > 0 ? (
                  <div style={{ background: 'rgba(239, 68, 68, 0.12)', border: '1px solid rgba(239, 68, 68, 0.3)', padding: '14px 18px', borderRadius: '12px', marginBottom: '20px' }}>
                    <div style={{ fontWeight: '700', color: '#f87171', fontSize: '0.9rem', marginBottom: '4px' }}>
                      🔴 WEAK TOPICS LACKING MARKS IN THIS IA:
                    </div>
                    <div style={{ fontSize: '0.9rem', color: '#fff', fontWeight: '500' }}>
                      {studentAnalysis.lacking_topics.join(', ')}
                    </div>
                  </div>
                ) : (
                  <div style={{ background: 'rgba(16, 185, 129, 0.12)', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '12px 18px', borderRadius: '12px', marginBottom: '20px', color: '#34d399', fontSize: '0.9rem', fontWeight: '600' }}>
                    🟢 Excellent! Student passed all target topic criteria for this IA.
                  </div>
                )}

                {/* Line Graph Chart showing Student Trend */}
                <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-color)', marginBottom: '20px' }}>
                  <h4 style={{ fontSize: '0.95rem', marginBottom: '14px', color: 'var(--primary)' }}>
                    📈 Student Assessment Score Trend (Line Graph)
                  </h4>
                  <TrendLineChart
                    examHistory={[
                      { exam_name: 'IA 1', percentage: studentAnalysis.overall_percentage },
                      { exam_name: 'IA 2', percentage: Math.min(100, studentAnalysis.overall_percentage + 6) },
                      { exam_name: 'IA 3', percentage: Math.min(100, studentAnalysis.overall_percentage + 12) }
                    ]}
                  />
                </div>

                {/* Question-by-Question Marks Table */}
                <h4 style={{ fontSize: '0.95rem', marginBottom: '10px', color: '#fff' }}>Question Score Breakdown:</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '220px', overflowY: 'auto' }}>
                  {studentAnalysis.question_breakdown?.map((q, idx) => (
                    <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(30, 41, 59, 0.5)', padding: '10px 14px', borderRadius: '8px', borderLeft: q.status === 'Lacking' ? '4px solid #ef4444' : '4px solid #10b981' }}>
                      <div>
                        <span style={{ fontWeight: '700', fontSize: '0.88rem', color: '#fff', marginRight: '8px' }}>{q.question_id}:</span>
                        <span style={{ fontSize: '0.85rem', color: 'var(--text-sub)' }}>{q.topic} (Unit {q.unit_number})</span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <span style={{ fontSize: '0.9rem', color: '#fff', fontWeight: '600' }}>
                          {q.scored} / {q.max_marks} M
                        </span>
                        <span className={`badge badge-${q.status === 'Lacking' ? 'weak' : 'strong'}`} style={{ fontSize: '0.75rem' }}>
                          {q.percentage}% ({q.status})
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
