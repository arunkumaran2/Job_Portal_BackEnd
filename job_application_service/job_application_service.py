"""Service layer: job application and resume business logic."""

import uuid
from pathlib import Path
from typing import Any, Optional

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from job_application_dao.job_application_dao import JobApplicationDAO
from job_applications.job_application_model import JobApplication

VALID_STATUSES = {
    "Applied",
    "Shortlisted",
    "Rejected",
    "Interview",
    "Selected",
    "Withdrawn",
}

ALLOWED_RESUME_EXTENSIONS = {".pdf", ".doc", ".docx"}
UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads" / "resumes"


class JobApplicationService:
    """Business rules for applications and resume uploads."""

    def __init__(self, dao: Optional[JobApplicationDAO] = None) -> None:
        self.dao = dao or JobApplicationDAO()

    def upload_resume(
        self,
        job_seeker_id: int,
        resume_url: Optional[str] = None,
        resume_file: Optional[FileStorage] = None,
    ) -> dict[str, Any]:
        if job_seeker_id is None or job_seeker_id <= 0:
            raise ValueError("A valid job_seeker_id is required.")

        if not self.dao.job_seeker_exists(job_seeker_id):
            raise LookupError(
                f"Job seeker with job_seeker_id {job_seeker_id} not found."
            )

        final_url: Optional[str] = None

        if resume_file is not None and getattr(resume_file, "filename", None):
            final_url = self._save_resume_file(job_seeker_id, resume_file)
        elif resume_url:
            final_url = resume_url.strip()

        if not final_url:
            raise ValueError(
                "Provide resume_url in JSON body or upload a resume file."
            )

        updated = self.dao.update_resume_url(job_seeker_id, final_url)
        if updated is None:
            raise LookupError(
                f"Job seeker with job_seeker_id {job_seeker_id} not found."
            )

        return {
            "message": "Resume uploaded successfully.",
            "job_seeker_id": job_seeker_id,
            "resume_url": updated.get("resume_url"),
        }

    def apply_for_job(self, job_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        if job_id is None or job_id <= 0:
            raise ValueError("A valid job_id is required.")

        job_status = self.dao.get_job_status(job_id)
        if job_status is None:
            raise LookupError(f"Job with job_id {job_id} not found.")
        if job_status != "Active":
            raise ValueError("Applications are only accepted for Active jobs.")

        job_seeker_id = self._to_int(payload.get("job_seeker_id"), required=True)
        if not self.dao.job_seeker_exists(job_seeker_id):
            raise ValueError(
                f"Job seeker with job_seeker_id {job_seeker_id} not found."
            )

        if self.dao.application_exists(job_id, job_seeker_id):
            raise ValueError("You have already applied for this job.")

        # Optional: update resume on apply if provided
        resume_url = (payload.get("resume_url") or "").strip() or None
        if resume_url:
            self.dao.update_resume_url(job_seeker_id, resume_url)

        application = JobApplication(
            job_id=job_id,
            job_seeker_id=job_seeker_id,
            cover_letter=(payload.get("cover_letter") or "").strip() or None,
            status="Applied",
        )
        created = self.dao.create_application(application)
        return {
            "message": "Application submitted successfully.",
            "application": created.to_dict(),
        }

    def get_job_applicants(self, job_id: int) -> dict[str, Any]:
        if job_id is None or job_id <= 0:
            raise ValueError("A valid job_id is required.")

        if not self.dao.job_exists(job_id):
            raise LookupError(f"Job with job_id {job_id} not found.")

        applicants = self.dao.find_by_job_id(job_id)
        return {
            "job_id": job_id,
            "count": len(applicants),
            "applicants": [app.to_dict() for app in applicants],
        }

    def update_application_status(
        self, application_id: int, payload: dict[str, Any]
    ) -> dict[str, Any]:
        if application_id is None or application_id <= 0:
            raise ValueError("A valid application_id is required.")

        status = (payload.get("status") or payload.get("application_status") or "").strip()
        if not status:
            raise ValueError("status is required.")
        if status not in VALID_STATUSES:
            raise ValueError(
                "status must be one of: " + ", ".join(sorted(VALID_STATUSES)) + "."
            )

        existing = self.dao.find_by_id(application_id)
        if existing is None:
            raise LookupError(
                f"Application with application_id {application_id} not found."
            )

        updated = self.dao.update_status(application_id, status)
        if updated is None:
            raise LookupError(
                f"Application with application_id {application_id} not found."
            )

        return {
            "message": "Application status updated successfully.",
            "application": updated.to_dict(),
        }

    def get_job_seeker_applications(self, job_seeker_id: int) -> dict[str, Any]:
        if job_seeker_id is None or job_seeker_id <= 0:
            raise ValueError("A valid job_seeker_id is required.")

        if not self.dao.job_seeker_exists(job_seeker_id):
            raise LookupError(
                f"Job seeker with job_seeker_id {job_seeker_id} not found."
            )

        applications = self.dao.find_by_job_seeker_id(job_seeker_id)
        return {
            "count": len(applications),
            "applications": [app.to_dict() for app in applications],
        }

    def _save_resume_file(
        self, job_seeker_id: int, resume_file: FileStorage
    ) -> str:
        filename = secure_filename(resume_file.filename or "")
        if not filename:
            raise ValueError("Invalid resume file name.")

        extension = Path(filename).suffix.lower()
        if extension not in ALLOWED_RESUME_EXTENSIONS:
            raise ValueError(
                "Resume must be a PDF or Word document (.pdf, .doc, .docx)."
            )

        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        stored_name = f"seeker_{job_seeker_id}_{uuid.uuid4().hex}{extension}"
        destination = UPLOAD_DIR / stored_name
        resume_file.save(destination)

        # Relative URL path for API consumers
        return f"/uploads/resumes/{stored_name}"

    @staticmethod
    def _to_int(
        value: Any, default: Optional[int] = None, required: bool = False
    ) -> Optional[int]:
        if value is None or value == "":
            if required:
                raise ValueError("job_seeker_id is required.")
            return default
        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid integer value: {value}") from exc
