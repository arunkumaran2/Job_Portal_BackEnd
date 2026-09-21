"""Controller layer: HTTP APIs for job seeker registration and login."""

from flask import Blueprint, jsonify, request

from jobseeker_service.job_seeker_service import JobSeekerService

jobseeker_bp = Blueprint("jobseeker", __name__, url_prefix="/api/jobseeker")
_service = JobSeekerService()


@jobseeker_bp.route("/register", methods=["POST"])
def register_job_seeker():
    """
    Save User / Registration API.

    Accepts job seeker details + password and stores them in MySQL.
    """
    payload = request.get_json(silent=True) or {}
    try:
        result = _service.register(payload)
        return jsonify(result), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": "Registration failed.", "details": str(exc)}), 500


@jobseeker_bp.route("/login", methods=["POST"])
def login_job_seeker():
    """
    Login API.

    Accepts either email + password or mobile_number + password.
    """
    payload = request.get_json(silent=True) or {}
    try:
        result = _service.login(payload)
        return jsonify(result), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 401
    except Exception as exc:
        return jsonify({"error": "Login failed.", "details": str(exc)}), 500
