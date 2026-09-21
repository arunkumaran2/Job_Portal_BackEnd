"""Job application entity matching the job_applications table."""

from dataclasses import asdict, dataclass
from datetime import date, datetime
from typing import Any, Optional


def _serialize_value(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


@dataclass
class JobApplication:
    """Model/entity for a job application."""

    job_id: int
    job_seeker_id: int
    application_id: Optional[int] = None
    cover_letter: Optional[str] = None
    status: str = "Applied"
    applied_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    # Optional joined fields for API responses
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    mobile_number: Optional[str] = None
    resume_url: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for key, value in list(data.items()):
            data[key] = _serialize_value(value)
        return data

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "JobApplication":
        return cls(
            application_id=row.get("application_id"),
            job_id=row.get("job_id"),
            job_seeker_id=row.get("job_seeker_id"),
            cover_letter=row.get("cover_letter"),
            status=row.get("status") or "Applied",
            applied_at=row.get("applied_at"),
            updated_at=row.get("updated_at"),
            job_title=row.get("job_title"),
            company_name=row.get("company_name"),
            first_name=row.get("first_name"),
            last_name=row.get("last_name"),
            email=row.get("email"),
            mobile_number=row.get("mobile_number"),
            resume_url=row.get("resume_url"),
        )
