"""Service layer: job seeker registration and login business logic."""

import re
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

from werkzeug.security import check_password_hash, generate_password_hash

from jobseeker.job_seeker_model import JobSeeker
from jobseeker_dao.job_seeker_dao import JobSeekerDAO

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class JobSeekerService:
    """Business rules for job seeker registration and authentication."""

    def __init__(self, dao: Optional[JobSeekerDAO] = None) -> None:
        self.dao = dao or JobSeekerDAO()

    def register(self, payload: dict[str, Any]) -> dict[str, Any]:
        first_name = (payload.get("first_name") or "").strip()
        email = (payload.get("email") or "").strip().lower()
        password = payload.get("password") or ""
        mobile_number = (payload.get("mobile_number") or "").strip() or None

        if not first_name:
            raise ValueError("first_name is required.")
        if not email or not EMAIL_PATTERN.match(email):
            raise ValueError("A valid email is required.")
        if not password or len(password) < 6:
            raise ValueError("password must be at least 6 characters.")

        if self.dao.email_exists(email):
            raise ValueError("Email is already registered.")
        if mobile_number and self.dao.mobile_exists(mobile_number):
            raise ValueError("Mobile number is already registered.")

        job_seeker = JobSeeker(
            first_name=first_name,
            last_name=(payload.get("last_name") or None),
            email=email,
            mobile_number=mobile_number,
            date_of_birth=payload.get("date_of_birth") or None,
            gender=payload.get("gender") or None,
            location=payload.get("location") or None,
            city=payload.get("city") or None,
            state=payload.get("state") or None,
            pincode=payload.get("pincode") or None,
            profile_summary=payload.get("profile_summary") or None,
            total_experience=self._to_decimal(
                payload.get("total_experience"), Decimal("0.0")
            ),
            current_company=payload.get("current_company") or None,
            current_job_title=payload.get("current_job_title") or None,
            expected_salary=self._to_decimal(payload.get("expected_salary")),
            notice_period=self._to_int(payload.get("notice_period")),
            resume_url=payload.get("resume_url") or None,
            profile_photo=payload.get("profile_photo") or None,
            linkedin_url=payload.get("linkedin_url") or None,
            github_url=payload.get("github_url") or None,
            portfolio_url=payload.get("portfolio_url") or None,
        )

        password_hash = generate_password_hash(password)
        created = self.dao.create_job_seeker(job_seeker, password_hash)
        return {
            "message": "Job seeker registered successfully.",
            "job_seeker": created.to_dict(),
        }

    def login(self, payload: dict[str, Any]) -> dict[str, Any]:
        email = (payload.get("email") or "").strip().lower() or None
        mobile_number = (payload.get("mobile_number") or "").strip() or None
        password = payload.get("password") or ""

        if not password:
            raise ValueError("password is required.")
        if not email and not mobile_number:
            raise ValueError("Provide either email or mobile_number to log in.")

        auth_row = None
        if email:
            auth_row = self.dao.find_auth_by_email(email)
        elif mobile_number:
            auth_row = self.dao.find_auth_by_mobile(mobile_number)

        if auth_row is None or not check_password_hash(
            auth_row["password_hash"], password
        ):
            raise ValueError("Invalid credentials.")

        job_seeker = JobSeeker.from_row(auth_row)
        return {
            "message": "Login successful.",
            "job_seeker": job_seeker.to_dict(),
        }

    def list_job_seekers(self) -> dict[str, Any]:
        """Return all job seeker users."""
        job_seekers = self.dao.find_all()
        return {
            "count": len(job_seekers),
            "job_seekers": [js.to_dict() for js in job_seekers],
        }

    def delete_job_seeker(self, user_id: int) -> dict[str, Any]:
        """Delete a job seeker (and auth user) by user_id."""
        if user_id is None or user_id <= 0:
            raise ValueError("A valid user_id is required.")

        existing = self.dao.find_by_user_id(user_id)
        if existing is None:
            raise LookupError(f"Job seeker with user_id {user_id} not found.")

        deleted = self.dao.delete_by_user_id(user_id)
        if not deleted:
            raise LookupError(f"Job seeker with user_id {user_id} not found.")

        return {
            "message": "Job seeker deleted successfully.",
            "user_id": user_id,
        }

    @staticmethod
    def _to_decimal(value: Any, default: Optional[Decimal] = None) -> Optional[Decimal]:
        if value is None or value == "":
            return default
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError) as exc:
            raise ValueError(f"Invalid decimal value: {value}") from exc

    @staticmethod
    def _to_int(value: Any) -> Optional[int]:
        if value is None or value == "":
            return None
        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid integer value: {value}") from exc
