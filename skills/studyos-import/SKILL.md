---
name: studyos-import
description: Safely propose and execute source import, then build the initial inventory and conceptual batch plan.
---

# Purpose

Import approved raw course files into `inputs/`, create the source inventory, and create the first conceptual batch plan.

# When to use

Use after StudyOS installation/setup is approved and before planning or processing batches. This skill replaces the old separate import-sources and inventory skills.

# Preflight checks

- `subject.yaml` exists and `setup.completed` is true.
- `raw_source.path` is configured and readable when import from an original folder is needed.
- `inputs/`, `analysis/inventory/`, `study-os/scripts/import_sources.py`, and `study-os/scripts/inventory.py` exist.
- Stop if any original raw file would need to be moved, renamed, deleted, overwritten, or modified.

# Reads

- `subject.yaml`
- original raw source folder configured by `raw_source.path`
- existing `analysis/inventory/import_plan.md`, when executing an approved plan
- copied files under `inputs/`, when inventorying

# Writes

- `analysis/inventory/import_plan.md`
- `analysis/inventory/import_log.md`
- approved copied files under `inputs/`
- `analysis/inventory/course_inventory.md`
- `analysis/inventory/batch_plan.md`
- StudyOS state files under `study-os/state/`

# Workflow

1. If no approved import plan exists, run proposal mode: scan the raw source folder read-only, classify files, and write `analysis/inventory/import_plan.md`.
2. Ask the user to review and approve the copy actions before execution.
3. In execute mode, copy only approved rows into the correct `inputs/` subfolders without overwriting destination files.
4. Run inventory on `inputs/` only.
5. Create a conceptual batch plan grouped by topics, lectures, modules, or tutorial sessions.
6. Treat exercises, exams, notes, readings, and transcripts as supporting sources unless they are explicitly conceptual material.

# Model routing and efficiency

- Use scripts for copying, hashing, and deterministic inventory.
- Use fast reasoning for filename/folder classification and straightforward batch grouping.
- Use deeper reasoning only when source roles or conceptual grouping are ambiguous.

# Quality rules

- Original raw files are read-only.
- Imported files under `inputs/` are copied, never moved.
- Destination files are never overwritten.
- Inventory scans only `inputs/`.
- The batch plan is conceptual, not merely alphabetical or file-type based.

# Stop conditions

- Setup is incomplete.
- `raw_source.path` is missing or unreadable and `inputs/` is empty.
- The import plan has not been approved for execution.
- Copying would overwrite an existing destination file.
- Inventory cannot confidently associate files with conceptual batches; write an unassigned section and stop for review.

# Completion report

Report the import plan path, copied file count, skipped file count, inventory path, batch plan path, and the next recommended skill: `studyos-plan`.
