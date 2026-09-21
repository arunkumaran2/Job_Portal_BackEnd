"""Job-related entities matching jobs, skills, applications, and category tables."""

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional


def _serialize_value(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


@dataclass
class JobSkill:
    """Model for a skill required by a job."""

    skill_name: str
    job_skill_id: Optional[int] = None
    job_id: Optional[int] = None
    skill_level: str = "Intermediate"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "JobSkill":
        return cls(
            job_skill_id=row.get("job_skill_id"),
            job_id=row.get("job_id"),
            skill_name=row.get("skill_name"),
            skill_level=row.get("skill_level") or "Intermediate",
        )


@dataclass
class JobCategory:
    """Model for a job category."""

    category_name: str
    category_id: Optional[int] = None
    description: Optional[str] = None
    status: str = "Active"
    created_at: Optional[datetime] = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for key, value in list(data.items()):
            data[key] = _serialize_value(value)
        return data

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "JobCategory":
        return cls(
            category_id=row.get("category_id"),
            category_name=row.get("category_name"),
            description=row.get("description"),
            status=row.get("status") or "Active",
            created_at=row.get("created_at"),
        )


@dataclass
class JobApplication:
    """Model for a job application."""

    job_id: int
    job_seeker_id: int
    application_id: Optional[int] = None
    resume_url: Optional[str] = None
    cover_letter: Optional[str] = None
    application_status: str = "Applied"
    applied_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    # Optional joined job fields for list responses
    job_title: Optional[str] = None
    company_name: Optional[str] = None

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
            resume_url=row.get("resume_url"),
            cover_letter=row.get("cover_letter"),
            application_status=row.get("application_status") or "Applied",
            applied_at=row.get("applied_at"),
            updated_at=row.get("updated_at"),
            job_title=row.get("job_title"),
            company_name=row.get("company_name"),
        )


@dataclass
class SavedJob:
    """Model for a saved job bookmark."""

    job_id: int
    job_seeker_id: int
    saved_job_id: Optional[int] = None
    saved_at: Optional[datetime] = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for key, value in list(data.items()):
            data[key] = _serialize_value(value)
        return data

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "SavedJob":
        return cls(
            saved_job_id=row.get("saved_job_id"),
            job_id=row.get("job_id"),
            job_seeker_id=row.get("job_seeker_id"),
            saved_at=row.get("saved_at"),
        )


@dataclass
class Job:
    """Model/entity for a Job posting."""

    job_title: str
    job_description: str
    company_name: str
    recruiter_id: int
    job_id: Optional[int] = None
    job_type: str = "Full-Time"
    work_mode: str = "Onsite"
    experience_min: int = 0
    experience_max: Optional[int] = None
    salary_min: Optional[Decimal] = None
    salary_max: Optional[Decimal] = None
    salary_type: Optional[str] = None
    location: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "India"
    education_required: Optional[str] = None
    department: Optional[str] = None
    industry: Optional[str] = None
    openings: int = 1
    application_deadline: Optional[date] = None
    status: str = "Draft"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    skills: list[JobSkill] = field(default_factory=list)
    categories: list[JobCategory] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["skills"] = [skill.to_dict() for skill in self.skills]
        data["categories"] = [category.to_dict() for category in self.categories]
        for key, value in list(data.items()):
            if key in ("skills", "categories"):
                continue
            data[key] = _serialize_value(value)
        return data

    @classmethod
    def from_row(
        cls,
        row: dict[str, Any],
        skills: Optional[list[JobSkill]] = None,
        categories: Optional[list[JobCategory]] = None,
    ) -> "Job":
        return cls(
            job_id=row.get("job_id"),
            recruiter_id=row.get("recruiter_id"),
            job_title=row.get("job_title"),
            job_description=row.get("job_description"),
            company_name=row.get("company_name"),
            job_type=row.get("job_type") or "Full-Time",
            work_mode=row.get("work_mode") or "Onsite",
            experience_min=row.get("experience_min") if row.get("experience_min") is not None else 0,
            experience_max=row.get("experience_max"),
            salary_min=row.get("salary_min"),
            salary_max=row.get("salary_max"),
            salary_type=row.get("salary_type"),
            location=row.get("location"),
            city=row.get("city"),
            state=row.get("state"),
            country=row.get("country") or "India",
            education_required=row.get("education_required"),
            department=row.get("department"),
            industry=row.get("industry"),
            openings=row.get("openings") if row.get("openings") is not None else 1,
            application_deadline=row.get("application_deadline"),
            status=row.get("status") or "Draft",
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
            skills=skills or [],
            categories=categories or [],
        )
