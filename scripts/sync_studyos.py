#!/usr/bin/env python3
"""Sync StudyOS core files into an existing subject folder."""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path


CORE_REPO_HINT = "~/Developer/studyos-core"

SKILL_DESTINATIONS = (
    "study-os/skills",
    ".agents/skills",
    ".claude/skills",
)

INTENTIONALLY_NOT_TOUCHED = (
    "inputs/",
    "outputs/",
    "working/",
    "review/",
    "subject.yaml",
    ".git/",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync StudyOS scripts and skills into a target subject folder."
    )
    parser.add_argument(
        "target",
        type=Path,
        help="Existing subject folder to update, for example ~/StudyOS-Test/TestCourse",
    )
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


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
            f"{missing}. Run sync from the core repo, for example: "
            f"cd {CORE_REPO_HINT} && python3 scripts/sync_studyos.py <target-subject-folder>."
        )

    if not list((source_root / "scripts").glob("*.py")):
        raise FileNotFoundError(f"No Python scripts found in {source_root / 'scripts'}")


def validate_target(target: Path) -> None:
    if not target.exists():
        raise FileNotFoundError(f"Target subject folder does not exist: {target}")
    if not target.is_dir():
        raise NotADirectoryError(f"Target is not a directory: {target}")


def copy_file_replace(source: Path, destination: Path) -> bool:
    destination.parent.mkdir(parents=True, exist_ok=True)
    existed = destination.exists() or destination.is_symlink()
    if destination.is_symlink():
        destination.unlink()
    elif destination.is_dir():
        shutil.rmtree(destination)
    shutil.copy2(source, destination)
    return existed


def copy_tree_replace(source: Path, destination: Path) -> int:
    if destination.exists() or destination.is_symlink():
        if destination.is_dir() and not destination.is_symlink():
            shutil.rmtree(destination)
        else:
            destination.unlink()

    copied = 0
    for source_path in sorted(source.rglob("*")):
        if "__pycache__" in source_path.parts or source_path.suffix == ".pyc":
            continue

        relative_path = source_path.relative_to(source)
        destination_path = destination / relative_path

        if source_path.is_dir():
            destination_path.mkdir(parents=True, exist_ok=True)
            continue

        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination_path)
        copied += 1

    return copied


def sync_scripts(source_root: Path, target: Path) -> tuple[int, int, tuple[str, ...]]:
    copied = 0
    replaced = 0
    copied_paths: list[str] = []
    scripts_source = source_root / "scripts"
    scripts_destination = target / "study-os/scripts"

    for script_source in sorted(scripts_source.glob("*.py")):
        was_replaced = copy_file_replace(
            script_source, scripts_destination / script_source.name
        )
        copied += 1
        copied_paths.append(f"study-os/scripts/{script_source.name}")
        if was_replaced:
            replaced += 1

    return copied, replaced, tuple(copied_paths)


def sync_skills(source_root: Path, target: Path) -> tuple[int, int, tuple[str, ...]]:
    copied = 0
    folders_synced = 0
    synced_paths: list[str] = []
    skills_source = source_root / "skills"

    for relative_destination in SKILL_DESTINATIONS:
        destination = target / relative_destination
        for skill_source in sorted(
            path for path in skills_source.iterdir() if path.is_dir()
        ):
            copied += copy_tree_replace(skill_source, destination / skill_source.name)
            folders_synced += 1
            synced_paths.append(f"{relative_destination}/{skill_source.name}")

    return copied, folders_synced, tuple(synced_paths)


def write_sync_log(
    target: Path,
    copied_scripts: int,
    replaced_scripts: int,
    copied_skill_files: int,
    synced_skill_folders: int,
    copied_script_paths: tuple[str, ...],
    synced_skill_paths: tuple[str, ...],
    warnings: tuple[str, ...] = (),
    errors: tuple[str, ...] = (),
) -> Path:
    state_directory = target / "study-os/state"
    state_directory.mkdir(parents=True, exist_ok=True)
    log_path = state_directory / "sync-log.md"

    warning_lines = "\n".join(f"- {warning}" for warning in warnings) or "- None"
    error_lines = "\n".join(f"- {error}" for error in errors) or "- None"
    copied_script_lines = (
        "\n".join(f"- `{relative_path}`" for relative_path in copied_script_paths)
        or "- None"
    )
    synced_skill_lines = (
        "\n".join(f"- `{relative_path}`" for relative_path in synced_skill_paths)
        or "- None"
    )
    untouched_lines = "\n".join(
        f"- `{relative_path}`" for relative_path in INTENTIONALLY_NOT_TOUCHED
    )

    log_path.write_text(
        "\n".join(
            (
                "# StudyOS Sync Log",
                "",
                f"- Timestamp: {datetime.now().astimezone().isoformat()}",
                f"- Target folder: {target}",
                f"- Scripts copied: {copied_scripts}",
                f"- Scripts replaced: {replaced_scripts}",
                f"- Skill files copied: {copied_skill_files}",
                f"- Skill folders synced: {synced_skill_folders}",
                "",
                "## Scripts Copied",
                "",
                copied_script_lines,
                "",
                "## Skill Folders Synced",
                "",
                synced_skill_lines,
                "",
                "## Files/Folders Intentionally Not Touched",
                "",
                untouched_lines,
                "",
                "## Warnings",
                "",
                warning_lines,
                "",
                "## Errors",
                "",
                error_lines,
                "",
            )
        ),
        encoding="utf-8",
    )
    return log_path


def main() -> int:
    args = parse_args()
    target = args.target.expanduser().resolve()
    source_root = repo_root()

    try:
        validate_sources(source_root)
        validate_target(target)
        copied_scripts, replaced_scripts, copied_script_paths = sync_scripts(
            source_root, target
        )
        (
            copied_skill_files,
            synced_skill_folders,
            synced_skill_paths,
        ) = sync_skills(source_root, target)
        log_path = write_sync_log(
            target,
            copied_scripts,
            replaced_scripts,
            copied_skill_files,
            synced_skill_folders,
            copied_script_paths,
            synced_skill_paths,
        )
    except OSError as error:
        print(f"StudyOS sync failed: {error}", file=sys.stderr)
        return 1

    print(f"StudyOS synced at: {target}")
    print(f"Scripts copied: {copied_scripts}")
    print(f"Scripts replaced: {replaced_scripts}")
    print("Copied scripts:")
    for copied_script_path in copied_script_paths:
        print(f"  - {copied_script_path}")
    print(f"Skill files copied: {copied_skill_files}")
    print(f"Skill folders synced: {synced_skill_folders}")
    print("Synced skill folders:")
    for synced_skill_path in synced_skill_paths:
        print(f"  - {synced_skill_path}")
    print(f"Sync log: {log_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
