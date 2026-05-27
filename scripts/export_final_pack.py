#!/usr/bin/env python3
"""Build a minimal Markdown StudyOS final review pack."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path


OUTPUT_PATH = Path("outputs/final-pack/final_review_pack.md")
LEARNING_CORES_DIR = Path("analysis/batches")
REVIEW_FILES = (
    Path("review/validation-report.md"),
    Path("review/source-coverage.md"),
    Path("review/formula_validation_report.md"),
    Path("review/weak-points.md"),
    Path("review/unresolved-questions.md"),
)
TEXT_SUFFIXES = {".md", ".text", ".txt"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a minimal Markdown final review pack from StudyOS artifacts."
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


def text_files(folder: Path) -> list[Path]:
    if not folder.is_dir():
        return []
    return sorted(
        path
        for path in folder.rglob("*")
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES
    )


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace").strip()


def build_final_pack(root: Path) -> Path:
    learning_cores = text_files(root / LEARNING_CORES_DIR)
    if not learning_cores:
        raise FileNotFoundError(
            f"No learning core files found under {LEARNING_CORES_DIR}. "
            "Run batch processing and validation before exporting a final pack."
        )

    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    lines = [
        "# StudyOS Final Review Pack",
        "",
        f"Generated: {generated_at}",
        f"Root: `{root}`",
        "",
        "This minimal pack is assembled from existing learning cores and review artifacts. "
        "It does not replace the `studyos-merge` skill for richer course-level merging.",
        "",
        "## Included Learning Cores",
        "",
    ]

    for path in learning_cores:
        lines.append(f"- `{relative(path, root)}`")

    lines.extend(["", "## Learning Core Material", ""])
    for path in learning_cores:
        lines.extend(
            [
                f"### {relative(path, root)}",
                "",
                read_text(path) or "_Empty file._",
                "",
            ]
        )

    existing_review_files = [root / path for path in REVIEW_FILES if (root / path).is_file()]
    lines.extend(["", "## Review Artifacts", ""])
    if not existing_review_files:
        lines.append("No review artifacts found.")
        lines.append("")
    else:
        for path in existing_review_files:
            lines.extend(
                [
                    f"### {relative(path, root)}",
                    "",
                    read_text(path) or "_Empty file._",
                    "",
                ]
            )

    output = root / OUTPUT_PATH
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    return output


def main() -> int:
    args = parse_args()
    root = args.root.expanduser().resolve()

    try:
        output = build_final_pack(root)
    except (OSError, FileNotFoundError) as error:
        print(f"StudyOS final pack export failed: {error}", file=sys.stderr)
        return 1

    print(f"Wrote final review pack: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
