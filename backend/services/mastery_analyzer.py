class MasteryAnalyzer:
    """Analyzes question-wise student marks against topic mappings to calculate concept mastery and gaps."""

    @staticmethod
    def calculate_student_mastery(student_marks_list, question_papers, units):
        """
        Calculates topic-wise, unit-wise, and overall mastery for a student.
        student_marks_list: list of student_mark documents for a student
        question_papers: list of question_paper documents for the subject
        units: list of unit documents for the subject
        """
        # Map exam_name to question_paper for fast lookup
        qp_map = {qp["exam_name"]: qp for qp in question_papers}
        unit_map = {u["unit_number"]: u for u in units}

        topic_stats = {}  # topic_name -> {"obtained": 0, "total": 0, "unit_number": X}
        exam_history = []

        for mark_record in student_marks_list:
            exam_name = mark_record.get("exam_name")
            qp = qp_map.get(exam_name)
            if not qp:
                continue

            q_mappings = {q["question_id"]: q for q in qp.get("questions", [])}
            student_scores = mark_record.get("question_scores", {})

            exam_obtained = 0
            exam_total = 0

            for q_id, scored in student_scores.items():
                scored = float(scored)
                q_info = q_mappings.get(q_id)
                if not q_info:
                    continue

                max_m = float(q_info.get("max_marks", 5))
                topic = q_info.get("topic", "General Topic")
                unit_num = q_info.get("unit_number", 1)

                exam_obtained += scored
                exam_total += max_m

                if topic not in topic_stats:
                    topic_stats[topic] = {"obtained": 0, "total": 0, "unit_number": unit_num}

                topic_stats[topic]["obtained"] += scored
                topic_stats[topic]["total"] += max_m

            if exam_total > 0:
                exam_pct = round((exam_obtained / exam_total) * 100, 1)
                exam_history.append({
                    "exam_name": exam_name,
                    "obtained": exam_obtained,
                    "total": exam_total,
                    "percentage": exam_pct
                })

        # Calculate Topic Mastery Breakdown
        weak_topics = []
        moderate_topics = []
        strong_topics = []
        mastery_by_topic = []

        for topic, stat in topic_stats.items():
            tot = stat["total"]
            obt = stat["obtained"]
            pct = round((obt / tot) * 100, 1) if tot > 0 else 0.0

            category = "Weak" if pct < 50.0 else ("Moderate" if pct <= 75.0 else "Strong")
            topic_info = {
                "topic": topic,
                "obtained": obt,
                "total": tot,
                "percentage": pct,
                "category": category,
                "unit_number": stat["unit_number"]
            }

            mastery_by_topic.append(topic_info)

            if category == "Weak":
                weak_topics.append(topic)
            elif category == "Moderate":
                moderate_topics.append(topic)
            else:
                strong_topics.append(topic)

        # Unit-wise breakdown
        unit_breakdown = {}
        for item in mastery_by_topic:
            u_num = item["unit_number"]
            if u_num not in unit_breakdown:
                unit_info = unit_map.get(u_num, {})
                unit_breakdown[u_num] = {
                    "unit_number": u_num,
                    "unit_title": unit_info.get("unit_title", f"Unit {u_num}"),
                    "obtained": 0,
                    "total": 0,
                    "topics_count": 0
                }
            unit_breakdown[u_num]["obtained"] += item["obtained"]
            unit_breakdown[u_num]["total"] += item["total"]
            unit_breakdown[u_num]["topics_count"] += 1

        unit_performance = []
        for u_num, data in sorted(unit_breakdown.items()):
            tot = data["total"]
            pct = round((data["obtained"] / tot) * 100, 1) if tot > 0 else 0.0
            unit_performance.append({
                "unit_number": u_num,
                "unit_title": data["unit_title"],
                "percentage": pct,
                "topics_count": data["topics_count"]
            })

        overall_obtained = sum(t["obtained"] for t in mastery_by_topic)
        overall_total = sum(t["total"] for t in mastery_by_topic)
        overall_pct = round((overall_obtained / overall_total) * 100, 1) if overall_total > 0 else 0.0

        return {
            "overall_mastery_pct": overall_pct,
            "topic_mastery": mastery_by_topic,
            "weak_topics": weak_topics,
            "moderate_topics": moderate_topics,
            "strong_topics": strong_topics,
            "unit_performance": unit_performance,
            "exam_history": exam_history
        }

    @staticmethod
    def calculate_class_analytics(all_student_marks, question_papers, units):
        """Calculates class-wide difficult topics and identifies students needing academic support."""
        if not all_student_marks:
            return {
                "total_students": 0,
                "class_average_pct": 0,
                "difficult_topics": [],
                "at_risk_students": []
            }

        student_ids = list(set(m.get("student_id") for m in all_student_marks))
        student_summaries = []

        for sid in student_ids:
            s_marks = [m for m in all_student_marks if m.get("student_id") == sid]
            res = MasteryAnalyzer.calculate_student_mastery(s_marks, question_papers, units)
            student_name = s_marks[0].get("student_name", sid)
            student_summaries.append({
                "student_id": sid,
                "student_name": student_name,
                "overall_pct": res["overall_mastery_pct"],
                "weak_topics_count": len(res["weak_topics"]),
                "weak_topics": res["weak_topics"]
            })

        # Class average
        avg_pct = round(sum(s["overall_pct"] for s in student_summaries) / len(student_summaries), 1) if student_summaries else 0.0

        # At-risk students (overall < 50% or > 2 weak topics)
        at_risk = [s for s in student_summaries if s["overall_pct"] < 50.0 or s["weak_topics_count"] >= 2]

        # Aggregate topic performance class-wide
        topic_totals = {}
        for sid in student_ids:
            s_marks = [m for m in all_student_marks if m.get("student_id") == sid]
            res = MasteryAnalyzer.calculate_student_mastery(s_marks, question_papers, units)
            for tm in res["topic_mastery"]:
                t_name = tm["topic"]
                if t_name not in topic_totals:
                    topic_totals[t_name] = []
                topic_totals[t_name].append(tm["percentage"])

        difficult_topics = []
        for t_name, pcts in topic_totals.items():
            t_avg = round(sum(pcts) / len(pcts), 1) if pcts else 0.0
            if t_avg < 60.0:
                difficult_topics.append({
                    "topic": t_name,
                    "class_average": t_avg,
                    "students_struggling": sum(1 for p in pcts if p < 50.0)
                })

        difficult_topics.sort(key=lambda x: x["class_average"])

        return {
            "total_students": len(student_ids),
            "class_average_pct": avg_pct,
            "difficult_topics": difficult_topics,
            "at_risk_students": at_risk,
            "student_summaries": student_summaries
        }
