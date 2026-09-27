from flask import Blueprint, request, jsonify
from database import db_adapter
from services.mastery_analyzer import MasteryAnalyzer
from services.recommendation_engine import RecommendationEngine

student_bp = Blueprint("student_bp", __name__)


@student_bp.route("/dashboard/<student_id>", methods=["GET"])
def get_student_dashboard(student_id):
    """
    Student Dashboard API:
    Returns question paper topics, topic performance histogram data, lacking topics,
    YouTube Video Lectures, Google Docs study resources, and assigned quizzes.
    """
    subject = request.args.get("subject", "Deep Learning")
    exam_name = request.args.get("exam_name", "Internal Assessment 1")

    student_marks = db_adapter.get_student_marks(student_id=student_id, subject=subject)
    question_papers = db_adapter.get_question_papers(subject=subject)
    units = db_adapter.get_units(subject=subject)

    # Find specified question paper for this exam
    qp = db_adapter.get_question_paper(subject, exam_name)
    if not qp:
        qp_list = [q for q in question_papers if exam_name.lower() in q.get("exam_name", "").lower()]
        qp = qp_list[0] if qp_list else (question_papers[0] if question_papers else {"questions": []})

    # Extract all topics present in the selected question paper
    qp_questions = qp.get("questions", [])
    qp_topics = list(set(q.get("topic") for q in qp_questions if q.get("topic")))

    # Calculate overall mastery and specific IA mastery
    mastery_analysis = MasteryAnalyzer.calculate_student_mastery(student_marks, question_papers, units)

    # Filter marks record for the selected IA
    ia_marks_record = [m for m in student_marks if m.get("exam_name") == exam_name or exam_name.lower() in m.get("exam_name", "").lower()]
    ia_scores = ia_marks_record[0].get("question_scores", {}) if ia_marks_record else {}

    # Calculate IA-specific topic performance for Histogram
    q_map = {q["question_id"]: q for q in qp_questions}
    ia_topic_totals = {}
    
    for q_id, scored in ia_scores.items():
        scored = float(scored)
        q_info = q_map.get(q_id, {"topic": "Core Concept", "max_marks": 5})
        topic = q_info.get("topic", "Core Concept")
        max_m = float(q_info.get("max_marks", 5))

        if topic not in ia_topic_totals:
            ia_topic_totals[topic] = {"scored": 0, "max": 0}
        ia_topic_totals[topic]["scored"] += scored
        ia_topic_totals[topic]["max"] += max_m

    # Histogram data structure for selected IA
    histogram_data = []
    ia_lacking_topics = []

    for t_name in qp_topics:
        tot = ia_topic_totals.get(t_name, {"scored": 0, "max": 10})
        s = tot["scored"]
        m = tot["max"] if tot["max"] > 0 else 10.0
        pct = round((s / m) * 100, 1)

        is_lacking = pct < 50.0
        histogram_data.append({
            "topic": t_name,
            "scored": s,
            "max_marks": m,
            "percentage": pct,
            "status": "Lacking" if is_lacking else "Proficient",
            "color": "#ef4444" if is_lacking else ("#f59e0b" if pct <= 75 else "#10b981")
        })

        if is_lacking:
            ia_lacking_topics.append(t_name)

    target_lacking_topics = ia_lacking_topics if ia_lacking_topics else mastery_analysis.get("weak_topics", [])

    # Generate Recommendations payload
    recommendations = RecommendationEngine.generate_recommendations(
        {"weak_topics": target_lacking_topics, "moderate_topics": mastery_analysis.get("moderate_topics", [])},
        units,
        subject=subject
    )

    # 🔴 Dedicated YouTube Video Lectures & 📄 Google Docs Resources for Lacking Topics
    youtube_resources = []
    google_docs_resources = []

    for t in (target_lacking_topics[:4] or qp_topics[:4]):
        query_str = f"{subject} {t}".replace(" ", "+")
        
        youtube_resources.append({
            "topic": t,
            "title": f"📺 YouTube Video Lecture: {t} Walkthrough",
            "url": f"https://www.youtube.com/results?search_query={query_str}+lecture+tutorial",
            "description": f"Watch visual animated video explanations, derivations, and step-by-step examples for {t}."
        })

        google_docs_resources.append({
            "topic": t,
            "title": f"📄 Google Docs & Study Notes: {t} Guide",
            "url": f"https://www.google.com/search?q={query_str}+notes+pdf+google+docs",
            "description": f"Read curated academic study notes, formulas, and cheatsheets for {t}."
        })

    student_name = student_marks[0].get("student_name", f"Student {student_id}") if student_marks else f"Student {student_id}"

    return jsonify({
        "status": "success",
        "student_id": student_id,
        "student_name": student_name,
        "subject": subject,
        "exam_name": exam_name,
        "qp_topics": qp_topics,
        "histogram_data": histogram_data,
        "ia_lacking_topics": ia_lacking_topics,
        "mastery_analysis": mastery_analysis,
        "recommendations": recommendations,
        "youtube_resources": youtube_resources,
        "google_docs_resources": google_docs_resources
    }), 200


@student_bp.route("/submit-quiz", methods=["POST"])
def submit_quiz():
    data = request.json or {}
    student_id = data.get("student_id", "STU101")
    user_answers = data.get("answers", [])

    correct_count = 0
    total_count = len(user_answers)
    detailed_results = []

    for item in user_answers:
        is_correct = (int(item.get("selected", -1)) == int(item.get("correct", -2)))
        if is_correct:
            correct_count += 1
        detailed_results.append({
            "question": item.get("question"),
            "selected_option": item.get("selected"),
            "correct_option": item.get("correct"),
            "is_correct": is_correct,
            "explanation": item.get("explanation", "")
        })

    score_pct = round((correct_count / total_count) * 100, 1) if total_count > 0 else 0.0

    return jsonify({
        "status": "success",
        "student_id": student_id,
        "total_questions": total_count,
        "correct_answers": correct_count,
        "score_percentage": score_pct,
        "grade_feedback": "Excellent Mastery!" if score_pct >= 80 else ("Good Progress" if score_pct >= 60 else "Review Weak Topics"),
        "detailed_results": detailed_results
    }), 200
