"""DAO layer: MySQL persistence for job applications and resumes."""

from typing import Any, Optional

from mysql.connector import Error

from db_connection.config import get_db_connection
from job_applications.job_application_model import JobApplication


class JobApplicationDAO:
    """Database access for job_applications and related lookups."""

    def job_exists(self, job_id: int) -> bool:
        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT 1 FROM jobs WHERE job_id = %s LIMIT 1",
                (job_id,),
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            connection.close()

    def get_job_status(self, job_id: int) -> Optional[str]:
        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT status FROM jobs WHERE job_id = %s LIMIT 1",
                (job_id,),
            )
            row = cursor.fetchone()
            return row[0] if row else None
        finally:
            cursor.close()
            connection.close()

    def job_seeker_exists(self, job_seeker_id: int) -> bool:
        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT 1 FROM job_seekers WHERE job_seeker_id = %s LIMIT 1",
                (job_seeker_id,),
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            connection.close()

    def find_job_seeker_by_id(self, job_seeker_id: int) -> Optional[dict[str, Any]]:
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM job_seekers WHERE job_seeker_id = %s",
                (job_seeker_id,),
            )
            return cursor.fetchone()
        finally:
            cursor.close()
            connection.close()

    def update_resume_url(
        self, job_seeker_id: int, resume_url: str
    ) -> Optional[dict[str, Any]]:
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """
                UPDATE job_seekers
                SET resume_url = %s
                WHERE job_seeker_id = %s
                """,
                (resume_url, job_seeker_id),
            )
            if cursor.rowcount == 0:
                connection.rollback()
                return None
            connection.commit()
            return self.find_job_seeker_by_id(job_seeker_id)
        except Error:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

    def application_exists(self, job_id: int, job_seeker_id: int) -> bool:
        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT 1 FROM job_applications
                WHERE job_id = %s AND job_seeker_id = %s
                LIMIT 1
                """,
                (job_id, job_seeker_id),
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            connection.close()

    def create_application(self, application: JobApplication) -> JobApplication:
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """
                INSERT INTO job_applications (
                    job_id, job_seeker_id, cover_letter, status
                ) VALUES (%s, %s, %s, %s)
                """,
                (
                    application.job_id,
                    application.job_seeker_id,
                    application.cover_letter,
                    application.status,
                ),
            )
            application_id = cursor.lastrowid
            connection.commit()
            created = self.find_by_id(application_id)
            if created is None:
                raise RuntimeError("Failed to load newly created application.")
            return created
        except Error:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

    def find_by_id(self, application_id: int) -> Optional[JobApplication]:
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT
                    ja.*,
                    j.job_title,
                    j.company_name,
                    js.first_name,
                    js.last_name,
                    js.email,
                    js.mobile_number,
                    js.resume_url
                FROM job_applications ja
                INNER JOIN jobs j ON j.job_id = ja.job_id
                INNER JOIN job_seekers js ON js.job_seeker_id = ja.job_seeker_id
                WHERE ja.application_id = %s
                """,
                (application_id,),
            )
            row = cursor.fetchone()
            return JobApplication.from_row(row) if row else None
        finally:
            cursor.close()
            connection.close()

    def find_by_job_id(self, job_id: int) -> list[JobApplication]:
        """Return all applicants for a job (recruiter view)."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT
                    ja.*,
                    j.job_title,
                    j.company_name,
                    js.first_name,
                    js.last_name,
                    js.email,
                    js.mobile_number,
                    js.resume_url
                FROM job_applications ja
                INNER JOIN jobs j ON j.job_id = ja.job_id
                INNER JOIN job_seekers js ON js.job_seeker_id = ja.job_seeker_id
                WHERE ja.job_id = %s
                ORDER BY ja.applied_at DESC
                """,
                (job_id,),
            )
            rows = cursor.fetchall()
            return [JobApplication.from_row(row) for row in rows]
        finally:
            cursor.close()
            connection.close()

    def find_by_job_seeker_id(self, job_seeker_id: int) -> list[JobApplication]:
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT
                    ja.*,
                    j.job_title,
                    j.company_name,
                    js.first_name,
                    js.last_name,
                    js.email,
                    js.mobile_number,
                    js.resume_url
                FROM job_applications ja
                INNER JOIN jobs j ON j.job_id = ja.job_id
                INNER JOIN job_seekers js ON js.job_seeker_id = ja.job_seeker_id
                WHERE ja.job_seeker_id = %s
                ORDER BY ja.applied_at DESC
                """,
                (job_seeker_id,),
            )
            rows = cursor.fetchall()
            return [JobApplication.from_row(row) for row in rows]
        finally:
            cursor.close()
            connection.close()

    def update_status(
        self, application_id: int, status: str
    ) -> Optional[JobApplication]:
        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                UPDATE job_applications
                SET status = %s
                WHERE application_id = %s
                """,
                (status, application_id),
            )
            if cursor.rowcount == 0:
                connection.rollback()
                return None
            connection.commit()
            return self.find_by_id(application_id)
        except Error:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()
