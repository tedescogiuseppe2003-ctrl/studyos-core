#!/usr/bin/env python3
"""Initialize the StudyOS SQLite database for an installed subject folder."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path


DB_PATH = Path("study-os/state/studyos.sqlite")


SCHEMA_STATEMENTS = (
    """
    CREATE TABLE IF NOT EXISTS sources (
        id INTEGER PRIMARY KEY,
        path TEXT,
        file_type TEXT,
        topic_guess TEXT,
        lecture_number TEXT,
        file_hash TEXT,
        status TEXT,
        difficulty TEXT,
        exam_relevance TEXT,
        last_processed TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS batches (
        id INTEGER PRIMARY KEY,
        title TEXT,
        status TEXT,
        difficulty TEXT,
        exam_relevance TEXT,
        notes TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS batch_sources (
        batch_id INTEGER,
        source_id INTEGER,
        PRIMARY KEY (batch_id, source_id),
        FOREIGN KEY (batch_id) REFERENCES batches (id),
        FOREIGN KEY (source_id) REFERENCES sources (id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS outputs (
        id INTEGER PRIMARY KEY,
        batch_id INTEGER,
        path TEXT,
        output_type TEXT,
        status TEXT,
        last_updated TEXT,
        FOREIGN KEY (batch_id) REFERENCES batches (id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS validation_issues (
        id INTEGER PRIMARY KEY,
        batch_id INTEGER,
        issue_type TEXT,
        severity TEXT,
        description TEXT,
        status TEXT,
        FOREIGN KEY (batch_id) REFERENCES batches (id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS runs (
        id INTEGER PRIMARY KEY,
        run_type TEXT,
        started_at TEXT,
        completed_at TEXT,
        summary TEXT
    )
    """,
)


def init_db(db_path: Path = DB_PATH) -> Path:
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        for statement in SCHEMA_STATEMENTS:
            connection.execute(statement)

    return db_path


def main() -> int:
    try:
        db_path = init_db()
    except OSError as error:
        print(f"StudyOS database initialization failed: {error}", file=sys.stderr)
        return 1
    except sqlite3.Error as error:
        print(f"StudyOS database initialization failed: {error}", file=sys.stderr)
        return 1

    print(f"StudyOS database initialized at: {db_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
