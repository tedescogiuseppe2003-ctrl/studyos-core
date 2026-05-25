#!/usr/bin/env python3
"""Build a StudyOS source inventory for an installed subject folder."""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

from init_db import init_db


DB_PATH = Path("study-os/state/studyos.sqlite")
INVENTORY_DIR = Path("working/inventory")
COURSE_INVENTORY_PATH = INVENTORY_DIR / "course_inventory.md"
BATCH_PLAN_PATH = INVENTORY_DIR / "batch_plan.md"

INPUT_FOLDERS = (
    ("inputs/slides", "slides"),
    ("inputs/readings", "readings"),
    ("inputs/notes", "notes"),
    ("inputs/exercises", "exercises"),
    ("inputs/exams", "exams"),
    ("inputs/transcripts", "transcripts"),
    ("inputs/miscellaneous", "miscellaneous"),
)

LECTURE_PATTERNS = (
    re.compile(
        r"\b(?:lecture|lect|lec|lesson|class|session)\s*[-_ ]*0*(\d{1,3})(?=\D|$)",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:l|wk|week|unit|module|chapter|ch)\s*[-_ ]*0*(\d{1,3})(?=\D|$)",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b0*(\d{1,3})\s*[-_ ]+(?:lecture|lect|lec|lesson|class|session)(?=\D|$)",
        re.IGNORECASE,
    ),
)

TOPIC_STOPWORDS = {
    "lecture",
    "lect",
    "lec",
    "lesson",
    "class",
    "session",
    "week",
    "wk",
    "unit",
    "module",
    "chapter",
    "ch",
    "slides",
    "slide",
    "reading",
    "readings",
    "notes",
    "note",
    "exercise",
    "exercises",
    "exam",
    "exams",
    "transcript",
    "transcripts",
    "misc",
    "miscellaneous",
}


@dataclass(frozen=True)
class SourceFile:
    path: str
    file_type: str
    topic_guess: str
    lecture_number: str | None
    file_hash: str
    status: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan StudyOS inputs and update the source inventory."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Installed subject folder root. Defaults to the current directory.",
    )
    return parser.parse_args()


def stable_relative_path(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def hash_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def discover_files(root: Path) -> list[tuple[Path, str]]:
    discovered: list[tuple[Path, str]] = []

    for relative_folder, file_type in INPUT_FOLDERS:
        folder = root / relative_folder
        if not folder.is_dir():
            continue

        for path in sorted(folder.rglob("*")):
            if path.is_file():
                discovered.append((path, file_type))

    return discovered


def guess_lecture_number(filename: str) -> str | None:
    stem = Path(filename).stem

    for pattern in LECTURE_PATTERNS:
        match = pattern.search(stem)
        if match:
            return str(int(match.group(1)))

    leading_number = re.match(r"^\s*0*(\d{1,3})(?:\D|$)", stem)
    if leading_number:
        return str(int(leading_number.group(1)))

    return None


def guess_topic(filename: str) -> str:
    stem = Path(filename).stem
    cleaned = re.sub(r"[_\-]+", " ", stem)
    cleaned = re.sub(
        r"\b(?:lecture|lect|lec|lesson|class|session)\s*0*\d{1,3}\b",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"\b(?:l|wk|week|unit|module|chapter|ch)\s*0*\d{1,3}\b",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"\b0*\d{1,3}\s*(?:lecture|lect|lec|lesson|class|session)\b",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"\b\d{1,4}\b", " ", cleaned)
    cleaned = re.sub(r"[^A-Za-z0-9]+", " ", cleaned)

    words = [
        word
        for word in cleaned.split()
        if word.lower() not in TOPIC_STOPWORDS
    ]

    if not words:
        return "Untitled"

    return " ".join(words).title()


def existing_source_by_path(
    connection: sqlite3.Connection, source_path: str
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, file_hash, status
        FROM sources
        WHERE path = ?
        ORDER BY id
        LIMIT 1
        """,
        (source_path,),
    ).fetchone()


def update_database(root: Path, files: list[tuple[Path, str]]) -> list[SourceFile]:
    init_db(root / DB_PATH)

    sources: list[SourceFile] = []
    completed_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    with sqlite3.connect(root / DB_PATH) as connection:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")

        for path, file_type in files:
            relative_path = stable_relative_path(path, root)
            file_hash = hash_file(path)
            lecture_number = guess_lecture_number(path.name)
            topic_guess = guess_topic(path.name)

            existing = existing_source_by_path(connection, relative_path)
            if existing is None:
                status = "new"
                connection.execute(
                    """
                    INSERT INTO sources (
                        path,
                        file_type,
                        topic_guess,
                        lecture_number,
                        file_hash,
                        status
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        relative_path,
                        file_type,
                        topic_guess,
                        lecture_number,
                        file_hash,
                        status,
                    ),
                )
            else:
                old_hash = existing["file_hash"]
                old_status = existing["status"]
                status = "stale" if old_hash != file_hash else old_status or "new"
                connection.execute(
                    """
                    UPDATE sources
                    SET file_type = ?,
                        topic_guess = ?,
                        lecture_number = ?,
                        file_hash = ?,
                        status = ?
                    WHERE id = ?
                    """,
                    (
                        file_type,
                        topic_guess,
                        lecture_number,
                        file_hash,
                        status,
                        existing["id"],
                    ),
                )

            sources.append(
                SourceFile(
                    path=relative_path,
                    file_type=file_type,
                    topic_guess=topic_guess,
                    lecture_number=lecture_number,
                    file_hash=file_hash,
                    status=status,
                )
            )

        connection.execute(
            """
            INSERT INTO runs (run_type, started_at, completed_at, summary)
            VALUES (?, ?, ?, ?)
            """,
            (
                "inventory",
                completed_at,
                completed_at,
                f"Scanned {len(sources)} source file(s).",
            ),
        )

    return sources


def markdown_table_row(values: list[str]) -> str:
    escaped = [value.replace("|", "\\|").replace("\n", " ") for value in values]
    return "| " + " | ".join(escaped) + " |"


def write_course_inventory(root: Path, sources: list[SourceFile]) -> None:
    target = root / COURSE_INVENTORY_PATH
    target.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Course Inventory",
        "",
        f"Total source files: {len(sources)}",
        "",
        markdown_table_row(
            [
                "Path",
                "Type",
                "Lecture",
                "Topic Guess",
                "Status",
                "SHA256",
            ]
        ),
        markdown_table_row(["---", "---", "---", "---", "---", "---"]),
    ]

    for source in sorted(sources, key=lambda item: item.path):
        lines.append(
            markdown_table_row(
                [
                    source.path,
                    source.file_type,
                    source.lecture_number or "",
                    source.topic_guess,
                    source.status,
                    source.file_hash,
                ]
            )
        )

    lines.append("")
    target.write_text("\n".join(lines), encoding="utf-8")


def batch_sort_key(batch_key: tuple[str, str]) -> tuple[int, int, str]:
    lecture, topic = batch_key
    if lecture == "Unassigned":
        return (1, 0, topic.lower())
    return (0, int(lecture), topic.lower())


def write_batch_plan(root: Path, sources: list[SourceFile]) -> None:
    target = root / BATCH_PLAN_PATH
    target.parent.mkdir(parents=True, exist_ok=True)

    grouped: dict[tuple[str, str], list[SourceFile]] = defaultdict(list)
    for source in sources:
        lecture = source.lecture_number or "Unassigned"
        topic = source.topic_guess or "Untitled"
        grouped[(lecture, topic)].append(source)

    lines = [
        "# Batch Plan",
        "",
        "This plan groups sources by filename-derived lecture number and topic guess.",
        "",
    ]

    if not grouped:
        lines.extend(["No source files found.", ""])
    else:
        for index, batch_key in enumerate(sorted(grouped, key=batch_sort_key), start=1):
            lecture, topic = batch_key
            batch_sources = sorted(grouped[batch_key], key=lambda item: item.path)
            lines.extend(
                [
                    f"## Batch {index}: {topic}",
                    "",
                    f"- Lecture: {lecture}",
                    f"- Source files: {len(batch_sources)}",
                    "",
                ]
            )
            for source in batch_sources:
                lines.append(
                    f"- `{source.path}` ({source.file_type}, {source.status})"
                )
            lines.append("")

    target.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    root = args.root.expanduser().resolve()

    try:
        files = discover_files(root)
        sources = update_database(root, files)
        write_course_inventory(root, sources)
        write_batch_plan(root, sources)
    except OSError as error:
        print(f"StudyOS inventory failed: {error}", file=sys.stderr)
        return 1
    except sqlite3.Error as error:
        print(f"StudyOS inventory failed: {error}", file=sys.stderr)
        return 1

    print(f"Scanned source files: {len(sources)}")
    print(f"Updated database: {root / DB_PATH}")
    print(f"Wrote inventory: {root / COURSE_INVENTORY_PATH}")
    print(f"Wrote batch plan: {root / BATCH_PLAN_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
