const API_BASE = "http://localhost:5000/api";

export async function loginUser(role, username, password) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ role, username, password })
  });
  return res.json();
}

export async function fetchSubjects() {
  const res = await fetch(`${API_BASE}/subjects`);
  return res.json();
}

export async function predictPerformance(payload) {
  const res = await fetch(`${API_BASE}/prediction/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  return res.json();
}

export async function uploadUnitPDF(formData) {
  const res = await fetch(`${API_BASE}/teacher/upload-unit`, {
    method: "POST",
    body: formData
  });
  return res.json();
}

export async function generatePaperFromPDF(subject, iaType, topics = [], unitNumber = 1) {
  const res = await fetch(`${API_BASE}/teacher/generate-paper-from-pdf`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ subject, ia_type: iaType, topics, unit_number: unitNumber })
  });
  return res.json();
}

export async function fetchStudentIAAnalysis(subject, studentId, examName) {
  const res = await fetch(`${API_BASE}/teacher/student-ia-analysis?subject=${encodeURIComponent(subject)}&student_id=${encodeURIComponent(studentId)}&exam_name=${encodeURIComponent(examName)}`);
  return res.json();
}

export async function fetchUnitTopics(subject, unitNumber) {
  const res = await fetch(`${API_BASE}/teacher/unit-topics?subject=${encodeURIComponent(subject)}&unit_number=${unitNumber}`);
  return res.json();
}

export async function uploadQuestionPaper(payload) {
  const res = await fetch(`${API_BASE}/teacher/upload-question-paper`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  return res.json();
}

export async function fetchQuestionPaper(subject, examName, iaType) {
  const params = new URLSearchParams({
    subject: subject || 'Deep Learning',
    exam_name: examName || 'Internal Assessment 1',
    ia_type: iaType || 'IA 1'
  });
  const res = await fetch(`${API_BASE}/teacher/question-paper?${params.toString()}`);
  return res.json();
}

export async function uploadStudentMarks(payload) {
  const res = await fetch(`${API_BASE}/teacher/upload-marks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  return res.json();
}

export async function evaluateStudentAnswerSheet(data) {
  const isFormData = data instanceof FormData;
  const res = await fetch(`${API_BASE}/teacher/evaluate-answer-sheet`, {
    method: "POST",
    headers: isFormData ? undefined : { "Content-Type": "application/json" },
    body: isFormData ? data : JSON.stringify(data)
  });
  return res.json();
}

export async function fetchClassAnalytics(subject) {
  const res = await fetch(`${API_BASE}/teacher/class-analytics?subject=${encodeURIComponent(subject)}`);
  return res.json();
}

export async function fetchStudentDashboard(studentId, subject, examName = "Internal Assessment 1") {
  const res = await fetch(`${API_BASE}/student/dashboard/${studentId}?subject=${encodeURIComponent(subject)}&exam_name=${encodeURIComponent(examName)}`);
  return res.json();
}

export async function submitAdaptiveQuiz(payload) {
  const res = await fetch(`${API_BASE}/student/submit-quiz`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  return res.json();
}

// Module 3 Placement API Methods
export async function analyzePlacementProfile(payload) {
  const res = await fetch(`${API_BASE}/placement/analyze-profile`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  return res.json();
}

export async function analyzeResume(payload) {
  const res = await fetch(`${API_BASE}/placement/analyze-resume`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  return res.json();
}

export async function uploadResumePDF(formData) {
  const res = await fetch(`${API_BASE}/placement/upload-resume-pdf`, {
    method: "POST",
    body: formData
  });
  return res.json();
}

export async function fetchJobMatch(payload) {
  const res = await fetch(`${API_BASE}/placement/job-match`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  return res.json();
}

export async function fetchPlacementPrepQuestions(targetRole = "ML Engineer") {
  const res = await fetch(`${API_BASE}/placement/prep-questions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ target_role: targetRole })
  });
  return res.json();
}

export async function evaluateMockInterview(payload) {
  const res = await fetch(`${API_BASE}/placement/evaluate-interview`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  return res.json();
}

// Admin API Methods
export async function fetchAdminOverview() {
  const res = await fetch(`${API_BASE}/admin/overview`);
  return res.json();
}

export async function fetchAdminUnits() {
  const res = await fetch(`${API_BASE}/admin/units`);
  return res.json();
}

export async function fetchAdminQuestionPapers() {
  const res = await fetch(`${API_BASE}/admin/question-papers`);
  return res.json();
}

export async function fetchAdminStudents() {
  const res = await fetch(`${API_BASE}/admin/students`);
  return res.json();
}

export async function deleteAdminUnit(subject, unitNumber) {
  const res = await fetch(`${API_BASE}/admin/delete-unit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ subject, unit_number: unitNumber })
  });
  return res.json();
}

