#!/usr/bin/env python3
"""Install StudyOS into a subject folder."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


CORE_REPO_HINT = "~/Developer/studyos-core"

COURSE_LOCAL_SCRIPTS = (
    "init_db.py",
    "inventory.py",
    "import_sources.py",
    "validate_outputs.py",
    "validate_citations.py",
    "validate_formulas.py",
    "export_final_pack.py",
)

SUBJECT_DIRECTORIES = (
    "inputs/slides",
    "inputs/readings",
    "inputs/notes",
    "inputs/exercises",
    "inputs/exams",
    "inputs/transcripts",
    "inputs/miscellaneous",
    "working/inventory",
    "working/digests",
    "working/learning-cores",
    "working/visual-notes",
    "working/validation",
    "outputs/master-notes",
    "outputs/formula-sheets",
    "outputs/flashcards",
    "outputs/exam-questions",
    "outputs/cheat-sheets",
    "outputs/study-plan",
    "outputs/final-review-pack",
    "outputs/assets",
    "review",
    "study-os/config",
    "study-os/state",
    "study-os/scripts",
    "study-os/skills",
    ".agents/skills",
    ".claude/skills",
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


def copy_templates(source_root: Path, target: Path) -> tuple[int, int]:
    return copy_tree_without_overwrite(source_root / "templates", target)


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
        for skill_source in sorted(
            path for path in skills_source.iterdir() if path.is_dir()
        ):
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


def main() -> int:
    args = parse_args()
    target = args.target.expanduser().resolve()
    source_root = repo_root()

    try:
        validate_sources(source_root)
        created_dirs = ensure_directories(target)
        copied_templates, skipped_templates = copy_templates(source_root, target)
        copied_scripts, skipped_scripts = copy_scripts(source_root, target)
        copied_skills, skipped_skills = copy_skills(source_root, target)
    except OSError as error:
        print(f"StudyOS installation failed: {error}", file=sys.stderr)
        return 1

    copied_files = copied_templates + copied_scripts + copied_skills
    skipped_files = skipped_templates + skipped_scripts + skipped_skills

    print(f"StudyOS installed at: {target}")
    print(f"Directories created: {created_dirs}")
    print(f"Files copied: {copied_files}")
    print(f"Existing files preserved: {skipped_files}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
