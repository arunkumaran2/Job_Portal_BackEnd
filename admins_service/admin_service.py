"""Service layer: admin registration and login business logic."""

import re
from typing import Any, Optional

from werkzeug.security import check_password_hash, generate_password_hash

from admins.admin_model import Admin
from admins_dao.admin_dao import AdminDAO

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
VALID_ROLES = {"SUPER_ADMIN", "ADMIN"}
VALID_STATUSES = {"ACTIVE", "INACTIVE", "BLOCKED"}


class AdminService:
    """Business rules for admin registration and authentication."""

    def __init__(self, dao: Optional[AdminDAO] = None) -> None:
        self.dao = dao or AdminDAO()

    def save_admin(self, payload: dict[str, Any]) -> dict[str, Any]:
        first_name = (payload.get("first_name") or "").strip()
        email = (payload.get("email") or "").strip().lower()
        password = payload.get("password") or ""
        phone = (
            payload.get("phone") or payload.get("mobile_number") or ""
        ).strip() or None

        if not first_name:
            raise ValueError("first_name is required.")
        if not email or not EMAIL_PATTERN.match(email):
            raise ValueError("A valid email is required.")
        if not password or len(password) < 6:
            raise ValueError("password must be at least 6 characters.")

        if self.dao.email_exists(email):
            raise ValueError("Email is already registered.")
        if phone and self.dao.phone_exists(phone):
            raise ValueError("Phone number is already registered.")

        role = (payload.get("role") or "ADMIN").strip().upper()
        if role not in VALID_ROLES:
            raise ValueError(
                f"role must be one of: {', '.join(sorted(VALID_ROLES))}."
            )

        status = (payload.get("status") or "ACTIVE").strip().upper()
        if status not in VALID_STATUSES:
            raise ValueError(
                f"status must be one of: {', '.join(sorted(VALID_STATUSES))}."
            )

        admin = Admin(
            first_name=first_name,
            last_name=(payload.get("last_name") or None),
            email=email,
            phone=phone,
            role=role,
            status=status,
        )

        password_hash = generate_password_hash(password)
        created = self.dao.create_admin(admin, password_hash)
        return {
            "message": "Admin saved successfully.",
            "admin": created.to_dict(),
        }

    def login(self, payload: dict[str, Any]) -> dict[str, Any]:
        email = (
            payload.get("email") or payload.get("gmail") or ""
        ).strip().lower() or None
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
            raise ValueError(
                "Provide either email (Gmail) or phone/mobile_number to log in."
            )

        auth_row = None
        if email:
            auth_row = self.dao.find_auth_by_email(email)
        elif phone:
            auth_row = self.dao.find_auth_by_phone(phone)

        if auth_row is None or not check_password_hash(
            auth_row["password_hash"], password
        ):
            raise ValueError("Invalid credentials.")

        if auth_row.get("status") == "BLOCKED":
            raise ValueError("Admin account is blocked.")
        if auth_row.get("status") == "INACTIVE":
            raise ValueError("Admin account is inactive.")

        admin = Admin.from_row(auth_row)
        if admin.admin_id is not None:
            self.dao.update_last_login(admin.admin_id)
            refreshed = self.dao.find_by_admin_id(admin.admin_id)
            if refreshed is not None:
                admin = refreshed

        return {
            "message": "Login successful.",
            "admin": admin.to_dict(),
        }

    def list_admins(self) -> dict[str, Any]:
        """Return all admin users."""
        admins = self.dao.find_all()
        return {
            "count": len(admins),
            "admins": [a.to_dict() for a in admins],
        }

    def delete_admin(self, user_id: int) -> dict[str, Any]:
        """Delete an admin (and auth user) by user_id."""
        if user_id is None or user_id <= 0:
            raise ValueError("A valid user_id is required.")

        existing = self.dao.find_by_user_id(user_id)
        if existing is None:
            raise LookupError(f"Admin with user_id {user_id} not found.")

        deleted = self.dao.delete_by_user_id(user_id)
        if not deleted:
            raise LookupError(f"Admin with user_id {user_id} not found.")

        return {
            "message": "Admin deleted successfully.",
            "user_id": user_id,
        }
