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
    escaped = re.escape(section)
    return (
        re.search(rf"(?im)^\s*#{1,6}\s+{escaped}\s*$", text) is not None
        or re.search(rf"(?im)^\s*(?:[-*]\s*)?\*\*{escaped}\*\*\s*:?\s*$", text)
        is not None
        or section.lower() in text.lower()
    )


def section_body(text: str, section: str) -> str:
    pattern = re.compile(
        rf"(?ims)^\s*#{1,6}\s+{re.escape(section)}\s*$\n(?P<body>.*?)(?=^\s*#{1,6}\s+\S|\Z)"
    )
    match = pattern.search(text)
    return match.group("body").strip() if match else ""


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


def validate(root: Path) -> tuple[list[Finding], list[Path]]:
    findings: list[Finding] = []
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

    digest_files = [context.digest for context in contexts.values() if context.digest]
    if digest_files and not (root / "review" / "source-coverage.md").is_file():
        append_finding(
            findings,
            "high",
            "source coverage report",
            "review/source-coverage.md",
            "Source Coverage report is missing.",
        )

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

    return findings, files


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
