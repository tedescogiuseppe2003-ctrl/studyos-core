#!/usr/bin/env python3
"""Validate StudyOS output folders and generated files for an installed subject."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


REPORT_PATH = Path("review/validation-report.md")
DETAIL_REPORT_PATH = Path("analysis/validation/output-structure.md")
SOURCE_COVERAGE_REPORT_PATH = Path("review/source-coverage.md")
SEVERITIES = ("low", "medium", "high", "blocking")

REQUIRED_FOLDERS = (
    "inputs",
    "analysis",
    "analysis/inventory",
    "analysis/batches",
    "analysis/visual",
    "analysis/validation",
    "outputs",
    "review",
    "study-os",
    "study-os/scripts",
)

REQUIRED_OUTPUT_CATEGORIES = (
    "notes",
    "formulas",
    "questions",
)

IGNORED_NAMES = {".DS_Store"}
TEXT_SUFFIXES = {".md", ".text", ".txt"}
VISUAL_SOURCE_SUFFIXES = {
    ".gif",
    ".jpeg",
    ".jpg",
    ".pdf",
    ".png",
    ".ppt",
    ".pptx",
    ".tif",
    ".tiff",
    ".webp",
}
REQUIRED_SCRIPTS = (
    "validate_outputs.py",
    "validate_citations.py",
    "validate_formulas.py",
)
REQUIRED_DIGEST_SECTIONS = ("Source Coverage",)
VISUAL_DIGEST_SECTION = "Visual Coverage"
REQUIRED_NOTES_SECTIONS = (
    "Scope",
    "Core Notes",
    "Definitions",
    "Examples",
    "Formula Intuition",
    "Exam Relevance",
    "Common Mistakes",
    "Weak Points",
    "Source References",
)
REQUIRED_QUESTION_SECTIONS = (
    "Exam Scope",
    "Questions by Topic",
    "Expected Answers",
    "Source References",
)
REQUIRED_FORMULA_SECTIONS = ("Formula Index", "Notation")
DISPLAY_LATEX_PATTERN = re.compile(
    r"(?s)(\$\$.*?\$\$|\\\[.*?\\\]|\\begin\{(?:align|aligned|equation|gather)\*?\}.*?\\end\{(?:align|aligned|equation|gather)\*?\})"
)
INLINE_CODE_PATTERN = re.compile(r"`[^`\n]+`")
PLAIN_ASCII_FORMULA_PATTERN = re.compile(
    r"(?im)^\s*(?:[-*]\s*)?Formula\s*:\s*([A-Za-z0-9_ ()+\-*/^=<>.,]+)\s*$"
)
QUALITY_NOTE_MINIMUMS = {
    "standard": 900,
    "rigorous": 1200,
    "rigorous_audit": 1200,
}
REMOVED_OUTPUT_MARKERS = (
    "flashcards",
    "cheat-sheets",
    "cheatsheets",
    "study-plans",
    "study_plans",
    "review-packs",
    "review_packs",
)
SOURCE_COVERAGE_STATUSES = {
    "used",
    "partially used",
    "unreadable",
    "irrelevant",
    "duplicate",
    "deferred",
}
SOURCE_COVERAGE_STATUS_ORDER = (
    "partially used",
    "used",
    "unreadable",
    "irrelevant",
    "duplicate",
    "deferred",
)
SOURCE_COVERAGE_REASON_REQUIRED = {"unreadable", "irrelevant", "duplicate", "deferred"}
SOURCE_PATH_SUFFIX_PATTERN = re.compile(
    r"[\w ./()@+\-]+?\.(?:csv|docx?|html?|jpe?g|md|pdf|png|pptx?|txt|xlsx?)",
    re.IGNORECASE,
)
MARKDOWN_HEADING_PATTERN = re.compile(r"^\s*(?P<marks>#{1,6})[ \t]+(?P<title>.*?)[ \t]*$")


@dataclass(frozen=True)
class Finding:
    severity: str
    check: str
    path: str
    detail: str


@dataclass(frozen=True)
class BatchContext:
    name: str
    digest: Path | None
    learning_core: Path | None
    notes: Path | None
    formulas: Path | None
    questions: Path | None
    formula_relevant: bool
    visual_relevant: bool
    exercise_relevant: bool


@dataclass(frozen=True)
class AssignedSource:
    batch: str
    path: str
    role: str


@dataclass(frozen=True)
class SourceCoverageEntry:
    batch: str
    source: str
    status: str
    reason: str


@dataclass(frozen=True)
class SourceCoverageResult:
    batch: str
    digest: str
    source: str
    role: str
    status: str
    reason: str
    severity: str
    issue: str
    recommended_repair: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate StudyOS output folder structure and non-empty files."
    )
    parser.add_argument(
        "--self-check",
        action="store_true",
        help="Run internal parser sanity checks and exit.",
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


def batch_files(root: Path) -> list[Path]:
    batches = root / "analysis" / "batches"
    if not batches.is_dir():
        return []
    return sorted(
        path
        for path in batches.rglob("*")
        if path.is_file() and path.name not in IGNORED_NAMES
    )


def text_output_files(root: Path, relative_folder: str) -> list[Path]:
    folder = root / relative_folder
    if not folder.is_dir():
        return []
    return sorted(
        path
        for path in folder.rglob("*")
        if path.is_file()
        and path.name not in IGNORED_NAMES
        and path.suffix.lower() in TEXT_SUFFIXES
    )


def category_has_non_empty_file(category: Path) -> bool:
    if not category.is_dir():
        return False

    for path in category.rglob("*"):
        if path.is_file() and path.name not in IGNORED_NAMES and path.stat().st_size > 0:
            return True
    return False


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def markdown_heading(line: str) -> tuple[int, str] | None:
    match = MARKDOWN_HEADING_PATTERN.match(line)
    if not match:
        return None

    title = match.group("title").strip()
    title = re.sub(r"[ \t]+#+[ \t]*$", "", title).strip()
    return len(match.group("marks")), title


def normalized_heading_title(title: str) -> str:
    return " ".join(title.split()).casefold()


def has_section(text: str, section: str) -> bool:
    escaped = re.escape(section)
    target = normalized_heading_title(section)
    markdown_match = False
    for line in text.splitlines():
        heading = markdown_heading(line)
        if heading is not None and normalized_heading_title(heading[1]) == target:
            markdown_match = True
            break

    return (
        markdown_match
        or re.search(rf"(?im)^\s*(?:[-*]\s*)?\*\*{escaped}\*\*\s*:?\s*$", text)
        is not None
        or section.lower() in text.lower()
    )


def section_body(text: str, section: str) -> str:
    target = normalized_heading_title(section)
    lines = text.splitlines(keepends=True)

    for index, line in enumerate(lines):
        heading = markdown_heading(line)
        if heading is None:
            continue

        section_level, title = heading
        if normalized_heading_title(title) != target:
            continue

        body_lines: list[str] = []
        for body_line in lines[index + 1 :]:
            next_heading = markdown_heading(body_line)
            if next_heading is not None and next_heading[0] <= section_level:
                break
            body_lines.append(body_line)
        return "".join(body_lines).strip()

    return ""


def run_self_check() -> None:
    sample = """
# Scope
Scope body.

## Core Notes
Core body.

### Model Setup
Nested body.

## Definitions
Definitions body.

### Term A
Nested definition.

## Examples
Examples body.
"""
    core = section_body(sample, "Core Notes")
    definitions = section_body(sample, "Definitions")
    level_three = section_body("### Definitions\nLevel-three body.\n## Next\nStop.", "Definitions")

    assert "Core body." in core
    assert "Nested body." in core
    assert "Definitions body." not in core
    assert "Definitions body." in definitions
    assert "Nested definition." in definitions
    assert "Examples body." not in definitions
    assert level_three == "Level-three body."


def flexible_section_body(text: str, section: str) -> str:
    body = section_body(text, section)
    if body:
        return body

    lines = text.splitlines()
    start_index: int | None = None
    section_pattern = re.compile(rf"(?i)\b{re.escape(section)}\b")
    for index, line in enumerate(lines):
        stripped = line.strip()
        if section_pattern.search(stripped) and (
            stripped.startswith("#")
            or stripped.startswith("**")
            or stripped.endswith(":")
        ):
            start_index = index + 1
            break

    if start_index is None:
        return ""

    body_lines: list[str] = []
    for line in lines[start_index:]:
        stripped = line.strip()
        if body_lines and (
            re.match(r"^#{1,6}\s+\S", stripped)
            or re.match(r"^\*\*[^*]+\*\*\s*:?\s*$", stripped)
        ):
            break
        body_lines.append(line)
    return "\n".join(body_lines).strip()


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def quality_mode(root: Path) -> str:
    subject = root / "subject.yaml"
    if not subject.is_file():
        return "standard"
    text = read_text(subject)
    match = re.search(r"(?im)^\s*quality_mode\s*:\s*[\"']?([\w-]+)", text)
    if match:
        return match.group(1).lower().replace("-", "_")
    match = re.search(r"(?im)^\s*validation_depth\s*:\s*[\"']?([\w-]+)", text)
    if match and match.group(1).lower().replace("-", "_") == "rigorous_audit":
        return "rigorous"
    return "standard"


def digest_mentions_visual_source(text: str) -> bool:
    lowered = text.lower()
    return any(suffix in lowered for suffix in VISUAL_SOURCE_SUFFIXES)


def visual_coverage_is_resolved(text: str) -> bool:
    lowered = text.lower()
    visual_start = lowered.find(VISUAL_DIGEST_SECTION.lower())
    if visual_start == -1:
        return False
    visual_text = lowered[visual_start:]
    return any(
        marker in visual_text
        for marker in (
            "no essential visual",
            "no essential visuals",
            "analyzed",
            "analysis/visual/",
            "unresolved",
            "review/visual-issues.md",
        )
    )


def visual_coverage_relevant(text: str) -> bool:
    lowered = text.lower()
    visual_start = lowered.find(VISUAL_DIGEST_SECTION.lower())
    visual_text = lowered[visual_start:]
    if visual_start != -1 and any(
        marker in visual_text for marker in ("no essential visual", "no visual")
    ):
        return False
    if digest_mentions_visual_source(text):
        return True
    if visual_start == -1:
        return False
    return any(
        marker in visual_text
        for marker in (
            "visual",
            "figure",
            "chart",
            "table",
            "diagram",
            "slide",
            "image",
            "screenshot",
        )
    )


def formula_relevant(text: str) -> bool:
    lowered = text.lower()
    formula_text = section_body(text, "Formulas").lower()
    if not formula_text:
        formula_text = lowered
    if re.search(
        r"(\bno\s+(standalone\s+|important\s+|relevant\s+)?formulas?\b|formulas?\s*:\s*(none|n/a|not applicable)|\bnone\b)",
        formula_text,
    ):
        return False
    return any(
        marker in lowered
        for marker in (
            "$$",
            "\\[",
            "\\begin{",
            "formula:",
            "formula sheet",
            "formula-like",
            "equation",
            "notation",
            "derivative",
            "variance",
            "probability",
            "optimization",
            "calculation",
        )
    )


def exercise_relevant(text: str) -> bool:
    lowered = text.lower()
    return any(
        marker in lowered
        for marker in (
            "inputs/exercises",
            "exercise",
            "problem set",
            "practice problem",
            "tutorial",
            "exam",
        )
    )


def questions_have_answers(text: str) -> bool:
    lowered = text.lower()
    return any(
        marker in lowered
        for marker in (
            "answer key",
            "expected answer",
            "worked solution",
            "solution:",
            "answer:",
        )
    )


def questions_grouped_by_topic(text: str) -> bool:
    lowered = text.lower()
    if "questions by topic" in lowered or "questions by concept" in lowered:
        return True
    topic_headings = re.findall(r"(?im)^\s*#{2,6}\s+.*\b(topic|concept)\b", text)
    return len(topic_headings) >= 1


def questions_have_conceptual_and_exam_style(text: str) -> bool:
    lowered = text.lower()
    has_conceptual = "conceptual" in lowered or "concept question" in lowered
    has_exam = (
        "exam-style" in lowered
        or "exam style" in lowered
        or "likely exam" in lowered
        or "exam question" in lowered
    )
    return has_conceptual and has_exam


def questions_have_formula_application(text: str) -> bool:
    lowered = text.lower()
    return any(
        marker in lowered
        for marker in (
            "formula",
            "calculation",
            "compute",
            "solve",
            "application",
            "apply",
            "derive",
            "$$",
            "\\[",
        )
    )


def questions_have_source_or_topic_references(text: str) -> bool:
    lowered = text.lower()
    return (
        "source references" in lowered
        or "topic references" in lowered
        or "inputs/" in lowered
        or re.search(r"(?im)^\s*(?:[-*]\s*)?(source|topic)\s*:", text) is not None
    )


def exercises_are_practice(text: str) -> bool:
    lowered = text.lower()
    if "exercise" not in lowered and "problem" not in lowered:
        return True
    return any(
        marker in lowered
        for marker in (
            "practice",
            "worked example",
            "worked solution",
            "solution",
            "answer key",
        )
    )


def source_references_present(text: str) -> bool:
    lowered = text.lower()
    return (
        "source references" in lowered
        and (
            "inputs/" in lowered
            or re.search(r"(?im)^\s*(?:[-*]\s*)?(source|sources)\s*:", text)
            is not None
            or re.search(r"\.(pdf|pptx?|docx?|xlsx?|txt|md|csv)\b", text, re.I)
            is not None
        )
    )


def normalize_source_path(value: str) -> str:
    cleaned = value.strip()
    cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cleaned)
    cleaned = cleaned.strip("`*_ \t\r\n'\".,;:)]}")
    cleaned = cleaned.lstrip("./")
    cleaned = cleaned.replace("\\", "/")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.lower()


def source_display_path(value: str) -> str:
    cleaned = value.strip()
    path_match = SOURCE_PATH_SUFFIX_PATTERN.search(cleaned)
    if path_match:
        return path_match.group(0).strip("`*_ \t\r\n'\".,;:)]}")
    return cleaned.strip("`*_ \t\r\n'\".,;:)]}")


def normalize_coverage_status(value: str) -> str:
    cleaned = re.sub(r"[_-]+", " ", value.lower())
    cleaned = re.sub(r"[^a-z ]+", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if cleaned in {"partial", "partially", "partly used", "part used"}:
        return "partially used"
    for status in SOURCE_COVERAGE_STATUS_ORDER:
        if re.search(rf"\b{re.escape(status)}\b", cleaned):
            return status
    return cleaned


def markdown_heading_level(line: str) -> int | None:
    match = re.match(r"^(#{1,6})\s+\S", line.strip())
    return len(match.group(1)) if match else None


def extract_sources_from_line(line: str) -> list[str]:
    if re.search(r"\bnone\b", line, re.IGNORECASE):
        return []
    backtick_sources = [
        source_display_path(match.group(1))
        for match in re.finditer(r"`([^`]+)`", line)
        if source_display_path(match.group(1))
    ]
    if backtick_sources:
        return backtick_sources
    return [
        source_display_path(match.group(0))
        for match in SOURCE_PATH_SUFFIX_PATTERN.finditer(line)
        if source_display_path(match.group(0))
    ]


def parse_batch_plan_assignments(path: Path) -> list[AssignedSource]:
    if not path.is_file():
        return []

    assignments: list[AssignedSource] = []
    current_batch: str | None = None
    current_role: str | None = None
    current_role_level: int | None = None

    for line in read_text(path).splitlines():
        heading_level = markdown_heading_level(line)
        stripped = line.strip()

        if heading_level == 2:
            heading = stripped.lstrip("#").strip()
            current_batch = heading.split()[0]
            if current_batch.lower().startswith("unassigned"):
                current_batch = None
            current_role = None
            current_role_level = None
            continue

        if heading_level is not None:
            heading = stripped.lstrip("#").strip().lower()
            if "primary source" in heading:
                current_role = "primary"
                current_role_level = heading_level
            elif "supporting source" in heading:
                current_role = "supporting"
                current_role_level = heading_level
            elif current_role_level is not None and heading_level <= current_role_level:
                current_role = None
                current_role_level = None
            continue

        if current_batch is None or current_role is None:
            continue

        for source in extract_sources_from_line(line):
            assignments.append(
                AssignedSource(batch=current_batch, path=source, role=current_role)
            )

    deduped: dict[tuple[str, str, str], AssignedSource] = {}
    for assignment in assignments:
        key = (
            assignment.batch,
            normalize_source_path(assignment.path),
            assignment.role,
        )
        deduped[key] = assignment
    return list(deduped.values())


def split_markdown_table_row(line: str) -> list[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    cells: list[str] = []
    current: list[str] = []
    escaped = False
    for character in stripped:
        if escaped:
            current.append(character)
            escaped = False
            continue
        if character == "\\":
            escaped = True
            current.append(character)
            continue
        if character == "|":
            cells.append("".join(current).strip())
            current = []
            continue
        current.append(character)
    cells.append("".join(current).strip())
    return cells


def is_markdown_separator_row(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def header_index(headers: list[str], *needles: str) -> int | None:
    normalized = [re.sub(r"[^a-z]+", " ", header.lower()).strip() for header in headers]
    for needle in needles:
        for index, header in enumerate(normalized):
            if needle in header:
                return index
    return None


def parse_source_coverage_entries(
    digest_text: str,
    batch: str,
) -> list[SourceCoverageEntry]:
    body = flexible_section_body(digest_text, "Source Coverage")
    if not body:
        return []

    entries: list[SourceCoverageEntry] = []
    table_lines = [line for line in body.splitlines() if line.strip().startswith("|")]
    if len(table_lines) >= 2:
        headers = split_markdown_table_row(table_lines[0])
        source_index = header_index(headers, "source", "file")
        status_index = header_index(headers, "status", "use")
        reason_index = header_index(headers, "reason", "explanation", "notes", "detail")

        for line in table_lines[1:]:
            cells = split_markdown_table_row(line)
            if is_markdown_separator_row(cells):
                continue
            if source_index is None or source_index >= len(cells):
                continue
            source = source_display_path(cells[source_index])
            if not source or re.search(r"\bnone\b", source, re.IGNORECASE):
                continue
            status = ""
            if status_index is not None and status_index < len(cells):
                status = normalize_coverage_status(cells[status_index])
            if not status:
                status = normalize_coverage_status(" ".join(cells))
            reason = ""
            if reason_index is not None and reason_index < len(cells):
                reason = cells[reason_index].strip()
            if not reason:
                non_source_cells = [
                    cell
                    for index, cell in enumerate(cells)
                    if index != source_index
                    and (status_index is None or index != status_index)
                    and cell.strip()
                ]
                reason = " ".join(non_source_cells).strip()
            if not reason and status in SOURCE_COVERAGE_REASON_REQUIRED:
                status_cell = (
                    cells[status_index].strip()
                    if status_index is not None and status_index < len(cells)
                    else ""
                )
                status_without_keyword = re.sub(
                    rf"(?i)\b{re.escape(status)}\b\s*[:\-–—]?\s*",
                    "",
                    status_cell,
                    count=1,
                ).strip()
                if status_without_keyword and status_without_keyword != status_cell:
                    reason = status_without_keyword
            entries.append(
                SourceCoverageEntry(
                    batch=batch,
                    source=source,
                    status=status,
                    reason=reason,
                )
            )

    if entries:
        return entries

    for line in body.splitlines():
        sources = extract_sources_from_line(line)
        if not sources:
            continue
        status = normalize_coverage_status(line)
        reason_match = re.search(
            r"(?i)\b(?:reason|because|notes?|explanation)\s*:?\s*(.+)$", line
        )
        reason = reason_match.group(1).strip() if reason_match else ""
        for source in sources:
            entries.append(
                SourceCoverageEntry(
                    batch=batch,
                    source=source,
                    status=status,
                    reason=reason,
                )
            )

    return entries


def source_basename(value: str) -> str:
    return Path(normalize_source_path(value)).name


def coverage_entry_for_assignment(
    assignment: AssignedSource,
    entries: list[SourceCoverageEntry],
    batch_assignments: list[AssignedSource],
) -> SourceCoverageEntry | None:
    assigned_normalized = normalize_source_path(assignment.path)
    for entry in entries:
        if normalize_source_path(entry.source) == assigned_normalized:
            return entry

    basename = source_basename(assignment.path)
    if not basename:
        return None
    assigned_basename_count = sum(
        1 for item in batch_assignments if source_basename(item.path) == basename
    )
    matching_entries = [
        entry for entry in entries if source_basename(entry.source) == basename
    ]
    if assigned_basename_count == 1 and len(matching_entries) == 1:
        return matching_entries[0]
    return None


def source_coverage_severity(
    assignment: AssignedSource,
    status: str,
    has_reason: bool,
    missing: bool,
) -> str:
    if missing:
        return "high" if assignment.role == "primary" else "medium"
    if status == "deferred" and not has_reason:
        return "high"
    if status in {"unreadable", "irrelevant"} and not has_reason:
        return "high" if assignment.role == "primary" else "medium"
    if status == "duplicate" and not has_reason:
        return "medium"
    if status in {"irrelevant", "duplicate"} and has_reason:
        return "medium" if assignment.role == "primary" else "low"
    if status == "unreadable" and has_reason:
        return "medium"
    if status == "deferred" and has_reason:
        return "medium"
    return "low"


def validate_assigned_source_coverage(
    findings: list[Finding],
    root: Path,
    contexts: dict[str, BatchContext],
) -> list[SourceCoverageResult]:
    assignments = parse_batch_plan_assignments(
        root / "analysis" / "inventory" / "batch_plan.md"
    )
    results: list[SourceCoverageResult] = []
    if not assignments:
        return results

    assignments_by_batch: dict[str, list[AssignedSource]] = {}
    for assignment in assignments:
        assignments_by_batch.setdefault(assignment.batch, []).append(assignment)

    for batch, batch_assignments in sorted(assignments_by_batch.items()):
        context = contexts.get(batch)
        digest = context.digest if context else None
        digest_rel = (
            relative(digest, root)
            if digest is not None
            else f"analysis/batches/{batch}_digest.md"
        )
        if digest is None:
            for assignment in batch_assignments:
                severity = "high" if assignment.role == "primary" else "medium"
                detail = (
                    f"Assigned {assignment.role} source `{assignment.path}` cannot be checked "
                    f"because digest `{digest_rel}` is missing."
                )
                append_finding(findings, severity, "source coverage assigned source", digest_rel, detail)
                results.append(
                    SourceCoverageResult(
                        batch=batch,
                        digest=digest_rel,
                        source=assignment.path,
                        role=assignment.role,
                        status="missing digest",
                        reason="",
                        severity=severity,
                        issue=detail,
                        recommended_repair=(
                            "Create or repair the batch digest and include this source in the Source Coverage table."
                        ),
                    )
                )
            continue

        entries = parse_source_coverage_entries(read_text(digest), batch)
        for assignment in batch_assignments:
            entry = coverage_entry_for_assignment(
                assignment, entries, batch_assignments
            )
            if entry is None:
                severity = source_coverage_severity(
                    assignment, "", False, missing=True
                )
                detail = (
                    f"Assigned {assignment.role} source `{assignment.path}` is missing from "
                    "the digest Source Coverage table. Recommended repair: update Source Coverage "
                    "with status used, partially used, unreadable, irrelevant, duplicate, or deferred."
                )
                append_finding(
                    findings,
                    severity,
                    "source coverage missing assigned source",
                    digest_rel,
                    detail,
                )
                results.append(
                    SourceCoverageResult(
                        batch=batch,
                        digest=digest_rel,
                        source=assignment.path,
                        role=assignment.role,
                        status="missing",
                        reason="",
                        severity=severity,
                        issue=detail,
                        recommended_repair=(
                            "Add the assigned source to Source Coverage with an explicit status and reason when not used."
                        ),
                    )
                )
                continue

            status = normalize_coverage_status(entry.status)
            has_reason = bool(entry.reason.strip())
            if status not in SOURCE_COVERAGE_STATUSES:
                detail = (
                    f"Assigned {assignment.role} source `{assignment.path}` has unsupported "
                    f"Source Coverage status `{entry.status or 'missing'}`. Use one of: "
                    "used, partially used, unreadable, irrelevant, duplicate, deferred."
                )
                append_finding(
                    findings,
                    "medium",
                    "source coverage status",
                    digest_rel,
                    detail,
                )
                results.append(
                    SourceCoverageResult(
                        batch=batch,
                        digest=digest_rel,
                        source=assignment.path,
                        role=assignment.role,
                        status=entry.status or "missing",
                        reason=entry.reason,
                        severity="medium",
                        issue=detail,
                        recommended_repair="Replace the status with one of the allowed Source Coverage statuses.",
                    )
                )
                continue

            if status in SOURCE_COVERAGE_REASON_REQUIRED and not has_reason:
                severity = source_coverage_severity(
                    assignment, status, has_reason, missing=False
                )
                detail = (
                    f"Assigned {assignment.role} source `{assignment.path}` is marked `{status}` "
                    "but Source Coverage does not give a reason."
                )
                append_finding(
                    findings,
                    severity,
                    "source coverage missing reason",
                    digest_rel,
                    detail,
                )
                results.append(
                    SourceCoverageResult(
                        batch=batch,
                        digest=digest_rel,
                        source=assignment.path,
                        role=assignment.role,
                        status=status,
                        reason=entry.reason,
                        severity=severity,
                        issue=detail,
                        recommended_repair=(
                            "Add a concrete reason explaining why this assigned source was not fully used."
                        ),
                    )
                )
                continue

            if status in {"irrelevant", "duplicate", "unreadable", "deferred"}:
                severity = source_coverage_severity(
                    assignment, status, has_reason, missing=False
                )
                detail = (
                    f"Assigned {assignment.role} source `{assignment.path}` is marked `{status}` "
                    f"with reason: {entry.reason}."
                )
                append_finding(
                    findings,
                    severity,
                    "source coverage explained non-use",
                    digest_rel,
                    detail,
                )
                results.append(
                    SourceCoverageResult(
                        batch=batch,
                        digest=digest_rel,
                        source=assignment.path,
                        role=assignment.role,
                        status=status,
                        reason=entry.reason,
                        severity=severity,
                        issue=detail,
                        recommended_repair=(
                            "No structural repair required if the explanation is accurate; review if this source should be processed."
                        ),
                    )
                )

    return results


def looks_like_compressed_summary(text: str) -> bool:
    words = word_count(text)
    core_words = word_count(section_body(text, "Core Notes"))
    thin_sections = sum(
        1
        for section in REQUIRED_NOTES_SECTIONS
        if has_section(text, section) and word_count(section_body(text, section)) < 35
    )
    lowered = text.lower()
    summary_signals = (
        "brief summary",
        "quick summary",
        "high-level summary",
        "compressed summary",
        "tl;dr",
    )
    return (
        words < 600
        or core_words < 200
        or thin_sections >= 5
        or any(signal in lowered for signal in summary_signals)
    )


def notes_include_visual_findings(text: str) -> bool:
    lowered = text.lower()
    return any(
        marker in lowered
        for marker in (
            "visual",
            "figure",
            "chart",
            "table",
            "diagram",
            "slide",
            "image",
            "screenshot",
        )
    )


def stem_without_suffix(path: Path, suffix: str) -> str:
    name = path.name
    return name[: -len(suffix)] if name.endswith(suffix) else path.stem


def batch_contexts(root: Path) -> dict[str, BatchContext]:
    digest_paths = {
        stem_without_suffix(path, "_digest.md"): path
        for path in text_output_files(root, "analysis/batches")
        if path.name.endswith("_digest.md")
    }
    learning_core_paths = {
        stem_without_suffix(path, "_learning_core.md"): path
        for path in text_output_files(root, "analysis/batches")
        if path.name.endswith("_learning_core.md")
    }
    notes_paths = {
        path.stem: path
        for path in text_output_files(root, "outputs/notes")
        if path.name != "full_course_notes.md"
    }
    formula_paths = {
        stem_without_suffix(path, "_formulas.md"): path
        for path in text_output_files(root, "outputs/formulas")
        if path.name != "full_formula_sheet.md" and path.name.endswith("_formulas.md")
    }
    question_paths = {
        stem_without_suffix(path, "_questions.md"): path
        for path in text_output_files(root, "outputs/questions")
        if path.name != "full_exam_practice_questions.md"
        and path.name.endswith("_questions.md")
    }

    names = sorted(
        set(digest_paths)
        | set(learning_core_paths)
        | set(notes_paths)
        | set(formula_paths)
        | set(question_paths)
    )
    contexts: dict[str, BatchContext] = {}
    for name in names:
        digest = digest_paths.get(name)
        learning_core = learning_core_paths.get(name)
        support_text = ""
        for path in (digest, learning_core):
            if path and path.is_file() and path.stat().st_size > 0:
                support_text += "\n" + read_text(path)
        contexts[name] = BatchContext(
            name=name,
            digest=digest,
            learning_core=learning_core,
            notes=notes_paths.get(name),
            formulas=formula_paths.get(name),
            questions=question_paths.get(name),
            formula_relevant=(name in formula_paths) or formula_relevant(support_text),
            visual_relevant=visual_coverage_relevant(support_text),
            exercise_relevant=exercise_relevant(support_text),
        )
    return contexts


def append_finding(
    findings: list[Finding],
    severity: str,
    check: str,
    path: str,
    detail: str,
) -> None:
    if severity not in SEVERITIES:
        raise ValueError(f"Unsupported severity: {severity}")
    findings.append(Finding(severity, check, path, detail))


def validate_notes_file(
    findings: list[Finding],
    path: Path,
    root: Path,
    mode: str,
    visual_relevant_for_file: bool,
) -> None:
    rel = relative(path, root)
    if path.stat().st_size == 0:
        append_finding(findings, "blocking", "notes empty", rel, "Notes file is empty.")
        return

    text = read_text(path)
    for section in REQUIRED_NOTES_SECTIONS:
        if not has_section(text, section):
            append_finding(
                findings,
                "high",
                "notes required section",
                rel,
                f"Required notes section is missing: {section}.",
            )

    minimum = QUALITY_NOTE_MINIMUMS.get(mode)
    words = word_count(text)
    if minimum and words < minimum:
        append_finding(
            findings,
            "medium",
            "notes short",
            rel,
            f"Notes have approximately {words} words; {mode} mode usually needs at least about {minimum} words unless the batch is genuinely small.",
        )

    if looks_like_compressed_summary(text):
        append_finding(
            findings,
            "high",
            "notes depth",
            rel,
            "Notes look like a compressed summary rather than complete study notes.",
        )

    if not source_references_present(text):
        append_finding(
            findings,
            "high",
            "notes source references",
            rel,
            "Notes do not include usable source references.",
        )

    if visual_relevant_for_file and not notes_include_visual_findings(text):
        append_finding(
            findings,
            "medium",
            "notes visual findings",
            rel,
            "Batch has relevant visual material, but notes do not clearly include visual findings.",
        )


def validate_questions_file(
    findings: list[Finding],
    path: Path,
    root: Path,
    formula_relevant_for_file: bool,
    exercise_relevant_for_file: bool,
) -> None:
    rel = relative(path, root)
    if path.stat().st_size == 0:
        append_finding(
            findings, "blocking", "questions empty", rel, "Questions file is empty."
        )
        return

    text = read_text(path)
    for section in REQUIRED_QUESTION_SECTIONS:
        if not has_section(text, section):
            append_finding(
                findings,
                "medium",
                "questions required section",
                rel,
                f"Expected questions section is missing or unclear: {section}.",
            )
    if not questions_have_answers(text):
        append_finding(
            findings,
            "high",
            "questions expected answers",
            rel,
            "Questions do not clearly include expected answers, an answer key, or worked solutions.",
        )
    if not questions_grouped_by_topic(text):
        append_finding(
            findings,
            "medium",
            "questions grouping",
            rel,
            "Questions are not clearly grouped by topic or concept.",
        )
    if not questions_have_conceptual_and_exam_style(text):
        append_finding(
            findings,
            "medium",
            "questions mix",
            rel,
            "Questions do not clearly include both conceptual and exam-style prompts.",
        )
    if formula_relevant_for_file and not questions_have_formula_application(text):
        append_finding(
            findings,
            "medium",
            "questions formula practice",
            rel,
            "Formula-heavy material lacks clear formula/application/calculation questions.",
        )
    if exercise_relevant_for_file and not exercises_are_practice(text):
        append_finding(
            findings,
            "medium",
            "exercise integration",
            rel,
            "Assigned exercises are not clearly reflected as practice questions with answer support.",
        )
    if not questions_have_source_or_topic_references(text):
        append_finding(
            findings,
            "medium",
            "questions references",
            rel,
            "Questions do not include source references or topic references.",
        )


def validate_formula_file_basic(
    findings: list[Finding],
    path: Path,
    root: Path,
) -> None:
    rel = relative(path, root)
    if path.stat().st_size == 0:
        append_finding(
            findings, "blocking", "formula sheet empty", rel, "Formula sheet is empty."
        )
        return

    text = read_text(path)
    for section in REQUIRED_FORMULA_SECTIONS:
        if not has_section(text, section):
            append_finding(
                findings,
                "high",
                "formula sheet section",
                rel,
                f"Required formula sheet section is missing: {section}.",
            )
    if DISPLAY_LATEX_PATTERN.search(text) is None:
        append_finding(
            findings,
            "high",
            "formula markdown",
            rel,
            "No display LaTeX was found; formulas must not be inline-only or plain ASCII.",
        )
    if (
        PLAIN_ASCII_FORMULA_PATTERN.search(text) is not None
        or INLINE_CODE_PATTERN.search(text) is not None
    ) and DISPLAY_LATEX_PATTERN.search(text) is None:
        append_finding(
            findings,
            "high",
            "formula markdown",
            rel,
            "Formula entries appear to be inline code or plain ASCII only.",
        )


def validate_internal_support(
    findings: list[Finding],
    context: BatchContext,
    root: Path,
) -> None:
    if context.digest is None:
        append_finding(
            findings,
            "high",
            "digest missing",
            f"analysis/batches/{context.name}_digest.md",
            "Batch has outputs or a learning core but no digest.",
        )
    else:
        digest_text = read_text(context.digest)
        rel = relative(context.digest, root)
        if not has_section(digest_text, "Source Coverage"):
            append_finding(
                findings,
                "high",
                "source coverage",
                rel,
                "Digest is missing Source Coverage.",
            )
        if digest_mentions_visual_source(digest_text) and not has_section(
            digest_text, VISUAL_DIGEST_SECTION
        ):
            append_finding(
                findings,
                "high",
                "visual coverage",
                rel,
                "Digest references slide/PDF/image sources but is missing Visual Coverage.",
            )
        elif has_section(digest_text, VISUAL_DIGEST_SECTION) and not visual_coverage_is_resolved(
            digest_text
        ):
            append_finding(
                findings,
                "medium",
                "visual coverage",
                rel,
                "Visual Coverage does not clearly say essential visuals were analyzed or unresolved.",
            )

    if context.learning_core is None:
        append_finding(
            findings,
            "high",
            "learning core missing",
            f"analysis/batches/{context.name}_learning_core.md",
            "Batch learning core is missing.",
        )
    elif context.digest is not None:
        digest_words = word_count(read_text(context.digest))
        core_words = word_count(read_text(context.learning_core))
        if digest_words >= 900 and (core_words < 300 or core_words < digest_words * 0.30):
            append_finding(
                findings,
                "medium",
                "learning core depth",
                relative(context.learning_core, root),
                f"Learning core appears over-compressed relative to digest ({core_words} vs {digest_words} words).",
            )

    unresolved_text = ""
    for path in (context.digest, context.learning_core):
        if path and path.is_file():
            unresolved_text += "\n" + read_text(path)
    lowered = unresolved_text.lower()
    if "unresolved" in lowered and ("visual" in lowered or "formula" in lowered):
        issue_files = [
            root / "review" / "visual-issues.md",
            root / "review" / "unresolved-questions.md",
        ]
        if not any(path.is_file() and path.stat().st_size > 0 for path in issue_files):
            append_finding(
                findings,
                "high",
                "unresolved issues tracking",
                f"analysis/batches/{context.name}",
                "Unresolved visual/formula issues are mentioned but not tracked in review/visual-issues.md or review/unresolved-questions.md.",
            )


def validate(root: Path) -> tuple[list[Finding], list[Path], list[SourceCoverageResult]]:
    findings: list[Finding] = []
    source_coverage_results: list[SourceCoverageResult] = []
    mode = quality_mode(root)

    if not (root / "subject.yaml").is_file():
        append_finding(
            findings,
            "blocking",
            "subject setup",
            "subject.yaml",
            "Subject setup file is missing.",
        )

    for folder in REQUIRED_FOLDERS:
        path = root / folder
        if not path.is_dir():
            append_finding(
                findings,
                "blocking",
                "required folder",
                folder,
                "Required folder is missing.",
            )

    for script in REQUIRED_SCRIPTS:
        path = root / "study-os" / "scripts" / script
        if not path.is_file():
            append_finding(
                findings,
                "blocking",
                "validation script",
                relative(path, root),
                "Required validation script is missing.",
            )

    for category in REQUIRED_OUTPUT_CATEGORIES:
        path = root / "outputs" / category
        if not path.is_dir():
            append_finding(
                findings,
                "high",
                "output category",
                f"outputs/{category}",
                "Required output category folder is missing.",
            )

    files = output_files(root)
    batches = batch_files(root)
    if not files and not batches:
        append_finding(
            findings,
            "medium",
            "preflight",
            "analysis/batches; outputs",
            "Nothing appears to have been processed yet. Run studyos-batch, studyos-course, or studyos-merge before validation.",
        )

    for path in files:
        if path.stat().st_size == 0:
            append_finding(
                findings,
                "blocking",
                "empty output file",
                relative(path, root),
                "Output file is empty.",
            )

    contexts = batch_contexts(root)
    source_coverage_results = validate_assigned_source_coverage(
        findings, root, contexts
    )
    for context in contexts.values():
        validate_internal_support(findings, context, root)

        if context.notes is None:
            append_finding(
                findings,
                "high",
                "notes missing",
                f"outputs/notes/{context.name}.md",
                "Expected batch notes are missing.",
            )
        else:
            validate_notes_file(
                findings, context.notes, root, mode, context.visual_relevant
            )

        if context.formula_relevant and context.formulas is None:
            append_finding(
                findings,
                "high",
                "formula sheet missing",
                f"outputs/formulas/{context.name}_formulas.md",
                "Formula sheet is expected because formulas or notation appear relevant to this batch.",
            )
        elif context.formulas is not None:
            validate_formula_file_basic(findings, context.formulas, root)

        if context.questions is None:
            append_finding(
                findings,
                "high",
                "questions missing",
                f"outputs/questions/{context.name}_questions.md",
                "Expected batch exam practice questions are missing.",
            )
        else:
            validate_questions_file(
                findings,
                context.questions,
                root,
                context.formula_relevant,
                context.exercise_relevant,
            )

    for path in text_output_files(root, "outputs/notes"):
        if path.name == "full_course_notes.md":
            validate_notes_file(findings, path, root, mode, True)

    for path in text_output_files(root, "outputs/questions"):
        if path.name == "full_exam_practice_questions.md":
            validate_questions_file(findings, path, root, True, True)

    for path in text_output_files(root, "outputs/formulas"):
        if path.name == "full_formula_sheet.md":
            validate_formula_file_basic(findings, path, root)

    for marker in REMOVED_OUTPUT_MARKERS:
        removed = root / "outputs" / marker
        if removed.exists():
            append_finding(
                findings,
                "low",
                "removed output present",
                relative(removed, root),
                "Removed/deprecated output type exists but is not required by validation.",
            )

    return findings, files, source_coverage_results


def table_row(values: list[str]) -> str:
    escaped = [value.replace("|", "\\|").replace("\n", " ") for value in values]
    return "| " + " | ".join(escaped) + " |"


def status_for_checks(findings: list[Finding], prefixes: tuple[str, ...]) -> str:
    matching = [
        finding for finding in findings if finding.check.startswith(prefixes)
    ]
    if any(finding.severity == "blocking" for finding in matching):
        return "blocking"
    if any(finding.severity == "high" for finding in matching):
        return "needs repair"
    if any(finding.severity == "medium" for finding in matching):
        return "warning"
    if any(finding.severity == "low" for finding in matching):
        return "minor warning"
    return "pass"


def recommended_repair_target(findings: list[Finding]) -> str:
    if not findings:
        return "None."
    severity_rank = {severity: index for index, severity in enumerate(SEVERITIES)}
    finding = max(findings, key=lambda item: severity_rank[item.severity])
    return f"{finding.path} ({finding.check}: {finding.detail})"


def write_markdown_report(
    root: Path,
    report_path: Path,
    findings: list[Finding],
    files: list[Path],
) -> Path:
    report = root / report_path
    report.parent.mkdir(parents=True, exist_ok=True)

    severity_counts = {
        severity: sum(1 for finding in findings if finding.severity == severity)
        for severity in SEVERITIES
    }
    status = "blocking" if severity_counts["blocking"] else "needs repair" if findings else "pass"
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    lines = [
        "# StudyOS Validation Report",
        "",
        f"Generated: {generated_at}",
        f"Root: `{root}`",
        f"Status: **{status}**",
        "",
        "## Summary",
        "",
        f"- Required folders checked: {len(REQUIRED_FOLDERS)}",
        f"- Required output categories checked: {len(REQUIRED_OUTPUT_CATEGORIES)}",
        f"- Output files checked: {len(files)}",
        f"- Notes status: {status_for_checks(findings, ('notes',))}",
        f"- Formulas status: {status_for_checks(findings, ('formula', 'unresolved issues'))}",
        f"- Questions status: {status_for_checks(findings, ('questions', 'exercise'))}",
        f"- Source coverage status: {status_for_checks(findings, ('source coverage', 'notes source'))}",
        f"- Visual coverage status: {status_for_checks(findings, ('visual', 'notes visual', 'unresolved issues'))}",
        f"- Blocking issues: {severity_counts['blocking']}",
        f"- Recommended repair target: {recommended_repair_target(findings)}",
    ]
    lines.extend(f"- {severity.title()}: {severity_counts[severity]}" for severity in SEVERITIES)
    lines.extend(
        [
            "",
            "## Required Output Categories",
            "",
            table_row(["Category", "Folder exists", "Has non-empty file"]),
            table_row(["---", "---", "---"]),
        ]
    )

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
        lines.append("No validation issues found.")

    lines.append("")
    report.write_text("\n".join(lines), encoding="utf-8")
    return report


def write_source_coverage_report(
    root: Path,
    source_coverage_results: list[SourceCoverageResult],
) -> Path:
    report = root / SOURCE_COVERAGE_REPORT_PATH
    report.parent.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    issues = [
        result
        for result in source_coverage_results
        if result.status != "used" and result.status != "partially used"
    ]
    severity_counts = {
        severity: sum(1 for result in source_coverage_results if result.severity == severity)
        for severity in SEVERITIES
    }

    lines = [
        "# StudyOS Source Coverage",
        "",
        f"Generated: {generated_at}",
        f"Root: `{root}`",
        "",
        "## Summary",
        "",
        f"- Assigned-source coverage findings: {len(source_coverage_results)}",
        f"- Assigned-source issues needing review: {len(issues)}",
        *(
            f"- {severity.title()}: {severity_counts[severity]}"
            for severity in SEVERITIES
        ),
        "",
        "## Assigned Source Coverage",
        "",
    ]

    if source_coverage_results:
        lines.extend(
            [
                table_row(
                    [
                        "Severity",
                        "Batch",
                        "Role",
                        "Source",
                        "Digest",
                        "Status",
                        "Reason",
                        "Recommended repair",
                    ]
                ),
                table_row(["---", "---", "---", "---", "---", "---", "---", "---"]),
            ]
        )
        for result in source_coverage_results:
            lines.append(
                table_row(
                    [
                        result.severity,
                        result.batch,
                        result.role,
                        f"`{result.source}`",
                        f"`{result.digest}`",
                        result.status,
                        result.reason,
                        result.recommended_repair,
                    ]
                )
            )
    else:
        lines.append(
            "No assigned-source coverage findings. If batches exist, ensure `analysis/inventory/batch_plan.md` lists primary and supporting sources."
        )

    lines.append("")
    report.write_text("\n".join(lines), encoding="utf-8")
    return report


def write_report(
    root: Path,
    findings: list[Finding],
    files: list[Path],
    source_coverage_results: list[SourceCoverageResult],
) -> Path:
    report = root / REPORT_PATH
    write_markdown_report(root, REPORT_PATH, findings, files)
    write_markdown_report(root, DETAIL_REPORT_PATH, findings, files)
    write_source_coverage_report(root, source_coverage_results)
    return report


def main() -> int:
    args = parse_args()
    if args.self_check:
        run_self_check()
        print("validate_outputs.py self-check passed.")
        return 0

    root = args.root.expanduser().resolve()

    try:
        findings, files, source_coverage_results = validate(root)
        report = write_report(root, findings, files, source_coverage_results)
    except OSError as error:
        print(f"StudyOS output validation failed: {error}", file=sys.stderr)
        return 2

    print(f"Wrote output validation report: {report}")
    return 1 if any(finding.severity in {"high", "blocking"} for finding in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
