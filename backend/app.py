from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys

# Ensure backend directory is on Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import SUBJECTS
from database import db_adapter
from routes.teacher_routes import teacher_bp
from routes.student_routes import student_bp
from routes.prediction_routes import prediction_bp
from routes.auth_routes import auth_bp
from routes.placement_routes import placement_bp
from routes.admin_routes import admin_bp

app = Flask(__name__)
CORS(app)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(teacher_bp, url_prefix="/api/teacher")
app.register_blueprint(student_bp, url_prefix="/api/student")
app.register_blueprint(prediction_bp, url_prefix="/api/prediction")
app.register_blueprint(placement_bp, url_prefix="/api/placement")
app.register_blueprint(admin_bp, url_prefix="/api/admin")


@app.route("/", methods=["GET"])
def health_check():
    return jsonify({
        "status": "online",
        "system": "NeuroLearn AI Backend Engine",
        "modules": [
            "Module 1: Student Performance & Mark Prediction Engine",
            "Module 2: Student & Teacher Collaboration Platform",
            "Module 3: AI-Based Placement & Career Guidance System"
        ],
        "database_status": "MongoDB" if db_adapter.use_mongo else "JSON Store Active",
        "supported_subjects": SUBJECTS
    })


@app.route("/api/subjects", methods=["GET"])
def get_subjects():
    return jsonify({"subjects": SUBJECTS})


if __name__ == "__main__":
    print("[NeuroLearn AI] Starting Flask backend server on port 5000...")
    app.run(host="0.0.0.0", port=5000, debug=True)
