# NeuroLearn AI: Intelligent Student Performance Prediction & Personalized Learning System

NeuroLearn AI is an end-to-end educational platform designed to predict semester examination performance (**Module 1**) and provide granular, topic-level learning recommendations (**Module 2**) by analyzing unit-wise PDFs, question paper mappings, and question-wise student marks.

---

## 🏗️ Project Architecture & Folder Structure

```
neurolearn_ai/
├── backend/
│   ├── app.py                      # Flask Server Entry Point (Port 5000)
│   ├── config.py                   # Global System Configuration & Path Constants
│   ├── database.py                 # MongoDB + Dual In-Memory/JSON Local Store Adapter
│   ├── seed_data.py                # Pre-populates Demo Data for DL, ML, MLOps, NLP & CCAD
│   ├── requirements.txt            # Python Dependencies
│   ├── services/
│   │   ├── pdf_processor.py        # PDF Parser (PyMuPDF + Gemini LLM fallback)
│   │   ├── mastery_analyzer.py     # Topic Mastery & Gap Analysis Engine
│   │   └── recommendation_engine.py# AI Adaptive Quiz & Study Plan Generator
│   ├── routes/
│   │   ├── teacher_routes.py       # PDF Upload, Question Mapping & Student Marks APIs
│   │   ├── student_routes.py       # Student Mastery, Study Plan & Quiz APIs
│   │   └── prediction_routes.py    # Module 1 Feed Forward Neural Network Prediction API
│   ├── data/                       # Local JSON Storage (store.json)
│   └── uploads/                    # Uploaded Unit PDF Files
│
└── frontend/                       # React + Vite Modern Web Application
    ├── index.html
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── App.jsx                 # Main Application Layout & Subject State
        ├── main.jsx                # React Entry Point
        ├── index.css               # Design System, Glassmorphism & Micro-animations
        ├── components/
        |   ├── Navbar.jsx          # Header with Module & Role Navigation
        |   ├── Module1Predictor.jsx# FFNN Semester Prediction Interface
        |   ├── StudentDashboard.jsx# Topic Mastery Radar/Charts & Recommendations
        |   ├── TeacherDashboard.jsx# PDF Upload, Question Mapping & Class Analytics
        |   ├── QuizModal.jsx       # Interactive AI Adaptive Quiz Component
        |   └── AnalyticsChart.jsx  # Chart.js Visualizations (Bar & Line)
        └── services/
            └── api.js              # API Client (HTTP REST Calls)
```

---

## ⚡ Quick Start Guide

### 1. Start the Flask Backend Server
In your terminal, navigate to the project directory and run:

```bash
cd D:\.gemini\antigravity\scratch\neurolearn_ai
python backend/app.py
```
*The backend server will launch at `http://localhost:5000`.*

---

### 2. Start the Frontend React Web Dashboard
Open a second terminal window and run:

```bash
cd D:\.gemini\antigravity\scratch\neurolearn_ai\frontend
npm install
npm run dev
```
*Open `http://localhost:3000` in your web browser.*

---

## 🎯 Key Features Demonstrated

1. **Module 1: Student Performance Prediction**
   - Inputs: IA1, IA2, Assignment, Quiz marks, Attendance %, and Previous GPA.
   - Output: Predicted Semester Score (e.g. `85.4 / 100`), Expected Grade (`A+`), and Performance Insights.

2. **Module 2: Personalized Learning Recommendation System**
   - **Teacher Dashboard**: Upload unit PDFs, define question paper topic mappings ($Q1 \rightarrow \text{CNN}$), submit student scores, and inspect class-wide difficult topics & at-risk student alerts.
   - **Student Dashboard**: Real-time topic mastery breakdown (Weak `<50%`, Moderate `50-75%`, Strong `>75%`), interactive Chart.js graphs, personalized unit study schedule, and high-priority practice questions.
   - **Adaptive AI Quiz Engine**: Interactive quiz modal offering dynamic questions targeting the student's exact weak topics with instant score feedback.
