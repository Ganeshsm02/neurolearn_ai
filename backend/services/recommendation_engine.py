from services.pdf_processor import PDFProcessor
from services.rag_engine import rag_engine
from services.question_generator import QuestionGenerator

class RecommendationEngine:
    """Generates RAG-retrieved learning materials, dynamic weak subject quizzes, and study plans."""

    @staticmethod
    def generate_recommendations(mastery_analysis, units_data, subject="Deep Learning"):
        """
        Generates personalized recommendation payload including RAG textbook excerpts & assigned quizzes for weak topics.
        """
        weak_topics = mastery_analysis.get("weak_topics", [])
        moderate_topics = mastery_analysis.get("moderate_topics", [])

        # 1. RAG Vector Retrieval: Fetch exact PDF textbook passages matching student weak topics
        rag_materials = rag_engine.retrieve_rag_materials(subject, weak_topics, top_k=4)

        # 2. Ensure units 1 to 5 exist in units_data
        existing_unit_nums = {u.get("unit_number") for u in units_data}
        all_units = list(units_data)

        for u_num in range(1, 6):
            if u_num not in existing_unit_nums:
                default_unit = PDFProcessor.analyze_unit_content(None, subject, u_num)
                all_units.append(default_unit)

        all_units.sort(key=lambda x: x.get("unit_number", 1))

        # 3. Actionable Weak Topics
        actionable_weak_topics = []
        topic_to_unit = {}
        for u in all_units:
            u_num = u.get("unit_number")
            u_title = u.get("unit_title", f"Unit {u_num}")
            topics = u.get("topics", [])
            for t in topics:
                topic_to_unit[t] = {"unit_number": u_num, "unit_title": u_title}

        for w_topic in weak_topics:
            u_info = topic_to_unit.get(w_topic, {"unit_number": 1, "unit_title": "Core Unit"})
            actionable_weak_topics.append({
                "topic": w_topic,
                "unit_number": u_info["unit_number"],
                "unit_title": u_info["unit_title"],
                "urgency": "High",
                "recommended_action": f"Re-read Unit {u_info['unit_number']} RAG section on {w_topic} and attempt assigned quiz."
            })

        # 4. Extract Important Questions FOR ALL 5 UNITS
        unit_questions_map = {}
        for u_num in range(1, 6):
            unit_questions_map[u_num] = []

        for u in all_units:
            u_num = u.get("unit_number")
            if u_num not in unit_questions_map:
                continue
            imp_qs = u.get("important_questions", [])
            if not imp_qs:
                imp_qs = QuestionGenerator.generate_important_questions_for_unit(
                    topics=u.get("topics", []),
                    unit_number=int(u_num),
                    subject=subject
                )
            for q in imp_qs:
                q_text = q.get("question", "")
                m_cat = q.get("marks_category", 10)
                freq = q.get("frequency", "High")
                unit_questions_map[u_num].append({
                    "unit_number": u_num,
                    "question": q_text,
                    "marks_category": m_cat,
                    "frequency": freq,
                    "priority": "High" if any(t.lower() in q_text.lower() for t in weak_topics) else "Medium"
                })

        # 5. Build Unit-wise Structured Study Plan
        study_plan = []
        for u in all_units:
            u_num = u.get("unit_number")
            u_title = u.get("unit_title", f"Unit {u_num}")
            u_topics = u.get("topics", [])
            u_weak = [t for t in u_topics if t in weak_topics]

            status = "Focus Required" if len(u_weak) > 0 else "Proficient"
            study_plan.append({
                "unit_number": u_num,
                "unit_title": u_title,
                "status": status,
                "focus_topics": u_weak if u_weak else u_topics[:2],
                "recommended_hours": 4.5 if len(u_weak) > 0 else 2.5,
                "tasks": [
                    f"Review RAG textbook passages for {', '.join(u_weak if u_weak else u_topics[:2])}",
                    f"Solve {len(u_weak) * 2 if u_weak else 2} practice questions from Unit {u_num}",
                    f"Attempt assigned weak-topic quiz"
                ]
            })

        # 6. Generate AI Adaptive Quiz Questions Grounded in Weak Topics & RAG
        quiz_questions = RecommendationEngine._generate_adaptive_quiz(
            weak_topics=weak_topics,
            moderate_topics=moderate_topics,
            subject=subject,
            rag_materials=rag_materials
        )

        return {
            "actionable_weak_topics": actionable_weak_topics,
            "rag_materials": rag_materials,             # RAG textbook excerpts & study notes
            "unit_questions_map": unit_questions_map,   # Questions for each unit 1..5
            "study_plan": study_plan,                  # Study plan for units 1..5
            "quiz_questions": quiz_questions,
            "assigned_quiz_title": f"Assigned Quiz: Weak Topics in {subject}" if weak_topics else f"Proficiency Quiz: {subject}"
        }

    @staticmethod
    def _generate_adaptive_quiz(weak_topics, moderate_topics, subject="Deep Learning", rag_materials=None):
        """Dynamically generates 4-choice academic MCQs targeted to the student's weak topics."""
        all_target_topics = list(weak_topics) + list(moderate_topics)
        if not all_target_topics:
            all_target_topics = [f"{subject} Core Principles", f"{subject} Methods"]

        return QuestionGenerator.generate_mcq_quiz(
            topics=all_target_topics,
            subject=subject,
            context_chunks=rag_materials,
            count=5
        )
