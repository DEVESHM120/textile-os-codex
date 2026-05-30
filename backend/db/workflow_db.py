"""
workflow_db.py — Submission workflow tables (ported from FFC).
All functions accept db_path as first argument — threaded in from Flask routes.
Tables: submissions, submission_files, messages, approvals
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional


DATA_BLOCKING_WARNING_CODES = {
    "MISSING_REQUIRED_FIELD",
    "COMPOSITION_UNPARSED",
}


def _conn(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_workflow_tables(db_path: Path) -> None:
    with _conn(db_path) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS submissions (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                designer_id     INTEGER NOT NULL,
                card_ref        TEXT,
                card_filename   TEXT,
                card_raw_text   TEXT,
                card_parsed     TEXT,
                check_result    TEXT,
                status          TEXT NOT NULL DEFAULT 'draft',
                ftc_notes       TEXT,
                created_at      TEXT NOT NULL,
                updated_at      TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS submission_files (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                submission_id   INTEGER NOT NULL REFERENCES submissions(id) ON DELETE CASCADE,
                filename        TEXT NOT NULL,
                original_name   TEXT NOT NULL,
                mime_type       TEXT,
                uploaded_by     INTEGER,
                uploaded_at     TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS messages (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                submission_id   INTEGER NOT NULL REFERENCES submissions(id) ON DELETE CASCADE,
                sender_id       INTEGER NOT NULL,
                sender_name     TEXT NOT NULL,
                sender_role     TEXT NOT NULL,
                body            TEXT NOT NULL,
                field_ref       TEXT,
                created_at      TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS approvals (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                submission_id   INTEGER NOT NULL UNIQUE REFERENCES submissions(id),
                ftc_member_id   INTEGER NOT NULL,
                ftc_member_name TEXT NOT NULL,
                approval_id     TEXT NOT NULL UNIQUE,
                signature       TEXT NOT NULL,
                approved_at     TEXT NOT NULL,
                notes           TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_sub_designer ON submissions(designer_id);
            CREATE INDEX IF NOT EXISTS idx_sub_status   ON submissions(status);
            CREATE INDEX IF NOT EXISTS idx_msg_sub      ON messages(submission_id);
            CREATE INDEX IF NOT EXISTS idx_files_sub    ON submission_files(submission_id);
        """)


# ── Submissions ───────────────────────────────────────────────────────────────

def submission_status_for_report(report: dict) -> str:
    return "ready" if report.get("gate") == "PASS" else "draft"


def create_submission(
    db_path: Path,
    designer_id: int,
    card_ref: str,
    card_filename: str,
    card_raw_text: str,
    card_parsed: dict,
    check_result: dict,
) -> int:
    now  = datetime.utcnow().isoformat()
    status = submission_status_for_report(check_result)
    with _conn(db_path) as conn:
        cur = conn.execute(
            """INSERT INTO submissions
               (designer_id, card_ref, card_filename, card_raw_text,
                card_parsed, check_result, status, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (designer_id, card_ref, card_filename, card_raw_text,
             json.dumps(card_parsed), json.dumps(check_result), status, now, now),
        )
        return cur.lastrowid


def update_submission_check(db_path: Path, submission_id: int, card_parsed: dict, check_result: dict) -> str:
    status = submission_status_for_report(check_result)
    now    = datetime.utcnow().isoformat()
    with _conn(db_path) as conn:
        conn.execute(
            "UPDATE submissions SET card_parsed=?, check_result=?, status=?, updated_at=? WHERE id=?",
            (json.dumps(card_parsed), json.dumps(check_result), status, now, submission_id),
        )
    return status


def update_submission_source_and_check(
    db_path: Path,
    submission_id: int,
    card_filename: str,
    card_raw_text: str,
    card_parsed: dict,
    check_result: dict,
) -> str:
    status = submission_status_for_report(check_result)
    now = datetime.utcnow().isoformat()
    with _conn(db_path) as conn:
        conn.execute(
            """UPDATE submissions
               SET card_ref=?, card_filename=?, card_raw_text=?, card_parsed=?,
                   check_result=?, status=?, updated_at=?
               WHERE id=?""",
            (
                card_parsed.get("card_ref") or card_filename,
                card_filename,
                card_raw_text,
                json.dumps(card_parsed),
                json.dumps(check_result),
                status,
                now,
                submission_id,
            ),
        )
    return status


def update_submission_status(db_path: Path, submission_id: int, status: str) -> None:
    now = datetime.utcnow().isoformat()
    with _conn(db_path) as conn:
        conn.execute(
            "UPDATE submissions SET status=?, updated_at=? WHERE id=?",
            (status, now, submission_id),
        )


def get_submission(db_path: Path, submission_id: int) -> Optional[dict]:
    with _conn(db_path) as conn:
        row = conn.execute(
            """SELECT s.*, u.username as designer_username, u.display_name as designer_display
               FROM submissions s
               JOIN users u ON u.id = s.designer_id
               WHERE s.id=?""",
            (submission_id,),
        ).fetchone()
    if not row:
        return None
    d = dict(row)
    d["card_parsed"]  = json.loads(d["card_parsed"]  or "{}")
    d["check_result"] = json.loads(d["check_result"] or "{}")
    return d


def list_designer_submissions(db_path: Path, designer_id: int) -> list[dict]:
    with _conn(db_path) as conn:
        rows = conn.execute(
            """SELECT id, card_ref, card_filename, status,
                      check_result, created_at, updated_at
               FROM submissions WHERE designer_id=?
               ORDER BY updated_at DESC""",
            (designer_id,),
        ).fetchall()
    result = []
    for row in rows:
        d  = dict(row)
        cr = json.loads(d.pop("check_result") or "{}")
        d["gate"]       = cr.get("gate", "—")
        d["n_errors"]   = len(cr.get("errors",   []))
        d["n_warnings"] = len(cr.get("warnings", []))
        result.append(d)
    return result


def list_ftc_inbox(db_path: Path, status_filter: Optional[str] = None) -> list[dict]:
    statuses     = (status_filter,) if status_filter else ("submitted", "needs_revision")
    placeholders = ",".join("?" for _ in statuses)
    with _conn(db_path) as conn:
        rows = conn.execute(
            f"""SELECT s.id, s.card_ref, s.card_filename, s.status,
                       s.check_result, s.created_at, s.updated_at,
                       u.username, u.display_name
                FROM submissions s
                JOIN users u ON u.id = s.designer_id
                WHERE s.status IN ({placeholders})
                ORDER BY s.updated_at DESC""",
            statuses,
        ).fetchall()
    result = []
    for row in rows:
        d  = dict(row)
        cr = json.loads(d.pop("check_result") or "{}")
        d["gate"]             = cr.get("gate", "—")
        d["n_errors"]         = len(cr.get("errors",   []))
        d["n_warnings"]       = len(cr.get("warnings", []))
        d["designer_display"] = d.pop("display_name") or d["username"]
        result.append(d)
    return result


def list_all_submissions_for_ftc(db_path: Path) -> list[dict]:
    with _conn(db_path) as conn:
        rows = conn.execute(
            """SELECT s.id, s.card_ref, s.card_filename, s.status,
                      s.check_result, s.created_at, s.updated_at,
                      u.username, u.display_name
               FROM submissions s
               JOIN users u ON u.id = s.designer_id
               ORDER BY s.updated_at DESC LIMIT 200""",
        ).fetchall()
    result = []
    for row in rows:
        d  = dict(row)
        cr = json.loads(d.pop("check_result") or "{}")
        d["gate"]             = cr.get("gate", "—")
        d["n_errors"]         = len(cr.get("errors",   []))
        d["n_warnings"]       = len(cr.get("warnings", []))
        d["designer_display"] = d.pop("display_name") or d["username"]
        result.append(d)
    return result


# ── Files ─────────────────────────────────────────────────────────────────────

def save_file(db_path: Path, submission_id: int, filename: str, original_name: str, mime_type: str, uploader_id: int) -> int:
    now = datetime.utcnow().isoformat()
    with _conn(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO submission_files (submission_id, filename, original_name, mime_type, uploaded_by, uploaded_at) VALUES (?,?,?,?,?,?)",
            (submission_id, filename, original_name, mime_type, uploader_id, now),
        )
        return cur.lastrowid


def list_files(db_path: Path, submission_id: int) -> list[dict]:
    with _conn(db_path) as conn:
        rows = conn.execute(
            "SELECT id, filename, original_name, mime_type, uploaded_at FROM submission_files WHERE submission_id=? ORDER BY uploaded_at",
            (submission_id,),
        ).fetchall()
    return [dict(r) for r in rows]


# ── Messages ──────────────────────────────────────────────────────────────────

def add_message(db_path: Path, submission_id: int, sender_id: int, sender_name: str, sender_role: str, body: str, field_ref: Optional[str] = None) -> int:
    now = datetime.utcnow().isoformat()
    with _conn(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO messages (submission_id, sender_id, sender_name, sender_role, body, field_ref, created_at) VALUES (?,?,?,?,?,?,?)",
            (submission_id, sender_id, sender_name, sender_role, body, field_ref, now),
        )
        return cur.lastrowid


def get_messages(db_path: Path, submission_id: int) -> list[dict]:
    with _conn(db_path) as conn:
        rows = conn.execute(
            "SELECT id, sender_id, sender_name, sender_role, body, field_ref, created_at FROM messages WHERE submission_id=? ORDER BY created_at ASC",
            (submission_id,),
        ).fetchall()
    return [dict(r) for r in rows]


# ── Approvals ─────────────────────────────────────────────────────────────────

def create_approval(db_path: Path, submission_id: int, ftc_member_id: int, ftc_member_name: str, approval_id: str, signature: str, notes: str = "") -> None:
    now = datetime.utcnow().isoformat()
    with _conn(db_path) as conn:
        conn.execute(
            "INSERT INTO approvals (submission_id, ftc_member_id, ftc_member_name, approval_id, signature, approved_at, notes) VALUES (?,?,?,?,?,?,?)",
            (submission_id, ftc_member_id, ftc_member_name, approval_id, signature, now, notes),
        )
    update_submission_status(db_path, submission_id, "approved")


def get_approval_by_id(db_path: Path, approval_id: str) -> Optional[dict]:
    with _conn(db_path) as conn:
        row = conn.execute(
            """SELECT a.*, s.card_ref, s.card_parsed, s.check_result, u.display_name as designer_name
               FROM approvals a
               JOIN submissions s ON s.id = a.submission_id
               JOIN users u ON u.id = s.designer_id
               WHERE a.approval_id=?""",
            (approval_id,),
        ).fetchone()
    if not row:
        return None
    d = dict(row)
    d["card_parsed"]  = json.loads(d["card_parsed"]  or "{}")
    d["check_result"] = json.loads(d["check_result"] or "{}")
    return d


def get_approval_for_submission(db_path: Path, submission_id: int) -> Optional[dict]:
    with _conn(db_path) as conn:
        row = conn.execute("SELECT * FROM approvals WHERE submission_id=?", (submission_id,)).fetchone()
    return dict(row) if row else None
