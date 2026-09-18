"""
db.py
-----
All SQLite database logic lives here: creating the table, inserting a new
violation, and reading violations back out (used by the dashboard).
"""

import sqlite3
import os
from datetime import datetime

from config import DB_PATH, OUTPUTS_DIR


def init_db():
    """Create the violations table if it doesn't already exist."""
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS violations (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp       TEXT NOT NULL,
            zone            TEXT NOT NULL,
            violation_type  TEXT NOT NULL,
            confidence      REAL,
            image_path      TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def log_violation(zone: str, violation_type: str, confidence: float, image_path: str = None):
    """Insert one violation record. Called from the detection loop."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        INSERT INTO violations (timestamp, zone, violation_type, confidence, image_path)
        VALUES (?, ?, ?, ?, ?)
        """,
        (datetime.now().isoformat(timespec="seconds"), zone, violation_type, confidence, image_path),
    )
    conn.commit()
    conn.close()


def get_all_violations():
    """Return every violation row as a list of dicts (used by dashboard.py)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM violations ORDER BY timestamp DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_last_violation_time(zone: str, violation_type: str):
    """Used for the cooldown logic — when did we last log this exact
    zone + violation_type combination?"""
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        """
        SELECT timestamp FROM violations
        WHERE zone = ? AND violation_type = ?
        ORDER BY timestamp DESC LIMIT 1
        """,
        (zone, violation_type),
    ).fetchone()
    conn.close()
    if row:
        return datetime.fromisoformat(row[0])
    return None


def clear_all_violations():
    """Wipe the table. Handy for demos when you want a clean slate."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM violations")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    # Running `python db.py` directly just sets up the database.
    init_db()
    print(f"Database ready at: {DB_PATH}")
