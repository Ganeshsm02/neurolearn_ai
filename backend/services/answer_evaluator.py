import re
import os
import math
from typing import List, Dict, Any, Optional, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

from database import db_adapter
from services.rag_engine import rag_engine

# Common stop words to exclude from keyword search
STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with", "by", "about",
    "against", "between", "into", "through", "during", "before", "after", "above", "below",
    "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then",
    "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few",
    "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so",
    "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now", "is", "are",
    "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did",
    "doing", "would", "could", "shall", "explain", "describe", "define", "what", "which", "discuss"
}


class AnswerSheetEvaluator:
    """
    Automated Student Answer Sheet Evaluation Engine.
    Compares student answers against authoritative reference content extracted from the uploaded PDF.
    Uses Dual Similarity:
      1. Keyword Search (lexical coverage of domain concepts)
      2. Semantic Search (vector cosine similarity on TF-IDF context representations)
    Calculates fair academic marks out of question max marks and provides constructive feedback.
    """

    @classmethod
    def extract_text_from_pdf_stream(cls, stream_bytes: bytes) -> str:
        """Extracts text from an in-memory PDF stream using PyMuPDF."""
        if not HAS_PYMUPDF or not stream_bytes:
            try:
                return stream_bytes.decode("utf-8", errors="ignore")
            except Exception:
                return ""

        try:
            doc = fitz.open(stream=stream_bytes, filetype="pdf")
            text_blocks = []
            for page in doc:
                text_blocks.append(page.get_text("text"))
            return "\n\n".join(text_blocks).strip()
        except Exception as e:
            print(f"[AnswerEvaluator] PDF parsing error: {e}")
            try:
                return stream_bytes.decode("utf-8", errors="ignore")
            except Exception:
                return ""

    @classmethod
    def parse_student_answers(cls, raw_text: str) -> Dict[str, str]:
        """
        Parses a student answer sheet text into question-indexed answers.
        Recognizes delimiters like 'Q1', 'Q1.', 'Question 1:', '1.', '1)', 'Ans 1:', 'Q6a', '6a', etc.
        """
        if not raw_text or not raw_text.strip():
            return {}

        answers = {}
        lines = raw_text.splitlines()

        # Regex for question heading patterns: e.g. "Q1", "Q1.", "Q1a", "Q6a", "Question 1", "Ans 1", "1."
        pattern = re.compile(
            r'^\s*(?:question|ans|q)?\.?\s*([0-9]{1,2}\s*[a-bA-B]?)\s*[\.\:\-\)\s]+(.*)$',
            re.IGNORECASE
        )

        current_qid = None
        current_buffer = []

        for line in lines:
            line_str = line.strip()
            if not line_str:
                if current_qid:
                    current_buffer.append("")
                continue

            match = pattern.match(line_str)
            if match and len(match.group(1).strip()) <= 4:
                # Save previous question
                if current_qid:
                    answers[current_qid] = "\n".join(current_buffer).strip()
                    current_buffer = []

                raw_q = match.group(1).replace(" ", "").upper()
                current_qid = f"Q{raw_q}" if not raw_q.startswith("Q") else raw_q
                remainder = match.group(2).strip()
                if remainder:
                    current_buffer.append(remainder)
            else:
                if current_qid:
                    current_buffer.append(line_str)
                else:
                    # Initial text before any question header, or unlabelled answer 1
                    if not current_qid and len(line_str) > 10:
                        current_qid = "Q1"
                        current_buffer.append(line_str)

        if current_qid and current_buffer:
            answers[current_qid] = "\n".join(current_buffer).strip()

        # If no explicit questions were detected, split by double newlines into paragraphs
        if not answers and len(raw_text.strip()) > 30:
            paragraphs = [p.strip() for p in raw_text.split("\n\n") if len(p.strip()) > 20]
            for i, p in enumerate(paragraphs):
                answers[f"Q{i+1}"] = p

        return answers

    @classmethod
    def get_ground_truth_for_question(cls, subject: str, unit_number: int, topic: str, question_text: str) -> str:
        """
        Retrieves authoritative ground-truth reference passage from the uploaded syllabus/textbook PDF.
        Queries RAG Engine vector chunks and unit database records.
        """
        ref_passages = []

        # 1. Query RAG vector store for semantic matches
        try:
            query = f"{topic} {question_text}"
            materials = rag_engine.retrieve_rag_materials(subject, [topic], top_k=3)
            for mat in materials:
                if mat.get("text_excerpt"):
                    ref_passages.append(mat["text_excerpt"])
        except Exception as e:
            print(f"[AnswerEvaluator] RAG query notice: {e}")

        # 2. Check Database units for extracted key concepts and subtopics
        try:
            unit_data = db_adapter.get_unit(subject, unit_number)
            if unit_data:
                # Key concepts
                for kc in unit_data.get("key_concepts", []):
                    if topic.lower() in kc.get("name", "").lower():
                        ref_passages.append(f"{kc.get('name')}: {kc.get('description', '')}")

                # Check extracted text for topic occurrence
                extracted_text = unit_data.get("extracted_text", "")
                if extracted_text and topic.lower() in extracted_text.lower():
                    # Extract surrounding paragraph
                    paras = extracted_text.split("\n\n")
                    for p in paras:
                        if topic.lower() in p.lower() and len(p.strip()) > 40:
                            ref_passages.append(p.strip())
                            if len(ref_passages) >= 4:
                                break
        except Exception as e:
            print(f"[AnswerEvaluator] Unit DB lookup notice: {e}")

        # Fallback reference if no PDF text was found
        if not ref_passages:
            ref_passages.append(
                f"{topic} is a core theoretical concept in {subject}. "
                f"It involves systematic algorithmic computation, parameter tuning, and operational pipeline integration. "
                f"Key governing mechanisms define how inputs are transformed, optimized, and evaluated to ensure convergence and generalization."
            )

        return "\n\n".join(ref_passages)

    @classmethod
    def extract_technical_keywords(cls, text: str) -> List[str]:
        """Extracts candidate domain technical terms and keywords from reference text."""
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        keywords = []
        for w in words:
            if w not in STOP_WORDS and len(w) >= 4:
                keywords.append(w)
        # Deduplicate while preserving order
        seen = set()
        unique = []
        for k in keywords:
            if k not in seen:
                seen.add(k)
                unique.append(k)
        return unique

    @classmethod
    def evaluate_single_answer(cls, student_ans: str, ref_text: str, topic: str, max_marks: float) -> Dict[str, Any]:
        """
        Evaluates a single answer using dual Keyword Search + Semantic Search.
        """
        student_ans = (student_ans or "").strip()
        if not student_ans or len(student_ans) < 5:
            return {
                "student_answer": student_ans or "(No answer provided)",
                "reference_excerpt": ref_text[:300] + ("..." if len(ref_text) > 300 else ""),
                "keyword_match_pct": 0.0,
                "semantic_sim_pct": 0.0,
                "hybrid_similarity_pct": 0.0,
                "matched_keywords": [],
                "missing_keywords": cls.extract_technical_keywords(ref_text)[:5],
                "awarded_marks": 0.0,
                "feedback": "No substantial answer provided. Missing core theoretical concepts."
            }

        # ----------------- 1. Keyword Search / Lexical Matching -----------------
        expected_keywords = cls.extract_technical_keywords(ref_text)
        # Also include topic words as vital keywords
        topic_words = [w.lower() for w in re.findall(r'\b[a-zA-Z]{3,}\b', topic) if w.lower() not in STOP_WORDS]
        vital_keywords = list(set(topic_words + expected_keywords[:15]))

        student_ans_lower = student_ans.lower()
        matched = [k for k in vital_keywords if k in student_ans_lower]
        missing = [k for k in vital_keywords if k not in student_ans_lower][:6]

        keyword_ratio = len(matched) / max(1, min(len(vital_keywords), 8))
        keyword_score = min(1.0, keyword_ratio)

        # ----------------- 2. Semantic Search / Vector Cosine Similarity -----------------
        semantic_score = 0.0
        try:
            corpus = [ref_text, student_ans]
            vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(corpus)
            cos_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            semantic_score = float(max(0.0, min(1.0, cos_sim)))
        except Exception as e:
            # Fallback length/overlap heuristic if vectorizer fails
            common_chars = set(student_ans_lower.split()) & set(ref_text.lower().split())
            semantic_score = min(1.0, len(common_chars) / max(10, len(student_ans_lower.split())))

        # ----------------- 3. Hybrid Score & Academic Mark Calibration -----------------
        # Weighted combination: 45% semantic context + 55% technical keyword precision
        hybrid_sim = (0.45 * semantic_score) + (0.55 * keyword_score)

        # Academic calibration: concise correct student answers get fair top marks
        if hybrid_sim >= 0.70:
            calibrated_ratio = min(1.0, 0.90 + (hybrid_sim - 0.70) * 0.33)
        elif hybrid_sim >= 0.45:
            calibrated_ratio = 0.75 + (hybrid_sim - 0.45) * 0.60
        elif hybrid_sim >= 0.25:
            calibrated_ratio = 0.50 + (hybrid_sim - 0.25) * 1.00
        elif hybrid_sim >= 0.10:
            calibrated_ratio = 0.30 + (hybrid_sim - 0.10) * 1.33
        else:
            calibrated_ratio = hybrid_sim * 2.0

        calibrated_ratio = min(1.0, max(0.0, calibrated_ratio))
        raw_marks = max_marks * calibrated_ratio

        # Round marks neatly (multiples of 0.5)
        awarded = round(raw_marks * 2) / 2
        awarded = min(float(max_marks), max(0.0, awarded))

        # Qualitative Feedback
        if awarded >= max_marks * 0.85:
            feedback = f"Excellent answer! Demonstrates strong understanding of {topic}. All primary technical points covered."
        elif awarded >= max_marks * 0.65:
            feedback = f"Good answer. Core concept of {topic} is addressed well, but missing deeper technical elaboration on: {', '.join(missing[:3])}."
        elif awarded >= max_marks * 0.40:
            feedback = f"Partial answer. Fundamental terminology present, but requires explanation of mechanisms and: {', '.join(missing[:3])}."
        else:
            feedback = f"Needs significant improvement. Missing critical technical aspects of {topic}. Review: {', '.join(missing[:4])}."

        return {
            "student_answer": student_ans,
            "reference_excerpt": ref_text[:350] + ("..." if len(ref_text) > 350 else ""),
            "keyword_match_pct": round(keyword_score * 100, 1),
            "semantic_sim_pct": round(semantic_score * 100, 1),
            "hybrid_similarity_pct": round(hybrid_sim * 100, 1),
            "matched_keywords": matched[:8],
            "missing_keywords": missing[:6],
            "awarded_marks": awarded,
            "feedback": feedback
        }

    @classmethod
    def evaluate_answer_sheet(
        cls,
        subject: str,
        exam_name: str,
        student_id: str,
        student_name: str,
        raw_text: Optional[str] = None,
        file_bytes: Optional[bytes] = None,
        question_paper: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main entry point for evaluating a complete student answer sheet against a question paper.
        """
        # 1. Extract text from uploaded PDF or raw text
        if file_bytes:
            extracted_text = cls.extract_text_from_pdf_stream(file_bytes)
            if not extracted_text and raw_text:
                extracted_text = raw_text
        else:
            extracted_text = raw_text or ""

        # 2. Parse answer sheet into question dictionary
        parsed_student_answers = cls.parse_student_answers(extracted_text)

        # 3. Retrieve target Question Paper
        qp = question_paper
        if not qp:
            qp = db_adapter.get_question_paper(subject, exam_name)

        # If question paper is still not found, load or generate blueprint
        if not qp or not qp.get("questions"):
            units = db_adapter.get_units(subject=subject)
            units_dict = {int(u.get("unit_number", 1)): u for u in units}
            from services.question_generator import QuestionGenerator
            ia_type = "IA 1" if "1" in exam_name else "IA 2" if "2" in exam_name else "IA 3"
            qp = QuestionGenerator.generate_blueprint_paper(subject, ia_type, units_dict)

        paper_questions = qp.get("questions", [])
        evaluated_questions = []
        question_scores = {}

        # 4. Evaluate each question using dual Keyword + Semantic search
        # To handle Either/Or pairs (e.g. Q6a or Q6b), group by base question number
        grouped_choices = {}
        for q in paper_questions:
            q_id = q.get("question_id", "Q1")
            q_topic = q.get("topic", f"{subject} Core Topic")
            q_text = q.get("question", "")
            max_m = float(q.get("max_marks", 2))
            u_num = int(q.get("unit_number", 1))

            # Case-insensitive robust lookup for student answer
            norm_q = q_id.strip().upper()
            num_only = norm_q.replace("Q", "").strip()

            student_ans = ""
            for key, val in parsed_student_answers.items():
                k_norm = key.strip().upper()
                if k_norm == norm_q or k_norm == f"Q{num_only}" or k_norm == num_only:
                    student_ans = val
                    break
                # If question is Q8 and student answered Q8A (or vice-versa)
                if norm_q.startswith(k_norm) or k_norm.startswith(norm_q):
                    student_ans = val
                    break

            # Retrieve authoritative ground-truth PDF answer uploaded during question generation
            ref_content = q.get("pdf_answer")
            if not ref_content or len(ref_content.strip()) < 20:
                ref_content = cls.get_ground_truth_for_question(subject, u_num, q_topic, q_text)

            # Evaluate using both semantic vector search and keyword search
            eval_res = cls.evaluate_single_answer(student_ans, ref_content, q_topic, max_m)
            eval_res.update({
                "question_id": q_id,
                "part": q.get("part", "Part A"),
                "question": q_text,
                "topic": q_topic,
                "max_marks": max_m,
                "unit_number": u_num,
                "pdf_answer": ref_content
            })

            evaluated_questions.append(eval_res)
            question_scores[q_id] = eval_res["awarded_marks"]

        # 5. Compute total marks considering Either/Or choices
        # For Part A questions (Q1 to Q5 or Q1 to Q10): sum all
        # For Part B questions (pairs: Q6a/Q6b, Q7a/Q7b, etc.): take max of (a, b)
        # For Part C questions (Q8a/Q8b or Q11a/Q11b): take max of (a, b)
        total_awarded = 0.0
        total_max = 0.0

        # Group by base ID
        base_groups = {}
        for eq in evaluated_questions:
            qid = eq["question_id"]
            # e.g. "Q6a" -> base "Q6", "Q1" -> base "Q1"
            base_match = re.match(r'^(Q\d+)[a-zA-Z]?$', qid)
            base_id = base_match.group(1) if base_match else qid

            if base_id not in base_groups:
                base_groups[base_id] = []
            base_groups[base_id].append(eq)

        for base_id, q_options in base_groups.items():
            if len(q_options) == 1:
                total_awarded += q_options[0]["awarded_marks"]
                total_max += q_options[0]["max_marks"]
            else:
                # Either / Or pair: take the higher scored option
                best_score = max(opt["awarded_marks"] for opt in q_options)
                max_score = q_options[0]["max_marks"]
                total_awarded += best_score
                total_max += max_score

        percentage = round((total_awarded / max(1.0, total_max)) * 100, 1)

        grade = "A+" if percentage >= 90 else "A" if percentage >= 80 else "B" if percentage >= 65 else "C" if percentage >= 50 else "RA (Re-Appear)"

        marks_record = {
            "subject": subject,
            "exam_name": exam_name,
            "student_id": student_id,
            "student_name": student_name,
            "total_score": round(total_awarded, 1),
            "max_score": round(total_max, 1),
            "percentage": percentage,
            "grade": grade,
            "question_scores": question_scores,
            "evaluated_questions": evaluated_questions,
            "evaluated_at": os.path.basename(subject)
        }

        # Auto-save student evaluation to Database
        db_adapter.save_student_marks(marks_record)

        return {
            "status": "success",
            "message": f"Answer sheet evaluated successfully for {student_name} ({student_id}) using Hybrid Semantic + Keyword Search.",
            "evaluation": marks_record
        }
