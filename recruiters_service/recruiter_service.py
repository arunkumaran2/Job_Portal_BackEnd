"""Service layer: recruiter registration and login business logic."""

import re
from typing import Any, Optional

from werkzeug.security import check_password_hash, generate_password_hash

from recruiters.recruiter_model import Recruiter
from recruiters_dao.recruiter_dao import RecruiterDAO

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
VALID_STATUSES = {"Active", "Inactive", "Blocked"}


class RecruiterService:
    """Business rules for recruiter registration and authentication."""

    def __init__(self, dao: Optional[RecruiterDAO] = None) -> None:
        self.dao = dao or RecruiterDAO()

    def save_recruiter(self, payload: dict[str, Any]) -> dict[str, Any]:
        first_name = (payload.get("first_name") or "").strip()
        email = (payload.get("email") or "").strip().lower()
        password = payload.get("password") or ""
        company_name = (payload.get("company_name") or "").strip()
        phone = (payload.get("phone") or payload.get("mobile_number") or "").strip() or None

        if not first_name:
            raise ValueError("first_name is required.")
        if not email or not EMAIL_PATTERN.match(email):
            raise ValueError("A valid email is required.")
        if not company_name:
            raise ValueError("company_name is required.")
        if not password or len(password) < 6:
            raise ValueError("password must be at least 6 characters.")

        if self.dao.email_exists(email):
            raise ValueError("Email is already registered.")
        if phone and self.dao.phone_exists(phone):
            raise ValueError("Phone number is already registered.")

        status = payload.get("status") or "Active"
        if status not in VALID_STATUSES:
            raise ValueError(
                f"status must be one of: {', '.join(sorted(VALID_STATUSES))}."
            )

        is_verified = payload.get("is_verified", False)
        if isinstance(is_verified, str):
            is_verified = is_verified.strip().lower() in {"1", "true", "yes"}

        recruiter = Recruiter(
            first_name=first_name,
            last_name=(payload.get("last_name") or None),
            email=email,
            phone=phone,
            designation=payload.get("designation") or None,
            department=payload.get("department") or None,
            company_name=company_name,
            company_email=(payload.get("company_email") or "").strip().lower() or None,
            company_phone=payload.get("company_phone") or None,
            company_website=payload.get("company_website") or None,
            company_description=payload.get("company_description") or None,
            industry=payload.get("industry") or None,
            company_size=payload.get("company_size") or None,
            company_type=payload.get("company_type") or None,
            location=payload.get("location") or None,
            city=payload.get("city") or None,
            state=payload.get("state") or None,
            pincode=payload.get("pincode") or None,
            country=payload.get("country") or "India",
            company_logo=payload.get("company_logo") or None,
            linkedin_url=payload.get("linkedin_url") or None,
            is_verified=bool(is_verified),
            status=status,
        )

        password_hash = generate_password_hash(password)
        created = self.dao.create_recruiter(recruiter, password_hash)
        return {
            "message": "Recruiter saved successfully.",
            "recruiter": created.to_dict(),
        }

    def login(self, payload: dict[str, Any]) -> dict[str, Any]:
        email = (payload.get("email") or payload.get("gmail") or "").strip().lower() or None
        phone = (
            payload.get("phone")
            or payload.get("mobile_number")
            or payload.get("mobile")
            or ""
        ).strip() or None
        password = payload.get("password") or ""

        if not password:
            raise ValueError("password is required.")
        if not email and not phone:
            raise ValueError("Provide either email (Gmail) or phone/mobile_number to log in.")

        auth_row = None
        if email:
            auth_row = self.dao.find_auth_by_email(email)
        elif phone:
            auth_row = self.dao.find_auth_by_phone(phone)

        if auth_row is None or not check_password_hash(
            auth_row["password_hash"], password
        ):
            raise ValueError("Invalid credentials.")

        recruiter = Recruiter.from_row(auth_row)
        return {
            "message": "Login successful.",
            "recruiter": recruiter.to_dict(),
        }

    def list_recruiters(self) -> dict[str, Any]:
        """Return all recruiter users."""
        recruiters = self.dao.find_all()
        return {
            "count": len(recruiters),
            "recruiters": [r.to_dict() for r in recruiters],
        }

    def delete_recruiter(self, user_id: int) -> dict[str, Any]:
        """Delete a recruiter (and auth user) by user_id."""
        if user_id is None or user_id <= 0:
            raise ValueError("A valid user_id is required.")

        existing = self.dao.find_by_user_id(user_id)
        if existing is None:
            raise LookupError(f"Recruiter with user_id {user_id} not found.")

        deleted = self.dao.delete_by_user_id(user_id)
        if not deleted:
            raise LookupError(f"Recruiter with user_id {user_id} not found.")

        return {
            "message": "Recruiter deleted successfully.",
            "user_id": user_id,
        }
