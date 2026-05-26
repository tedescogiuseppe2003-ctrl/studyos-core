#!/usr/bin/env python3
"""Build a StudyOS source inventory for an installed subject folder."""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
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

SUPPORT_SOURCE_TYPES = {"notes", "exercises", "readings", "transcripts", "exams"}
NON_SLIDE_BATCH_SOURCE_TYPES = {"notes", "readings", "transcripts"}

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
    re.compile(
        r"\b(?:slide|slides|note|notes|exercise|exercises|reading|readings|"
        r"transcript|transcripts)\s*[-_ ]*0*(\d{1,3})(?=\D|$)",
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
    "assignment",
    "assignments",
    "problem",
    "problems",
    "sheet",
    "sheets",
    "solution",
    "solutions",
    "practice",
    "sample",
    "final",
    "midterm",
    "quiz",
    "homework",
    "hw",
}

FORMULA_KEYWORDS = {
    "algebra",
    "calculus",
    "derivative",
    "equation",
    "formula",
    "formulas",
    "math",
    "mathematics",
    "model",
    "models",
    "probability",
    "proof",
    "quantitative",
    "regression",
    "statistics",
    "theorem",
}


@dataclass(frozen=True)
class SourceFile:
    path: str
    file_type: str
    topic_guess: str
    lecture_number: str | None
    file_hash: str
    status: str


@dataclass
class BatchPlan:
    title: str
    primary_sources: list[SourceFile]
    supporting_sources: list[SourceFile]
    lecture_number: str | None
    topic_tokens: set[str]
    notes: list[str]


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


def topic_tokens(source: SourceFile) -> set[str]:
    words = re.findall(r"[A-Za-z0-9]+", source.topic_guess.lower())
    return {
        word
        for word in words
        if len(word) > 2 and word not in TOPIC_STOPWORDS and not word.isdigit()
    }


def path_tokens(source: SourceFile) -> set[str]:
    words = re.findall(r"[A-Za-z0-9]+", Path(source.path).stem.lower())
    return {
        word
        for word in words
        if len(word) > 2 and word not in TOPIC_STOPWORDS and not word.isdigit()
    }


def title_slug(title: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", title)
    slug = "_".join(words[:8]) or "Untitled"
    return slug[:80]


def batch_sort_key(batch: BatchPlan) -> tuple[int, int, str]:
    if batch.lecture_number is None:
        return (1, 0, batch.title.lower())
    return (0, int(batch.lecture_number), batch.title.lower())


def source_list_lines(sources: list[SourceFile], indent: str = "-") -> list[str]:
    if not sources:
        return [f"{indent} None"]
    return [f"{indent} `{source.path}`" for source in sources]


def formula_sheet_likely(sources: list[SourceFile]) -> bool:
    for source in sources:
        tokens = topic_tokens(source) | path_tokens(source)
        if tokens & FORMULA_KEYWORDS:
            return True

    return False


def expected_output_lines(all_sources: list[SourceFile]) -> list[str]:
    lines = ["- master notes"]

    if formula_sheet_likely(all_sources):
        lines.append("- formula sheet")

    lines.extend(
        [
            "- flashcards",
            "- exam questions",
            "- weak points",
        ]
    )

    return lines


def source_matches_batch(source: SourceFile, batch: BatchPlan) -> bool:
    if source.lecture_number and batch.lecture_number == source.lecture_number:
        return True

    source_tokens = topic_tokens(source) | path_tokens(source)
    return bool(source_tokens and source_tokens & batch.topic_tokens)


def matching_batches(source: SourceFile, batches: list[BatchPlan]) -> list[BatchPlan]:
    return [batch for batch in batches if source_matches_batch(source, batch)]


def build_slide_batches(sources: list[SourceFile]) -> list[BatchPlan]:
    slide_groups: dict[tuple[str | None, str], list[SourceFile]] = {}

    for source in sources:
        if source.file_type != "slides":
            continue

        key = (source.lecture_number, source.topic_guess or "Untitled")
        slide_groups.setdefault(key, []).append(source)

    batches: list[BatchPlan] = []
    sorted_groups = sorted(
        slide_groups.items(),
        key=lambda item: (
            item[0][0] is None,
            int(item[0][0] or 0),
            item[0][1].lower(),
        ),
    )

    for (lecture_number, topic), primary_sources in sorted_groups:
        batch_tokens: set[str] = set()
        for source in primary_sources:
            batch_tokens.update(topic_tokens(source))
            batch_tokens.update(path_tokens(source))

        note = "Created from slide source metadata; slides usually define conceptual lecture batches."
        if lecture_number:
            note += f" Lecture {lecture_number} is used as the strongest matching signal."

        batches.append(
            BatchPlan(
                title=topic,
                primary_sources=sorted(primary_sources, key=lambda item: item.path),
                supporting_sources=[],
                lecture_number=lecture_number,
                topic_tokens=batch_tokens,
                notes=[note],
            )
        )

    return batches


def clearly_conceptual_non_slide(source: SourceFile) -> bool:
    if source.file_type not in NON_SLIDE_BATCH_SOURCE_TYPES:
        return False

    if source.topic_guess == "Untitled":
        return False

    tokens = topic_tokens(source) | path_tokens(source)
    conceptual_markers = {
        "lecture",
        "lesson",
        "module",
        "topic",
        "unit",
        "chapter",
        "seminar",
        "tutorial",
    }

    return bool(source.lecture_number or tokens & conceptual_markers or len(tokens) >= 2)


def build_non_slide_batches(sources: list[SourceFile]) -> list[BatchPlan]:
    source_groups: dict[tuple[str, str], list[SourceFile]] = {}

    for source in sorted(sources, key=lambda item: item.path):
        if not clearly_conceptual_non_slide(source):
            continue

        if source.lecture_number:
            key = ("lecture", source.lecture_number)
        else:
            key = ("topic", source.topic_guess.lower())
        source_groups.setdefault(key, []).append(source)

    batches: list[BatchPlan] = []
    sorted_groups = sorted(
        source_groups.items(),
        key=lambda item: (
            item[0][0] != "lecture",
            int(item[0][1]) if item[0][0] == "lecture" else 0,
            item[0][1],
        ),
    )

    for (key_type, key_value), primary_sources in sorted_groups:
        batch_tokens: set[str] = set()
        for source in primary_sources:
            batch_tokens.update(topic_tokens(source))
            batch_tokens.update(path_tokens(source))

        title = primary_sources[0].topic_guess or "Untitled"
        lecture_number = key_value if key_type == "lecture" else None
        batches.append(
            BatchPlan(
                title=title,
                primary_sources=primary_sources,
                supporting_sources=[],
                lecture_number=lecture_number,
                topic_tokens=batch_tokens,
                notes=[
                    "Created from non-slide lecture/topic source metadata because no slide sources were found."
                ],
            )
        )

    return batches


def attach_source_to_batch(
    source: SourceFile,
    batches: list[BatchPlan],
) -> str | None:
    matches = matching_batches(source, batches)

    if source.file_type == "exams":
        topic_matched = [
            batch
            for batch in matches
            if topic_tokens(source) & batch.topic_tokens
        ]
        if len(topic_matched) == 1:
            topic_matched[0].supporting_sources.append(source)
            return "Attached exam as supporting material because lecture/topic metadata matched one conceptual batch."
        return None

    if len(matches) != 1:
        return None

    matches[0].supporting_sources.append(source)
    if source.lecture_number and matches[0].lecture_number == source.lecture_number:
        return f"Attached {source.file_type} by matching lecture number {source.lecture_number}."
    return f"Attached {source.file_type} by simple topic keyword matching."


def build_batch_plan(
    sources: list[SourceFile],
) -> tuple[list[BatchPlan], list[tuple[SourceFile, str]]]:
    batches = build_slide_batches(sources)
    created_from_slides = bool(batches)

    if not batches:
        batches = build_non_slide_batches(sources)

    assigned_paths = {
        source.path
        for batch in batches
        for source in batch.primary_sources
    }
    unassigned: list[tuple[SourceFile, str]] = []

    for source in sorted(sources, key=lambda item: item.path):
        if source.path in assigned_paths:
            continue

        if source.file_type not in SUPPORT_SOURCE_TYPES:
            unassigned.append(
                (source, "No conceptual batch could be inferred from metadata.")
            )
            continue

        reason = attach_source_to_batch(source, batches)
        if reason:
            matches = matching_batches(source, batches)
            if len(matches) == 1:
                matches[0].notes.append(reason)
            assigned_paths.add(source.path)
            continue

        if source.file_type == "exams":
            unassigned.append(
                (
                    source,
                    "Exam file left for review; exams do not create normal conceptual batches by default.",
                )
            )
        elif created_from_slides:
            unassigned.append(
                (
                    source,
                    "No unique slide-led conceptual batch matched by lecture number or topic words.",
                )
            )
        else:
            unassigned.append(
                (
                    source,
                    "No clear lecture/topic source or matching conceptual batch was found.",
                )
            )

    for batch in batches:
        batch.supporting_sources.sort(key=lambda item: item.path)
        batch.notes = list(dict.fromkeys(batch.notes))

    return sorted(batches, key=batch_sort_key), unassigned


def difficulty_for_batch(batch: BatchPlan) -> str:
    all_sources = [*batch.primary_sources, *batch.supporting_sources]
    tokens: set[str] = set()
    for source in all_sources:
        tokens.update(topic_tokens(source))
        tokens.update(path_tokens(source))

    if tokens & {"advanced", "proof", "theorem", "derivative", "optimization"}:
        return "high"

    return "medium"


def exam_relevance_for_batch(batch: BatchPlan) -> str:
    source_types = {
        source.file_type
        for source in [*batch.primary_sources, *batch.supporting_sources]
    }

    if source_types & {"exams", "exercises"}:
        return "high"
    if source_types & {"slides", "notes"}:
        return "medium"

    return "low"


def write_batch_plan(root: Path, sources: list[SourceFile]) -> None:
    target = root / BATCH_PLAN_PATH
    target.parent.mkdir(parents=True, exist_ok=True)

    batches, unassigned = build_batch_plan(sources)

    lines = [
        "# Batch Plan",
        "",
        "This first-pass plan uses filenames, folders, lecture numbers, and simple topic keywords only. "
        "Slides usually define conceptual batches; exercises, readings, transcripts, notes, and exams "
        "are attached conservatively as supporting sources.",
        "",
    ]

    if not sources:
        lines.extend(["No source files found.", ""])
    else:
        for index, batch in enumerate(batches, start=1):
            title = title_slug(batch.title)
            all_batch_sources = [*batch.primary_sources, *batch.supporting_sources]
            lines.extend(
                [
                    f"## Batch_{index:02d}_{title}",
                    "",
                    "Status: planned",
                    f"Difficulty: {difficulty_for_batch(batch)}",
                    f"Exam relevance: {exam_relevance_for_batch(batch)}",
                    "",
                    "### Primary sources",
                    "",
                    *source_list_lines(batch.primary_sources),
                    "",
                    "### Supporting sources",
                    "",
                    *source_list_lines(batch.supporting_sources),
                    "",
                    "### Expected outputs",
                    "",
                    *expected_output_lines(all_batch_sources),
                    "",
                    "### Notes",
                    "",
                    " ".join(batch.notes),
                ]
            )
            lines.append("")

        if unassigned:
            lines.extend(
                [
                    "## Unassigned / needs review",
                    "",
                    "These files were discovered but could not be confidently attached to a conceptual batch from metadata alone.",
                    "",
                ]
            )
            for source, reason in unassigned:
                lines.append(f"- `{source.path}` - {reason}")
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
