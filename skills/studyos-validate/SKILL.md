---
name: studyos-validate
description: Validate StudyOS batch, course, or merged outputs for structure, grounding, citations, formulas, and visual coverage.
---

# Purpose

Check StudyOS outputs before more work builds on them, and identify targeted repairs.

# When to use

Use after `studyos-batch`, after course-level output generation, after repairs, and after `studyos-merge` when merged outputs need audit.

# Preflight checks

- Relevant output files exist.
- Referenced sources exist under `inputs/`.
- Validation scripts exist under `study-os/scripts/`.
- Stop if there is no processed material to validate.

# Reads

- `subject.yaml`
- `analysis/inventory/batch_plan.md`
- `analysis/batches/`
- `analysis/visual/`
- `outputs/`
- `inputs/`
- existing `review/` files

# Writes

- `review/validation-report.md`
- `review/source-coverage.md`
- `review/formula_validation_report.md`
- validation notes under `analysis/validation/`
- updates to weak points and unresolved questions when validation finds gaps

# Workflow

1. Identify the validation target: one batch, course-level outputs, repaired outputs, or merged outputs.
2. Run deterministic structure, citation, and formula checks where applicable.
3. Check that claims, formulas, and visual references are grounded in source material.
4. Apply the configured validation depth for LLM review.
5. Classify issues as blocking, repairable, or informational.
6. Recommend targeted repairs before any broad regeneration.

# Model routing and efficiency

- Use scripts for deterministic checks.
- Use fast reasoning for simple structural review.
- Use deeper reasoning for grounding, formula consistency, visual coverage, and exam-usefulness audits.

# Quality rules

- Validation does not silently rewrite outputs.
- Blocking issues stop downstream work.
- Repairs should patch affected sections only and preserve valid content.
- Remaining uncertainty must be visible in review files.

# Stop conditions

- No validation target exists.
- Required source files are absent.
- Citations or formulas cannot be checked because required metadata is missing.
- Severe grounding issues require repair before continuing.

# Completion report

Report validation target, checks run, files written, blocking issues, recommended repairs, and the next skill to run after repair or approval.
