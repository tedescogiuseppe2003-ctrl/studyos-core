#!/usr/bin/env python3
"""Validate StudyOS source references in analysis files and outputs."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


REPORT_PATH = Path("review/source-coverage.md")

SCAN_FOLDERS = ("analysis/batches", "analysis/visual", "outputs")
TEXT_SUFFIXES = {
    ".csv",
    ".json",
    ".md",
    ".text",
    ".txt",
    ".yaml",
    ".yml",
}
SOURCE_LINE_PATTERN = re.compile(
    r"^\s*(?:[-*]\s*)?(?:source|sources|source references?|citations?)\s*:\s*(.+)$",
    re.IGNORECASE | re.MULTILINE,
)
INPUTS_PATH_PATTERN = re.compile(
    r"(inputs/[^\n\r`\]\)\},;:|]+)",
    re.IGNORECASE,
)
REFERENCE_TOKEN_PATTERN = re.compile(
    r"(?P<token>[\w ./()@+\-]+?\.(?:csv|docx?|html?|jpe?g|md|pdf|png|pptx?|txt|xlsx?))",
    re.IGNORECASE,
)
PLACEHOLDER_PATTERN = re.compile(
    r"\b(?:citation needed|source needed|missing source|todo source|unknown source|tbd source)\b",
    re.IGNORECASE,
)
TRAILING_PUNCTUATION = " \t\r\n`'\".,;:)]}"
LEADING_PUNCTUATION = " \t\r\n`'\"([{"
PIPELINE_REFERENCE_PREFIXES = (
    "analysis/",
    "outputs/",
    "review/",
    "study-os/",
)


@dataclass(frozen=True)
class SourceIndex:
    relative_paths: set[str]
    basenames: set[str]


@dataclass(frozen=True)
class FileCitationResult:
    path: str
    reference_count: int
    missing_references: list[str]
    suspicious_references: list[str]
    placeholders: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate StudyOS source references against inputs/."
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


def build_source_index(root: Path) -> SourceIndex:
    inputs = root / "inputs"
    relative_paths: set[str] = set()
    basenames: set[str] = set()

    if inputs.is_dir():
        for path in sorted(inputs.rglob("*")):
            if path.is_file():
                relative_paths.add(relative(path, root).lower())
                basenames.add(path.name.lower())

    return SourceIndex(relative_paths=relative_paths, basenames=basenames)


def text_files(root: Path) -> list[Path]:
    files: list[Path] = []

    for folder in SCAN_FOLDERS:
        base = root / folder
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
                files.append(path)

    return files


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def clean_reference(value: str) -> str:
    cleaned = value.strip(LEADING_PUNCTUATION + TRAILING_PUNCTUATION)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip(LEADING_PUNCTUATION + TRAILING_PUNCTUATION)


def split_source_line(value: str) -> list[str]:
    parts = re.split(r"\s*(?:;|,|\band\b)\s*", value, flags=re.IGNORECASE)
    return [clean_reference(part) for part in parts if clean_reference(part)]


def is_pipeline_reference(reference: str) -> bool:
    normalized = reference.replace("\\", "/").lower().removeprefix("./")
    return normalized.startswith(PIPELINE_REFERENCE_PREFIXES)


def extract_references(text: str) -> list[str]:
    references: list[str] = []

    for match in INPUTS_PATH_PATTERN.finditer(text):
        references.append(clean_reference(match.group(1)))

    for match in SOURCE_LINE_PATTERN.finditer(text):
        source_line = match.group(1)
        line_references = split_source_line(source_line)
        found_file_token = False
        for reference in line_references:
            token_matches = list(REFERENCE_TOKEN_PATTERN.finditer(reference))
            if token_matches:
                found_file_token = True
                for token_match in token_matches:
                    token = clean_reference(token_match.group("token"))
                    if not is_pipeline_reference(token):
                        references.append(token)
            elif (
                reference
                and not PLACEHOLDER_PATTERN.search(reference)
                and not is_pipeline_reference(reference)
            ):
                references.append(reference)

        if not found_file_token:
            for token_match in REFERENCE_TOKEN_PATTERN.finditer(source_line):
                token = clean_reference(token_match.group("token"))
                if not is_pipeline_reference(token):
                    references.append(token)

    return sorted({reference for reference in references if reference})


def is_reference_valid(reference: str, source_index: SourceIndex) -> bool:
    normalized = reference.replace("\\", "/").lower()
    normalized = normalized.removeprefix("./")

    if normalized.startswith("inputs/"):
        return normalized in source_index.relative_paths

    return Path(normalized).name in source_index.basenames


def is_suspicious_reference(reference: str) -> bool:
    normalized = reference.strip().lower()
    if normalized in {"source", "sources", "source references", "n/a", "none"}:
        return True
    if len(normalized) < 4:
        return True
    if "placeholder" in normalized or "example source" in normalized:
        return True
    return "." not in normalized and not normalized.startswith("inputs/")


def validate_file(path: Path, root: Path, source_index: SourceIndex) -> FileCitationResult:
    text = read_text(path)
    references = extract_references(text)
    placeholders = sorted({match.group(0) for match in PLACEHOLDER_PATTERN.finditer(text)})

    missing = [
        reference
        for reference in references
        if not is_suspicious_reference(reference)
        and not is_reference_valid(reference, source_index)
    ]
    suspicious = [
        reference for reference in references if is_suspicious_reference(reference)
    ]

    return FileCitationResult(
        path=relative(path, root),
        reference_count=len(references),
        missing_references=sorted(set(missing)),
        suspicious_references=sorted(set(suspicious)),
        placeholders=placeholders,
    )


def table_row(values: list[str]) -> str:
    escaped = [value.replace("|", "\\|").replace("\n", " ") for value in values]
    return "| " + " | ".join(escaped) + " |"


def format_list(values: list[str]) -> str:
    if not values:
        return ""
    return "<br>".join(f"`{value}`" for value in values)


def write_report(
    root: Path,
    source_index: SourceIndex,
    results: list[FileCitationResult],
    scan_files: list[Path],
) -> Path:
    report = root / REPORT_PATH
    report.parent.mkdir(parents=True, exist_ok=True)

    no_reference = [result for result in results if result.reference_count == 0]
    missing = [result for result in results if result.missing_references]
    suspicious = [
        result
        for result in results
        if result.suspicious_references or result.placeholders
    ]
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    lines = [
        "# StudyOS Source Coverage",
        "",
        f"Generated: {generated_at}",
        f"Root: `{root}`",
        "",
        "## Summary",
        "",
        f"- Source files in inputs: {len(source_index.relative_paths)}",
        f"- Analysis/output text files checked: {len(scan_files)}",
        f"- Files with no source references: {len(no_reference)}",
        f"- Files with missing cited source files: {len(missing)}",
        f"- Files with suspicious source references: {len(suspicious)}",
        "",
    ]

    if not source_index.relative_paths:
        lines.extend(
            [
                "## Input Sources",
                "",
                "No source files were found under `inputs/`.",
                "",
            ]
        )

    lines.extend(["## File Coverage", ""])
    if results:
        lines.extend(
            [
                table_row(
                    [
                        "File",
                        "References",
                        "Missing cited files",
                        "Suspicious references",
                        "Placeholders",
                    ]
                ),
                table_row(["---", "---", "---", "---", "---"]),
            ]
        )
        for result in results:
            lines.append(
                table_row(
                    [
                        result.path,
                        str(result.reference_count),
                        format_list(result.missing_references),
                        format_list(result.suspicious_references),
                        format_list(result.placeholders),
                    ]
                )
            )
    else:
        lines.append("No analysis or output text files were found.")

    lines.append("")
    report.write_text("\n".join(lines), encoding="utf-8")
    return report


def main() -> int:
    args = parse_args()
    root = args.root.expanduser().resolve()

    try:
        source_index = build_source_index(root)
        scan_files = text_files(root)
        results = [
            validate_file(path, root, source_index)
            for path in scan_files
            if path.stat().st_size > 0
        ]
        report = write_report(root, source_index, results, scan_files)
    except OSError as error:
        print(f"StudyOS citation validation failed: {error}", file=sys.stderr)
        return 2

    has_errors = (
        not source_index.relative_paths
        or any(result.reference_count == 0 for result in results)
        or any(result.missing_references for result in results)
        or any(result.suspicious_references or result.placeholders for result in results)
    )
    print(f"Wrote citation validation report: {report}")
    return 1 if has_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
