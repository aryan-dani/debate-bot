"""Local SQLite session history for offline practice review."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_DATA_DIR = Path(__file__).resolve().parent / "data"
_DB_PATH = _DATA_DIR / "sessions.db"


def _connect() -> sqlite3.Connection:
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                provider TEXT NOT NULL,
                model TEXT NOT NULL,
                topic TEXT NOT NULL,
                tone TEXT,
                difficulty TEXT,
                transcript_json TEXT NOT NULL,
                report_json TEXT
            )
            """
        )
        conn.commit()


def save_session(
    *,
    provider: str,
    model: str,
    topic: str,
    tone: str,
    difficulty: str,
    transcript: Any,
    report: Any,
) -> int:
    init_db()
    created_at = datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO sessions
            (created_at, provider, model, topic, tone, difficulty, transcript_json, report_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                created_at,
                provider,
                model,
                topic,
                tone,
                difficulty,
                json.dumps(transcript),
                json.dumps(report),
            ),
        )
        conn.commit()
        return int(cur.lastrowid)


def list_sessions(limit: int = 20) -> list[dict]:
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT id, created_at, provider, model, topic, tone, difficulty
            FROM sessions
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


def get_session(session_id: int) -> dict | None:
    init_db()
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
    if not row:
        return None
    data = dict(row)
    data["transcript"] = json.loads(data.pop("transcript_json") or "{}")
    data["report"] = json.loads(data.pop("report_json") or "null")
    return data
