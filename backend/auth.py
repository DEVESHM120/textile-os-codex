"""
auth.py — Authentication & session management (ported from FFC).
Uses stdlib only: hashlib, secrets, sqlite3. No external auth dependencies.
Roles: designer | ftc_member | admin
"""
from __future__ import annotations

import hashlib
import os
import secrets
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

DEFAULT_ADMIN_PASSWORD    = os.getenv("FF_ADMIN_PASSWORD",    "admin1234")
DEFAULT_DESIGNER_PASSWORD = os.getenv("FF_DESIGNER_PASSWORD", "designer123")
DEFAULT_FTC_PASSWORD      = os.getenv("FF_FTC_PASSWORD",      "ftcmember123")


def _hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 260_000
    ).hex()


class AuthManager:
    """Manages users (SQLite) + sessions (in-memory cache + SQLite fallback)."""

    _sessions: dict[str, dict] = {}

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    username      TEXT    NOT NULL UNIQUE,
                    password_hash TEXT    NOT NULL,
                    salt          TEXT    NOT NULL,
                    role          TEXT    NOT NULL DEFAULT 'designer',
                    display_name  TEXT,
                    created_at    TEXT    NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    token        TEXT PRIMARY KEY,
                    user_id      INTEGER NOT NULL,
                    username     TEXT NOT NULL,
                    role         TEXT NOT NULL,
                    display_name TEXT,
                    created_at   TEXT NOT NULL
                )
            """)
            conn.commit()

    def seed_default_users(self) -> None:
        defaults = [
            ("admin",     DEFAULT_ADMIN_PASSWORD,    "admin",      "Administrator"),
            ("designer1", DEFAULT_DESIGNER_PASSWORD,  "designer",   "Design Team"),
            ("ftc1",      DEFAULT_FTC_PASSWORD,       "ftc_member", "FTC Member"),
        ]
        for username, password, role, display_name in defaults:
            with sqlite3.connect(self.db_path) as conn:
                if conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone():
                    continue
                salt    = secrets.token_hex(16)
                pw_hash = _hash_password(password, salt)
                conn.execute(
                    "INSERT INTO users (username, password_hash, salt, role, display_name, created_at) "
                    "VALUES (?,?,?,?,?,?)",
                    (username, pw_hash, salt, role, display_name, datetime.utcnow().isoformat()),
                )
                conn.commit()

    def create_user(self, username: str, password: str, role: str = "designer", display_name: str = "") -> dict:
        if len(password) < 6:
            return {"success": False, "error": "Password must be at least 6 characters"}
        if role not in ("designer", "ftc_member", "admin"):
            return {"success": False, "error": "Invalid role"}
        salt    = secrets.token_hex(16)
        pw_hash = _hash_password(password, salt)
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.execute(
                    "INSERT INTO users (username, password_hash, salt, role, display_name, created_at) "
                    "VALUES (?,?,?,?,?,?)",
                    (username, pw_hash, salt, role, display_name or username, datetime.utcnow().isoformat()),
                )
                conn.commit()
                return {"success": True, "user_id": cur.lastrowid}
        except sqlite3.IntegrityError:
            return {"success": False, "error": "Username already taken"}

    def authenticate(self, username: str, password: str) -> Optional[dict]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT id, username, password_hash, salt, role, display_name FROM users WHERE username=?",
                (username,),
            ).fetchone()
        if not row:
            return None
        user_id, uname, stored_hash, salt, role, display_name = row
        if not secrets.compare_digest(_hash_password(password, salt), stored_hash):
            return None
        return {"user_id": user_id, "username": uname, "role": role, "display_name": display_name or uname}

    def create_session(self, user: dict) -> str:
        session_id = secrets.token_hex(32)
        record = {
            "user_id":      user["user_id"],
            "username":     user["username"],
            "role":         user["role"],
            "display_name": user.get("display_name", user["username"]),
        }
        AuthManager._sessions[session_id] = record
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO sessions (token, user_id, username, role, display_name, created_at) "
                "VALUES (?,?,?,?,?,?)",
                (session_id, record["user_id"], record["username"],
                 record["role"], record["display_name"], datetime.utcnow().isoformat()),
            )
        return session_id

    def get_session(self, session_id: str) -> Optional[dict]:
        if not session_id:
            return None
        cached = AuthManager._sessions.get(session_id)
        if cached:
            return cached
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT user_id, username, role, display_name FROM sessions WHERE token=?",
                (session_id,),
            ).fetchone()
        if not row:
            return None
        record = {"user_id": row[0], "username": row[1], "role": row[2], "display_name": row[3]}
        AuthManager._sessions[session_id] = record
        return record

    def destroy_session(self, session_id: str) -> None:
        AuthManager._sessions.pop(session_id, None)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM sessions WHERE token=?", (session_id,))

    def list_users(self) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT id, username, role, display_name, created_at FROM users ORDER BY id"
            ).fetchall()
        return [{"id": r[0], "username": r[1], "role": r[2], "display_name": r[3], "created_at": r[4]} for r in rows]


def get_auth_manager():
    from flask import current_app
    return current_app.config["AUTH_MANAGER"]
