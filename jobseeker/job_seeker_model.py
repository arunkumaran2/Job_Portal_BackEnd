"""Job Seeker entity matching the job_seekers table."""

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional


@dataclass
class JobSeeker:
    """Model/entity for a Job Seeker user."""

    first_name: str
    email: str
    user_id: Optional[int] = None
    job_seeker_id: Optional[int] = None
    last_name: Optional[str] = None
    mobile_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    profile_summary: Optional[str] = None
    total_experience: Decimal = field(default_factory=lambda: Decimal("0.0"))
    current_company: Optional[str] = None
    current_job_title: Optional[str] = None
    expected_salary: Optional[Decimal] = None
    notice_period: Optional[int] = None
    resume_url: Optional[str] = None
    profile_photo: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    # Used only during registration; never persisted on job_seekers
    password: Optional[str] = field(default=None, repr=False)

    def to_dict(self, include_password: bool = False) -> dict[str, Any]:
        """Serialize the entity for API responses."""
        data = asdict(self)
        if not include_password:
            data.pop("password", None)

        for key, value in list(data.items()):
            if isinstance(value, (date, datetime)):
                data[key] = value.isoformat()
            elif isinstance(value, Decimal):
                data[key] = float(value)

        return data

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "JobSeeker":
        """Build a JobSeeker from a database row mapping."""
        return cls(
            job_seeker_id=row.get("job_seeker_id"),
            user_id=row.get("user_id"),
            first_name=row.get("first_name"),
            last_name=row.get("last_name"),
            email=row.get("email"),
            mobile_number=row.get("mobile_number"),
            date_of_birth=row.get("date_of_birth"),
            gender=row.get("gender"),
            location=row.get("location"),
            city=row.get("city"),
            state=row.get("state"),
            pincode=row.get("pincode"),
            profile_summary=row.get("profile_summary"),
            total_experience=row.get("total_experience") or Decimal("0.0"),
            current_company=row.get("current_company"),
            current_job_title=row.get("current_job_title"),
            expected_salary=row.get("expected_salary"),
            notice_period=row.get("notice_period"),
            resume_url=row.get("resume_url"),
            profile_photo=row.get("profile_photo"),
            linkedin_url=row.get("linkedin_url"),
            github_url=row.get("github_url"),
            portfolio_url=row.get("portfolio_url"),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )
