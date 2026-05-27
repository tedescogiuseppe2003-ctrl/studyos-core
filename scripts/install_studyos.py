#!/usr/bin/env python3
"""Install StudyOS into a subject folder."""

from __future__ import annotations

import argparse
import shutil
import sqlite3
import sys
from pathlib import Path

from init_db import init_db


CORE_REPO_HINT = "~/Developer/studyos-core"

COURSE_LOCAL_SCRIPTS = (
    "studyos.py",
    "init_db.py",
    "inventory.py",
    "import_sources.py",
    "validate_outputs.py",
    "validate_citations.py",
    "validate_formulas.py",
    "export_final_pack.py",
)

INSTALLED_SKILL_NAMES = (
    "studyos-import",
    "studyos-plan",
    "studyos-batch",
    "studyos-validate",
    "studyos-course",
    "studyos-merge",
    "studyos-export",
)

DEPRECATED_RELATIVE_PATHS = (
    "study-os/scripts/install_studyos.py",
    "study-os/skills/study-os-install",
    "study-os/skills/study-os-import-sources",
    "study-os/skills/study-os-inventory",
    "study-os/skills/study-os-process-batch",
    "study-os/skills/study-os-process-course",
    "study-os/skills/study-os-validate",
    "study-os/skills/study-os-synthesize",
    "study-os/skills/studyos-synthesize",
    ".agents/skills/study-os-install",
    ".agents/skills/study-os-import-sources",
    ".agents/skills/study-os-inventory",
    ".agents/skills/study-os-process-batch",
    ".agents/skills/study-os-process-course",
    ".agents/skills/study-os-validate",
    ".agents/skills/study-os-synthesize",
    ".agents/skills/studyos-synthesize",
    ".claude/skills/study-os-install",
    ".claude/skills/study-os-import-sources",
    ".claude/skills/study-os-inventory",
    ".claude/skills/study-os-process-batch",
    ".claude/skills/study-os-process-course",
    ".claude/skills/study-os-validate",
    ".claude/skills/study-os-synthesize",
    ".claude/skills/studyos-synthesize",
)

TEMPLATE_DESTINATIONS = {
    "SKILLS_GUIDE.md": Path("study-os/config/SKILLS_GUIDE.md"),
    "STUDYOS_GUIDE.md": Path("STUDYOS_GUIDE.md"),
}

SUBJECT_DIRECTORIES = (
    "inputs/slides",
    "inputs/readings",
    "inputs/notes",
    "inputs/exercises",
    "inputs/exams",
    "inputs/transcripts",
    "inputs/miscellaneous",
    "analysis/inventory",
    "analysis/batches",
    "analysis/visual",
    "analysis/validation",
    "analysis/state",
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

REVIEW_FILES = (
    "review/weak-points.md",
    "review/unresolved-questions.md",
    "review/visual-issues.md",
    "review/source-coverage.md",
    "review/validation-report.md",
    "review/progress-tracker.md",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install StudyOS into a target subject folder."
    )
    parser.add_argument(
        "target",
        type=Path,
        help="Subject folder to create or update, for example ~/StudyOS-Test/TestCourse",
    )
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def ensure_directories(target: Path) -> int:
    created = 0
    target.mkdir(parents=True, exist_ok=True)

    for relative_path in SUBJECT_DIRECTORIES:
        directory = target / relative_path
        if not directory.exists():
            created += 1
        directory.mkdir(parents=True, exist_ok=True)

    return created


def ensure_review_files(target: Path) -> int:
    created = 0

    for relative_path in REVIEW_FILES:
        path = target / relative_path
        if path.exists() or path.is_symlink():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
        created += 1

    return created


def copy_file_without_overwrite(source: Path, destination: Path) -> bool:
    if destination.exists() or destination.is_symlink():
        return False

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return True


def copy_tree_without_overwrite(source: Path, destination: Path) -> tuple[int, int]:
    copied = 0
    skipped = 0

    for source_path in sorted(source.rglob("*")):
        if "__pycache__" in source_path.parts or source_path.suffix == ".pyc":
            continue

        relative_path = source_path.relative_to(source)
        destination_path = destination / relative_path

        if source_path.is_dir():
            destination_path.mkdir(parents=True, exist_ok=True)
            continue

        if copy_file_without_overwrite(source_path, destination_path):
            copied += 1
        else:
            skipped += 1

    return copied, skipped


def count_copyable_files(source: Path) -> int:
    return sum(
        1
        for source_path in source.rglob("*")
        if source_path.is_file()
        and "__pycache__" not in source_path.parts
        and source_path.suffix != ".pyc"
    )


def copy_skill_without_overwrite(source: Path, destination: Path) -> tuple[int, int]:
    if destination.exists() or destination.is_symlink():
        return 0, count_copyable_files(source)

    return copy_tree_without_overwrite(source, destination)


def remove_deprecated_paths(target: Path) -> tuple[str, ...]:
    removed: list[str] = []

    for relative_path in DEPRECATED_RELATIVE_PATHS:
        path = target / relative_path
        if not path.exists() and not path.is_symlink():
            continue

        if path.is_dir() and not path.is_symlink():
            shutil.rmtree(path)
        else:
            path.unlink()
        removed.append(relative_path)

    for relative_destination in (
        "study-os/skills",
        ".agents/skills",
        ".claude/skills",
    ):
        destination = target / relative_destination
        if not destination.is_dir():
            continue
        for path in sorted(destination.iterdir()):
            if not path.name.startswith("study-os-"):
                continue
            if path.is_dir() and not path.is_symlink():
                shutil.rmtree(path)
            else:
                path.unlink()
            removed.append(f"{relative_destination}/{path.name}")

    return tuple(removed)


def copy_templates(source_root: Path, target: Path) -> tuple[int, int]:
    copied = 0
    skipped = 0
    templates_source = source_root / "templates"

    for template_source in sorted(templates_source.iterdir()):
        relative_destination = TEMPLATE_DESTINATIONS.get(
            template_source.name, Path(template_source.name)
        )
        destination = target / relative_destination

        if template_source.is_dir():
            copied_count, skipped_count = copy_tree_without_overwrite(
                template_source, destination
            )
            copied += copied_count
            skipped += skipped_count
            continue

        if copy_file_without_overwrite(template_source, destination):
            copied += 1
        else:
            skipped += 1

    return copied, skipped


def copy_scripts(source_root: Path, target: Path) -> tuple[int, int]:
    copied = 0
    skipped = 0
    scripts_source = source_root / "scripts"
    scripts_destination = target / "study-os/scripts"

    for script_name in COURSE_LOCAL_SCRIPTS:
        if copy_file_without_overwrite(
            scripts_source / script_name, scripts_destination / script_name
        ):
            copied += 1
        else:
            skipped += 1

    return copied, skipped


def copy_skills(source_root: Path, target: Path) -> tuple[int, int]:
    copied = 0
    skipped = 0
    skills_source = source_root / "skills"
    skill_destinations = (
        target / "study-os/skills",
        target / ".agents/skills",
        target / ".claude/skills",
    )

    for destination in skill_destinations:
        for skill_name in INSTALLED_SKILL_NAMES:
            skill_source = skills_source / skill_name
            skill_destination = destination / skill_source.name
            copied_count, skipped_count = copy_skill_without_overwrite(
                skill_source, skill_destination
            )
            copied += copied_count
            skipped += skipped_count

    return copied, skipped


def validate_sources(source_root: Path) -> None:
    required_sources = (
        source_root / "templates",
        source_root / "scripts",
        source_root / "skills",
    )

    missing_sources = [path for path in required_sources if not path.is_dir()]
    if missing_sources:
        missing = ", ".join(str(path) for path in missing_sources)
        raise FileNotFoundError(
            "Missing required StudyOS core directories: "
            f"{missing}. Run this installer from the core repo, for example: "
            f"cd {CORE_REPO_HINT} && python3 scripts/install_studyos.py <target-subject-folder>."
        )

    missing_scripts = [
        source_root / "scripts" / script_name
        for script_name in COURSE_LOCAL_SCRIPTS
        if not (source_root / "scripts" / script_name).is_file()
    ]
    if missing_scripts:
        missing = ", ".join(str(path) for path in missing_scripts)
        raise FileNotFoundError(f"Missing required StudyOS scripts: {missing}")

    missing_skills = [
        source_root / "skills" / skill_name / "SKILL.md"
        for skill_name in INSTALLED_SKILL_NAMES
        if not (source_root / "skills" / skill_name / "SKILL.md").is_file()
    ]
    if missing_skills:
        missing = ", ".join(str(path) for path in missing_skills)
        raise FileNotFoundError(f"Missing required StudyOS skills: {missing}")

    required_templates = (
        source_root / "templates/STUDYOS_GUIDE.md",
        source_root / "templates/SKILLS_GUIDE.md",
        source_root / "templates/subject.yaml",
    )
    missing_templates = [path for path in required_templates if not path.is_file()]
    if missing_templates:
        missing = ", ".join(str(path) for path in missing_templates)
        raise FileNotFoundError(f"Missing required StudyOS templates: {missing}")


def initialize_database(target: Path) -> Path:
    return init_db(target / "study-os/state/studyos.sqlite")


def main() -> int:
    args = parse_args()
    target = args.target.expanduser().resolve()
    source_root = repo_root()

    try:
        validate_sources(source_root)
        created_dirs = ensure_directories(target)
        removed_deprecated_paths = remove_deprecated_paths(target)
        created_review_files = ensure_review_files(target)
        copied_templates, skipped_templates = copy_templates(source_root, target)
        copied_scripts, skipped_scripts = copy_scripts(source_root, target)
        copied_skills, skipped_skills = copy_skills(source_root, target)
        db_path = initialize_database(target)
    except OSError as error:
        print(f"StudyOS installation failed: {error}", file=sys.stderr)
        return 1
    except sqlite3.Error as error:
        print(f"StudyOS database initialization failed: {error}", file=sys.stderr)
        return 1

    copied_files = copied_templates + copied_scripts + copied_skills
    skipped_files = skipped_templates + skipped_scripts + skipped_skills

    print(f"StudyOS installed at: {target}")
    print(f"Directories created: {created_dirs}")
    print(f"Review files created: {created_review_files}")
    print(f"Files copied: {copied_files}")
    print(f"Existing files preserved: {skipped_files}")
    print(f"Deprecated paths removed: {len(removed_deprecated_paths)}")
    print(f"Database initialized: {db_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
