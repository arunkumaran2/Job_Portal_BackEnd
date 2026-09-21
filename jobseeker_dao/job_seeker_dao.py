"""DAO layer: MySQL persistence for job seekers and auth users."""

from typing import Any, Optional

from mysql.connector import Error

from db_connection.config import get_db_connection
from jobseeker.job_seeker_model import JobSeeker


class JobSeekerDAO:
    """Database access for users and job_seekers tables."""

    def email_exists(self, email: str) -> bool:
        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT 1 FROM users WHERE email = %s LIMIT 1",
                (email,),
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            connection.close()

    def mobile_exists(self, mobile_number: str) -> bool:
        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT 1 FROM users WHERE mobile_number = %s LIMIT 1",
                (mobile_number,),
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            connection.close()

    def create_job_seeker(self, job_seeker: JobSeeker, password_hash: str) -> JobSeeker:
        """Insert into users then job_seekers in a single transaction."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                INSERT INTO users (email, mobile_number, password_hash, role)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    job_seeker.email,
                    job_seeker.mobile_number,
                    password_hash,
                    "job_seeker",
                ),
            )
            user_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO job_seekers (
                    user_id, first_name, last_name, email, mobile_number,
                    date_of_birth, gender, location, city, state, pincode,
                    profile_summary, total_experience, current_company,
                    current_job_title, expected_salary, notice_period,
                    resume_url, profile_photo, linkedin_url, github_url,
                    portfolio_url
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s,
                    %s
                )
                """,
                (
                    user_id,
                    job_seeker.first_name,
                    job_seeker.last_name,
                    job_seeker.email,
                    job_seeker.mobile_number,
                    job_seeker.date_of_birth,
                    job_seeker.gender,
                    job_seeker.location,
                    job_seeker.city,
                    job_seeker.state,
                    job_seeker.pincode,
                    job_seeker.profile_summary,
                    job_seeker.total_experience,
                    job_seeker.current_company,
                    job_seeker.current_job_title,
                    job_seeker.expected_salary,
                    job_seeker.notice_period,
                    job_seeker.resume_url,
                    job_seeker.profile_photo,
                    job_seeker.linkedin_url,
                    job_seeker.github_url,
                    job_seeker.portfolio_url,
                ),
            )
            job_seeker_id = cursor.lastrowid
            connection.commit()

            created = self.find_by_job_seeker_id(job_seeker_id)
            if created is None:
                raise RuntimeError("Failed to load newly created job seeker.")
            return created
        except Error:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

    def find_by_job_seeker_id(self, job_seeker_id: int) -> Optional[JobSeeker]:
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM job_seekers WHERE job_seeker_id = %s",
                (job_seeker_id,),
            )
            row = cursor.fetchone()
            return JobSeeker.from_row(row) if row else None
        finally:
            cursor.close()
            connection.close()

    def find_auth_by_email(self, email: str) -> Optional[dict[str, Any]]:
        """Return user auth row joined with job seeker profile by email."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT js.*, u.password_hash
                FROM users u
                INNER JOIN job_seekers js ON js.user_id = u.user_id
                WHERE u.email = %s
                LIMIT 1
                """,
                (email,),
            )
            return cursor.fetchone()
        finally:
            cursor.close()
            connection.close()

    def find_auth_by_mobile(self, mobile_number: str) -> Optional[dict[str, Any]]:
        """Return user auth row joined with job seeker profile by mobile."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT js.*, u.password_hash
                FROM users u
                INNER JOIN job_seekers js ON js.user_id = u.user_id
                WHERE u.mobile_number = %s
                LIMIT 1
                """,
                (mobile_number,),
            )
            return cursor.fetchone()
        finally:
            cursor.close()
            connection.close()
