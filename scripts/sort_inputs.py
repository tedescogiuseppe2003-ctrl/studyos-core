#!/usr/bin/env python3
"""Execute an approved StudyOS input sorting plan."""

from __future__ import annotations

import argparse
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


PLAN_PATH = Path("working/inventory/sorting_plan.md")
LOG_PATH = Path("working/inventory/sorting_log.md")

PROTECTED_TOP_LEVELS = {
    "inputs",
    "working",
    "outputs",
    "review",
    "study-os",
    ".git",
    ".agents",
    ".claude",
}

SKIP_ACTIONS = {"skip", "needs review"}


class SortingPlanError(ValueError):
    """Raised when the sorting plan cannot be safely executed."""


@dataclass(frozen=True)
class PlanRow:
    source: str
    destination_folder: str
    clean_filename: str
    action: str


@dataclass(frozen=True)
class LogRow:
    source: str
    destination: str
    status: str
    reason: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Execute an approved StudyOS sorting plan."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Installed subject folder root. Defaults to the current directory.",
    )
    return parser.parse_args()


def normalize_header(value: str) -> str:
    return " ".join(value.strip().lower().split())


def normalize_action(value: str) -> str:
    return " ".join(value.strip().lower().split())


def split_markdown_row(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        raise SortingPlanError(f"Malformed Markdown table row: {line}")

    content = stripped[1:-1]
    cells: list[str] = []
    current: list[str] = []
    escaped = False

    for character in content:
        if escaped:
            current.append(character)
            escaped = False
        elif character == "\\":
            escaped = True
        elif character == "|":
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(character)

    if escaped:
        current.append("\\")

    cells.append("".join(current).strip())
    return cells


def is_separator_cell(value: str) -> bool:
    stripped = value.strip()
    return bool(stripped) and set(stripped) <= {"-", ":"} and "-" in stripped


def find_plan_table(lines: list[str]) -> tuple[list[str], list[list[str]]]:
    for index, line in enumerate(lines):
        if not line.strip().startswith("|"):
            continue

        header = split_markdown_row(line)
        header_lookup = {normalize_header(value) for value in header}
        if "current path" not in header_lookup or "action" not in header_lookup:
            continue

        if index + 1 >= len(lines):
            raise SortingPlanError("Sorting plan table is missing a separator row.")

        separator = split_markdown_row(lines[index + 1])
        if len(separator) != len(header) or not all(
            is_separator_cell(cell) for cell in separator
        ):
            raise SortingPlanError("Sorting plan table has an invalid separator row.")

        rows: list[list[str]] = []
        for line_number, row_line in enumerate(lines[index + 2 :], start=index + 3):
            if not row_line.strip():
                if rows:
                    break
                continue

            if not row_line.strip().startswith("|"):
                break

            row = split_markdown_row(row_line)
            if len(row) != len(header):
                raise SortingPlanError(
                    f"Sorting plan table row {line_number} has {len(row)} cells; "
                    f"expected {len(header)}."
                )
            rows.append(row)

        return header, rows

    raise SortingPlanError("No sorting plan Markdown table was found.")


def read_plan(root: Path) -> list[PlanRow]:
    plan_path = root / PLAN_PATH
    if not plan_path.is_file():
        raise SortingPlanError(f"Missing sorting plan: {PLAN_PATH}")

    lines = plan_path.read_text(encoding="utf-8").splitlines()
    header, rows = find_plan_table(lines)

    column_lookup = {
        normalize_header(column): index for index, column in enumerate(header)
    }
    required_columns = {
        "current path": "Current path",
        "proposed destination folder": "Proposed destination folder",
        "action": "Action",
    }
    missing = [
        label for key, label in required_columns.items() if key not in column_lookup
    ]
    if missing:
        raise SortingPlanError(
            "Sorting plan table is missing required column(s): "
            + ", ".join(missing)
        )

    filename_index = column_lookup.get("proposed clean filename")

    plan_rows: list[PlanRow] = []
    for row_number, row in enumerate(rows, start=1):
        action = normalize_action(row[column_lookup["action"]])
        if action not in {"move", *SKIP_ACTIONS}:
            raise SortingPlanError(
                f"Sorting plan row {row_number} has unsupported action: {action}"
            )

        plan_rows.append(
            PlanRow(
                source=row[column_lookup["current path"]].strip(),
                destination_folder=row[
                    column_lookup["proposed destination folder"]
                ].strip(),
                clean_filename=(
                    row[filename_index].strip()
                    if filename_index is not None
                    else ""
                ),
                action=action,
            )
        )

    return plan_rows


def resolve_relative_path(root: Path, raw_path: str, label: str) -> Path:
    path = Path(raw_path)
    if not raw_path or path.is_absolute():
        raise SortingPlanError(f"{label} must be a relative path: {raw_path}")

    resolved = (root / path).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise SortingPlanError(
            f"{label} escapes the subject folder: {raw_path}"
        ) from error

    return resolved


def is_under(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def source_is_protected(raw_path: str) -> bool:
    parts = Path(raw_path).parts
    return bool(parts) and parts[0] in PROTECTED_TOP_LEVELS


def destination_is_allowed(destination_folder: Path, inputs_root: Path) -> bool:
    return destination_folder != inputs_root and is_under(
        destination_folder, inputs_root
    )


def destination_filename(source_path: Path, clean_filename: str) -> str:
    if not clean_filename:
        return source_path.name

    clean_path = Path(clean_filename)
    if clean_path.name != clean_filename:
        raise SortingPlanError(
            f"Proposed clean filename must not contain a path: {clean_filename}"
        )

    source_suffix = source_path.suffix
    if not source_suffix:
        return clean_path.stem if clean_path.suffix else clean_filename

    if clean_path.suffix.lower() == source_suffix.lower():
        return f"{clean_path.stem}{source_suffix}"

    if clean_path.suffix:
        return f"{clean_path.stem}{source_suffix}"

    return f"{clean_filename}{source_suffix}"


def unique_destination_path(destination_folder: Path, filename: str) -> Path:
    candidate = destination_folder / filename
    if not candidate.exists() and not candidate.is_symlink():
        return candidate

    path = Path(filename)
    suffix = path.suffix
    stem = path.stem
    counter = 1

    while True:
        candidate = destination_folder / f"{stem}_{counter}{suffix}"
        if not candidate.exists() and not candidate.is_symlink():
            return candidate
        counter += 1


def execute_move(root: Path, row: PlanRow) -> LogRow:
    if source_is_protected(row.source):
        return LogRow(
            row.source,
            "",
            "error",
            "source path is inside a protected StudyOS folder",
        )

    try:
        source_path = resolve_relative_path(root, row.source, "Current path")
        destination_folder = resolve_relative_path(
            root, row.destination_folder, "Proposed destination folder"
        )
        filename = destination_filename(source_path, row.clean_filename)
    except SortingPlanError as error:
        return LogRow(row.source, "", "error", str(error))

    inputs_root = (root / "inputs").resolve()
    if not destination_is_allowed(destination_folder, inputs_root):
        return LogRow(
            row.source,
            "",
            "error",
            "destination folder is not under inputs/",
        )

    if source_path.is_symlink():
        return LogRow(row.source, "", "error", "source path is a symlink")

    if not source_path.is_file():
        return LogRow(row.source, "", "error", "source file does not exist")

    final_path = unique_destination_path(destination_folder, filename)

    destination_folder.mkdir(parents=True, exist_ok=True)
    try:
        shutil.move(str(source_path), str(final_path))
    except OSError as error:
        return LogRow(
            row.source,
            final_path.relative_to(root).as_posix(),
            "error",
            str(error),
        )

    return LogRow(
        row.source,
        final_path.relative_to(root).as_posix(),
        "moved",
        "moved according to approved sorting plan",
    )


def execute_plan(root: Path, rows: list[PlanRow]) -> list[LogRow]:
    log_rows: list[LogRow] = []

    for row in rows:
        if row.action in SKIP_ACTIONS:
            log_rows.append(
                LogRow(
                    row.source,
                    "",
                    "skipped",
                    f"action is {row.action}",
                )
            )
            continue

        log_rows.append(execute_move(root, row))

    return log_rows


def markdown_table_row(values: list[str]) -> str:
    escaped = [value.replace("|", "\\|").replace("\n", " ") for value in values]
    return "| " + " | ".join(escaped) + " |"


def write_log(root: Path, rows: list[LogRow], plan_error: str | None = None) -> None:
    moved = sum(1 for row in rows if row.status == "moved")
    skipped = sum(1 for row in rows if row.status == "skipped")
    failed = sum(1 for row in rows if row.status == "error")
    executed_at = datetime.now(timezone.utc).date().isoformat()

    lines = [
        "# Sorting Log",
        "",
        f"Executed: {executed_at}",
        f"Plan: {PLAN_PATH.as_posix()}",
        "",
        "## Summary",
        "",
        f"- Moved: {moved}",
        f"- Skipped: {skipped}",
        f"- Failed: {failed + (1 if plan_error else 0)}",
        "",
        "## Log",
        "",
        markdown_table_row(["Source", "Destination", "Status", "Reason"]),
        markdown_table_row(["---", "---", "---", "---"]),
    ]

    if plan_error:
        lines.append(markdown_table_row(["", "", "error", plan_error]))
    else:
        for row in rows:
            lines.append(
                markdown_table_row(
                    [row.source, row.destination, row.status, row.reason]
                )
            )

    lines.append("")

    target = root / LOG_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    root = args.root.expanduser().resolve()

    try:
        rows = read_plan(root)
    except (OSError, SortingPlanError) as error:
        write_log(root, [], str(error))
        print(f"StudyOS sorting failed safely: {error}", file=sys.stderr)
        print(f"Wrote sorting log: {root / LOG_PATH}", file=sys.stderr)
        return 1

    log_rows = execute_plan(root, rows)
    write_log(root, log_rows)

    moved = sum(1 for row in log_rows if row.status == "moved")
    skipped = sum(1 for row in log_rows if row.status == "skipped")
    failed = sum(1 for row in log_rows if row.status == "error")

    print(f"Moved: {moved}")
    print(f"Skipped: {skipped}")
    print(f"Failed: {failed}")
    print(f"Wrote sorting log: {root / LOG_PATH}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
