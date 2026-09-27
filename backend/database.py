import os
import json

class LocalJsonStorage:
    """Fallback file-based database adapter when MongoDB is not running."""
    def __init__(self, filepath):
        self.filepath = filepath
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.filepath):
            initial_data = {
                "units": [],
                "question_papers": [],
                "student_marks": [],
                "predictions": []
            }
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(initial_data, f, indent=2)

    def _read_data(self):
        self._ensure_file()
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"units": [], "question_papers": [], "student_marks": [], "predictions": []}

    def _write_data(self, data):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def insert_unit(self, unit_data):
        data = self._read_data()
        # Remove any existing unit for same subject and unit_number
        data["units"] = [
            u for u in data["units"]
            if not (u.get("subject") == unit_data.get("subject") and u.get("unit_number") == unit_data.get("unit_number"))
        ]
        data["units"].append(unit_data)
        self._write_data(data)
        return unit_data

    def get_units(self, subject=None):
        data = self._read_data()
        units = data.get("units", [])
        if subject:
            units = [u for u in units if u.get("subject") == subject]
        return units

    def get_unit(self, subject, unit_number):
        units = self.get_units(subject)
        for u in units:
            if u.get("unit_number") == int(unit_number):
                return u
        return None

    def delete_unit(self, subject, unit_number):
        data = self._read_data()
        data["units"] = [
            u for u in data.get("units", [])
            if not (u.get("subject") == subject and u.get("unit_number") == int(unit_number))
        ]
        self._write_data(data)
        return True

    def insert_question_paper(self, qp_data):
        data = self._read_data()
        data["question_papers"] = [
            qp for qp in data.get("question_papers", [])
            if not (qp.get("subject") == qp_data.get("subject") and qp.get("exam_name") == qp_data.get("exam_name"))
        ]
        data["question_papers"].append(qp_data)
        self._write_data(data)
        return qp_data

    def get_question_paper(self, subject, exam_name):
        data = self._read_data()
        for qp in data.get("question_papers", []):
            if qp.get("subject") == subject and qp.get("exam_name") == exam_name:
                return qp
        return None

    def get_question_papers(self, subject=None):
        data = self._read_data()
        qps = data.get("question_papers", [])
        if subject:
            qps = [qp for qp in qps if qp.get("subject") == subject]
        return qps

    def save_student_marks(self, marks_data):
        data = self._read_data()
        # Filter existing for same student, subject, exam
        data["student_marks"] = [
            sm for sm in data.get("student_marks", [])
            if not (sm.get("student_id") == marks_data.get("student_id") and
                    sm.get("subject") == marks_data.get("subject") and
                    sm.get("exam_name") == marks_data.get("exam_name"))
        ]
        data["student_marks"].append(marks_data)
        self._write_data(data)
        return marks_data

    def get_student_marks(self, student_id=None, subject=None):
        data = self._read_data()
        marks = data.get("student_marks", [])
        if student_id:
            marks = [m for m in marks if m.get("student_id") == student_id]
        if subject:
            marks = [m for m in marks if m.get("subject") == subject]
        return marks

    def get_all_marks_for_subject(self, subject):
        return self.get_student_marks(subject=subject)


class DatabaseAdapter:
    def __init__(self):
        from config import DATA_DIR, MONGO_URI, DB_NAME
        self.json_db = LocalJsonStorage(os.path.join(DATA_DIR, "store.json"))
        self.mongo_db = None
        self.use_mongo = False

        try:
            from pymongo import MongoClient
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=1000)
            client.server_info()  # Will trigger exception if Mongo isn't running
            self.mongo_db = client[DB_NAME]
            self.use_mongo = True
            print("[DatabaseAdapter] Connected to MongoDB.")
        except Exception:
            print("[DatabaseAdapter] MongoDB not available. Operating with JSON Store.")

    def save_unit(self, unit_data):
        if self.use_mongo:
            self.mongo_db.units.update_one(
                {"subject": unit_data["subject"], "unit_number": unit_data["unit_number"]},
                {"$set": unit_data},
                upsert=True
            )
            return unit_data
        return self.json_db.insert_unit(unit_data)

    def get_units(self, subject=None):
        if self.use_mongo:
            query = {"subject": subject} if subject else {}
            units = list(self.mongo_db.units.find(query, {"_id": 0}))
            return units
        return self.json_db.get_units(subject)

    def get_unit(self, subject, unit_number):
        if self.use_mongo:
            return self.mongo_db.units.find_one({"subject": subject, "unit_number": int(unit_number)}, {"_id": 0})
        return self.json_db.get_unit(subject, unit_number)

    def delete_unit(self, subject, unit_number):
        if self.use_mongo:
            self.mongo_db.units.delete_one({"subject": subject, "unit_number": int(unit_number)})
            return True
        return self.json_db.delete_unit(subject, unit_number)

    def save_question_paper(self, qp_data):
        if self.use_mongo:
            self.mongo_db.question_papers.update_one(
                {"subject": qp_data["subject"], "exam_name": qp_data["exam_name"]},
                {"$set": qp_data},
                upsert=True
            )
            return qp_data
        return self.json_db.insert_question_paper(qp_data)

    def get_question_paper(self, subject, exam_name):
        if self.use_mongo:
            return self.mongo_db.question_papers.find_one({"subject": subject, "exam_name": exam_name}, {"_id": 0})
        return self.json_db.get_question_paper(subject, exam_name)

    def get_question_papers(self, subject=None):
        if self.use_mongo:
            query = {"subject": subject} if subject else {}
            return list(self.mongo_db.question_papers.find(query, {"_id": 0}))
        return self.json_db.get_question_papers(subject)

    def save_student_marks(self, marks_data):
        if self.use_mongo:
            self.mongo_db.student_marks.update_one(
                {
                    "student_id": marks_data["student_id"],
                    "subject": marks_data["subject"],
                    "exam_name": marks_data["exam_name"]
                },
                {"$set": marks_data},
                upsert=True
            )
            return marks_data
        return self.json_db.save_student_marks(marks_data)

    def get_student_marks(self, student_id=None, subject=None):
        if self.use_mongo:
            query = {}
            if student_id:
                query["student_id"] = student_id
            if subject:
                query["subject"] = subject
            return list(self.mongo_db.student_marks.find(query, {"_id": 0}))
        return self.json_db.get_student_marks(student_id, subject)

db_adapter = DatabaseAdapter()
