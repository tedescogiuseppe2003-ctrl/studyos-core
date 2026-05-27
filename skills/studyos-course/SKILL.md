---
name: studyos-course
description: Process remaining StudyOS batches sequentially and create course-level outputs without merging the final course pack.
---

# Purpose

Continue batch processing across the course and create course-level outputs while preserving batch boundaries.

# When to use

Use after at least one batch has been processed and validated successfully, when the user wants to process remaining planned batches.

# Preflight checks

- `analysis/inventory/batch_plan.md` exists and has planned or stale batches.
- At least one representative batch has passed validation, unless the user explicitly accepts the risk.
- Assigned source files exist under `inputs/`.
- Stop on unresolved blocking validation issues.

# Reads

- `subject.yaml`
- `analysis/inventory/course_inventory.md`
- `analysis/inventory/batch_plan.md`
- existing batch digests and learning cores
- validation reports and review files
- assigned sources under `inputs/`

# Writes

- additional batch digests and learning cores under `analysis/batches/`
- configured unmerged outputs under `outputs/`
- course-level outputs under `outputs/`
- visual notes under `analysis/visual/`
- validation handoff notes under `analysis/validation/`
- `review/progress-tracker.md`

# Workflow

1. Identify remaining planned, stale, or failed batches.
2. Process batches sequentially using `studyos-batch` semantics.
3. Validate each batch with `studyos-validate` semantics before moving to the next.
4. Repair minor issues locally when appropriate and revalidate.
5. Stop on severe issues.
6. Create requested course-level outputs from validated batch material without merging the final full-course pack.

# Model routing and efficiency

- Reuse existing digests, learning cores, and validation results when current.
- Use deeper reasoning for technical, formula-heavy, or visually dense batches.
- Avoid processing the whole course as one giant context.

# Quality rules

- Preserve batch boundaries.
- Do not skip validation between batches.
- Course-level outputs must be grounded in validated batch material.
- Do not create merged final outputs; that belongs to `studyos-merge`.

# Stop conditions

- Batch plan is missing or ambiguous.
- Assigned source files are missing.
- A batch fails validation with blocking issues.
- The work would require modifying protected raw files or `inputs/`.

# Completion report

Report batches processed, batches skipped, validation status, files written, remaining issues, and the next recommended skill: `studyos-merge`.
