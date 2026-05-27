---
name: studyos-import
description: Propose and execute safe source import, build inventory, and create the first conceptual batch plan.
---

# Purpose

`studyos-import` combines import proposal, import execution, source inventory, and first-pass batch planning. It replaces the old separated import-sources and inventory user-facing skills.

# Modes

## Mode 1: proposal

Use when `analysis/inventory/import_plan.md` does not exist or the user asks for an import proposal.

Preflight:
- `subject.yaml` exists.
- `subject.yaml` has `raw_source.path`.
- `raw_source.path` is readable.

Behavior:
- Read `subject.yaml`.
- Scan `raw_source.path` read-only.
- Ignore StudyOS system folders and files:
  - `inputs/`
  - `analysis/`
  - `outputs/`
  - `exports/`
  - `review/`
  - `study-os/`
  - `.agents/`
  - `.claude/`
  - `.git/`
  - `__pycache__/`
  - `.DS_Store`
- Write `analysis/inventory/import_plan.md`.
- Do not copy files.
- Do not move files.
- Do not modify original files.

Command:

```sh
python3 study-os/scripts/import_sources.py --mode proposal
```

Stop if `subject.yaml` or `raw_source.path` is missing or unreadable.

## Mode 2: execute

Use only after the user approves `analysis/inventory/import_plan.md`.

Preflight:
- `analysis/inventory/import_plan.md` exists.
- The user has approved the proposed copy actions.

Behavior:
- Read `analysis/inventory/import_plan.md`.
- Copy approved rows into `inputs/`.
- Never move originals.
- Never delete originals.
- Never modify originals.
- Never overwrite destination files.
- Write `analysis/inventory/import_log.md`.

Command:

```sh
python3 study-os/scripts/import_sources.py --mode execute
```

Stop if `import_plan.md` is missing, if a proposed destination is outside the approved folders, or if a destination file already exists.

Approved destination folders are restricted to:
- `inputs/slides/`
- `inputs/readings/`
- `inputs/notes/`
- `inputs/exercises/`
- `inputs/exams/`
- `inputs/transcripts/`
- `inputs/miscellaneous/`

## Mode 3: inventory

Use after import execution or when approved course files already exist under `inputs/`.

Preflight:
- `inputs/` contains at least one file.

Behavior:
- Scan only `inputs/`.
- Create `analysis/inventory/course_inventory.md`.
- Create `analysis/inventory/batch_plan.md`.
- Update SQLite state under `study-os/state/`.
- Do not process material.

Command:

```sh
python3 study-os/scripts/inventory.py
```

Stop if `inputs/` is empty.

## Mode 4: full import flow

Use when the user asks to run `studyos-import` without a specific mode.

Behavior:
1. If `analysis/inventory/import_plan.md` does not exist, run proposal mode.
2. Stop and ask the user to review and approve `analysis/inventory/import_plan.md`.
3. After approval, run execute mode.
4. Run inventory mode.
5. Leave the first-pass `analysis/inventory/batch_plan.md` ready for `studyos-plan`.

Do not silently continue from proposal to execute. User approval is required between those steps.

# Reads

- `subject.yaml`
- original raw source folder configured by `raw_source.path`
- `analysis/inventory/import_plan.md`, when executing
- copied files under `inputs/`, when inventorying

# Writes

- `analysis/inventory/import_plan.md`
- `analysis/inventory/import_log.md`
- approved copied files under `inputs/`
- `analysis/inventory/course_inventory.md`
- `analysis/inventory/batch_plan.md`
- SQLite state under `study-os/state/`

# Quality Rules

- Original raw files are read-only.
- Original raw files are never moved, renamed, deleted, overwritten, or modified.
- Imported files under `inputs/` are copied, never moved.
- Destination files are never overwritten.
- Inventory scans only `inputs/`.
- The batch plan is conceptual, not merely alphabetical or file-type based.
- Exercises, exams, notes, readings, and transcripts are supporting sources unless clearly conceptual.

# Stop Conditions

- `subject.yaml` is missing.
- `raw_source.path` is missing or unreadable for proposal mode.
- `analysis/inventory/import_plan.md` is missing for execute mode.
- The user has not approved the import plan for execute mode.
- `inputs/` is empty for inventory mode.
- A proposed destination is outside the approved `inputs/` folders.
- Copying would overwrite an existing destination file.
- Inventory cannot confidently associate files with conceptual batches; write an unassigned section and stop for review.

# Completion Report

Report the mode run, import plan path, copied file count, skipped file count, import log path, inventory path, batch plan path, and the next recommended skill: `studyos-plan`.
