"""DAO layer: MySQL persistence for recruiters and auth users."""

from typing import Any, Optional

from mysql.connector import Error

from db_connection.config import get_db_connection
from recruiters.recruiter_model import Recruiter


class RecruiterDAO:
    """Database access for users and recruiters tables."""

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

    def phone_exists(self, phone: str) -> bool:
        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT 1 FROM users WHERE mobile_number = %s LIMIT 1",
                (phone,),
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            connection.close()

    def create_recruiter(self, recruiter: Recruiter, password_hash: str) -> Recruiter:
        """Insert into users then recruiters in a single transaction."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                INSERT INTO users (email, mobile_number, password_hash, role)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    recruiter.email,
                    recruiter.phone,
                    password_hash,
                    "recruiter",
                ),
            )
            user_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO recruiters (
                    user_id, first_name, last_name, email, phone,
                    designation, department, company_name, company_email,
                    company_phone, company_website, company_description,
                    industry, company_size, company_type, location, city,
                    state, pincode, country, company_logo, linkedin_url,
                    is_verified, status
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s
                )
                """,
                (
                    user_id,
                    recruiter.first_name,
                    recruiter.last_name,
                    recruiter.email,
                    recruiter.phone,
                    recruiter.designation,
                    recruiter.department,
                    recruiter.company_name,
                    recruiter.company_email,
                    recruiter.company_phone,
                    recruiter.company_website,
                    recruiter.company_description,
                    recruiter.industry,
                    recruiter.company_size,
                    recruiter.company_type,
                    recruiter.location,
                    recruiter.city,
                    recruiter.state,
                    recruiter.pincode,
                    recruiter.country,
                    recruiter.company_logo,
                    recruiter.linkedin_url,
                    recruiter.is_verified,
                    recruiter.status,
                ),
            )
            recruiter_id = cursor.lastrowid
            connection.commit()

            created = self.find_by_recruiter_id(recruiter_id)
            if created is None:
                raise RuntimeError("Failed to load newly created recruiter.")
            return created
        except Error:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

    def find_by_recruiter_id(self, recruiter_id: int) -> Optional[Recruiter]:
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM recruiters WHERE recruiter_id = %s",
                (recruiter_id,),
            )
            row = cursor.fetchone()
            return Recruiter.from_row(row) if row else None
        finally:
            cursor.close()
            connection.close()

    def find_by_user_id(self, user_id: int) -> Optional[Recruiter]:
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM recruiters WHERE user_id = %s",
                (user_id,),
            )
            row = cursor.fetchone()
            return Recruiter.from_row(row) if row else None
        finally:
            cursor.close()
            connection.close()

    def find_all(self) -> list[Recruiter]:
        """Fetch all recruiter records."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM recruiters ORDER BY recruiter_id ASC"
            )
            rows = cursor.fetchall()
            return [Recruiter.from_row(row) for row in rows]
        finally:
            cursor.close()
            connection.close()

    def delete_by_user_id(self, user_id: int) -> bool:
        """Delete recruiter and linked user row by user_id. Returns True if deleted."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM recruiters WHERE user_id = %s",
                (user_id,),
            )
            recruiter_deleted = cursor.rowcount > 0

            cursor.execute(
                "DELETE FROM users WHERE user_id = %s",
                (user_id,),
            )
            user_deleted = cursor.rowcount > 0
            connection.commit()
            return recruiter_deleted or user_deleted
        except Error:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

    def find_auth_by_email(self, email: str) -> Optional[dict[str, Any]]:
        """Return user auth row joined with recruiter profile by email."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT r.*, u.password_hash
                FROM users u
                INNER JOIN recruiters r ON r.user_id = u.user_id
                WHERE u.email = %s
                LIMIT 1
                """,
                (email,),
            )
            return cursor.fetchone()
        finally:
            cursor.close()
            connection.close()

    def find_auth_by_phone(self, phone: str) -> Optional[dict[str, Any]]:
        """Return user auth row joined with recruiter profile by phone/mobile."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT r.*, u.password_hash
                FROM users u
                INNER JOIN recruiters r ON r.user_id = u.user_id
                WHERE u.mobile_number = %s
                LIMIT 1
                """,
                (phone,),
            )
            return cursor.fetchone()
        finally:
            cursor.close()
            connection.close()
