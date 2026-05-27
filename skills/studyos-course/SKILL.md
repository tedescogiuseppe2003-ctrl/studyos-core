---
name: studyos-course
description: Process remaining planned or unprocessed StudyOS batches sequentially, validating each batch before continuing.
---

# Purpose

Process remaining planned or unprocessed batches across the course while preserving batch boundaries.

This skill is a controlled sequential runner for batch work. It must not process the whole course as one giant batch, must not skip validation, and must stop when blocking validation or essential unresolved visual content prevents safe continuation.

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
- flashcards under `outputs/flashcards/`
- exam questions under `outputs/questions/`
- review updates under `review/`
- `review/progress-tracker.md`
- optional processing state under `study-os/state/`

# Workflow

1. Run preflight checks.
2. Read `analysis/inventory/batch_plan.md`.
3. Read `analysis/inventory/processing_queue.md` when present.
4. Identify planned, unprocessed, stale, or previously failed batches.
5. For each batch, in dependency-safe order:
   - run the `studyos-batch` workflow conceptually for that batch;
   - create or update digest, learning core, visual notes, and configured outputs;
   - validate the batch with `studyos-validate` semantics;
   - repair minor localized issues when appropriate;
   - revalidate repaired files before continuing;
   - stop on blocking issues.
6. Update review files and progress state after each validated batch.
7. Report processed, skipped, and stopped batches.

Do not create merged final outputs. Full-course consolidation belongs to `studyos-merge`.

# Batch selection

- Planned batches are batches listed in `batch_plan.md` with a processable status.
- Unprocessed batches are planned batches with missing digest, learning core, outputs, or validation records.
- Stale batches are batches whose assigned sources, digest, learning core, or outputs appear newer or inconsistent with existing validation.
- Failed batches are batches with prior validation issues that are not blocking and can be repaired locally.
- Skip batches that are already processed and validated, unless their sources or outputs are stale.

# Model routing and efficiency

- Reuse existing digests, learning cores, and validation results when current.
- Use deeper reasoning for technical, formula-heavy, or visually dense batches.
- Avoid processing the whole course as one giant context.

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
- Do not continue if essential visual content is unresolved and blocking.
- Outputs must be grounded in validated batch material.
- Do not modify protected raw files or files under `inputs/`.
- Do not create merged final outputs; that belongs to `studyos-merge`.

# Stop conditions

- Batch plan is missing or ambiguous.
- `inputs/` is empty.
- Assigned source files are missing.
- A batch fails validation with blocking issues.
- Essential visual content is unresolved and blocking.
- The work would require modifying protected raw files or `inputs/`.

# Completion report

Report:

- batches processed
- batches skipped
- stopped batch, if any
- validation status
- unresolved issues
- files written
- recommended next skill: `studyos-merge`
