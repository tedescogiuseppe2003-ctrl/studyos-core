---
name: studyos-export
description: Export StudyOS unmerged and merged outputs to PDF deliverables.
---

# Purpose

Create exportable PDF deliverables for both unmerged batch-level material and merged full-course material.

# When to use

Use after the desired batch, course, or merged outputs exist and have been validated to the user’s required depth.

# Preflight checks

- Output files exist under `outputs/`.
- `exports/pdf/unmerged/` and `exports/pdf/merged/` exist.
- Export scripts or local PDF tooling are available.
- Stop if no eligible outputs exist.

# Reads

- `subject.yaml`
- unmerged batch and course outputs under `outputs/`
- merged outputs under `outputs/`
- validation and source-coverage reports under `review/`

# Writes

- unmerged PDFs under `exports/pdf/unmerged/`
- merged PDFs under `exports/pdf/merged/`
- optional export log under `study-os/state/`

# Workflow

1. Identify eligible unmerged batch/course outputs.
2. Identify eligible merged full-course outputs from `studyos-merge`.
3. Export unmerged material while preserving batch boundaries.
4. Export merged material as consolidated deliverables.
5. Record skipped files and export failures.

# Model routing and efficiency

- Use scripts or deterministic tooling for PDF generation.
- Use fast reasoning for file selection and export reporting.
- Do not use deep reasoning unless export readiness depends on interpreting validation findings.

# Quality rules

- Unmerged exports preserve batch boundaries.
- Merged exports represent cleaned full-course outputs.
- Do not export stale or clearly failed outputs without warning.
- Do not modify source outputs during export.

# Stop conditions

- No eligible outputs exist.
- Required export tooling is unavailable.
- Validation reports show blocking issues for requested deliverables.

# Completion report

Report exported unmerged PDFs, exported merged PDFs, skipped outputs, failures, and export folders.
