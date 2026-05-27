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

Use after setup approval. This skill proposes safe import, executes approved copy actions, then builds the first inventory and first-pass batch plan.

- Proposal mode scans `raw_source.path` read-only and writes `analysis/inventory/import_plan.md`.
- Execute mode copies only approved rows into `inputs/` and writes `analysis/inventory/import_log.md`.
- Inventory scans only `inputs/` and writes `analysis/inventory/course_inventory.md`.
- Initial planning writes `analysis/inventory/batch_plan.md` from filenames, folders, lecture numbers, and simple topic keywords.
- Full import flow creates a proposal if no plan exists, stops for user approval, then after approval runs execute and inventory.

Proposal mode requires `subject.yaml` and `raw_source.path`. Execute mode requires `analysis/inventory/import_plan.md`. Inventory mode requires at least one file under `inputs/`.

Original raw files are never moved, renamed, deleted, overwritten, or modified. Destination files are never overwritten. Approved copy destinations are restricted to `inputs/slides/`, `inputs/readings/`, `inputs/notes/`, `inputs/exercises/`, `inputs/exams/`, `inputs/transcripts/`, and `inputs/miscellaneous/`.

## studyos-plan

Use after `studyos-import`. This skill refines the first-pass `analysis/inventory/batch_plan.md` before processing. It is distinct from inventory: inventory discovers and classifies files, while planning turns the draft into conceptual batches.

- Batches should represent concepts, lectures, modules, or tutorial themes.
- Slides and lecture-topic files usually define primary batches.
- Exercises, readings, transcripts, notes, and exams should support conceptual batches where possible.
- Ordinary exercises should not become standalone master-note batches unless they are explicitly tutorial or conceptual.
- Each refined batch should include title, status, difficulty, exam relevance, dependencies, primary sources, supporting sources, expected outputs, and notes.
- Ambiguous files remain in a needs-review section instead of being hidden.
- The skill writes `analysis/inventory/batch_plan_repair_log.md` and may write `analysis/inventory/processing_queue.md` when useful.
- It must not process, summarize, solve, validate, or transform course material.

## studyos-batch

Use to process one selected conceptual batch.

- Requires `analysis/inventory/batch_plan.md`, `analysis/inventory/course_inventory.md`, a selected batch, and files under `inputs/`.
- Reads assigned sources under `inputs/`.
- Reads existing review files when present.
- Builds Source Coverage before generating outputs.
- Screens visuals internally and analyzes essential visuals when needed.
- Writes `analysis/batches/<batch>_digest.md`.
- Writes `analysis/batches/<batch>_learning_core.md`.
- Writes `analysis/visual/<batch>_visual_notes.md` when visual findings exist.
- Writes `outputs/notes/<batch>.md`.
- Writes `outputs/formulas/<batch>_formulas.md` when formulas exist.
- Writes `outputs/flashcards/<batch>_flashcards.md`.
- Writes `outputs/questions/<batch>_questions.md`.
- Updates `review/weak-points.md`, `review/unresolved-questions.md`, and `review/visual-issues.md` when visual issues exist.

Every digest includes Batch Processing Plan, Source Coverage, Visual Coverage, Core extracted content, Definitions, Formulas, Important tables/charts/diagrams, Examples, Weak points, Unresolved questions, and Source references.

If the batch has slides, PDFs, or images, Visual Coverage is required. If no essential visuals exist, the digest says so explicitly. Essential visuals include formulas in images, definitions in images, charts, tables, rankings, benchmark values, model diagrams, process diagrams, and summary visual slides.

Use model routing from `subject.yaml` and `study-os/config/model-routing.yaml` when available: balanced for normal batches, deep for formula-heavy batches, deep only for affected essential visuals, fast or balanced for flashcards, and balanced or deep for exam questions depending on difficulty. Repair affected sections before regenerating entire outputs.

Run `studyos-validate` after each processed batch.

## studyos-validate

Use after batch processing, course-level processing, repairs, or merging.

- Requires processed batch outputs under `analysis/batches/` or generated outputs under `outputs/`.
- Requires validation scripts under `study-os/scripts/`.
- Runs deterministic structural checks, citation/source checks, and formula field checks where applicable.
- Reviews grounding, unsupported claims, source coverage, visual coverage, clarity, flashcard usefulness, exam-question answer quality, exercise integration, weak points, and unresolved questions according to configured depth.
- Confirms `review/source-coverage.md` exists after validation.
- Checks Visual Coverage for any batch with slide, PDF, or image sources.
- Writes reports under `review/` and detailed notes under `analysis/validation/`.
- Writes or updates `review/visual-issues.md` and `review/unresolved-questions.md` when relevant.

Validation severity levels are `low`, `medium`, `high`, and `blocking`. Blocking issues stop downstream work. Validation should lead to targeted repair before regeneration: repair affected sections, preserve valid content, avoid regenerating unrelated outputs, and rerun validation after repair.

Completion reports include validation status, blocking issues, high-priority fixes, minor fixes, files written, and the recommended next skill.

## studyos-course

Use after import and planning when the user wants remaining planned or unprocessed batches processed in order. If no validated batch exists yet, warn:

> Recommended: process and validate one batch manually before full course processing.

- Requires `analysis/inventory/batch_plan.md` and files under `inputs/`.
- Reads optional `analysis/inventory/processing_queue.md` when present.
- Reads `analysis/batches/`, `outputs/`, and `review/` to identify planned, unprocessed, stale, failed, and already validated batches.
- Processes remaining planned, unprocessed, stale, or repairable failed batches sequentially by default.
- Uses `studyos-batch` semantics for each batch.
- Uses `studyos-validate` semantics before moving to the next batch and does not skip validation.
- Repairs minor localized issues when appropriate, then revalidates before continuing.
- Stops on blocking validation issues, missing assigned sources, unsafe batch ordering, or unresolved essential visual content.
- Writes to `analysis/batches/`, `analysis/visual/`, `analysis/validation/`, `outputs/notes/`, `outputs/formulas/`, `outputs/flashcards/`, `outputs/questions/`, `review/`, and optional processing state under `study-os/state/`.
- Includes integrated visual screening; no separate visual skill is needed.

Parallelism is off by default. Use safe parallelism only when configured in `subject.yaml`; do not parallelize dependent batches, do not parallelize digest and learning core for the same batch, and require merged validation before downstream work continues.

Completion reports include batches processed, batches skipped, stopped batch if any, validation status, unresolved issues, and the recommended next skill: `studyos-merge`.

This skill does not process the whole course as one giant batch and does not create merged final outputs.

## studyos-merge

Use after relevant batch outputs are processed and validated.

- Reads learning cores from `analysis/batches/*_learning_core.md`.
- Reads validated batch outputs from `outputs/notes/Batch_*.md`, `outputs/formulas/Batch_*.md`, `outputs/flashcards/Batch_*.md`, and `outputs/questions/Batch_*.md`.
- Reads `review/weak-points.md`, `review/unresolved-questions.md`, and `review/validation-report.md`.
- Merges by consolidating duplicate concepts, harmonizing notation, deduplicating formulas, identifying dependencies, and preserving source references.
- Prioritizes weak points, unresolved questions, likely exam questions, and exam-relevant visual findings.
- Writes `outputs/notes/full_course_notes.md`.
- Writes `outputs/formulas/full_formula_sheet.md`.
- Writes `outputs/flashcards/full_flashcards.md`.
- Writes `outputs/questions/full_question_bank.md`.
- Writes `outputs/cheat-sheets/final_cheat_sheet.md`.
- Writes `outputs/study-plan/full_course_study_plan.md`, including a final 7-day plan and last-48-hour plan.
- Writes `outputs/final-pack/final_review_pack.md`.

Merge does not mean concatenate. Run audit validation on the final merged pack when validation depth or exam risk requires it.

## studyos-export

Use after desired outputs exist and have acceptable validation status.

- Reads unmerged batch-level outputs from `outputs/notes/Batch_*.md`, `outputs/formulas/Batch_*.md`, `outputs/flashcards/Batch_*.md`, and `outputs/questions/Batch_*.md`.
- Writes unmerged exports to `exports/pdf/unmerged/notes/`, `exports/pdf/unmerged/formulas/`, `exports/pdf/unmerged/flashcards/`, and `exports/pdf/unmerged/questions/`.
- Reads merged full-course outputs from `outputs/notes/full_course_notes.md`, `outputs/formulas/full_formula_sheet.md`, `outputs/flashcards/full_flashcards.md`, `outputs/questions/full_question_bank.md`, `outputs/cheat-sheets/final_cheat_sheet.md`, `outputs/study-plan/full_course_study_plan.md`, and `outputs/final-pack/final_review_pack.md`.
- Writes merged exports to `exports/pdf/merged/`.
- Preserves batch boundaries, content, LaTeX expressions, and source references.
- Does not export `analysis/`, `review/`, validation, debug, or internal files by default.
- Uses `python3 study-os/scripts/export_outputs.py --root .`.

The exporter prefers PDF when `pandoc` and a LaTeX PDF engine are available. If PDF tooling is unavailable, it writes clean print-ready HTML in the same export folders and reports the fallback.

If merged outputs are missing, export only unmerged outputs and warn. If unmerged outputs are missing, export only merged outputs and warn. If no exportable outputs exist, stop and tell the user to run `studyos-batch`, `studyos-course`, or `studyos-merge` first.

## Preflight Behavior

If a skill is called too early, it must stop and report what is missing, why it cannot continue, and which skill to run first.
