#!/usr/bin/env python3
"""Validate StudyOS formula sheet entries."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


FORMULA_DIR = Path("outputs/formula-sheets")
REPORT_PATH = Path("review/formula_validation_report.md")
TEXT_SUFFIXES = {".md", ".text", ".txt"}
REQUIRED_FIELDS = (
    "Formula:",
    "Variables:",
    "Assumptions:",
    "Use when:",
    "Interpretation:",
    "Common mistake:",
    "Source:",
)
FORMULA_HEADING_PATTERN = re.compile(r"(?im)^\s*(?:[-*]\s*)?Formula\s*:")


@dataclass(frozen=True)
class FormulaEntry:
    file_path: str
    entry_number: int
    title: str
    missing_fields: list[str]


@dataclass(frozen=True)
class FormulaFileResult:
    path: str
    entry_count: int
    entries: list[FormulaEntry]
    file_errors: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate StudyOS formula sheets for required entry fields."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Installed subject folder root. Defaults to the current directory.",
    )
    return parser.parse_args()


def relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def formula_files(root: Path) -> list[Path]:
    folder = root / FORMULA_DIR
    if not folder.is_dir():
        return []
    return sorted(
        path
        for path in folder.rglob("*")
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES
    )


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def field_present(entry_text: str, field: str) -> bool:
    name = re.escape(field[:-1])
    return re.search(rf"(?im)^\s*(?:[-*]\s*)?{name}\s*:", entry_text) is not None


def entry_title(entry_text: str) -> str:
    for line in entry_text.splitlines():
        cleaned = line.strip()
        if cleaned:
            return cleaned[:80]
    return "Untitled formula entry"


def split_formula_entries(text: str) -> list[str]:
    matches = list(FORMULA_HEADING_PATTERN.finditer(text))
    if not matches:
        return []

    entries: list[str] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        entries.append(text[start:end].strip())
    return [entry for entry in entries if entry]


def validate_file(path: Path, root: Path) -> FormulaFileResult:
    errors: list[str] = []
    if path.stat().st_size == 0:
        errors.append("Formula sheet is empty.")
        return FormulaFileResult(relative(path, root), 0, [], errors)

    text = read_text(path)
    entries_text = split_formula_entries(text)
    if not entries_text:
        errors.append("No formula entries beginning with `Formula:` were found.")
        return FormulaFileResult(relative(path, root), 0, [], errors)

    entries: list[FormulaEntry] = []
    relative_path = relative(path, root)
    for index, entry_text in enumerate(entries_text, start=1):
        missing = [
            field for field in REQUIRED_FIELDS if not field_present(entry_text, field)
        ]
        entries.append(
            FormulaEntry(
                file_path=relative_path,
                entry_number=index,
                title=entry_title(entry_text),
                missing_fields=missing,
            )
        )

    return FormulaFileResult(relative_path, len(entries), entries, errors)


def table_row(values: list[str]) -> str:
    escaped = [value.replace("|", "\\|").replace("\n", " ") for value in values]
    return "| " + " | ".join(escaped) + " |"


def write_report(root: Path, results: list[FormulaFileResult], files: list[Path]) -> Path:
    report = root / REPORT_PATH
    report.parent.mkdir(parents=True, exist_ok=True)

    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    total_entries = sum(result.entry_count for result in results)
    entries_with_missing = [
        entry
        for result in results
        for entry in result.entries
        if entry.missing_fields
    ]
    file_errors = [
        (result.path, error)
        for result in results
        for error in result.file_errors
    ]

    lines = [
        "# StudyOS Formula Validation Report",
        "",
        f"Generated: {generated_at}",
        f"Root: `{root}`",
        "",
        "## Summary",
        "",
        f"- Formula sheet folder exists: {'yes' if (root / FORMULA_DIR).is_dir() else 'no'}",
        f"- Formula sheet files checked: {len(files)}",
        f"- Formula entries checked: {total_entries}",
        f"- Entries with missing fields: {len(entries_with_missing)}",
        f"- File-level errors: {len(file_errors)}",
        "",
        "## Required Fields",
        "",
    ]

    lines.extend(f"- `{field}`" for field in REQUIRED_FIELDS)
    lines.extend(["", "## File Results", ""])

    if results:
        lines.extend(
            [
                table_row(["File", "Entries", "File errors"]),
                table_row(["---", "---", "---"]),
            ]
        )
        for result in results:
            errors = "<br>".join(result.file_errors)
            lines.append(table_row([result.path, str(result.entry_count), errors]))
    else:
        lines.append("No formula sheet files were found.")

    lines.extend(["", "## Missing Fields", ""])
    if entries_with_missing:
        lines.extend(
            [
                table_row(["File", "Entry", "Formula", "Missing fields"]),
                table_row(["---", "---", "---", "---"]),
            ]
        )
        for entry in entries_with_missing:
            lines.append(
                table_row(
                    [
                        entry.file_path,
                        str(entry.entry_number),
                        entry.title,
                        "<br>".join(f"`{field}`" for field in entry.missing_fields),
                    ]
                )
            )
    else:
        lines.append("No missing formula fields found.")

    lines.append("")
    report.write_text("\n".join(lines), encoding="utf-8")
    return report


def main() -> int:
    args = parse_args()
    root = args.root.expanduser().resolve()

    try:
        files = formula_files(root)
        results = [validate_file(path, root) for path in files]
        report = write_report(root, results, files)
    except OSError as error:
        print(f"StudyOS formula validation failed: {error}", file=sys.stderr)
        return 2

    has_errors = (
        not (root / FORMULA_DIR).is_dir()
        or not files
        or any(result.file_errors for result in results)
        or any(entry.missing_fields for result in results for entry in result.entries)
    )
    print(f"Wrote formula validation report: {report}")
    return 1 if has_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
