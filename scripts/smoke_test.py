#!/usr/bin/env python3
"""Core StudyOS smoke test for install, sync, import, and inventory."""

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
        raise AssertionError(
            "Command failed:\n"
            f"  cwd: {cwd}\n"
            f"  cmd: {' '.join(command)}\n"
            f"  stdout:\n{completed.stdout}\n"
            f"  stderr:\n{completed.stderr}"
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

        print(f"StudyOS smoke test passed: {course}")
        return 0
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
