"""DAO layer: MySQL persistence for jobs, skills, and categories."""

from typing import Any, Optional

from mysql.connector import Error

from db_connection.config import get_db_connection
from job.job_model import Job, JobCategory, JobSkill


class JobDAO:
    """Database access for jobs and related tables."""

    def recruiter_exists(self, recruiter_id: int) -> bool:
        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT 1 FROM recruiters WHERE recruiter_id = %s LIMIT 1",
                (recruiter_id,),
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            connection.close()

    def create_job(
        self,
        job: Job,
        skills: list[dict[str, Any]],
        category_ids: list[int],
    ) -> Job:
        """Insert a job with optional skills and category mappings."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """
                INSERT INTO jobs (
                    recruiter_id, job_title, job_description, company_name,
                    job_type, work_mode, experience_min, experience_max,
                    salary_min, salary_max, salary_type, location, city,
                    state, country, education_required, department, industry,
                    openings, application_deadline, status
                ) VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s
                )
                """,
                (
                    job.recruiter_id,
                    job.job_title,
                    job.job_description,
                    job.company_name,
                    job.job_type,
                    job.work_mode,
                    job.experience_min,
                    job.experience_max,
                    job.salary_min,
                    job.salary_max,
                    job.salary_type,
                    job.location,
                    job.city,
                    job.state,
                    job.country,
                    job.education_required,
                    job.department,
                    job.industry,
                    job.openings,
                    job.application_deadline,
                    job.status,
                ),
            )
            job_id = cursor.lastrowid
            self._replace_skills(cursor, job_id, skills)
            self._replace_category_mappings(cursor, job_id, category_ids)
            connection.commit()

            created = self.find_by_id(job_id)
            if created is None:
                raise RuntimeError("Failed to load newly created job.")
            return created
        except Error:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

    def update_job(
        self,
        job_id: int,
        job: Job,
        skills: Optional[list[dict[str, Any]]] = None,
        category_ids: Optional[list[int]] = None,
    ) -> Optional[Job]:
        """Update a job; optionally replace skills and category mappings."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """
                UPDATE jobs SET
                    recruiter_id = %s,
                    job_title = %s,
                    job_description = %s,
                    company_name = %s,
                    job_type = %s,
                    work_mode = %s,
                    experience_min = %s,
                    experience_max = %s,
                    salary_min = %s,
                    salary_max = %s,
                    salary_type = %s,
                    location = %s,
                    city = %s,
                    state = %s,
                    country = %s,
                    education_required = %s,
                    department = %s,
                    industry = %s,
                    openings = %s,
                    application_deadline = %s,
                    status = %s
                WHERE job_id = %s
                """,
                (
                    job.recruiter_id,
                    job.job_title,
                    job.job_description,
                    job.company_name,
                    job.job_type,
                    job.work_mode,
                    job.experience_min,
                    job.experience_max,
                    job.salary_min,
                    job.salary_max,
                    job.salary_type,
                    job.location,
                    job.city,
                    job.state,
                    job.country,
                    job.education_required,
                    job.department,
                    job.industry,
                    job.openings,
                    job.application_deadline,
                    job.status,
                    job_id,
                ),
            )
            if cursor.rowcount == 0:
                connection.rollback()
                return None

            if skills is not None:
                self._replace_skills(cursor, job_id, skills)
            if category_ids is not None:
                self._replace_category_mappings(cursor, job_id, category_ids)

            connection.commit()
            return self.find_by_id(job_id)
        except Error:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

    def find_by_id(self, job_id: int) -> Optional[Job]:
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM jobs WHERE job_id = %s", (job_id,))
            row = cursor.fetchone()
            if not row:
                return None
            skills = self._fetch_skills(cursor, job_id)
            categories = self._fetch_categories(cursor, job_id)
            return Job.from_row(row, skills=skills, categories=categories)
        finally:
            cursor.close()
            connection.close()

    def find_all(self) -> list[Job]:
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM jobs ORDER BY job_id DESC")
            rows = cursor.fetchall()
            jobs: list[Job] = []
            for row in rows:
                job_id = row["job_id"]
                skills = self._fetch_skills(cursor, job_id)
                categories = self._fetch_categories(cursor, job_id)
                jobs.append(Job.from_row(row, skills=skills, categories=categories))
            return jobs
        finally:
            cursor.close()
            connection.close()

    def delete_by_id(self, job_id: int) -> bool:
        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM jobs WHERE job_id = %s", (job_id,))
            deleted = cursor.rowcount > 0
            connection.commit()
            return deleted
        except Error:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

    def category_exists(self, category_id: int) -> bool:
        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT 1 FROM job_categories WHERE category_id = %s LIMIT 1",
                (category_id,),
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def _replace_skills(cursor, job_id: int, skills: list[dict[str, Any]]) -> None:
        cursor.execute("DELETE FROM job_skills WHERE job_id = %s", (job_id,))
        for skill in skills:
            cursor.execute(
                """
                INSERT INTO job_skills (job_id, skill_name, skill_level)
                VALUES (%s, %s, %s)
                """,
                (
                    job_id,
                    skill["skill_name"],
                    skill.get("skill_level") or "Intermediate",
                ),
            )

    @staticmethod
    def _replace_category_mappings(
        cursor, job_id: int, category_ids: list[int]
    ) -> None:
        cursor.execute(
            "DELETE FROM job_category_mapping WHERE job_id = %s", (job_id,)
        )
        for category_id in category_ids:
            cursor.execute(
                """
                INSERT INTO job_category_mapping (job_id, category_id)
                VALUES (%s, %s)
                """,
                (job_id, category_id),
            )

    @staticmethod
    def _fetch_skills(cursor, job_id: int) -> list[JobSkill]:
        cursor.execute(
            "SELECT * FROM job_skills WHERE job_id = %s ORDER BY job_skill_id ASC",
            (job_id,),
        )
        return [JobSkill.from_row(row) for row in cursor.fetchall()]

    @staticmethod
    def _fetch_categories(cursor, job_id: int) -> list[JobCategory]:
        cursor.execute(
            """
            SELECT c.*
            FROM job_categories c
            INNER JOIN job_category_mapping m ON m.category_id = c.category_id
            WHERE m.job_id = %s
            ORDER BY c.category_id ASC
            """,
            (job_id,),
        )
        return [JobCategory.from_row(row) for row in cursor.fetchall()]
