from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db(db_path: Path) -> None:
    with _connect(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS workflow_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                source_filename TEXT,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS fabric_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id INTEGER NOT NULL REFERENCES workflow_runs(id) ON DELETE CASCADE,
                raw_text TEXT NOT NULL,
                parsed_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS feasibility_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id INTEGER NOT NULL REFERENCES workflow_runs(id) ON DELETE CASCADE,
                gate TEXT NOT NULL,
                report_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS generated_artifacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id INTEGER REFERENCES workflow_runs(id) ON DELETE SET NULL,
                artifact_type TEXT NOT NULL,
                filename TEXT NOT NULL,
                mime_type TEXT NOT NULL,
                meta_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS decision_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id INTEGER REFERENCES workflow_runs(id) ON DELETE CASCADE,
                event_type TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_workflow_updated ON workflow_runs(updated_at);
            CREATE INDEX IF NOT EXISTS idx_artifact_workflow ON generated_artifacts(workflow_id);
            CREATE INDEX IF NOT EXISTS idx_event_workflow ON decision_events(workflow_id);
            """
        )


def _row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row else None


def create_workflow(
    db_path: Path,
    *,
    title: str,
    source_filename: str,
    raw_text: str,
    parsed_card: dict[str, Any],
    report: dict[str, Any],
) -> int:
    now = utc_now()
    status = "blocked" if report.get("gate") == "ERROR" else "ready"
    with _connect(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO workflow_runs (title, source_filename, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (title, source_filename, status, now, now),
        )
        workflow_id = int(cur.lastrowid)
        conn.execute(
            """
            INSERT INTO fabric_records (workflow_id, raw_text, parsed_json, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (workflow_id, raw_text, json.dumps(parsed_card), now),
        )
        conn.execute(
            """
            INSERT INTO feasibility_reports (workflow_id, gate, report_json, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (workflow_id, report.get("gate", "ERROR"), json.dumps(report), now),
        )
        conn.execute(
            """
            INSERT INTO decision_events (workflow_id, event_type, payload_json, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                workflow_id,
                "workflow_created",
                json.dumps({"gate": report.get("gate"), "source_filename": source_filename}),
                now,
            ),
        )
    return workflow_id


def get_workflow(db_path: Path, workflow_id: int) -> dict[str, Any] | None:
    with _connect(db_path) as conn:
        workflow = _row_to_dict(
            conn.execute("SELECT * FROM workflow_runs WHERE id=?", (workflow_id,)).fetchone()
        )
        if not workflow:
            return None
        fabric = _row_to_dict(
            conn.execute(
                "SELECT * FROM fabric_records WHERE workflow_id=? ORDER BY id DESC LIMIT 1",
                (workflow_id,),
            ).fetchone()
        )
        report = _row_to_dict(
            conn.execute(
                "SELECT * FROM feasibility_reports WHERE workflow_id=? ORDER BY id DESC LIMIT 1",
                (workflow_id,),
            ).fetchone()
        )
        ai_event = _row_to_dict(
            conn.execute(
                """
                SELECT * FROM decision_events
                WHERE workflow_id=? AND event_type='ai_summary'
                ORDER BY id DESC LIMIT 1
                """,
                (workflow_id,),
            ).fetchone()
        )

    workflow["fabric"] = {
        "raw_text": fabric["raw_text"],
        "parsed": json.loads(fabric["parsed_json"]),
        "created_at": fabric["created_at"],
    }
    workflow["feasibility_report"] = json.loads(report["report_json"]) if report else {}
    workflow["ai_summary"] = json.loads(ai_event["payload_json"]) if ai_event else None
    workflow["artifacts"] = list_artifacts_for_workflow(db_path, workflow_id)
    return workflow


def list_recent_workflows(db_path: Path, limit: int = 20) -> list[dict[str, Any]]:
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT wr.*, fr.parsed_json, rep.gate, rep.report_json
            FROM workflow_runs wr
            LEFT JOIN fabric_records fr ON fr.workflow_id = wr.id
            LEFT JOIN feasibility_reports rep ON rep.workflow_id = wr.id
            ORDER BY wr.updated_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        item["parsed"] = json.loads(item.pop("parsed_json") or "{}")
        item["report"] = json.loads(item.pop("report_json") or "{}")
        result.append(item)
    return result


def save_ai_summary(db_path: Path, workflow_id: int, summary: dict[str, Any]) -> None:
    record_decision_event(db_path, workflow_id, "ai_summary", summary)


def create_artifact(
    db_path: Path,
    *,
    workflow_id: int | None,
    artifact_type: str,
    filename: str,
    mime_type: str,
    meta: dict[str, Any] | None = None,
) -> int:
    now = utc_now()
    with _connect(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO generated_artifacts
            (workflow_id, artifact_type, filename, mime_type, meta_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (workflow_id, artifact_type, filename, mime_type, json.dumps(meta or {}), now),
        )
        if workflow_id:
            conn.execute(
                "UPDATE workflow_runs SET updated_at=? WHERE id=?",
                (now, workflow_id),
            )
        return int(cur.lastrowid)


def get_artifact(db_path: Path, artifact_id: int) -> dict[str, Any] | None:
    with _connect(db_path) as conn:
        row = _row_to_dict(
            conn.execute("SELECT * FROM generated_artifacts WHERE id=?", (artifact_id,)).fetchone()
        )
    if not row:
        return None
    row["meta"] = json.loads(row.pop("meta_json") or "{}")
    return row


def list_artifacts_for_workflow(db_path: Path, workflow_id: int) -> list[dict[str, Any]]:
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT * FROM generated_artifacts
            WHERE workflow_id=?
            ORDER BY created_at DESC
            """,
            (workflow_id,),
        ).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        item["meta"] = json.loads(item.pop("meta_json") or "{}")
        result.append(item)
    return result


def record_decision_event(
    db_path: Path,
    workflow_id: int | None,
    event_type: str,
    payload: dict[str, Any],
) -> None:
    now = utc_now()
    with _connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO decision_events (workflow_id, event_type, payload_json, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (workflow_id, event_type, json.dumps(payload), now),
        )
        if workflow_id:
            conn.execute("UPDATE workflow_runs SET updated_at=? WHERE id=?", (now, workflow_id))
