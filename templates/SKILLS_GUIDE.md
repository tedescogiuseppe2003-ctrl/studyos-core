# StudyOS Skills Guide

This guide describes the installed StudyOS skills and the order to use them. The workflow is manual and guided: the user chooses each step, and each skill stops when required earlier artifacts are missing.

## Installation Boundary

Installation/setup ends after the agent runs the external core installer, runs sync, initializes or confirms the database, asks setup questions, fills `subject.yaml`, and creates or updates `STUDYOS_GUIDE.md`.

Installation/setup must not import files, run inventory, create an import plan, create a batch plan, summarize material, validate outputs, or process course material. After setup, the user manually calls the skills below step by step.

## Quality Modes

Quality mode controls how much detail each processing skill should produce.

- `economy`: compact and faster. Master notes target 800-1200 words per batch, flashcards 15-25, exam questions 5-10, and formula sheets include only essential formulas.
- `standard`: balanced default. Master notes target 1200-2200 words per batch, flashcards 25-45, exam questions 8-18, and formula sheets include all important formulas.
- `rigorous`: completeness-oriented. Master notes can be as long as needed, flashcards can reach 40-70 per exam-heavy batch, exam questions 15-30, and formula sheets include formulas, assumptions, derivations, and common mistakes.

Higher visual, formula, or validation depth increases source screening and checking rigor, especially for exam-critical diagrams, tables, charts, formulas, assumptions, and weak points.

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

Run this before `study-os-process-batch`. Use `study-os-process-course` only when the user explicitly asks to process remaining batches sequentially.

## study-os-process-batch

Use this to process one planned batch from `working/inventory/batch_plan.md`.

- Processes one batch at a time.
- Reads every assigned source for that batch.
- Creates a source digest in `working/digests/`.
- Creates a learning core in `working/learning-cores/`.
- Creates configured batch outputs under `outputs/`.
- Updates weak points and unresolved questions under `review/`.
- Is best for testing quality one topic at a time before running the rest of the course.

Source-type rules:

- Slides are the primary theory source when assigned as core lecture material.
- Notes feed professor emphasis, doubts, traps, clarifications, and weak points.
- Exercises become practice questions, repeated problem types, weak points, and concept/formula links instead of theory summaries by default.
- Readings add relevant theory, definitions, assumptions, limitations, and deeper explanations without unnecessary over-summary.
- Exams add patterns, likely question types, answer expectations, and final-review signals.
- Transcripts add explanations, examples, emphasis, and professor-style phrasing.
- Miscellaneous sources are classified before use, with uncertainty flagged in the digest.

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

When fixes are in scope, validation should lead to targeted repair before regeneration: patch only affected sections, preserve valid content, avoid regenerating unrelated outputs, rerun validation after repair, and mark remaining uncertainty clearly.

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

During course processing, validation issues are repaired batch by batch. A minor issue should trigger a focused patch and recheck for the current batch, not regeneration of unrelated outputs or other batches.

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
