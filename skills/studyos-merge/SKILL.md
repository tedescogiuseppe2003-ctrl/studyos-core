---
name: studyos-merge
description: Merge validated StudyOS batch and course outputs into consolidated full-course study material.
---

# Purpose

Create cleaned, consolidated full-course outputs from validated batch and course material.

# When to use

Use after relevant batches and course-level outputs have been processed and validated.

# Preflight checks

- Validated batch learning cores or course outputs exist.
- `review/validation-report.md` has no unresolved blocking issues for included material.
- Source coverage and unresolved questions are available.
- Stop if the course is not sufficiently processed for the requested merged output.

# Reads

- `subject.yaml`
- `analysis/inventory/batch_plan.md`
- validated learning cores under `analysis/batches/`
- course-level outputs under `outputs/`
- `review/validation-report.md`
- `review/source-coverage.md`
- `review/weak-points.md`
- `review/unresolved-questions.md`

# Writes

- merged notes under `outputs/notes/`
- merged formula sheets under `outputs/formulas/`
- merged flashcards under `outputs/flashcards/`
- merged questions under `outputs/questions/`
- merged cheat sheets under `outputs/cheat-sheets/`
- merged study plans under `outputs/study-plan/`
- final review pack under `outputs/final-pack/`

# Workflow

1. Select validated material to include.
2. Merge overlapping concepts across batches.
3. Remove duplication while preserving source references and important nuance.
4. Consolidate formulas, assumptions, weak points, and unresolved questions.
5. Create the requested merged outputs and final review pack.
6. Recommend validation of merged outputs.

# Model routing and efficiency

- Use fast reasoning for deduplication and formatting when material is straightforward.
- Use deeper reasoning for cross-batch integration, formula consistency, and exam-critical prioritization.
- Do not reread raw sources unless validated intermediates are insufficient.

# Quality rules

- Use merge language, not synthesis language, in user-facing reports.
- Merged outputs are based on validated intermediates.
- Preserve traceability to sources and batches.
- Do not hide unresolved questions or weak points.

# Stop conditions

- Required validated material is missing.
- Blocking validation issues remain.
- Source coverage is too incomplete to merge reliably.

# Completion report

Report included batches/material, merged files written, unresolved issues carried forward, and the next recommended skill: `studyos-validate` or `studyos-export`.
