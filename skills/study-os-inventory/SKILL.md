---
name: study-os-inventory
description: Build or refresh the StudyOS source inventory for one installed subject folder by scanning input metadata and creating batch planning files.
---

# StudyOS Inventory

Use this skill before processing course material. Inventory discovers raw sources and creates a batch plan; it does not summarize, interpret, or transform course content.

## Scope

Inventory is metadata-only. It prepares batches for later processing.

Keep v1 lean. Do not add Graphify, hooks, subagents, Anki export, Obsidian export, dashboards, or web apps.

## May Read

- `PROJECT_BRIEF.md` when working in the core repo.
- Installed subject configuration:
  - `subject.yaml`
  - `workflow.yaml`
  - `output-standards.yaml`
- File metadata and bytes for hashing under:
  - `inputs/slides/`
  - `inputs/readings/`
  - `inputs/notes/`
  - `inputs/exercises/`
  - `inputs/exams/`
  - `inputs/transcripts/`
  - `inputs/miscellaneous/`
- Existing inventory files and SQLite state:
  - `working/inventory/course_inventory.md`
  - `working/inventory/batch_plan.md`
  - `study-os/state/studyos.sqlite`

## May Write

- `working/inventory/course_inventory.md`
- `working/inventory/batch_plan.md`
- `study-os/state/studyos.sqlite`
- `study-os/state/` support files required by the local inventory script.

## Must Not Write

- Never modify files inside `inputs/`.
- Do not write to `working/digests/`, `working/learning-cores/`, `outputs/`, or `review/`.
- Do not extract PDF text, OCR images, analyze slides visually, or summarize content during inventory.

## Required Inventory Fields

For each source file, record:

- relative path from the subject root,
- input folder-derived source type,
- filename-derived lecture number when possible,
- filename-derived topic guess,
- SHA256 hash,
- status such as `new`, `stale`, or unchanged existing status.

## Batch planning rules

Batches should represent conceptual topics, lectures, or modules, not individual files.

Slides and lecture-topic notes usually define batches.

Exercises, exams, readings, transcripts, and personal notes should usually be attached as supporting sources to the closest relevant conceptual batch.

Do not create standalone exercise batches unless:

- the exercise file is explicitly a tutorial/session;
- the exercise contains new theoretical material;
- no related conceptual batch can be identified.

If a source cannot be confidently matched, place it under “Unassigned / needs review.”

- Each planned batch should include title, primary sources, supporting sources, expected outputs, status, difficulty, and exam relevance.
- Group sources conservatively by lecture number and topic guess when no stronger topic structure is available.
- Keep batches small enough to process one at a time.
- Do not merge unrelated lectures only because they share a broad topic word.
- Include every discovered input file in the batch plan, even if lecture/topic is uncertain.
- Use `Unassigned` when a lecture number cannot be inferred.

## Workflow

1. Run from the installed subject folder root unless the user supplies `--root`.
2. Confirm required StudyOS folders exist.
3. Scan only approved `inputs/` subfolders.
4. Hash each file and compare with existing inventory state.
5. Update SQLite source rows idempotently.
6. Write `working/inventory/course_inventory.md` as a readable Markdown table.
7. Write `working/inventory/batch_plan.md` with batch headings and source file lists.
8. Report source count, inventory path, batch plan path, and database path.

## Quality Bar

- The command can be run repeatedly without duplicating source rows.
- Changed file hashes mark existing sources as stale.
- The inventory is useful for selecting one batch for `study-os-process-batch`.
- `inputs/` remains read-only.
