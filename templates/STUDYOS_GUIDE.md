# StudyOS Guide

StudyOS is a guided study-material workflow for one course. It keeps original course files protected, copies approved material into `inputs/`, then helps an agent build inventory, batch outputs, validation reports, merged study material, and PDF exports step by step.

## Normal Installation UX

Before installation, this course folder may not have local StudyOS skills yet. Installation is done through the external StudyOS core repo, usually `~/Developer/studyos-core`.

Normal request:

> Install StudyOS in this folder using ~/Developer/studyos-core.

The installing agent runs the external core installer, initializes or confirms the database, runs core sync, inspects the folder name and visible raw course files read-only, proposes a complete setup, asks for approval or modifications, fills `subject.yaml` only after approval, creates or updates this guide, and stops.

Installation/setup does not import files, run inventory, create a batch plan, validate, process, merge, or export material.

## Setup Proposal After Installation

The proposal includes subject name, course level, material language, exam type, raw source folder path, read-only original files, copy-into-inputs strategy, desired outputs, quality/depth mode, visual handling depth, formula handling depth, and validation depth.

The agent asks:

> Do you approve this setup, or do you want modifications?

The agent fills `subject.yaml` only after approval.

## Folder Structure

- `inputs/` contains copied course files after import. Treat these files as read-only.
- `analysis/` contains import plans, inventory, first-pass and refined batch plans, repair logs, source digests, learning cores, visual notes, validation records, and processing state.
- `outputs/` contains batch-level, course-level, and merged study outputs.
- `exports/pdf/unmerged/` and `exports/pdf/merged/` contain PDF exports, or print-ready HTML fallbacks when local PDF tooling is unavailable.
- `review/` contains validation reports, weak points, unresolved questions, source coverage, and progress tracking.
- `study-os/` contains installed scripts, skills, config guides, and local state.

## Protected Files

The original raw course folder configured at `subject.yaml` -> `raw_source.path` is read-only. StudyOS must never move, rename, delete, overwrite, or modify anything there.

Import copies approved files into `inputs/`. Files under `inputs/` are also treated as read-only after import.

## Skill Commands

- `python3 study-os/scripts/studyos.py status` reports the current workspace state and next recommended manual skill.
- `python3 study-os/scripts/studyos.py doctor` checks local readiness without modifying files.
- `studyos-import` proposes safe import, stops for approval, executes approved copy actions, then creates inventory and the first-pass batch plan from metadata.
- `studyos-plan` refines that first-pass plan into conceptual lectures, topics, modules, or tutorials before processing.
- `studyos-batch` processes one selected conceptual batch into digest, learning core, configured outputs, review updates, and integrated visual screening.
- `studyos-validate` validates batch, course, repaired, or merged outputs.
- `studyos-course` processes remaining planned or unprocessed batches sequentially, validates each batch before continuing, and reports processed, skipped, and stopped batches.
- `studyos-merge` merges validated batch outputs into consolidated full-course outputs and the final review pack.
- `studyos-export` exports unmerged and merged study-facing deliverables to PDF when possible, with clean print-ready HTML fallback.

## Recommended Workflow

1. Optionally run `python3 study-os/scripts/studyos.py status` or `python3 study-os/scripts/studyos.py doctor`.
2. Run `studyos-import` proposal mode to create `analysis/inventory/import_plan.md`.
3. Review and approve the import plan.
4. Run `studyos-import` execute mode to copy approved files into `inputs/`.
5. Run `studyos-import` inventory mode to create `analysis/inventory/course_inventory.md` and the first-pass `analysis/inventory/batch_plan.md`.
6. Run `studyos-plan` to refine conceptual batches, source assignments, dependencies, and any `Unassigned / needs review` entries.
7. Run `studyos-batch` for one selected conceptual batch.
8. Run `studyos-validate`.
9. Run `studyos-course` if you want remaining planned or unprocessed batches processed sequentially with validation after each batch.
10. Run `studyos-merge` when batch outputs are processed and validated.
11. Run `studyos-export`.

Review `analysis/inventory/import_plan.md` before import execute. Do not continue with execute mode unless the proposed copies are acceptable.

`studyos-import` full flow runs proposal first if no plan exists, then stops for approval. It must not silently execute without an approved plan.

## Common Missing-Step Warnings

- Missing `subject.yaml` or `study-os/`: install StudyOS first.
- Missing `raw_source.path`: complete approved setup before importing.
- Missing import plan: run `studyos-import` proposal mode.
- Empty `inputs/`: run `studyos-import` proposal mode, approve the plan, then run execute mode.
- Missing `batch_plan.md`: run `studyos-import` inventory mode, then `studyos-plan`.
- Random file-level or exercise-only batches in `batch_plan.md`: run `studyos-plan` before processing.
- Missing digest, learning core, or outputs: run `studyos-batch`.
- Missing validation reports: run `studyos-validate`.
- Missing merged outputs: run `studyos-merge`.

## Output Locations

- Batch digests: `analysis/batches/<batch>_digest.md`
- Batch learning cores: `analysis/batches/<batch>_learning_core.md`
- Batch visual notes: `analysis/visual/<batch>_visual_notes.md` when visual findings exist
- Validation notes: `analysis/validation/`
- Notes: `outputs/notes/`
- Formula sheets: `outputs/formulas/`
- Flashcards: `outputs/flashcards/`
- Exam questions: `outputs/questions/`
- Cheat sheets: `outputs/cheat-sheets/`
- Study plans: `outputs/study-plan/`
- Final review packs: `outputs/final-pack/`
- Unmerged exports: `exports/pdf/unmerged/notes/`, `exports/pdf/unmerged/formulas/`, `exports/pdf/unmerged/flashcards/`, and `exports/pdf/unmerged/questions/`
- Merged exports: `exports/pdf/merged/`

Batch output files use these names:

- Notes: `outputs/notes/<batch>.md`
- Formula sheets: `outputs/formulas/<batch>_formulas.md` when formulas exist
- Flashcards: `outputs/flashcards/<batch>_flashcards.md`
- Exam questions: `outputs/questions/<batch>_questions.md`

Merged full-course output files use these names:

- Notes: `outputs/notes/full_course_notes.md`
- Formula sheet: `outputs/formulas/full_formula_sheet.md`
- Flashcards: `outputs/flashcards/full_flashcards.md`
- Question bank: `outputs/questions/full_question_bank.md`
- Cheat sheet: `outputs/cheat-sheets/final_cheat_sheet.md`
- Study plan: `outputs/study-plan/full_course_study_plan.md`
- Final review pack: `outputs/final-pack/final_review_pack.md`

`studyos-batch` updates `review/weak-points.md`, `review/unresolved-questions.md`, and `review/visual-issues.md` when visual issues exist.

## Course Processing

`studyos-course` reads `subject.yaml`, `analysis/inventory/batch_plan.md`, optional `analysis/inventory/processing_queue.md`, `analysis/batches/`, `outputs/`, and `review/`. It requires files under `inputs/` and stops if the batch plan is missing.

If no validated batch exists yet, the agent warns:

> Recommended: process and validate one batch manually before full course processing.

The skill identifies planned, unprocessed, stale, or previously failed batches and processes them one batch at a time using `studyos-batch` semantics. Each batch is validated with `studyos-validate` semantics before the next batch starts. Minor localized issues may be repaired and revalidated. Blocking validation issues, missing assigned sources, ambiguous ordering, or unresolved essential visual content stop processing.

Default processing is sequential. Safe parallel processing is allowed only when configured in `subject.yaml`; dependent batches must not be parallelized, digest and learning-core work for the same batch must not be parallelized, and merged validation is required before downstream work continues.

The completion report lists batches processed, batches skipped, stopped batch if any, validation status, unresolved issues, files written, and the recommended next skill: `studyos-merge`.

## Merge Outputs

`studyos-merge` reads validated learning cores from `analysis/batches/*_learning_core.md`, batch outputs from `outputs/notes/Batch_*.md`, `outputs/formulas/Batch_*.md`, `outputs/flashcards/Batch_*.md`, and `outputs/questions/Batch_*.md`, plus `review/weak-points.md`, `review/unresolved-questions.md`, and `review/validation-report.md`.

Merge does not mean concatenate. The skill consolidates duplicate concepts, harmonizes notation, deduplicates formulas, identifies dependencies, preserves source references, prioritizes weak points, includes unresolved questions, includes likely exam questions, carries exam-relevant visual findings, and creates a final 7-day plan plus a last-48-hour plan.

The completion report lists merged outputs created, unresolved issues included, validation or audit recommendations, and the recommended next skill: `studyos-export`.

## Export Outputs

`studyos-export` reads only study-facing Markdown outputs and writes polished exports. It does not export internal analysis files, validation reports, review/debug files, or raw sources by default.

Unmerged batch-level inputs:

- `outputs/notes/Batch_*.md`
- `outputs/formulas/Batch_*.md`
- `outputs/flashcards/Batch_*.md`
- `outputs/questions/Batch_*.md`

Unmerged exports are written by category under:

- `exports/pdf/unmerged/notes/`
- `exports/pdf/unmerged/formulas/`
- `exports/pdf/unmerged/flashcards/`
- `exports/pdf/unmerged/questions/`

Merged full-course inputs:

- `outputs/notes/full_course_notes.md`
- `outputs/formulas/full_formula_sheet.md`
- `outputs/flashcards/full_flashcards.md`
- `outputs/questions/full_question_bank.md`
- `outputs/cheat-sheets/final_cheat_sheet.md`
- `outputs/study-plan/full_course_study_plan.md`
- `outputs/final-pack/final_review_pack.md`

Merged exports are written to `exports/pdf/merged/`.

Run:

```sh
python3 study-os/scripts/export_outputs.py --root .
```

The exporter preserves content and source references. It prefers PDF when `pandoc` and a LaTeX PDF engine are available. If those dependencies are unavailable, it writes print-ready HTML with MathJax support and reports the fallback in `study-os/state/export-log.md`.

## Integrated Visual Screening

Visual screening is part of `studyos-batch`, `studyos-course`, and `studyos-validate`. There is no separate visual skill.

Every batch with slides, PDFs, or images must include Visual Coverage in the digest. If no essential visuals exist, the digest says so explicitly. Essential visuals include formulas, definitions, charts, tables, rankings, benchmark values, model diagrams, process diagrams, and summary visual slides.

`studyos-validate` checks Visual Coverage again. Essential visuals must be analyzed in `analysis/visual/` or explicitly carried into `review/visual-issues.md` or `review/unresolved-questions.md`.

## Validation Outputs

`studyos-validate` reads `analysis/batches/`, `analysis/visual/`, `outputs/`, `review/`, `inputs/`, and `subject.yaml`. It writes validation detail under `analysis/validation/` and review reports under `review/`.

Expected validation reports:

- `review/validation-report.md`
- `review/source-coverage.md`
- `review/visual-issues.md` when visual issues exist
- `review/unresolved-questions.md` when unresolved questions remain

Validation uses severity levels `low`, `medium`, `high`, and `blocking`. Blocking issues stop downstream merge or export until repaired.

## Repair Before Regenerate

When validation finds issues, repair only the affected sections or files. Preserve valid content, do not regenerate unrelated outputs, rerun validation after repair, and leave remaining uncertainty clearly marked.
