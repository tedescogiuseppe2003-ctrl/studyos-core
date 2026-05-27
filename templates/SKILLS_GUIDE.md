# StudyOS Skills Guide

This guide describes the installed StudyOS skills and the order to use them. The workflow is manual: after installation and approved setup, the user calls one skill at a time.

## Installation Boundary

Installation/setup ends after the agent runs the external core installer, initializes or confirms the database, runs sync, inspects the folder name and visible raw course files read-only, proposes a complete setup, gets approval, fills `subject.yaml`, and creates or updates `STUDYOS_GUIDE.md`.

Installation/setup must not import files, create an import plan, run inventory, create a batch plan, process material, validate outputs, merge outputs, or export PDFs.

## Status And Readiness

- `python3 study-os/scripts/studyos.py status` prints workspace state and the next recommended manual skill.
- `python3 study-os/scripts/studyos.py doctor` checks required folders, scripts, skills, config files, `subject.yaml`, readable `raw_source.path`, and obvious stale setup issues.

These commands are read-only.

## Skill Order

1. `studyos-import`
2. `studyos-plan`
3. `studyos-batch`
4. `studyos-validate`
5. `studyos-course`
6. `studyos-merge`
7. `studyos-export`

## studyos-import

Use after setup approval. This skill proposes safe import, executes approved copy actions, then builds the first inventory and conceptual batch plan.

- Proposal mode scans `raw_source.path` read-only and writes `analysis/inventory/import_plan.md`.
- Execute mode copies only approved rows into `inputs/` and writes `analysis/inventory/import_log.md`.
- Inventory scans only `inputs/` and writes `analysis/inventory/course_inventory.md`.
- Initial planning writes `analysis/inventory/batch_plan.md`.
- Full import flow creates a proposal if no plan exists, stops for user approval, then after approval runs execute and inventory.

Proposal mode requires `subject.yaml` and `raw_source.path`. Execute mode requires `analysis/inventory/import_plan.md`. Inventory mode requires at least one file under `inputs/`.

Original raw files are never moved, renamed, deleted, overwritten, or modified. Destination files are never overwritten. Approved copy destinations are restricted to `inputs/slides/`, `inputs/readings/`, `inputs/notes/`, `inputs/exercises/`, `inputs/exams/`, `inputs/transcripts/`, and `inputs/miscellaneous/`.

## studyos-plan

Use after `studyos-import`. This skill refines `analysis/inventory/batch_plan.md` before processing.

- Batches should represent concepts, lectures, modules, or tutorial themes.
- Exercises, readings, transcripts, notes, and exams should support conceptual batches where possible.
- Ambiguous files remain in a needs-review section instead of being hidden.

## studyos-batch

Use to process one selected planned batch.

- Reads assigned sources under `inputs/`.
- Writes batch digests and learning cores under `analysis/batches/`.
- Writes configured batch outputs under `outputs/`.
- Adds visual notes under `analysis/visual/` when relevant.
- Updates weak points and unresolved questions under `review/`.

Run `studyos-validate` after each processed batch.

## studyos-validate

Use after batch processing, course-level processing, repairs, or merging.

- Runs deterministic structure, citation, and formula checks where available.
- Reviews grounding, source coverage, visual coverage, clarity, and exam usefulness according to configured depth.
- Writes reports under `review/` and `analysis/validation/`.

Validation should lead to targeted repair before regeneration. It must not silently rewrite outputs.

## studyos-course

Use after at least one representative batch has been processed and validated.

- Processes remaining planned or stale batches sequentially.
- Uses `studyos-batch` semantics for each batch.
- Uses `studyos-validate` semantics before moving to the next batch.
- Creates course-level outputs while preserving batch boundaries.

This skill does not create merged final outputs.

## studyos-merge

Use after relevant batch and course outputs are processed and validated.

- Merges validated batch and course material into consolidated full-course outputs.
- Preserves source references, weak points, unresolved questions, and validation findings.
- Writes merged deliverables under `outputs/`, including the final review pack.

Run `studyos-validate` on merged outputs when validation depth requires it.

## studyos-export

Use after desired outputs exist and have acceptable validation status.

- Exports unmerged batch/course outputs to `exports/pdf/unmerged/`.
- Exports merged full-course outputs to `exports/pdf/merged/`.
- Preserves batch boundaries for unmerged exports.

## Preflight Behavior

If a skill is called too early, it must stop and report what is missing, why it cannot continue, and which skill to run first.
