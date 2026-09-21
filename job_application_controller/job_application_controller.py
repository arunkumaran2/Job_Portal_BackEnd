"""Controller layer: HTTP APIs for job applications and resumes."""

from flask import Blueprint, jsonify, request

from job_application_service.job_application_service import JobApplicationService

job_application_bp = Blueprint("job_application", __name__, url_prefix="/api")
_service = JobApplicationService()


@job_application_bp.route(
    "/job-seekers/<int:job_seeker_id>/resume", methods=["PUT"]
)
def upload_resume(job_seeker_id: int):
    """Upload/Update Resume API."""
    try:
        resume_file = request.files.get("resume") or request.files.get("file")
        resume_url = None

        if request.is_json:
            payload = request.get_json(silent=True) or {}
            resume_url = payload.get("resume_url")
        else:
            resume_url = request.form.get("resume_url")

        result = _service.upload_resume(
            job_seeker_id,
            resume_url=resume_url,
            resume_file=resume_file,
        )
        return jsonify(result), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except LookupError as exc:
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:
        return jsonify({"error": "Failed to upload resume.", "details": str(exc)}), 500


@job_application_bp.route("/jobs/<int:job_id>/apply", methods=["POST"])
def apply_for_job(job_id: int):
    """Apply for Job API."""
    payload = request.get_json(silent=True) or {}
    try:
        result = _service.apply_for_job(job_id, payload)
        return jsonify(result), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except LookupError as exc:
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:
        return jsonify({"error": "Failed to apply for job.", "details": str(exc)}), 500


@job_application_bp.route("/jobs/<int:job_id>/applicants", methods=["GET"])
def get_job_applicants(job_id: int):
    """Recruiter View Applicants API."""
    try:
        result = _service.get_job_applicants(job_id)
        return jsonify(result), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except LookupError as exc:
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:
        return jsonify(
            {"error": "Failed to fetch applicants.", "details": str(exc)}
        ), 500


@job_application_bp.route(
    "/applications/<int:application_id>/status", methods=["PATCH"]
)
def update_application_status(application_id: int):
    """Shortlist/Reject/Update Application Status API."""
    payload = request.get_json(silent=True) or {}
    try:
        result = _service.update_application_status(application_id, payload)
        return jsonify(result), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except LookupError as exc:
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:
        return jsonify(
            {"error": "Failed to update application status.", "details": str(exc)}
        ), 500


@job_application_bp.route(
    "/job-seekers/<int:job_seeker_id>/applications", methods=["GET"]
)
def get_job_seeker_applications(job_seeker_id: int):
    """Get Job Seeker Applications API."""
    try:
        result = _service.get_job_seeker_applications(job_seeker_id)
        return jsonify(result), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except LookupError as exc:
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:
        return jsonify(
            {"error": "Failed to fetch applications.", "details": str(exc)}
        ), 500
