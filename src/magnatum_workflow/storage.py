from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .models import WorkflowState


class SQLiteStore:
    def __init__(self, path: str | Path = ":memory:"):
        self.path = str(path)
        self._connection = sqlite3.connect(self.path)
        self._connection.row_factory = sqlite3.Row
        self._initialize()

    def _initialize(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS workflow_state (
                opportunity_id TEXT PRIMARY KEY,
                stage TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                opportunity_id TEXT NOT NULL,
                agent TEXT NOT NULL,
                stage TEXT NOT NULL,
                detail TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )

    def save(self, state: WorkflowState) -> None:
        opportunity_id = state.opportunity.opportunity_id
        self._connection.execute(
            """
            INSERT INTO workflow_state (opportunity_id, stage, payload_json)
            VALUES (?, ?, ?)
            ON CONFLICT(opportunity_id) DO UPDATE SET
                stage=excluded.stage,
                payload_json=excluded.payload_json,
                updated_at=CURRENT_TIMESTAMP
            """,
            (opportunity_id, state.opportunity.stage, json.dumps(state.to_dict(), ensure_ascii=False)),
        )
        self._connection.execute("DELETE FROM audit_events WHERE opportunity_id = ?", (opportunity_id,))
        self._connection.executemany(
            "INSERT INTO audit_events (opportunity_id, agent, stage, detail, created_at) VALUES (?, ?, ?, ?, ?)",
            [(opportunity_id, event.agent, event.stage, event.detail, event.created_at) for event in state.audit],
        )
        self._connection.commit()

    def load(self, opportunity_id: str) -> WorkflowState | None:
        row = self._connection.execute(
            "SELECT payload_json FROM workflow_state WHERE opportunity_id = ?", (opportunity_id,)
        ).fetchone()
        return WorkflowState.from_dict(json.loads(row["payload_json"])) if row else None

    def audit_count(self, opportunity_id: str) -> int:
        row = self._connection.execute(
            "SELECT COUNT(*) AS total FROM audit_events WHERE opportunity_id = ?", (opportunity_id,)
        ).fetchone()
        return int(row["total"])

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> "SQLiteStore":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()

