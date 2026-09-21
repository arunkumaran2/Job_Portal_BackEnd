"""Service layer: job posting and listing business logic."""

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

from job.job_model import Job
from job_dao.job_dao import JobDAO

VALID_JOB_TYPES = {
    "Full-Time",
    "Part-Time",
    "Contract",
    "Internship",
    "Freelance",
}
VALID_WORK_MODES = {"Onsite", "Remote", "Hybrid"}
VALID_SALARY_TYPES = {"Monthly", "Yearly"}
VALID_JOB_STATUSES = {"Draft", "Active", "Closed", "Expired"}
VALID_SKILL_LEVELS = {"Beginner", "Intermediate", "Advanced"}


class JobService:
    """Business rules for jobs."""

    def __init__(self, dao: Optional[JobDAO] = None) -> None:
        self.dao = dao or JobDAO()

    def create_job(self, payload: dict[str, Any]) -> dict[str, Any]:
        job, skills, category_ids = self._build_job_from_payload(payload, require_all=True)

        if not self.dao.recruiter_exists(job.recruiter_id):
            raise ValueError(f"Recruiter with recruiter_id {job.recruiter_id} not found.")

        for category_id in category_ids:
            if not self.dao.category_exists(category_id):
                raise ValueError(f"Category with category_id {category_id} not found.")

        created = self.dao.create_job(job, skills, category_ids)
        return {
            "message": "Job created successfully.",
            "job": created.to_dict(),
        }

    def list_jobs(self) -> dict[str, Any]:
        jobs = self.dao.find_all()
        return {
            "count": len(jobs),
            "jobs": [job.to_dict() for job in jobs],
        }

    def get_job(self, job_id: int) -> dict[str, Any]:
        if job_id is None or job_id <= 0:
            raise ValueError("A valid job_id is required.")

        job = self.dao.find_by_id(job_id)
        if job is None:
            raise LookupError(f"Job with job_id {job_id} not found.")

        return {"job": job.to_dict()}

    def update_job(self, job_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        if job_id is None or job_id <= 0:
            raise ValueError("A valid job_id is required.")

        existing = self.dao.find_by_id(job_id)
        if existing is None:
            raise LookupError(f"Job with job_id {job_id} not found.")

        # Merge with existing values so partial updates are allowed
        merged = existing.to_dict()
        merged.update({k: v for k, v in payload.items() if v is not None or k in payload})
        # Keep recruiter_id from existing unless explicitly provided
        if "recruiter_id" not in payload:
            merged["recruiter_id"] = existing.recruiter_id

        job, skills, category_ids = self._build_job_from_payload(
            merged, require_all=True
        )
        job.job_id = job_id

        if not self.dao.recruiter_exists(job.recruiter_id):
            raise ValueError(f"Recruiter with recruiter_id {job.recruiter_id} not found.")

        replace_skills = "skills" in payload
        replace_categories = "category_ids" in payload or "categories" in payload

        if replace_categories:
            for category_id in category_ids:
                if not self.dao.category_exists(category_id):
                    raise ValueError(
                        f"Category with category_id {category_id} not found."
                    )

        updated = self.dao.update_job(
            job_id,
            job,
            skills=skills if replace_skills else None,
            category_ids=category_ids if replace_categories else None,
        )
        if updated is None:
            raise LookupError(f"Job with job_id {job_id} not found.")

        return {
            "message": "Job updated successfully.",
            "job": updated.to_dict(),
        }

    def delete_job(self, job_id: int) -> dict[str, Any]:
        if job_id is None or job_id <= 0:
            raise ValueError("A valid job_id is required.")

        existing = self.dao.find_by_id(job_id)
        if existing is None:
            raise LookupError(f"Job with job_id {job_id} not found.")

        deleted = self.dao.delete_by_id(job_id)
        if not deleted:
            raise LookupError(f"Job with job_id {job_id} not found.")

        return {
            "message": "Job deleted successfully.",
            "job_id": job_id,
        }

    def _build_job_from_payload(
        self, payload: dict[str, Any], require_all: bool = True
    ) -> tuple[Job, list[dict[str, Any]], list[int]]:
        job_title = (payload.get("job_title") or "").strip()
        job_description = (payload.get("job_description") or "").strip()
        company_name = (payload.get("company_name") or "").strip()
        recruiter_id = self._to_int(payload.get("recruiter_id"), required=require_all)

        if require_all:
            if not job_title:
                raise ValueError("job_title is required.")
            if not job_description:
                raise ValueError("job_description is required.")
            if not company_name:
                raise ValueError("company_name is required.")
            if recruiter_id is None:
                raise ValueError("recruiter_id is required.")

        job_type = payload.get("job_type") or "Full-Time"
        if job_type not in VALID_JOB_TYPES:
            raise ValueError(
                f"job_type must be one of: {', '.join(sorted(VALID_JOB_TYPES))}."
            )

        work_mode = payload.get("work_mode") or "Onsite"
        if work_mode not in VALID_WORK_MODES:
            raise ValueError(
                f"work_mode must be one of: {', '.join(sorted(VALID_WORK_MODES))}."
            )

        salary_type = payload.get("salary_type") or None
        if salary_type and salary_type not in VALID_SALARY_TYPES:
            raise ValueError(
                f"salary_type must be one of: {', '.join(sorted(VALID_SALARY_TYPES))}."
            )

        status = payload.get("status") or "Draft"
        if status not in VALID_JOB_STATUSES:
            raise ValueError(
                f"status must be one of: {', '.join(sorted(VALID_JOB_STATUSES))}."
            )

        experience_min = self._to_int(payload.get("experience_min"), default=0) or 0
        experience_max = self._to_int(payload.get("experience_max"))
        if experience_max is not None and experience_max < experience_min:
            raise ValueError("experience_max cannot be less than experience_min.")

        salary_min = self._to_decimal(payload.get("salary_min"))
        salary_max = self._to_decimal(payload.get("salary_max"))
        if (
            salary_min is not None
            and salary_max is not None
            and salary_max < salary_min
        ):
            raise ValueError("salary_max cannot be less than salary_min.")

        openings = self._to_int(payload.get("openings"), default=1) or 1
        if openings < 1:
            raise ValueError("openings must be at least 1.")

        skills = self._parse_skills(payload.get("skills") or [])
        category_ids = self._parse_category_ids(payload)

        job = Job(
            recruiter_id=recruiter_id or 0,
            job_title=job_title,
            job_description=job_description,
            company_name=company_name,
            job_type=job_type,
            work_mode=work_mode,
            experience_min=experience_min,
            experience_max=experience_max,
            salary_min=salary_min,
            salary_max=salary_max,
            salary_type=salary_type,
            location=(payload.get("location") or None),
            city=(payload.get("city") or None),
            state=(payload.get("state") or None),
            country=payload.get("country") or "India",
            education_required=payload.get("education_required") or None,
            department=payload.get("department") or None,
            industry=payload.get("industry") or None,
            openings=openings,
            application_deadline=self._to_date(payload.get("application_deadline")),
            status=status,
        )
        return job, skills, category_ids

    @staticmethod
    def _parse_skills(raw_skills: Any) -> list[dict[str, Any]]:
        if raw_skills is None:
            return []
        if not isinstance(raw_skills, list):
            raise ValueError("skills must be a list.")

        parsed: list[dict[str, Any]] = []
        for item in raw_skills:
            if isinstance(item, str):
                skill_name = item.strip()
                skill_level = "Intermediate"
            elif isinstance(item, dict):
                skill_name = (item.get("skill_name") or "").strip()
                skill_level = item.get("skill_level") or "Intermediate"
            else:
                raise ValueError("Each skill must be a string or an object.")

            if not skill_name:
                raise ValueError("skill_name is required for each skill.")
            if skill_level not in VALID_SKILL_LEVELS:
                raise ValueError(
                    "skill_level must be one of: "
                    + ", ".join(sorted(VALID_SKILL_LEVELS))
                    + "."
                )
            parsed.append({"skill_name": skill_name, "skill_level": skill_level})
        return parsed

    @staticmethod
    def _parse_category_ids(payload: dict[str, Any]) -> list[int]:
        raw = payload.get("category_ids")
        if raw is None and "categories" in payload:
            raw = payload.get("categories")
        if raw is None:
            return []
        if not isinstance(raw, list):
            raise ValueError("category_ids must be a list of integers.")

        ids: list[int] = []
        for item in raw:
            if isinstance(item, dict):
                value = item.get("category_id")
            else:
                value = item
            try:
                category_id = int(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid category_id: {value}") from exc
            if category_id <= 0:
                raise ValueError("category_id must be a positive integer.")
            if category_id not in ids:
                ids.append(category_id)
        return ids

    @staticmethod
    def _to_int(
        value: Any, default: Optional[int] = None, required: bool = False
    ) -> Optional[int]:
        if value is None or value == "":
            if required:
                raise ValueError("A required integer field is missing.")
            return default
        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid integer value: {value}") from exc

    @staticmethod
    def _to_decimal(value: Any) -> Optional[Decimal]:
        if value is None or value == "":
            return None
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError) as exc:
            raise ValueError(f"Invalid decimal value: {value}") from exc

    @staticmethod
    def _to_date(value: Any) -> Optional[date]:
        if value is None or value == "":
            return None
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        if isinstance(value, datetime):
            return value.date()
        try:
            return date.fromisoformat(str(value)[:10])
        except ValueError as exc:
            raise ValueError(
                "application_deadline must be a valid date (YYYY-MM-DD)."
            ) from exc
