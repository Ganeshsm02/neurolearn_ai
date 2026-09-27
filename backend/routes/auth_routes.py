from flask import Blueprint, request, jsonify

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Authentication Endpoint for Students and Teachers.
    """
    data = request.json or {}
    role = data.get("role", "student")  # 'student' or 'teacher'
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username:
        return jsonify({"status": "error", "message": "Username / Student ID is required."}), 400

    if role == "admin" or username.lower() == "admin":
        # Admin credentials (default demo: admin / admin123 or any password for demo)
        return jsonify({
            "status": "success",
            "role": "admin",
            "user": {
                "username": username,
                "name": "System Administrator",
                "email": "admin@neurolearn.ai",
                "token": "admin-token-auth"
            }
        }), 200

    elif role == "teacher":
        if username.lower() in ["teacher", "prof"] or len(username) >= 2:
            return jsonify({
                "status": "success",
                "role": "teacher",
                "user": {
                    "username": username,
                    "name": f"Prof. {username.capitalize()}",
                    "token": "teacher-token-auth"
                }
            }), 200
        else:
            return jsonify({"status": "error", "message": "Invalid Teacher credentials."}), 401
    else:
        # Student Login
        student_id = username.upper()
        return jsonify({
            "status": "success",
            "role": "student",
            "user": {
                "student_id": student_id,
                "name": f"Student {student_id}",
                "token": "student-token-auth"
            }
        }), 200
