from flask import Blueprint, request, jsonify
import re
import os
from services.pdf_processor import PDFProcessor

placement_bp = Blueprint("placement_bp", __name__)

ROLE_SKILL_DATABASE = {
    "Software Developer": {
        "required_skills": ["Python", "Java", "C++", "DSA", "SQL", "Git", "OOP", "System Design"],
        "roadmap": ["Programming Fundamentals (Python/Java)", "Data Structures & Algorithms (DSA)", "Object-Oriented Programming (OOP)", "Database Management (SQL)", "Version Control (Git)", "System Design Principles"]
    },
    "Data Scientist": {
        "required_skills": ["Python", "SQL", "Statistics", "Machine Learning", "Data Visualization", "Deep Learning", "Pandas", "Scikit-Learn"],
        "roadmap": ["Python Programming", "Statistics & Linear Algebra", "SQL & Data Extraction", "Exploratory Data Analysis (Pandas)", "Machine Learning (Scikit-Learn)", "Deep Learning (TensorFlow/PyTorch)"]
    },
    "ML Engineer": {
        "required_skills": ["Python", "SQL", "Machine Learning", "Deep Learning", "PyTorch", "Docker", "MLOps", "Model Deployment"],
        "roadmap": ["Python", "SQL", "Machine Learning", "Deep Learning", "PyTorch", "Docker", "MLOps & Model Deployment"]
    },
    "Data Analyst": {
        "required_skills": ["SQL", "Python", "Excel", "PowerBI", "Tableau", "Statistics", "Data Cleaning"],
        "roadmap": ["Advanced Excel", "SQL Queries & Joins", "Python for Data Analysis (Pandas)", "Data Visualization (PowerBI/Tableau)", "Business Intelligence & Reporting"]
    },
    "Cloud Engineer": {
        "required_skills": ["Linux", "Networking", "AWS", "Azure", "Docker", "Kubernetes", "Terraform", "CI/CD"],
        "roadmap": ["Linux System Administration", "Computer Networking", "AWS / Azure Cloud Fundamentals", "Containerization (Docker)", "Orchestration (Kubernetes)", "Infrastructure as Code (Terraform)"]
    },
    "DevOps Engineer": {
        "required_skills": ["Linux", "Python", "Git", "Docker", "Kubernetes", "CI/CD", "Terraform", "Monitoring (Prometheus)"],
        "roadmap": ["Linux & Bash Scripting", "Version Control (Git)", "CI/CD Automation", "Docker & Containerization", "Kubernetes Orchestration", "Monitoring & Telemetry"]
    }
}


@placement_bp.route("/analyze-profile", methods=["POST"])
def analyze_profile():
    data = request.json or {}
    cgpa = float(data.get("cgpa", 8.0))
    student_skills = [s.strip().lower() for s in data.get("skills", ["python", "machine learning", "sql", "deep learning"])]
    target_role = data.get("target_role", "ML Engineer")

    suitability_scores = []
    
    for role_name, req in ROLE_SKILL_DATABASE.items():
        req_skills = req["required_skills"]
        matched = [r for r in req_skills if r.lower() in student_skills]
        missing = [r for r in req_skills if r.lower() not in student_skills]

        skill_score = (len(matched) / len(req_skills)) * 80 if req_skills else 0
        cgpa_score = min(20, (cgpa / 10.0) * 20)
        total_suitability = round(skill_score + cgpa_score, 1)

        suitability_scores.append({
            "role": role_name,
            "suitability_score": total_suitability,
            "matched_skills": matched,
            "missing_skills": missing,
            "roadmap": req["roadmap"]
        })

    suitability_scores.sort(key=lambda x: x["suitability_score"], reverse=True)
    target_info = next((s for s in suitability_scores if s["role"] == target_role), suitability_scores[0])
    readiness_score = round(target_info["suitability_score"], 1)

    return jsonify({
        "status": "success",
        "cgpa": cgpa,
        "target_role": target_role,
        "readiness_score": readiness_score,
        "suitability_scores": suitability_scores,
        "target_skill_gap": {
            "role": target_info["role"],
            "matched": target_info["matched_skills"],
            "missing": target_info["missing_skills"],
            "roadmap": target_info["roadmap"]
        }
    }), 200


@placement_bp.route("/analyze-resume", methods=["POST"])
def analyze_resume():
    data = request.json or {}
    resume_text = data.get("resume_text", "")
    target_role = data.get("target_role", "ML Engineer")

    role_req = ROLE_SKILL_DATABASE.get(target_role, ROLE_SKILL_DATABASE["ML Engineer"])["required_skills"]

    found_skills = []
    missing_skills = []

    for sk in role_req:
        if re.search(r'\b' + re.escape(sk) + r'\b', resume_text, re.I):
            found_skills.append(sk)
        else:
            missing_skills.append(sk)

    ats_score = round((len(found_skills) / len(role_req)) * 100, 1) if role_req else 75.0

    improvements = []
    if "Docker" in missing_skills or "MLOps" in missing_skills:
        improvements.append("Add containerization and model deployment keywords (Docker, MLOps, CI/CD).")
    if "PyTorch" in missing_skills or "Deep Learning" in missing_skills:
        improvements.append("Highlight deep learning framework projects (PyTorch/TensorFlow).")
    if ats_score < 70:
        improvements.append("Quantify project impact with metric achievements (e.g. 'Improved accuracy by 15%').")

    return jsonify({
        "status": "success",
        "ats_score": ats_score,
        "found_skills": found_skills,
        "missing_skills": missing_skills,
        "improvements": improvements
    }), 200


# ATS PDF File Upload Endpoint
@placement_bp.route("/upload-resume-pdf", methods=["POST"])
def upload_resume_pdf():
    if "resume_file" not in request.files:
        return jsonify({"error": "No resume PDF file uploaded"}), 400

    file = request.files["resume_file"]
    target_role = request.form.get("target_role", "ML Engineer")

    temp_path = os.path.join("uploads", file.filename)
    os.makedirs("uploads", exist_ok=True)
    file.save(temp_path)

    try:
        chunks = PDFProcessor.extract_text_from_pdf(temp_path)
        extracted_text = "\n".join(c.text for c in chunks)
        if not extracted_text.strip():
            extracted_text = "Sample resume content fallback text"
    except Exception as err:
        print(f"[Placement] PDF extract warning: {err}")
        extracted_text = ""

    if os.path.exists(temp_path):
        os.remove(temp_path)

    role_req = ROLE_SKILL_DATABASE.get(target_role, ROLE_SKILL_DATABASE["ML Engineer"])["required_skills"]

    found_skills = []
    missing_skills = []

    for sk in role_req:
        if re.search(r'\b' + re.escape(sk) + r'\b', extracted_text, re.I):
            found_skills.append(sk)
        else:
            missing_skills.append(sk)

    ats_score = round((len(found_skills) / len(role_req)) * 100, 1) if role_req else 75.0

    improvements = [
        "Include quantifiable project results (e.g. 'Reduced latency by 20%').",
        f"Add missing keywords for {target_role}: {', '.join(missing_skills[:3]) if missing_skills else 'None'}."
    ]

    return jsonify({
        "status": "success",
        "filename": file.filename,
        "extracted_text_snippet": extracted_text[:300] + "...",
        "ats_score": ats_score,
        "found_skills": found_skills,
        "missing_skills": missing_skills,
        "improvements": improvements
    }), 200


@placement_bp.route("/job-match", methods=["POST"])
def job_match():
    data = request.json or {}
    student_skills = [s.strip().lower() for s in data.get("skills", ["python", "machine learning", "sql", "deep learning"])]

    job_listings = [
        {"job_title": "AI / ML Intern", "company": "TechCorp AI", "location": "Remote / Bengaluru", "required_skills": ["Python", "Machine Learning", "Deep Learning", "PyTorch", "Docker"], "stipend": "₹35,000 / month"},
        {"job_title": "Associate Data Scientist", "company": "Analytics Lab", "location": "Hyderabad", "required_skills": ["Python", "SQL", "Statistics", "Machine Learning", "Pandas"], "stipend": "₹8.5 LPA"},
        {"job_title": "Junior MLOps Engineer", "company": "CloudScale Systems", "location": "Chennai / Remote", "required_skills": ["Python", "Docker", "Kubernetes", "MLOps", "Git"], "stipend": "₹9.0 LPA"},
        {"job_title": "Software Development Engineer (SDE-1)", "company": "Innovate Solutions", "location": "Pune", "required_skills": ["Java", "DSA", "SQL", "System Design", "Git"], "stipend": "₹10.0 LPA"}
    ]

    matched_jobs = []
    for job in job_listings:
        req = job["required_skills"]
        m_skills = [s for s in req if s.lower() in student_skills]
        miss_skills = [s for s in req if s.lower() not in student_skills]
        match_pct = round((len(m_skills) / len(req)) * 100, 1)

        matched_jobs.append({
            "job_title": job["job_title"],
            "company": job["company"],
            "location": job["location"],
            "stipend": job["stipend"],
            "match_percentage": match_pct,
            "matched_skills": m_skills,
            "missing_skills": miss_skills
        })

    matched_jobs.sort(key=lambda x: x["match_percentage"], reverse=True)
    return jsonify({"status": "success", "jobs": matched_jobs}), 200


@placement_bp.route("/prep-questions", methods=["POST"])
def prep_questions():
    data = request.json or {}
    target_role = data.get("target_role", "ML Engineer")

    # Role-tailored question bank
    question_bank = {
        "ML Engineer": [
            {"question": "How do you detect and mitigate Data Drift in production MLOps pipelines?", "answer": "Using Kolmogorov-Smirnov statistical drift tests and Prometheus telemetry.", "explanation": "Data drift occurs when input feature distributions shift relative to training data."},
            {"question": "Explain Monte Carlo policy evaluation vs Temporal Difference (TD) learning.", "answer": "Monte Carlo requires complete episode termination; TD updates bootstrapped per step.", "explanation": "Monte Carlo is unbiased with higher variance; TD updates online with lower variance."},
            {"question": "What is the role of Docker and containerization in machine learning deployments?", "answer": "Ensures reproducible runtime environments and dependency isolation.", "explanation": "Containers bundle code, model artifacts, and CUDA/CUDNN libraries into portable images."}
        ],
        "Software Developer": [
            {"question": "How do you detect a loop in a Linked List in O(N) time and O(1) memory?", "answer": "Floyd's Cycle Detection Algorithm (Slow and Fast Pointer)", "explanation": "Move slow pointer by 1 step and fast pointer by 2 steps. If they meet, a cycle exists."},
            {"question": "What is the difference between REST and gRPC microservice APIs?", "answer": "REST uses HTTP JSON payload; gRPC uses HTTP/2 Protocol Buffers.", "explanation": "gRPC provides strongly typed binary serialization and bidirectional streaming."}
        ],
        "Data Scientist": [
            {"question": "Explain Bias-Variance Tradeoff and how L1/L2 regularization affects it.", "answer": "High bias causes underfitting; high variance causes overfitting. Regularization constrains weights.", "explanation": "L1 (Lasso) performs feature selection by zeroing weights; L2 (Ridge) shrinks weights smoothly."},
            {"question": "How does Precision differ from Recall, and when would you optimize for Recall?", "answer": "Recall measures true positives out of actual positives. Optimize Recall in medical diagnosis.", "explanation": "Precision = TP/(TP+FP); Recall = TP/(TP+FN). False negatives carry high risk in medical screening."}
        ],
        "Data Analyst": [
            {"question": "What is the difference between WHERE and HAVING clauses in SQL?", "answer": "WHERE filters individual rows before grouping; HAVING filters aggregated groups.", "explanation": "WHERE cannot aggregate functions like SUM/AVG; HAVING is evaluated post-GROUP BY."},
            {"question": "How do Window Functions (e.g. ROW_NUMBER, RANK) differ from GROUP BY?", "answer": "Window functions retain original row details while computing aggregate metrics.", "explanation": "GROUP BY collapses rows; window functions keep all rows intact alongside partition calculations."}
        ],
        "Cloud Engineer": [
            {"question": "Explain the difference between AWS Security Groups and Network ACLs (NACLs).", "answer": "Security Groups are stateful per instance; NACLs are stateless per subnet.", "explanation": "Security Groups automatically allow return traffic; NACLs require explicit inbound/outbound rules."},
            {"question": "What is Infrastructure as Code (IaC) and how does Terraform manage state?", "answer": "IaC defines infrastructure declaratively; Terraform tracks resources via `.tfstate`.", "explanation": "Terraform compares actual cloud infrastructure against state file to compute execution plans."}
        ],
        "DevOps Engineer": [
            {"question": "Explain Blue-Green deployment strategy vs Canary deployment.", "answer": "Blue-Green switches 100% traffic instantly; Canary gradually routes a small percentage.", "explanation": "Canary mitigates risk by testing production traffic on a subset of users before full rollout."},
            {"question": "How does Kubernetes handle self-healing for crashed pods?", "answer": "Kubelet monitors pod liveness probes and automatically restarts failing containers.", "explanation": "ReplicaSets reconcile desired vs current running pod counts."}
        ]
    }

    questions = question_bank.get(target_role, question_bank["ML Engineer"])
    return jsonify({"status": "success", "target_role": target_role, "questions": questions}), 200


@placement_bp.route("/evaluate-interview", methods=["POST"])
def evaluate_interview():
    data = request.json or {}
    user_answer = data.get("user_answer", "")
    target_role = data.get("target_role", "ML Engineer")
    question_idx = int(data.get("question_idx", 0))

    interview_questions = [
        "Explain how you would deploy a Deep Learning model to production and monitor data drift.",
        "How do you approach hyperparameter tuning and model optimization under latency constraints?",
        "Describe a challenging technical project you built, detailing your architectural choices and performance results.",
        "What strategies do you use to prevent model overfitting when working with small datasets?"
    ]

    words = len(user_answer.split())
    has_keywords = any(kw in user_answer.lower() for kw in ["gradient", "loss", "model", "data", "architecture", "optimization", "algorithm", "python", "sql", "accuracy", "docker", "pipeline"])

    score = 65
    if words > 20:
        score += 20
    if has_keywords:
        score += 12

    score = min(98, score)
    next_idx = (question_idx + 1) % len(interview_questions)

    return jsonify({
        "status": "success",
        "score": score,
        "technical_depth": "High" if score >= 80 else "Moderate",
        "communication_rating": "Strong" if words >= 20 else "Needs Detail",
        "feedback": ["Great technical depth and clear structure."] if score >= 75 else ["Add specific framework terms and architectural metrics."],
        "next_question_idx": next_idx,
        "next_question": interview_questions[next_idx]
    }), 200
