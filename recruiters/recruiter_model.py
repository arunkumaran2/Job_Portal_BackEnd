"""Recruiter entity matching the recruiters table."""

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class Recruiter:
    """Model/entity for a Recruiter user."""

    first_name: str
    email: str
    company_name: str
    recruiter_id: Optional[int] = None
    user_id: Optional[int] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    designation: Optional[str] = None
    department: Optional[str] = None
    company_email: Optional[str] = None
    company_phone: Optional[str] = None
    company_website: Optional[str] = None
    company_description: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    company_type: Optional[str] = None
    location: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    country: str = "India"
    company_logo: Optional[str] = None
    linkedin_url: Optional[str] = None
    is_verified: bool = False
    status: str = "Active"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    # Used only during registration; never persisted on recruiters
    password: Optional[str] = field(default=None, repr=False)

    def to_dict(self, include_password: bool = False) -> dict[str, Any]:
        """Serialize the entity for API responses."""
        data = asdict(self)
        if not include_password:
            data.pop("password", None)

        for key, value in list(data.items()):
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, bool):
                data[key] = value

        return data

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "Recruiter":
        """Build a Recruiter from a database row mapping."""
        return cls(
            recruiter_id=row.get("recruiter_id"),
            user_id=row.get("user_id"),
            first_name=row.get("first_name"),
            last_name=row.get("last_name"),
            email=row.get("email"),
            phone=row.get("phone"),
            designation=row.get("designation"),
            department=row.get("department"),
            company_name=row.get("company_name"),
            company_email=row.get("company_email"),
            company_phone=row.get("company_phone"),
            company_website=row.get("company_website"),
            company_description=row.get("company_description"),
            industry=row.get("industry"),
            company_size=row.get("company_size"),
            company_type=row.get("company_type"),
            location=row.get("location"),
            city=row.get("city"),
            state=row.get("state"),
            pincode=row.get("pincode"),
            country=row.get("country") or "India",
            company_logo=row.get("company_logo"),
            linkedin_url=row.get("linkedin_url"),
            is_verified=bool(row.get("is_verified", False)),
            status=row.get("status") or "Active",
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )
