#!/usr/bin/env python3
"""Validate StudyOS output folders and files for an installed subject."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


REPORT_PATH = Path("review/validation-report.md")

REQUIRED_FOLDERS = (
    "inputs",
    "working",
    "working/inventory",
    "working/digests",
    "working/learning-cores",
    "outputs",
    "review",
    "study-os",
)

REQUIRED_OUTPUT_CATEGORIES = (
    "master-notes",
    "formula-sheets",
    "flashcards",
    "exam-questions",
    "cheat-sheets",
    "study-plan",
)

IGNORED_NAMES = {".DS_Store"}


@dataclass(frozen=True)
class Finding:
    severity: str
    check: str
    path: str
    detail: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate StudyOS output folder structure and non-empty files."
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


def output_files(root: Path) -> list[Path]:
    outputs = root / "outputs"
    if not outputs.is_dir():
        return []

    return sorted(
        path
        for path in outputs.rglob("*")
        if path.is_file() and path.name not in IGNORED_NAMES
    )


def category_has_non_empty_file(category: Path) -> bool:
    if not category.is_dir():
        return False

    for path in category.rglob("*"):
        if path.is_file() and path.name not in IGNORED_NAMES and path.stat().st_size > 0:
            return True
    return False


def validate(root: Path) -> tuple[list[Finding], list[Path]]:
    findings: list[Finding] = []

    for folder in REQUIRED_FOLDERS:
        path = root / folder
        if not path.is_dir():
            findings.append(
                Finding(
                    "error",
                    "required folder",
                    folder,
                    "Required folder is missing.",
                )
            )

    for category in REQUIRED_OUTPUT_CATEGORIES:
        path = root / "outputs" / category
        if not path.is_dir():
            findings.append(
                Finding(
                    "error",
                    "output category",
                    f"outputs/{category}",
                    "Required output category folder is missing.",
                )
            )

    files = output_files(root)
    if (root / "outputs").is_dir() and not files:
        findings.append(
            Finding("error", "output files", "outputs", "No output files found.")
        )

    for path in files:
        if path.stat().st_size == 0:
            findings.append(
                Finding(
                    "error",
                    "empty output file",
                    relative(path, root),
                    "Output file is empty.",
                )
            )

    return findings, files


def table_row(values: list[str]) -> str:
    escaped = [value.replace("|", "\\|").replace("\n", " ") for value in values]
    return "| " + " | ".join(escaped) + " |"


def write_report(root: Path, findings: list[Finding], files: list[Path]) -> Path:
    report = root / REPORT_PATH
    report.parent.mkdir(parents=True, exist_ok=True)

    error_count = sum(1 for finding in findings if finding.severity == "error")
    warning_count = sum(1 for finding in findings if finding.severity == "warning")
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    lines = [
        "# StudyOS Validation Report",
        "",
        f"Generated: {generated_at}",
        f"Root: `{root}`",
        "",
        "## Summary",
        "",
        f"- Required folders checked: {len(REQUIRED_FOLDERS)}",
        f"- Required output categories checked: {len(REQUIRED_OUTPUT_CATEGORIES)}",
        f"- Output files checked: {len(files)}",
        f"- Errors: {error_count}",
        f"- Warnings: {warning_count}",
        "",
        "## Required Output Categories",
        "",
        table_row(["Category", "Folder exists", "Has non-empty file"]),
        table_row(["---", "---", "---"]),
    ]

    for category in REQUIRED_OUTPUT_CATEGORIES:
        path = root / "outputs" / category
        lines.append(
            table_row(
                [
                    f"outputs/{category}",
                    "yes" if path.is_dir() else "no",
                    "yes" if category_has_non_empty_file(path) else "no",
                ]
            )
        )

    lines.extend(["", "## Findings", ""])
    if findings:
        lines.extend(
            [
                table_row(["Severity", "Check", "Path", "Detail"]),
                table_row(["---", "---", "---", "---"]),
            ]
        )
        for finding in findings:
            lines.append(
                table_row(
                    [finding.severity, finding.check, finding.path, finding.detail]
                )
            )
    else:
        lines.append("No validation errors found.")

    lines.append("")
    report.write_text("\n".join(lines), encoding="utf-8")
    return report


def main() -> int:
    args = parse_args()
    root = args.root.expanduser().resolve()

    try:
        findings, files = validate(root)
        report = write_report(root, findings, files)
    except OSError as error:
        print(f"StudyOS output validation failed: {error}", file=sys.stderr)
        return 2

    print(f"Wrote output validation report: {report}")
    return 1 if any(finding.severity == "error" for finding in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
