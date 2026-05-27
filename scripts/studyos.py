#!/usr/bin/env python3
"""Read-only StudyOS workspace status and readiness checks."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any


REQUIRED_FOLDERS = (
    "inputs",
    "inputs/slides",
    "inputs/readings",
    "inputs/notes",
    "inputs/exercises",
    "inputs/exams",
    "inputs/transcripts",
    "inputs/miscellaneous",
    "analysis",
    "analysis/inventory",
    "analysis/batches",
    "analysis/visual",
    "analysis/validation",
    "analysis/state",
    "outputs",
    "outputs/notes",
    "outputs/formulas",
    "outputs/flashcards",
    "outputs/questions",
    "outputs/cheat-sheets",
    "outputs/study-plan",
    "outputs/final-pack",
    "exports/pdf/unmerged",
    "exports/pdf/merged",
    "review",
    "study-os/config",
    "study-os/state",
    "study-os/scripts",
    "study-os/skills",
    ".agents/skills",
    ".claude/skills",
)

REQUIRED_SCRIPTS = (
    "study-os/scripts/studyos.py",
    "study-os/scripts/init_db.py",
    "study-os/scripts/inventory.py",
    "study-os/scripts/import_sources.py",
    "study-os/scripts/validate_outputs.py",
    "study-os/scripts/validate_citations.py",
    "study-os/scripts/validate_formulas.py",
    "study-os/scripts/export_final_pack.py",
)

REQUIRED_SKILLS = (
    "study-os/skills/studyos-import",
    "study-os/skills/studyos-plan",
    "study-os/skills/studyos-batch",
    "study-os/skills/studyos-validate",
    "study-os/skills/studyos-course",
    "study-os/skills/studyos-merge",
    "study-os/skills/studyos-export",
    ".agents/skills/studyos-import",
    ".agents/skills/studyos-plan",
    ".agents/skills/studyos-batch",
    ".agents/skills/studyos-validate",
    ".agents/skills/studyos-course",
    ".agents/skills/studyos-merge",
    ".agents/skills/studyos-export",
    ".claude/skills/studyos-import",
    ".claude/skills/studyos-plan",
    ".claude/skills/studyos-batch",
    ".claude/skills/studyos-validate",
    ".claude/skills/studyos-course",
    ".claude/skills/studyos-merge",
    ".claude/skills/studyos-export",
)

REQUIRED_CONFIG_FILES = (
    "STUDYOS_GUIDE.md",
    "workflow.yaml",
    "output-standards.yaml",
    "model-routing.yaml",
    "study-os/config/SKILLS_GUIDE.md",
)

INPUT_SUBFOLDERS = (
    "slides",
    "readings",
    "notes",
    "exercises",
    "exams",
    "transcripts",
    "miscellaneous",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Report StudyOS status without running the pipeline."
    )
    parser.add_argument(
        "command",
        choices=("status", "doctor"),
        help="Read-only command to run.",
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=None,
        help="StudyOS workspace folder. Defaults to the current working directory.",
    )
    return parser.parse_args()


def workspace_root(explicit_workspace: Path | None) -> Path:
    if explicit_workspace is not None:
        return explicit_workspace.expanduser().resolve()

    script_path = Path(__file__).resolve()
    if (
        script_path.parent.name == "scripts"
        and script_path.parent.parent.name == "study-os"
    ):
        return script_path.parents[2]

    return Path.cwd().resolve()


def strip_inline_comment(value: str) -> str:
    in_quote: str | None = None
    escaped = False
    result: list[str] = []

    for character in value:
        if escaped:
            result.append(character)
            escaped = False
            continue
        if character == "\\":
            result.append(character)
            escaped = True
            continue
        if character in ("'", '"'):
            if in_quote == character:
                in_quote = None
            elif in_quote is None:
                in_quote = character
            result.append(character)
            continue
        if character == "#" and in_quote is None:
            break
        result.append(character)

    return "".join(result).strip()


def parse_scalar(value: str) -> Any:
    value = strip_inline_comment(value)
    if value == "":
        return ""
    if value in ("true", "True"):
        return True
    if value in ("false", "False"):
        return False
    if (
        len(value) >= 2
        and value[0] == value[-1]
        and value[0] in ("'", '"')
    ):
        return value[1:-1]
    return value


def read_simple_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}

    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        lines = path.read_text(errors="replace").splitlines()

    for raw_line in lines:
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if raw_line.lstrip().startswith("- "):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        if ":" not in line:
            continue

        key, raw_value = line.split(":", 1)
        key = key.strip()
        if not key:
            continue

        while stack and indent <= stack[-1][0]:
            stack.pop()

        parent = stack[-1][1]
        value = parse_scalar(raw_value.strip())
        if raw_value.strip() == "":
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = value

    return root


def nested_get(data: dict[str, Any], *keys: str) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def yes_no(value: bool) -> str:
    return "yes" if value else "no"


def count_files(directory: Path) -> int:
    if not directory.is_dir():
        return 0
    return sum(1 for path in directory.rglob("*") if path.is_file())


def has_files(directory: Path) -> bool:
    return count_files(directory) > 0


def path_is_readable(path: Path) -> bool:
    return path.exists() and os.access(path, os.R_OK)


def configured_path(raw_path: Any, root: Path) -> Path | None:
    if not isinstance(raw_path, str) or raw_path.strip() == "":
        return None
    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return path
    return root / path


def subject_config(root: Path) -> dict[str, Any]:
    return read_simple_yaml(root / "subject.yaml")


def studyos_installed(root: Path) -> bool:
    return (
        (root / "study-os").is_dir()
        and (root / "study-os/scripts/studyos.py").is_file()
    )


def next_recommended_skill(root: Path, config: dict[str, Any]) -> str:
    raw_path = configured_path(nested_get(config, "raw_source", "path"), root)
    inputs_count = sum(
        count_files(root / "inputs" / folder) for folder in INPUT_SUBFOLDERS
    )

    if not studyos_installed(root):
        return "install StudyOS"
    if not (root / "subject.yaml").is_file() or not nested_get(
        config, "setup", "completed"
    ):
        return "complete StudyOS setup"
    if raw_path is not None and not path_is_readable(raw_path):
        return "fix subject.yaml raw_source.path"
    if raw_path is not None and not (
        root / "analysis/inventory/import_plan.md"
    ).is_file():
        return "studyos-import proposal"
    if (root / "analysis/inventory/import_plan.md").is_file() and not (
        root / "analysis/inventory/import_log.md"
    ).is_file() and inputs_count == 0:
        return "studyos-import execute"
    if inputs_count == 0:
        return "studyos-import"
    if not (root / "analysis/inventory/course_inventory.md").is_file() or not (
        root / "analysis/inventory/batch_plan.md"
    ).is_file():
        return "studyos-import"
    if (
        count_files(root / "analysis/batches") == 0
    ):
        return "studyos-plan, then studyos-batch"
    if not (root / "review/validation-report.md").is_file():
        return "studyos-validate"
    if not has_files(root / "outputs/final-pack"):
        return "studyos-course, then studyos-merge"
    return "review outputs"


def print_row(label: str, value: object) -> None:
    print(f"{label}: {value}")


def run_status(root: Path) -> int:
    config = subject_config(root)
    raw_path = configured_path(nested_get(config, "raw_source", "path"), root)
    inputs_count = sum(
        count_files(root / "inputs" / folder) for folder in INPUT_SUBFOLDERS
    )
    subject_name = nested_get(config, "subject", "name")

    print("StudyOS Status")
    print_row("workspace", root)
    print_row("StudyOS installed", yes_no(studyos_installed(root)))
    print_row(
        "setup completed", yes_no(nested_get(config, "setup", "completed") is True)
    )
    print_row("subject name", subject_name if subject_name else "(not set)")
    print_row("raw_source.path configured", yes_no(raw_path is not None))
    print_row(
        "raw_source.path readable",
        yes_no(raw_path is not None and path_is_readable(raw_path)),
    )
    print_row(
        "import_plan.md exists",
        yes_no((root / "analysis/inventory/import_plan.md").is_file()),
    )
    print_row(
        "import_log.md exists",
        yes_no((root / "analysis/inventory/import_log.md").is_file()),
    )
    print_row("files in inputs/", inputs_count)
    print_row(
        "course_inventory.md exists",
        yes_no((root / "analysis/inventory/course_inventory.md").is_file()),
    )
    print_row(
        "batch_plan.md exists",
        yes_no((root / "analysis/inventory/batch_plan.md").is_file()),
    )
    print_row("batch analysis files count", count_files(root / "analysis/batches"))
    print_row("output files count", count_files(root / "outputs"))
    print_row(
        "validation report exists",
        yes_no((root / "review/validation-report.md").is_file()),
    )
    print_row(
        "final review pack exists",
        yes_no(has_files(root / "outputs/final-pack")),
    )
    print_row("next recommended skill", next_recommended_skill(root, config))
    return 0


def check_paths(root: Path, paths: tuple[str, ...], kind: str) -> list[str]:
    issues: list[str] = []
    for relative_path in paths:
        path = root / relative_path
        if kind == "folder" and not path.is_dir():
            issues.append(f"missing folder: {relative_path}")
        elif kind == "file" and not path.is_file():
            issues.append(f"missing file: {relative_path}")
        elif kind == "skill" and not (path / "SKILL.md").is_file():
            issues.append(f"missing skill: {relative_path}")
    return issues


def stale_setup_issues(root: Path, config: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    setup_completed = nested_get(config, "setup", "completed") is True
    subject_name = nested_get(config, "subject", "name")
    raw_path = configured_path(nested_get(config, "raw_source", "path"), root)

    if setup_completed and not subject_name:
        issues.append("setup.completed is true but subject.name is empty")
    if setup_completed and raw_path is None:
        issues.append("setup.completed is true but raw_source.path is empty")
    if (root / "analysis/inventory/import_log.md").is_file() and not (
        root / "analysis/inventory/import_plan.md"
    ).is_file():
        issues.append("import_log.md exists without import_plan.md")
    if (root / "analysis/inventory/batch_plan.md").is_file() and not (
        root / "analysis/inventory/course_inventory.md"
    ).is_file():
        issues.append("batch_plan.md exists without course_inventory.md")
    if (
        count_files(root / "outputs") > 0
        and count_files(root / "analysis/batches") == 0
    ):
        issues.append("outputs exist but no batch analysis files were found")

    return issues


def run_doctor(root: Path) -> int:
    config = subject_config(root)
    raw_path = configured_path(nested_get(config, "raw_source", "path"), root)
    issues: list[str] = []

    issues.extend(check_paths(root, REQUIRED_FOLDERS, "folder"))
    issues.extend(check_paths(root, REQUIRED_SCRIPTS, "file"))
    issues.extend(check_paths(root, REQUIRED_SKILLS, "skill"))
    issues.extend(check_paths(root, REQUIRED_CONFIG_FILES, "file"))

    if not (root / "subject.yaml").is_file():
        issues.append("missing file: subject.yaml")
    if raw_path is not None and not path_is_readable(raw_path):
        issues.append(f"raw_source.path is not readable: {raw_path}")
    if (root / "study-os/scripts/install_studyos.py").exists():
        issues.append(
            "install_studyos.py should not be present inside study-os/scripts/"
        )

    issues.extend(stale_setup_issues(root, config))

    print("StudyOS Doctor")
    print_row("workspace", root)
    if issues:
        print("readiness: issues found")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("readiness: ok")
    print("No readiness issues found.")
    return 0


def main() -> int:
    args = parse_args()
    root = workspace_root(args.workspace)

    if args.command == "status":
        return run_status(root)
    if args.command == "doctor":
        return run_doctor(root)

    print(f"Unknown command: {args.command}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
