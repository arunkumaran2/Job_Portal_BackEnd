"""Controller layer: HTTP APIs for jobs."""

from flask import Blueprint, jsonify, request

from job_service.job_service import JobService

job_bp = Blueprint("job", __name__, url_prefix="/api")
_service = JobService()


@job_bp.route("/jobs", methods=["POST"])
def create_job():
    """Save/Create Job API."""
    payload = request.get_json(silent=True) or {}
    try:
        result = _service.create_job(payload)
        return jsonify(result), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": "Failed to create job.", "details": str(exc)}), 500


@job_bp.route("/jobs", methods=["GET"])
def list_jobs():
    """Get Job List API."""
    try:
        result = _service.list_jobs()
        return jsonify(result), 200
    except Exception as exc:
        return jsonify({"error": "Failed to fetch jobs.", "details": str(exc)}), 500


@job_bp.route("/jobs/<int:job_id>", methods=["GET"])
def get_job(job_id: int):
    """Get Job by ID API."""
    try:
        result = _service.get_job(job_id)
        return jsonify(result), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except LookupError as exc:
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:
        return jsonify({"error": "Failed to fetch job.", "details": str(exc)}), 500


@job_bp.route("/jobs/<int:job_id>", methods=["PUT"])
def update_job(job_id: int):
    """Update Job API."""
    payload = request.get_json(silent=True) or {}
    try:
        result = _service.update_job(job_id, payload)
        return jsonify(result), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except LookupError as exc:
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:
        return jsonify({"error": "Failed to update job.", "details": str(exc)}), 500


@job_bp.route("/jobs/<int:job_id>", methods=["DELETE"])
def delete_job(job_id: int):
    """Delete Job API."""
    try:
        result = _service.delete_job(job_id)
        return jsonify(result), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except LookupError as exc:
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:
        return jsonify({"error": "Failed to delete job.", "details": str(exc)}), 500
