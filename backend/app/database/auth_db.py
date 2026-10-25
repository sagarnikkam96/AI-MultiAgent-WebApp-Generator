"""SQLite-backed authentication and user management module.

Provides password hashing using PBKDF2-HMAC-SHA256, cryptographically signed
session tokens, and persistent SQLite storage for user registration and login.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import time
from pathlib import Path
from typing import Any, Optional

DB_FILE = Path(__file__).resolve().parent / "auth.db"
TOKEN_SECRET = os.environ.get("AUTH_SECRET_KEY", "agy-multiagent-webapp-generator-secure-secret-2026")
TOKEN_TTL_SECONDS = 7 * 24 * 3600  # 7 days


def get_db_connection() -> sqlite3.Connection:
    """Return a connection to the SQLite auth database with row factory enabled."""
    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row
    return conn


def init_auth_db() -> None:
    """Initialize the users table in SQLite if it does not already exist."""
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                full_name TEXT DEFAULT '',
                created_at INTEGER NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS generated_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                project_slug TEXT NOT NULL,
                project_name TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                UNIQUE(user_id, project_slug),
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        conn.commit()


def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Hash a password using PBKDF2-HMAC-SHA256 with 100,000 iterations.
    
    Returns (hex_digest, salt).
    """
    if salt is None:
        salt = secrets.token_hex(16)
    salt_bytes = salt.encode("utf-8")
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt_bytes, 100_000)
    return key.hex(), salt


def verify_password(plain_password: str, stored_hash: str, salt: str) -> bool:
    """Verify that a plaintext password matches the stored PBKDF2 hash."""
    computed_hash, _ = hash_password(plain_password, salt)
    return hmac.compare_digest(computed_hash, stored_hash)


def create_token(user_id: int, email: str, username: str) -> str:
    """Create a signed, URL-safe base64 authentication token with expiration."""
    payload = {
        "uid": user_id,
        "email": email,
        "username": username,
        "exp": int(time.time()) + TOKEN_TTL_SECONDS,
    }
    payload_json = json.dumps(payload, separators=(",", ":"))
    payload_b64 = base64.urlsafe_b64encode(payload_json.encode("utf-8")).decode("utf-8").rstrip("=")
    
    signature = hmac.new(
        TOKEN_SECRET.encode("utf-8"),
        payload_b64.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    
    return f"{payload_b64}.{signature}"


def verify_token(token: str) -> Optional[dict[str, Any]]:
    """Verify a signed authentication token and return its payload if valid."""
    if not token or "." not in token:
        return None
    try:
        payload_b64, signature = token.split(".", 1)
        expected_sig = hmac.new(
            TOKEN_SECRET.encode("utf-8"),
            payload_b64.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_sig):
            return None
        
        # Add padding back for base64 decode
        rem = len(payload_b64) % 4
        padded = payload_b64 + ("=" * (4 - rem) if rem else "")
        payload_json = base64.urlsafe_b64decode(padded.encode("utf-8")).decode("utf-8")
        payload = json.loads(payload_json)
        
        if payload.get("exp", 0) < int(time.time()):
            return None  # Expired
            
        return payload
    except Exception:
        return None


def register_user(username: str, email: str, password: str, full_name: str = "") -> dict[str, Any]:
    """Register a new user. Raises ValueError if email or username already exists."""
    clean_username = username.strip().lower()
    clean_email = email.strip().lower()
    clean_name = full_name.strip() or clean_username

    if not clean_username or len(clean_username) < 3:
        raise ValueError("Username must be at least 3 characters long.")
    if not clean_email or "@" not in clean_email:
        raise ValueError("Please provide a valid email address.")
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters long.")

    init_auth_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ? OR username = ?", (clean_email, clean_username))
        existing = cursor.fetchone()
        if existing:
            raise ValueError("An account with this email or username already exists. Please log in.")

        pwd_hash, salt = hash_password(password)
        now = int(time.time())
        cursor.execute(
            """
            INSERT INTO users (username, email, password_hash, salt, full_name, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (clean_username, clean_email, pwd_hash, salt, clean_name, now),
        )
        conn.commit()
        user_id = cursor.lastrowid

    token = create_token(user_id, clean_email, clean_username)
    return {
        "id": user_id,
        "username": clean_username,
        "email": clean_email,
        "full_name": clean_name,
        "token": token,
    }


def authenticate_user(login_identifier: str, password: str) -> dict[str, Any]:
    """Authenticate a user by username or email. Raises ValueError on failure."""
    ident = login_identifier.strip().lower()
    if not ident:
        raise ValueError("Email or username is required.")
    if not password:
        raise ValueError("Password is required.")

    init_auth_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, email, password_hash, salt, full_name FROM users WHERE email = ? OR username = ?",
            (ident, ident),
        )
        user = cursor.fetchone()
        if not user:
            raise ValueError("Invalid email/username or password. If you are new, please register first.")

        if not verify_password(password, user["password_hash"], user["salt"]):
            raise ValueError("Invalid email/username or password.")

        token = create_token(user["id"], user["email"], user["username"])
        return {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "token": token,
        }


def get_user_by_id(user_id: int) -> Optional[dict[str, Any]]:
    """Lookup user by primary key ID."""
    init_auth_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, full_name, created_at FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            return None
        return dict(user)


def record_generated_project(user_id: int, project_slug: str, project_name: str) -> None:
    """Record a generated project for its authenticated owner."""
    init_auth_db()
    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO generated_projects (user_id, project_slug, project_name, created_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, project_slug) DO UPDATE SET
                project_name = excluded.project_name,
                created_at = excluded.created_at
            """,
            (user_id, project_slug, project_name, int(time.time())),
        )
        conn.commit()


def get_generated_projects(user_id: int) -> list[dict[str, Any]]:
    """Return a user's generated project history, newest first."""
    init_auth_db()
    with get_db_connection() as conn:
        rows = conn.execute(
            """
            SELECT project_slug, project_name, created_at
            FROM generated_projects
            WHERE user_id = ?
            ORDER BY created_at DESC, id DESC
            """,
            (user_id,),
        ).fetchall()
        return [dict(row) for row in rows]
