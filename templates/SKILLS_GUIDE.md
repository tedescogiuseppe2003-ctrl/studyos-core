# StudyOS Skills Guide

This guide describes the installed StudyOS skills and the order to use them. The workflow is manual and guided: the user chooses each step, and each skill stops when required earlier artifacts are missing.

## study-os-import-sources

Use this first when the course material is still in an original raw folder.

Proposal mode:

- Scans `subject.yaml` -> `raw_source.path` read-only.
- Classifies raw course files by filename, folder, metadata, and minimal skimming only when needed.
- Writes `working/inventory/import_plan.md`.
- Does not copy, move, rename, delete, modify, summarize, or process files.

Execute mode:

- Reads the approved `working/inventory/import_plan.md`.
- Copies approved rows into `inputs/`.
- Writes `working/inventory/import_log.md`.
- Never modifies original files.
- Never overwrites destination files.

Run this before `study-os-inventory` unless `inputs/` already contains approved copied course files.

## study-os-inventory

Use this after source files exist under `inputs/`.

- Scans only approved `inputs/` folders.
- Creates `working/inventory/course_inventory.md`.
- Creates `working/inventory/batch_plan.md`.
- Groups files into conceptual batches such as topics, lectures, modules, or tutorial sessions.
- Treats exercises as supporting sources unless they are explicitly tutorial or conceptual material.
- Does not summarize, process, validate, or generate study outputs.

Run this before `study-os-process-batch` or `study-os-process-course`.

## study-os-process-batch

Use this to process one planned batch from `working/inventory/batch_plan.md`.

- Processes one batch at a time.
- Reads every assigned source for that batch.
- Creates a source digest in `working/digests/`.
- Creates a learning core in `working/learning-cores/`.
- Creates configured batch outputs under `outputs/`.
- Updates weak points and unresolved questions under `review/`.
- Is best for testing quality one topic at a time before running the rest of the course.

Run `study-os-validate` after processing a batch.

## study-os-validate

Use this after a batch has digest, learning core, and outputs.

- Runs deterministic structure checks.
- Checks citations when configured.
- Checks formula fields and formula sources when configured.
- Performs LLM review if requested in `subject.yaml`.
- Reviews grounding, clarity, active recall quality, exam usefulness, weak points, and unresolved questions.
- Writes validation reports under `review/`.
- May write additional handoff notes under `working/validation/`.

Validation does not rewrite outputs unless the user explicitly asks for fixes.

## study-os-process-course

Use this after one batch has been processed and validated successfully.

- Reads `working/inventory/batch_plan.md`.
- Processes remaining planned or stale batches sequentially.
- Uses the `study-os-process-batch` workflow for each batch.
- Validates each batch before continuing.
- Repairs minor validation issues when appropriate.
- Stops on severe issues such as missing sources, ambiguous batch plans, unsupported claims, inconsistent formulas, missing source coverage, or any need to modify protected files.
- Updates `review/progress-tracker.md` and `study-os/state/run-log.md`.

This skill does not synthesize final course-level outputs.

## study-os-synthesize

Use this after relevant batches have been processed and validated.

- Creates final full-course notes when requested.
- Creates a course-level formula sheet when requested.
- Creates flashcards when requested.
- Creates a question bank when requested.
- Creates a cheat sheet when requested.
- Creates a study plan when requested.
- Creates a final review pack when requested.
- Uses validated learning cores and validated outputs as the primary basis.

Synthesis should preserve source references, weak points, unresolved questions, and validation findings.

## Preflight Behavior

If a skill is called too early, it must stop and report:

- what is missing,
- why it cannot continue,
- which skill to run first.

Do not skip earlier steps to keep moving. Run the missing prerequisite skill, then retry the current skill.
