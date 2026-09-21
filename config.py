"""Load MySQL database settings from environment variables."""

import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


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
