"""DAO layer: MySQL persistence for admins and auth users."""

from typing import Any, Optional

from mysql.connector import Error

from admins.admin_model import Admin
from db_connection.config import get_db_connection


class AdminDAO:
    """Database access for users and admins tables."""

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

    def create_admin(self, admin: Admin, password_hash: str) -> Admin:
        """Insert into users then admins in a single transaction."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                INSERT INTO users (email, mobile_number, password_hash, role)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    admin.email,
                    admin.phone,
                    password_hash,
                    "admin",
                ),
            )
            user_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO admins (
                    user_id, first_name, last_name, email, phone,
                    password, role, status
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s
                )
                """,
                (
                    user_id,
                    admin.first_name,
                    admin.last_name,
                    admin.email,
                    admin.phone,
                    password_hash,
                    admin.role,
                    admin.status,
                ),
            )
            admin_id = cursor.lastrowid
            connection.commit()

            created = self.find_by_admin_id(admin_id)
            if created is None:
                raise RuntimeError("Failed to load newly created admin.")
            return created
        except Error:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

    def find_by_admin_id(self, admin_id: int) -> Optional[Admin]:
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM admins WHERE admin_id = %s",
                (admin_id,),
            )
            row = cursor.fetchone()
            return Admin.from_row(row) if row else None
        finally:
            cursor.close()
            connection.close()

    def find_by_user_id(self, user_id: int) -> Optional[Admin]:
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM admins WHERE user_id = %s",
                (user_id,),
            )
            row = cursor.fetchone()
            return Admin.from_row(row) if row else None
        finally:
            cursor.close()
            connection.close()

    def find_all(self) -> list[Admin]:
        """Fetch all admin records."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM admins ORDER BY admin_id ASC")
            rows = cursor.fetchall()
            return [Admin.from_row(row) for row in rows]
        finally:
            cursor.close()
            connection.close()

    def delete_by_user_id(self, user_id: int) -> bool:
        """Delete admin and linked user row by user_id. Returns True if deleted."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM admins WHERE user_id = %s",
                (user_id,),
            )
            admin_deleted = cursor.rowcount > 0

            cursor.execute(
                "DELETE FROM users WHERE user_id = %s",
                (user_id,),
            )
            user_deleted = cursor.rowcount > 0
            connection.commit()
            return admin_deleted or user_deleted
        except Error:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

    def update_last_login(self, admin_id: int) -> None:
        """Set last_login to the current timestamp for the given admin."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE admins SET last_login = NOW() WHERE admin_id = %s",
                (admin_id,),
            )
            connection.commit()
        except Error:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

    def find_auth_by_email(self, email: str) -> Optional[dict[str, Any]]:
        """Return user auth row joined with admin profile by email."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT a.*, u.password_hash
                FROM users u
                INNER JOIN admins a ON a.user_id = u.user_id
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
        """Return user auth row joined with admin profile by phone/mobile."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT a.*, u.password_hash
                FROM users u
                INNER JOIN admins a ON a.user_id = u.user_id
                WHERE u.mobile_number = %s
                LIMIT 1
                """,
                (phone,),
            )
            return cursor.fetchone()
        finally:
            cursor.close()
            connection.close()
