#!/usr/bin/env python3
"""Core StudyOS smoke test for install, sync, import, inventory, validation, export."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        validation_report = cwd / "review/validation-report.md"
        report_text = ""
        if validation_report.is_file():
            report_text = (
                "\n  validation report:\n"
                + validation_report.read_text(encoding="utf-8", errors="replace")
            )
        raise AssertionError(
            "Command failed:\n"
            f"  cwd: {cwd}\n"
            f"  cmd: {' '.join(command)}\n"
            f"  stdout:\n{completed.stdout}\n"
            f"  stderr:\n{completed.stderr}"
            f"{report_text}"
        )
    return completed


def write_subject_config(course: Path, raw: Path) -> None:
    (course / "subject.yaml").write_text(
        "\n".join(
            (
                "subject:",
                '  name: "Smoke Course"',
                '  level: "Bachelor"',
                '  language: "English"',
                "  exam_type:",
                "    written: true",
                "    oral: false",
                "    project: false",
                "    mixed: false",
                "    unknown: false",
                "raw_source:",
                f'  path: "{raw}" # inline comments must be ignored',
                '  mode: "read_only"',
                '  copy_strategy: "copy_into_inputs"',
                "setup:",
                "  completed: true",
                '  completed_at: "2026-05-28T00:00:00+00:00"',
                "processing:",
                '  quality_mode: "standard"',
                "outputs:",
                "  notes: true",
                "  formulas: true",
                "  exam_practice_questions: true",
                "",
            )
        ),
        encoding="utf-8",
    )


def create_raw_sources(raw: Path) -> None:
    raw.mkdir(parents=True)
    (raw / "Lecture_01_Introduction.pdf").write_text(
        "Smoke lecture source with definitions and concepts.",
        encoding="utf-8",
    )
    (raw / "Exercise_01_Practice.txt").write_text(
        "Smoke exercise source with exam-style practice.",
        encoding="utf-8",
    )
    (raw / "misc_reference.md").write_text(
        "Low-confidence reference that should need review.",
        encoding="utf-8",
    )


def assert_contains(path: Path, text: str) -> None:
    content = path.read_text(encoding="utf-8")
    if text not in content:
        raise AssertionError(f"Expected `{path}` to contain `{text}`.")


def assert_not_contains(path: Path, text: str) -> None:
    content = path.read_text(encoding="utf-8")
    if text in content:
        raise AssertionError(f"Expected `{path}` not to contain `{text}`.")


def repeated_sentence(sentence: str, count: int) -> str:
    return " ".join(sentence for _ in range(count))


def write_representative_outputs(course: Path) -> None:
    batch = "Batch_01_Introduction"
    lecture = "inputs/slides/Lecture_01_Introduction.pdf"
    exercise = "inputs/exercises/Exercise_01_Practice.txt"

    digest_text = "\n".join(
        (
            f"# {batch} Digest",
            "",
            "## Batch Processing Plan",
            "",
            "Process the introduction batch from the lecture and exercise source.",
            "",
            "## Source Coverage",
            "",
            "| Source | Role | Status | Reason |",
            "| --- | --- | --- | --- |",
            f"| `{lecture}` | primary | used | Main conceptual source. |",
            f"| `{exercise}` | supporting | used | Practice and exam signal source. |",
            "",
            "## Visual Coverage",
            "",
            "No essential visuals were present in the smoke fixture sources.",
            "",
            "## Core extracted content",
            "",
            repeated_sentence(
                "The smoke course introduces a grounded concept, a definition, "
                "a study example, and an exam signal from the assigned inputs.",
                20,
            ),
            "",
            "## Definitions",
            "",
            "Smoke concept: a placeholder concept grounded in the lecture source.",
            "",
            "## Formulas",
            "",
            "No standalone formulas are relevant for this smoke batch.",
            "",
            "## Important tables/charts/diagrams",
            "",
            "No essential tables, charts, or diagrams are present.",
            "",
            "## Examples",
            "",
            "The exercise source provides a practice example for the smoke concept.",
            "",
            "## Exercise and Exam Signals",
            "",
            "The exercise source signals that expected answers should explain the concept.",
            "",
            "## Weak points",
            "",
            "Students may confuse a definition check with an application question.",
            "",
            "## Unresolved questions",
            "",
            "None.",
            "",
            "## Source references",
            "",
            f"- `{lecture}`",
            f"- `{exercise}`",
            "",
        )
    )

    learning_core_text = "\n".join(
        (
            f"# {batch} Learning Core",
            "",
            "## Learning Objectives",
            "",
            "- Define the smoke concept.",
            "- Explain how the practice source tests the concept.",
            "",
            "## Core Concepts",
            "",
            repeated_sentence(
                "The core concept is preserved with enough detail for complete "
                "study notes and is grounded in both assigned sources.",
                25,
            ),
            "",
            "## Explanations",
            "",
            repeated_sentence(
                "The explanation connects the definition, the example, the common "
                "mistake, and the expected answer pattern.",
                20,
            ),
            "",
            "## Connections Between Topics",
            "",
            "This opening batch has no prerequisite dependency.",
            "",
            "## Worked Examples",
            "",
            "A worked answer should identify the concept and explain why it applies.",
            "",
            "## Formula Intuition",
            "",
            "No standalone formulas are relevant.",
            "",
            "## Common Mistakes",
            "",
            "A common mistake is answering with a label but no explanation.",
            "",
            "## Exam-Relevant Points",
            "",
            "Expected answers should define the concept and apply it to the prompt.",
            "",
            "## Weak Points",
            "",
            "Definition-only answers are weak.",
            "",
            "## Unresolved Questions",
            "",
            "None.",
            "",
            "## Source References",
            "",
            f"- `{lecture}`",
            f"- `{exercise}`",
            "",
        )
    )

    notes_text = "\n".join(
        (
            f"# {batch}",
            "",
            "## Scope",
            "",
            repeated_sentence(
                "This smoke output covers both assigned sources for the introduction "
                "batch and states exactly how the lecture and practice material are "
                "used for study.",
                4,
            ),
            "",
            "## Core Notes",
            "",
            repeated_sentence(
                "The smoke concept is explained as a source-grounded definition "
                "with a practical application and an exam-facing answer pattern.",
                90,
            ),
            "",
            "## Definitions",
            "",
            repeated_sentence(
                "Smoke concept: a source-grounded introductory concept that must be "
                "defined, explained, connected to the assigned exercise, and used in "
                "an answer with supporting reasoning.",
                4,
            ),
            "",
            "## Examples",
            "",
            repeated_sentence(
                "The practice source asks the student to apply the concept in a short "
                "answer, identify the relevant definition, and explain why the answer "
                "follows from the assigned material.",
                4,
            ),
            "",
            "## Formula Intuition",
            "",
            repeated_sentence(
                "No standalone formulas are relevant; the quantitative layer is not "
                "present, so the student should focus on conceptual precision, source "
                "grounding, and answer structure.",
                4,
            ),
            "",
            "## Exam Relevance",
            "",
            repeated_sentence(
                "A likely exam question asks for a definition plus a short application, "
                "so a strong answer should include the concept, the reason, and the "
                "exercise-style application pattern.",
                4,
            ),
            "",
            "## Common Mistakes",
            "",
            repeated_sentence(
                "Do not answer only with a label; include the reason, the source-grounded "
                "detail, and the connection between the lecture definition and the "
                "practice prompt.",
                4,
            ),
            "",
            "## Weak Points",
            "",
            repeated_sentence(
                "Definition-only answers need repair because they do not demonstrate "
                "application, source grounding, or the expected explanation pattern "
                "from the exercise source.",
                4,
            ),
            "",
            "## Source References",
            "",
            f"- `{lecture}`",
            f"- `{exercise}`",
            "",
        )
    )

    questions_text = "\n".join(
        (
            f"# {batch} Questions",
            "",
            "## Exam Scope",
            "",
            "Questions cover the introduction batch and both assigned sources.",
            "",
            "## Questions by Topic",
            "",
            "### Topic: Smoke Concept",
            "",
            "1. Conceptual question: Define the smoke concept.",
            "2. Exam-style open question: Apply the smoke concept to a short prompt.",
            "3. Common-trap question: Why is a label-only answer incomplete?",
            "",
            "## Expected Answers",
            "",
            "Answer: A complete answer defines the concept, applies it, and explains the reason.",
            "Expected answer: The exercise-derived prompt requires concept plus justification.",
            "",
            "## Common Traps",
            "",
            "The main trap is omitting the explanation.",
            "",
            "## Source References",
            "",
            f"- `{lecture}`",
            f"- `{exercise}`",
            "",
        )
    )

    (course / "analysis/batches").mkdir(parents=True, exist_ok=True)
    (course / "outputs/notes").mkdir(parents=True, exist_ok=True)
    (course / "outputs/questions").mkdir(parents=True, exist_ok=True)
    (course / f"analysis/batches/{batch}_digest.md").write_text(
        digest_text,
        encoding="utf-8",
    )
    (course / f"analysis/batches/{batch}_learning_core.md").write_text(
        learning_core_text,
        encoding="utf-8",
    )
    (course / f"outputs/notes/{batch}.md").write_text(notes_text, encoding="utf-8")
    (course / f"outputs/questions/{batch}_questions.md").write_text(
        questions_text,
        encoding="utf-8",
    )


def main() -> int:
    root = repo_root()
    temp_dir = Path(tempfile.mkdtemp(prefix="studyos-core-smoke-"))
    try:
        course = temp_dir / "Course"
        raw = temp_dir / "Raw"
        create_raw_sources(raw)

        run(["python3", "scripts/install_studyos.py", str(course)], root)
        run(["python3", "scripts/sync_studyos.py", str(course)], root)
        run(["python3", "study-os/scripts/studyos.py", "doctor"], course)

        status = run(["python3", "study-os/scripts/studyos.py", "status"], course)
        if "validation report exists: no" not in status.stdout:
            raise AssertionError(
                "Empty placeholder validation report was treated as real."
            )

        write_subject_config(course, raw)
        proposal = run(
            ["python3", "study-os/scripts/import_sources.py", "--mode", "proposal"],
            course,
        )
        if "Proposed copies: 2" not in proposal.stdout:
            raise AssertionError(
                "Import proposal did not classify the expected copy rows."
            )

        run(
            ["python3", "study-os/scripts/import_sources.py", "--mode", "execute"],
            course,
        )
        run(["python3", "study-os/scripts/inventory.py"], course)

        batch_plan = course / "analysis/inventory/batch_plan.md"
        assert_contains(batch_plan, "Depends on:")
        assert_contains(batch_plan, "- source digest")
        assert_contains(batch_plan, "- learning core")
        assert_contains(batch_plan, "- batch notes")
        assert_contains(batch_plan, "- batch exam practice questions")
        assert_not_contains(batch_plan, "- master notes")

        final_status = run(["python3", "study-os/scripts/studyos.py", "status"], course)
        expected_next = "next recommended skill: studyos-plan, then studyos-batch"
        if expected_next not in final_status.stdout:
            raise AssertionError(
                "Status did not recommend the expected post-inventory step."
            )

        write_representative_outputs(course)
        run(["python3", "study-os/scripts/validate_outputs.py"], course)
        run(["python3", "study-os/scripts/validate_citations.py"], course)
        run(["python3", "study-os/scripts/validate_formulas.py"], course)
        run(
            [
                "python3",
                "study-os/scripts/export_outputs.py",
                "--format",
                "markdown",
            ],
            course,
        )
        assert_contains(course / "review/validation-report.md", "Status: **pass**")
        assert_contains(
            course / "study-os/state/export-log.md",
            "Exported Files",
        )

        print(f"StudyOS smoke test passed: {course}")
        return 0
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
