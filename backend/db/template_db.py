from __future__ import annotations

import json
import sqlite3
from pathlib import Path


def init_template_tables(db_path: Path) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sticker_templates (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL,
                description TEXT    DEFAULT '',
                filename    TEXT,
                field_mapping TEXT  NOT NULL,
                is_default  INTEGER DEFAULT 0,
                created_at  TEXT    DEFAULT (datetime('now'))
            )
        """)
        conn.commit()


def seed_default_template(db_path: Path) -> None:
    from services.stickers.service import default_template_spec
    with sqlite3.connect(db_path) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM sticker_templates WHERE is_default = 1"
        ).fetchone()[0]
        if count == 0:
            spec = default_template_spec()
            conn.execute(
                """INSERT INTO sticker_templates
                   (name, description, filename, field_mapping, is_default)
                   VALUES (?, ?, ?, ?, 1)""",
                (
                    "Standard Template",
                    "Default 8-field layout: Article, Content, Construction, Width, GSM, Dyeing, Finish, Country",
                    None,
                    json.dumps(spec["mapping"]),
                ),
            )
            conn.commit()


def list_templates(db_path: Path) -> list[dict]:
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM sticker_templates ORDER BY is_default DESC, id"
        ).fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d["field_mapping"] = json.loads(d["field_mapping"])
        result.append(d)
    return result


def get_template(db_path: Path, template_id: int) -> dict | None:
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM sticker_templates WHERE id = ?", (template_id,)
        ).fetchone()
    if not row:
        return None
    d = dict(row)
    d["field_mapping"] = json.loads(d["field_mapping"])
    return d


def save_template(
    db_path: Path,
    *,
    name: str,
    description: str,
    filename: str | None,
    field_mapping: list,
) -> int:
    with sqlite3.connect(db_path) as conn:
        cur = conn.execute(
            """INSERT INTO sticker_templates (name, description, filename, field_mapping)
               VALUES (?, ?, ?, ?)""",
            (name, description, filename, json.dumps(field_mapping)),
        )
        conn.commit()
        return cur.lastrowid


def delete_template(db_path: Path, template_id: int) -> bool:
    with sqlite3.connect(db_path) as conn:
        cur = conn.execute(
            "DELETE FROM sticker_templates WHERE id = ? AND is_default = 0",
            (template_id,),
        )
        conn.commit()
        return cur.rowcount > 0
