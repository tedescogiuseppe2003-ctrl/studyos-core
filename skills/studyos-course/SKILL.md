---
name: studyos-course
description: Process remaining planned or unprocessed StudyOS batches sequentially, validating each batch before continuing.
---

# Purpose

Process remaining planned or unprocessed batches across the course while preserving batch boundaries.

This skill is a controlled sequential runner for batch work. It must not process the whole course as one giant batch, must not skip validation, and must stop when blocking validation or essential unresolved visual content prevents safe continuation.

Final batch outputs are limited to batch notes, batch formula sheets, and batch exam practice questions. Digest, learning core, visual notes, validation files, and review files remain internal process evidence.

The course runner prioritizes output quality and exhaustive assigned-input coverage over speed. Time and token optimization may reduce duplicated work, but it must not reduce source coverage, notes depth, formula completeness, visual handling, or exam-question quality.

# When to use

Use when the user wants remaining planned, unprocessed, stale, or previously failed batches handled in order after import and planning are complete.

# Preflight checks

- `analysis/inventory/batch_plan.md` exists.
- At least one file exists under `inputs/`.
- `analysis/inventory/processing_queue.md` may be used when present to determine execution order.
- Assigned source files for each candidate batch exist under `inputs/`.
- Existing validation reports and review files do not contain unresolved blocking issues for prerequisite material.
- Warn if no validated batch exists yet:
  `Recommended: process and validate one batch manually before full course processing.`

Stop before processing when `batch_plan.md` is missing, `inputs/` is empty, assigned source files are missing for the next batch, the batch plan is ambiguous enough to make ordering unsafe, or a blocking validation issue is already present.

# Reads

- `subject.yaml`
- `analysis/inventory/batch_plan.md`
- `analysis/inventory/processing_queue.md`, if present
- `analysis/batches/`
- `outputs/`
- `review/`
- assigned source files under `inputs/`

# Writes

- batch digests and learning cores under `analysis/batches/`
- visual notes under `analysis/visual/`
- validation details under `analysis/validation/`
- notes under `outputs/notes/`
- formula sheets under `outputs/formulas/`
- exam questions under `outputs/questions/`
- review updates under `review/`
- `review/progress-tracker.md`
- optional processing state under `study-os/state/`

Do not write flashcards, cheat sheets, study plans, final review packs, or deprecated output folders for those formats.

# Workflow

1. Run preflight checks.
2. Read `analysis/inventory/batch_plan.md`.
3. Read `analysis/inventory/processing_queue.md` when present.
4. Identify planned, unprocessed, stale, or previously failed batches.
5. For each batch, in dependency-safe order:
   - run the `studyos-batch` workflow conceptually for that batch;
   - create or update internal digest, learning core, and visual notes;
   - create or update only the final batch notes, batch formula sheet when relevant, and batch exam practice questions;
   - validate the batch with `studyos-validate` semantics;
   - repair minor localized issues when appropriate;
   - revalidate repaired files before continuing;
   - stop on blocking issues or insufficient source coverage, formula quality, notes depth, or essential visual coverage.
6. Update review files and progress state after each validated batch.
7. Report processed, skipped, and stopped batches.

Do not create merged final outputs. Full-course consolidation belongs to `studyos-merge`.

# Batch selection

- Planned batches are batches listed in `batch_plan.md` with a processable status.
- Unprocessed batches are planned batches with missing digest, learning core, batch notes, required formula sheet, exam practice questions, or validation records.
- Stale batches are batches whose assigned sources, digest, learning core, batch notes, formula sheet, exam practice questions, or validation records appear newer or inconsistent with existing validation.
- Failed batches are batches with prior validation issues that are not blocking and can be repaired locally.
- Skip batches that are already processed and validated, unless their sources or reduced-scope outputs are stale.

# Model routing and efficiency

- Reuse existing digests, learning cores, and validation results when current.
- Use deeper reasoning for technical, formula-heavy, or visually dense batches.
- Spend saved effort from the reduced output scope on notes depth, formula quality, exam-question quality, source coverage, and essential visual coverage.
- Use targeted repair for affected files or sections instead of regenerating unrelated outputs.
- Avoid processing the whole course as one giant context.
- Maintain a per-batch processing ledger in `review/progress-tracker.md` with processed, skipped, repaired, validation status, unresolved issues, and next dependency.
- For each batch, load only the selected batch sources plus prior validated dependency summaries unless cross-batch reasoning is required.
- Prefer shallow rereads for already validated dependency batches and deep rereads only when notation, assumptions, formulas, or exam integration depend on them.
- Stop and repair early when one batch fails validation instead of letting defects propagate to later batches.

# Parallelism

- Default to sequential processing.
- Use parallelism only when `subject.yaml` explicitly enables safe parallel batches.
- Do not use aggressive parallelism by default.
- Do not parallelize dependent batches.
- Do not parallelize digest creation and learning-core generation for the same batch.
- Validate and merge validation findings from all parallel branches before any downstream batch continues.

# Quality rules

- Preserve batch boundaries.
- Do not skip validation between batches.
- Do not continue if source coverage, formula quality, notes depth, or essential visual coverage is insufficient.
- Outputs must be grounded in validated batch material and assigned sources.
- Do not modify protected raw files or files under `inputs/`.
- Do not create merged final outputs; that belongs to `studyos-merge`.
- The course run is complete only when every planned batch is processed, skipped with a concrete reason, or blocked with a visible unresolved issue.
- Token and time optimization must never mean omitting an assigned source from Source Coverage or final output consideration.
- Long batch outputs are acceptable when the planned source material requires them.
- A batch is not complete if it is merely concise; it is complete only when all assigned inputs have been exhausted or explicitly justified as duplicate, irrelevant, unreadable, or deferred.

# Stop conditions

- Batch plan is missing or ambiguous.
- `inputs/` is empty.
- Assigned source files are missing.
- A batch fails validation with blocking issues.
- Source coverage is insufficient for assigned material.
- Formula quality or provenance is insufficient for formula-heavy material.
- Notes depth is insufficient for exam-useful study notes.
- Essential visual content is unresolved and blocking.
- Essential visual coverage is insufficient for slide, PDF, or image sources.
- The work would require modifying protected raw files or `inputs/`.

# Completion report

Report:

- batches processed
- batches skipped
- blocking issues and stopped batch, if any
- notes, formula sheets, and exam practice questions created
- validation status
- unresolved issues
- files written
- recommended next skill: `studyos-merge`
