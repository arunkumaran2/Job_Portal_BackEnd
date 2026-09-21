"""Centralized MySQL database connection configuration."""

import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv
from mysql.connector import MySQLConnection

# Load .env from the project root (one level above this package)
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def get_db_config() -> dict:
    """Return database connection settings from environment variables."""
    if not all([DB_USER, DB_PASSWORD, DB_NAME]):
        raise ValueError(
            "Missing required database environment variables. "
            "Set DB_USER, DB_PASSWORD, and DB_NAME in your .env file."
        )
    return {
        "host": DB_HOST,
        "port": DB_PORT,
        "user": DB_USER,
        "password": DB_PASSWORD,
        "database": DB_NAME,
    }


def get_db_connection() -> MySQLConnection:
    """Create and return a MySQL database connection using .env credentials."""
    return mysql.connector.connect(**get_db_config())


def _split_sql_statements(sql: str) -> list[str]:
    """Split a SQL script into individual statements, ignoring comment-only lines."""
    statements: list[str] = []
    buffer: list[str] = []

    for line in sql.splitlines():
        stripped = line.strip()
        if stripped.startswith("--"):
            continue
        buffer.append(line)
        if stripped.endswith(";"):
            statement = "\n".join(buffer).strip().rstrip(";").strip()
            if statement:
                statements.append(statement)
            buffer = []

    trailing = "\n".join(buffer).strip().rstrip(";").strip()
    if trailing:
        statements.append(trailing)
    return statements


def init_db() -> None:
    """Create the database (if needed) and apply schema.sql tables."""
    if not all([DB_USER, DB_PASSWORD, DB_NAME]):
        raise ValueError(
            "Missing required database environment variables. "
            "Set DB_USER, DB_PASSWORD, and DB_NAME in your .env file."
        )
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_PATH}")

    # Connect without selecting a database so we can create it first.
    server_connection = mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
    )
    try:
        cursor = server_connection.cursor()
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        server_connection.commit()
    finally:
        cursor.close()
        server_connection.close()

    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    statements = _split_sql_statements(schema_sql)

    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        for statement in statements:
            cursor.execute(statement)
        connection.commit()
        print(f"Database '{DB_NAME}' is ready ({len(statements)} statements applied).")
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()
