"""Controller layer: HTTP APIs for recruiter registration and login."""

from flask import Blueprint, jsonify, request

from recruiters_service.recruiter_service import RecruiterService

recruiter_bp = Blueprint("recruiter", __name__, url_prefix="/api/recruiter")
_service = RecruiterService()


@recruiter_bp.route("/register", methods=["POST"])
def save_recruiter():
    """
    Save Recruiter API.

    Accepts recruiter details + password and stores them in MySQL.
    """
    payload = request.get_json(silent=True) or {}
    try:
        result = _service.save_recruiter(payload)
        return jsonify(result), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": "Failed to save recruiter.", "details": str(exc)}), 500


@recruiter_bp.route("/login", methods=["POST"])
def login_recruiter():
    """
    Recruiter Login API.

    Accepts either email (Gmail) + password or phone/mobile_number + password.
    """
    payload = request.get_json(silent=True) or {}
    try:
        result = _service.login(payload)
        return jsonify(result), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 401
    except Exception as exc:
        return jsonify({"error": "Login failed.", "details": str(exc)}), 500


@recruiter_bp.route("/users", methods=["GET"])
def list_recruiters():
    """
    Recruiter List API.

    Returns all recruiter users from the database.
    """
    try:
        result = _service.list_recruiters()
        return jsonify(result), 200
    except Exception as exc:
        return jsonify({"error": "Failed to fetch recruiters.", "details": str(exc)}), 500


@recruiter_bp.route("/users/<int:user_id>", methods=["DELETE"])
def delete_recruiter(user_id: int):
    """
    Recruiter Delete API.

    Deletes a recruiter user by their user ID.
    """
    try:
        result = _service.delete_recruiter(user_id)
        return jsonify(result), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except LookupError as exc:
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:
        return jsonify({"error": "Failed to delete recruiter.", "details": str(exc)}), 500
