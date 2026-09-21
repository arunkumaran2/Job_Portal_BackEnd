"""Controller layer: HTTP APIs for admin registration and login."""

from flask import Blueprint, jsonify, request

from admins_service.admin_service import AdminService

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")
_service = AdminService()


@admin_bp.route("/register", methods=["POST"])
def save_admin():
    """
    Save Admins API.

    Accepts admin details + password and stores them in MySQL.
    """
    payload = request.get_json(silent=True) or {}
    try:
        result = _service.save_admin(payload)
        return jsonify(result), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": "Failed to save admin.", "details": str(exc)}), 500


@admin_bp.route("/login", methods=["POST"])
def login_admin():
    """
    Admins Login API.

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


@admin_bp.route("/users", methods=["GET"])
def list_admins():
    """
    Admins List API.

    Returns all admin users from the database.
    """
    try:
        result = _service.list_admins()
        return jsonify(result), 200
    except Exception as exc:
        return jsonify({"error": "Failed to fetch admins.", "details": str(exc)}), 500


@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
def delete_admin(user_id: int):
    """
    Admins Delete API.

    Deletes an admin user by their user ID.
    """
    try:
        result = _service.delete_admin(user_id)
        return jsonify(result), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except LookupError as exc:
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:
        return jsonify({"error": "Failed to delete admin.", "details": str(exc)}), 500
