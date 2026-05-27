#!/usr/bin/env python3
"""Validate StudyOS output folders and generated files for an installed subject."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


REPORT_PATH = Path("review/validation-report.md")
DETAIL_REPORT_PATH = Path("analysis/validation/output-structure.md")
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
    "flashcards",
    "questions",
    "cheat-sheets",
    "study-plan",
    "final-pack",
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


def has_section(text: str, section: str) -> bool:
    return section.lower() in text.lower()


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


def flashcards_are_active_recall(text: str) -> bool:
    lowered = text.lower()
    if "source references" not in lowered:
        return False
    active_markers = (
        "front:",
        "back:",
        "q:",
        "a:",
        "question:",
        "answer:",
        "?",
    )
    passive_markers = (
        "summary:",
        "note:",
        "definition:",
    )
    return any(marker in lowered for marker in active_markers) and not (
        lowered.count("card") > 0
        and sum(lowered.count(marker) for marker in passive_markers)
        > sum(lowered.count(marker) for marker in active_markers)
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


def validate(root: Path) -> tuple[list[Finding], list[Path]]:
    findings: list[Finding] = []

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

    digest_files = [
        path
        for path in text_output_files(root, "analysis/batches")
        if path.name.endswith("_digest.md")
    ]
    for path in digest_files:
        text = read_text(path)
        rel = relative(path, root)
        for section in REQUIRED_DIGEST_SECTIONS:
            if not has_section(text, section):
                append_finding(
                    findings,
                    "high",
                    "batch digest section",
                    rel,
                    f"Required digest section is missing: {section}.",
                )
        if digest_mentions_visual_source(text) and not has_section(
            text, VISUAL_DIGEST_SECTION
        ):
            append_finding(
                findings,
                "high",
                "visual coverage",
                rel,
                "Digest references slide/PDF/image sources but is missing Visual Coverage.",
            )
        elif has_section(text, VISUAL_DIGEST_SECTION) and not visual_coverage_is_resolved(
            text
        ):
            append_finding(
                findings,
                "medium",
                "visual coverage",
                rel,
                "Visual Coverage does not clearly say essential visuals were analyzed or unresolved.",
            )

    if digest_files and not (root / "review" / "source-coverage.md").is_file():
        append_finding(
            findings,
            "high",
            "source coverage report",
            "review/source-coverage.md",
            "Source Coverage report is missing.",
        )

    for path in text_output_files(root, "outputs/flashcards"):
        if path.stat().st_size > 0 and not flashcards_are_active_recall(read_text(path)):
            append_finding(
                findings,
                "medium",
                "flashcards",
                relative(path, root),
                "Flashcards do not clearly use active-recall question/answer prompts.",
            )

    for path in text_output_files(root, "outputs/questions"):
        if path.stat().st_size > 0:
            text = read_text(path)
            if not questions_have_answers(text):
                append_finding(
                    findings,
                    "high",
                    "exam questions",
                    relative(path, root),
                    "Exam questions do not clearly include expected answers, an answer key, or worked solutions.",
                )
            if not exercises_are_practice(text):
                append_finding(
                    findings,
                    "medium",
                    "exercise integration",
                    relative(path, root),
                    "Exercises appear without clear practice framing or solutions.",
                )

    return findings, files


def table_row(values: list[str]) -> str:
    escaped = [value.replace("|", "\\|").replace("\n", " ") for value in values]
    return "| " + " | ".join(escaped) + " |"


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


def write_report(root: Path, findings: list[Finding], files: list[Path]) -> Path:
    report = root / REPORT_PATH
    write_markdown_report(root, REPORT_PATH, findings, files)
    write_markdown_report(root, DETAIL_REPORT_PATH, findings, files)
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
    return 1 if any(finding.severity in {"high", "blocking"} for finding in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
