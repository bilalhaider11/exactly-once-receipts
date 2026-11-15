"""Tiny receipt store. Each statement is serialised by a lock, like a DB
connection would serialise it. Check-then-write across two statements is not."""
import sqlite3
import threading


class ReceiptStore:
    def __init__(self):
        self._conn = sqlite3.connect(":memory:", check_same_thread=False)
        self._lock = threading.Lock()
        self._conn.execute(
            "CREATE TABLE receipts (stage_id TEXT PRIMARY KEY, outcome TEXT NOT NULL)"
        )

    def get(self, stage_id):
        with self._lock:
            return self._conn.execute(
                "SELECT outcome FROM receipts WHERE stage_id = ?", (stage_id,)
            ).fetchone()

    def insert(self, stage_id, outcome):
        with self._lock:
            cur = self._conn.execute(
                "INSERT OR IGNORE INTO receipts (stage_id, outcome) VALUES (?, ?)",
                (stage_id, outcome),
            )
            self._conn.commit()
            return cur.rowcount == 1  # True only for the writer that won

    def all(self, stage_id):
        with self._lock:
            return [
                r[0]
                for r in self._conn.execute(
                    "SELECT outcome FROM receipts WHERE stage_id = ?", (stage_id,)
                )
            ]
