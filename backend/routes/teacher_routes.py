from flask import Blueprint, request, jsonify
import os
from werkzeug.utils import secure_filename

from config import UPLOADS_DIR, SUBJECTS
from database import db_adapter
from services.pdf_processor import PDFProcessor
from services.mastery_analyzer import MasteryAnalyzer
from services.rag_engine import rag_engine
from services.question_generator import QuestionGenerator
from services.answer_evaluator import AnswerSheetEvaluator

teacher_bp = Blueprint("teacher_bp", __name__)


@teacher_bp.route("/upload-unit", methods=["POST"])
def upload_unit():
    """
    Teacher Step 1: Upload Unit PDF & Extract Topics.
    Extracts topics, subtopics, key concepts & indexes PDF text chunks.
    """
    subject = request.form.get("subject", "Deep Learning")
    unit_number = int(request.form.get("unit_number", 1))

    pdf_file = request.files.get("unit_pdf")
    pdf_path = None
    raw_text = request.form.get("raw_text", None)

    if pdf_file and pdf_file.filename:
        filename = secure_filename(f"{subject}_Unit{unit_number}_{pdf_file.filename}")
        pdf_path = os.path.join(UPLOADS_DIR, filename)
        pdf_file.save(pdf_path)

    # Analyze PDF content & extract topics + questions
    extracted_data = PDFProcessor.analyze_unit_content(pdf_path, subject, unit_number, raw_text)

    # Convert PDF page text to string
    page_text = PDFProcessor.extract_text_from_pdf(pdf_path) if pdf_path else ""
    extracted_str_text = page_text if page_text else (raw_text or "")

    # Index text chunks into RAG Vector Store
    indexed_chunks = rag_engine.index_pdf_content(subject, unit_number, extracted_str_text, extracted_data.get("topics", []))
    extracted_data["indexed_chunks"] = indexed_chunks
    extracted_data["extracted_text"] = extracted_str_text
    extracted_data["pdf_path"] = pdf_path if pdf_path else ""

    # Save extracted unit to Database
    db_adapter.save_unit(extracted_data)

    return jsonify({
        "status": "success",
        "message": f"Unit {unit_number} PDF processed & topics extracted successfully for {subject}.",
        "unit_data": extracted_data
    }), 201


@teacher_bp.route("/unit-topics", methods=["GET"])
def get_unit_topics():
    """
    Get extracted topics, subtopics, key concepts & important questions for a specific unit.
    """
    subject = request.args.get("subject", "Deep Learning")
    unit_number = int(request.args.get("unit_number", 1))

    units = db_adapter.get_units(subject=subject)
    unit_doc = next((u for u in units if int(u.get("unit_number", 0)) == unit_number), None)

    if not unit_doc:
        unit_doc = PDFProcessor.analyze_unit_content(None, subject, unit_number)

    important_questions = unit_doc.get("important_questions", [])
    if not important_questions:
        important_questions = QuestionGenerator.generate_important_questions_for_unit(
            unit_doc.get("topics", []),
            unit_number,
            subject
        )

    return jsonify({
        "status": "success",
        "subject": subject,
        "unit_number": unit_number,
        "unit_title": unit_doc.get("unit_title", f"Unit {unit_number}"),
        "topics": unit_doc.get("topics", []),
        "subtopics": unit_doc.get("subtopics", []),
        "key_concepts": unit_doc.get("key_concepts", []),
        "important_questions": important_questions
    }), 200


@teacher_bp.route("/generate-paper-from-pdf", methods=["POST"])
def generate_paper_from_pdf():
    """
    Step 2: Auto Question Paper Preparation Engine.
    Generates exact Blueprint paper based on Assessment Type (IA 1, IA 2, IA 3) and extracted PDF unit topics.
    """
    data = request.json or {}
    subject = data.get("subject", "Deep Learning")
    ia_type = data.get("ia_type", "IA 1")
    provided_topics = data.get("topics", [])
    current_unit = int(data.get("unit_number", 1))

    # Retrieve all 5 unit docs from DB
    units = db_adapter.get_units(subject=subject)
    units_dict = {int(u.get("unit_number", 1)): u for u in units}

    # If extracted topics were passed, update the targeted unit in units_dict
    if provided_topics:
        if current_unit not in units_dict:
            units_dict[current_unit] = {"unit_number": current_unit, "topics": provided_topics}
        else:
            units_dict[current_unit]["topics"] = provided_topics

    # Strictly prioritize extracted topics from the uploaded PDF
    primary_topics = provided_topics if provided_topics else units_dict.get(current_unit, {}).get("topics", [])
    qp_doc = QuestionGenerator.generate_blueprint_paper(subject, ia_type, units_dict, primary_topics=primary_topics, current_unit=current_unit)

    # Save generated paper to database so teacher can edit/modify
    db_adapter.save_question_paper(qp_doc)

    return jsonify({
        "status": "success",
        "message": f"Blueprint Question Paper prepared for {ia_type} ({subject}) using extracted topics!",
        "question_paper": qp_doc
    }), 201


@teacher_bp.route("/upload-question-paper", methods=["POST"])
def upload_question_paper():
    data = request.json or {}
    subject = data.get("subject", "Deep Learning")
    exam_name = data.get("exam_name", "Internal Assessment 1")
    unit_number = int(data.get("unit_number", 1))
    questions = data.get("questions", [])

    qp_data = {
        "subject": subject,
        "exam_name": exam_name,
        "unit_number": unit_number,
        "questions": questions
    }

    db_adapter.save_question_paper(qp_data)

    return jsonify({
        "status": "success",
        "message": f"Question paper mapping saved for {exam_name} ({subject}).",
        "question_paper": qp_data
    }), 201


@teacher_bp.route("/question-paper", methods=["GET"])
def get_question_paper():
    """
    Get question paper for subject and exam_name or ia_type.
    If not already in DB, auto-generates the blueprint paper.
    """
    subject = request.args.get("subject", "Deep Learning")
    exam_name = request.args.get("exam_name", "Internal Assessment 1")
    ia_type = request.args.get("ia_type", "IA 1")

    # Match canonical exam name
    if "1" in ia_type or "1" in exam_name:
        target_exam = "Internal Assessment 1"
        canonical_ia = "IA 1"
    elif "2" in ia_type or "2" in exam_name:
        target_exam = "Internal Assessment 2"
        canonical_ia = "IA 2"
    else:
        target_exam = "Internal Assessment 3 / Model Exam"
        canonical_ia = "IA 3"

    qp = db_adapter.get_question_paper(subject, target_exam)
    if not qp or not qp.get("questions"):
        # Auto-generate blueprint from database units or default topics
        units = db_adapter.get_units(subject=subject)
        units_dict = {int(u.get("unit_number", 1)): u for u in units}
        qp = QuestionGenerator.generate_blueprint_paper(subject, canonical_ia, units_dict)
        db_adapter.save_question_paper(qp)

    return jsonify({
        "status": "success",
        "exam_name": target_exam,
        "ia_type": canonical_ia,
        "question_paper": qp
    }), 200



@teacher_bp.route("/evaluate-answer-sheet", methods=["POST"])
def evaluate_answer_sheet():
    """
    Teacher Step 3: Automated Answer Sheet Evaluation Engine.
    Compares the uploaded student answer sheet against authoritative PDF reference content
    using both Semantic Vector Search and Keyword Search.
    """
    if request.content_type and "multipart/form-data" in request.content_type:
        subject = request.form.get("subject", "Deep Learning")
        exam_name = request.form.get("exam_name", "Internal Assessment 1")
        student_id = request.form.get("student_id", "STU101")
        student_name = request.form.get("student_name", "John Doe")
        raw_text = request.form.get("raw_text", "")
        file = request.files.get("answer_pdf")
        file_bytes = file.read() if file else None
    else:
        data = request.json or {}
        subject = data.get("subject", "Deep Learning")
        exam_name = data.get("exam_name", "Internal Assessment 1")
        student_id = data.get("student_id", "STU101")
        student_name = data.get("student_name", "John Doe")
        raw_text = data.get("raw_text", "")
        file_bytes = None

    result = AnswerSheetEvaluator.evaluate_answer_sheet(
        subject=subject,
        exam_name=exam_name,
        student_id=student_id,
        student_name=student_name,
        raw_text=raw_text,
        file_bytes=file_bytes
    )

    return jsonify(result), 200


@teacher_bp.route("/upload-marks", methods=["POST"])
def upload_marks():
    data = request.json or {}
    subject = data.get("subject", "Deep Learning")
    exam_name = data.get("exam_name", "Internal Assessment 1")
    student_id = data.get("student_id", "STU101")
    student_name = data.get("student_name", "John Doe")
    question_scores = data.get("question_scores", {})
    total_score = data.get("total_score")
    max_score = data.get("max_score", 50.0)
    percentage = data.get("percentage")
    grade = data.get("grade")
    evaluated_questions = data.get("evaluated_questions", [])

    marks_data = {
        "subject": subject,
        "exam_name": exam_name,
        "student_id": student_id,
        "student_name": student_name,
        "question_scores": question_scores,
        "total_score": total_score if total_score is not None else round(sum(question_scores.values()), 1),
        "max_score": max_score,
        "percentage": percentage if percentage is not None else round((sum(question_scores.values()) / max(1.0, max_score)) * 100, 1),
        "grade": grade or "A",
        "evaluated_questions": evaluated_questions
    }

    db_adapter.save_student_marks(marks_data)

    return jsonify({
        "status": "success",
        "message": f"Marks saved for student {student_id} ({student_name}). RAG materials & weak topic quiz assigned!",
        "marks_record": marks_data
    }), 201


@teacher_bp.route("/student-ia-analysis", methods=["GET"])
def get_student_ia_analysis():
    """
    Teacher Feature: Analyzes a student's performance on a specified IA (IA 1, IA 2, IA 3)
    and highlights exact topics where the student is lacking marks.
    """
    subject = request.args.get("subject", "Deep Learning")
    student_id = request.args.get("student_id", "STU101")
    exam_name = request.args.get("exam_name", "Internal Assessment 1")

    all_marks = db_adapter.get_student_marks(student_id=student_id, subject=subject)
    ia_marks = [m for m in all_marks if m.get("exam_name") == exam_name or exam_name.lower() in m.get("exam_name", "").lower()]
    
    qp = db_adapter.get_question_paper(subject, exam_name)
    if not qp:
        qps = db_adapter.get_question_papers(subject=subject)
        qp = qps[0] if qps else {"questions": []}

    q_mappings = {q["question_id"]: q for q in qp.get("questions", [])}

    scores = ia_marks[0].get("question_scores", {}) if ia_marks else {}
    student_name = ia_marks[0].get("student_name", f"Student {student_id}") if ia_marks else f"Student {student_id}"

    lacking_topics = []
    question_breakdown = []

    total_obtained = 0
    total_max = 0

    for q_id, scored in scores.items():
        scored = float(scored)
        q_info = q_mappings.get(q_id, {"topic": "Core Topic", "max_marks": 5, "unit_number": 1})
        max_m = float(q_info.get("max_marks", 5))
        topic = q_info.get("topic", "Core Topic")
        pct = round((scored / max_m) * 100, 1) if max_m > 0 else 0.0

        total_obtained += scored
        total_max += max_m

        is_lacking = pct < 50.0
        question_breakdown.append({
            "question_id": q_id,
            "topic": topic,
            "scored": scored,
            "max_marks": max_m,
            "percentage": pct,
            "status": "Lacking" if is_lacking else "Proficient",
            "unit_number": q_info.get("unit_number", 1)
        })

        if is_lacking and topic not in lacking_topics:
            lacking_topics.append(topic)

    overall_pct = round((total_obtained / total_max) * 100, 1) if total_max > 0 else 0.0

    return jsonify({
        "status": "success",
        "student_id": student_id,
        "student_name": student_name,
        "subject": subject,
        "exam_name": exam_name,
        "overall_percentage": overall_pct,
        "lacking_topics": lacking_topics,
        "question_breakdown": question_breakdown
    }), 200


@teacher_bp.route("/class-analytics", methods=["GET"])
def get_class_analytics():
    subject = request.args.get("subject", "Deep Learning")

    all_marks = db_adapter.get_student_marks(subject=subject)
    qps = db_adapter.get_question_papers(subject=subject)
    units = db_adapter.get_units(subject=subject)

    analytics = MasteryAnalyzer.calculate_class_analytics(all_marks, qps, units)

    return jsonify({
        "status": "success",
        "subject": subject,
        "analytics": {
            "total_students": analytics.get("total_students", 0),
            "class_average_pct": analytics.get("class_average_pct", 0),
            "at_risk_students": analytics.get("at_risk_students", []),
            "student_summaries": analytics.get("student_summaries", [])
        }
    }), 200
