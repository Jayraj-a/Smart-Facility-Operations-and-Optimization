import os
import sqlite3
from pathlib import Path

import bcrypt


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_FILE = PROJECT_ROOT / "backend" / "users.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")

    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]

    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    )

    return hashed.decode("utf-8")


def verify_password(
    password: str,
    password_hash: str
) -> bool:

    password_bytes = password.encode("utf-8")

    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]

    return bcrypt.checkpw(
        password_bytes,
        password_hash.encode("utf-8")
    )


def initialise_users_database():

    connection = get_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'facility_manager'
        )
        """
    )

    connection.commit()

    default_username = os.getenv(
        "ADMIN_USERNAME",
        "admin"
    )

    default_password = os.getenv(
        "ADMIN_PASSWORD",
        "Admin@123"
    )

    existing = connection.execute(
        """
        SELECT id
        FROM users
        WHERE username = ?
        """,
        (default_username,)
    ).fetchone()

    if existing is None:

        password_hash = hash_password(
            default_password
        )

        connection.execute(
            """
            INSERT INTO users (
                username,
                full_name,
                password_hash,
                role
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                default_username,
                "Facility Administrator",
                password_hash,
                "administrator"
            )
        )

        connection.commit()

    connection.close()


def authenticate_user(
    username: str,
    password: str
):

    connection = get_connection()

    user = connection.execute(
        """
        SELECT *
        FROM users
        WHERE username = ?
        """,
        (username,)
    ).fetchone()

    connection.close()

    if user is None:
        return None

    if not verify_password(
        password,
        user["password_hash"]
    ):
        return None

    return {
        "id": user["id"],
        "username": user["username"],
        "full_name": user["full_name"],
        "role": user["role"]
    }