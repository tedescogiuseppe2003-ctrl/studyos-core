---
name: studyos-validate
description: Validate StudyOS batch, course, or merged outputs for structure, grounding, citations, formulas, and visual coverage.
---

# Purpose

Validate generated StudyOS outputs before more work builds on them. The skill checks structure, source grounding, formulas, output usefulness, weak points, unresolved questions, and visual coverage, then identifies targeted repairs.

# When to use

Use after `studyos-batch`, after course-level output generation, after repairs, and after `studyos-merge` when merged outputs need audit.

# Preflight checks

- `subject.yaml` exists.
- `study-os/scripts/validate_outputs.py`, `study-os/scripts/validate_citations.py`, and `study-os/scripts/validate_formulas.py` exist.
- At least one processed batch file exists under `analysis/batches/` or at least one generated output exists under `outputs/`.
- Referenced source files exist under `inputs/`.
- Warn and stop if nothing has been processed. Run `studyos-batch`, `studyos-course`, or `studyos-merge` first.

# Reads

- `subject.yaml`
- `analysis/batches/`
- `analysis/visual/`
- `outputs/`
- `review/`
- `inputs/`
- `analysis/inventory/batch_plan.md` when validating batch-aware coverage

# Writes

- `analysis/validation/`
- `review/validation-report.md`
- `review/source-coverage.md`
- `review/visual-issues.md` when visual coverage issues exist
- `review/unresolved-questions.md` when unanswered validation questions remain
- updates to `review/weak-points.md` when validation finds weak or fragile areas

# Workflow

1. Identify the validation target: one batch, course-level outputs, repaired outputs, or merged outputs.
2. Confirm preflight. Use `analysis/batches/` for batch-aware validation and `outputs/notes`, `outputs/formulas`, and `outputs/questions` for generated outputs.
3. Run deterministic structural checks with `python3 study-os/scripts/validate_outputs.py`.
4. Run citation/source checks with `python3 study-os/scripts/validate_citations.py`.
5. Run formula field checks with `python3 study-os/scripts/validate_formulas.py` when formula outputs exist or the course is formula-heavy.
6. Perform LLM quality review according to `subject.yaml` validation depth.
7. Perform visual coverage review for any batch with slide, PDF, or image sources.
8. Classify each issue with severity: `low`, `medium`, `high`, or `blocking`.
9. Recommend targeted repairs before broad regeneration.

# Validation layers

1. Deterministic structural checks.
2. Citation and source checks.
3. Formula field checks.
4. LLM quality review.
5. Visual coverage review.

# Required checks

- Required files and folders exist.
- Outputs are not empty.
- Formula entries include required fields.
- Source references are meaningful and resolve to `inputs/`.
- `review/source-coverage.md` exists after validation.
- Visual Coverage exists for batches with slide, PDF, or image inputs.
- Essential visuals are either analyzed in `analysis/visual/` or explicitly listed as unresolved in `review/visual-issues.md` or `review/unresolved-questions.md`.
- Exam questions include expected answers, answer keys, or worked solutions.
- Exercises are integrated as practice, not rewritten as fake theory.
- Unsupported claims are flagged.
- Weak points are captured and carried into `review/weak-points.md`.

# Batch-aware validation

For a selected batch, inspect the batch digest and outputs together:

- `analysis/batches/<batch>_digest.md`
- `analysis/batches/<batch>_learning_core.md`
- `analysis/visual/<batch>_visual_notes.md` when visual findings exist
- `outputs/notes/<batch>.md`
- `outputs/formulas/<batch>_formulas.md` when formulas exist
- `outputs/questions/<batch>_questions.md`

The digest must include Source Coverage. If assigned sources include slides, PDFs, or images, the digest must also include Visual Coverage. If no essential visuals exist, that must be stated explicitly.

# Model routing and efficiency

- Use scripts for deterministic checks.
- Use fast reasoning for simple structural review.
- Use deeper reasoning for grounding, unsupported-claim review, formula consistency, visual coverage, weak-point capture, and exam-usefulness audits.

# Quality rules

- Validation does not silently rewrite outputs.
- Blocking issues stop downstream work.
- Prefer targeted repair.
- Do not regenerate unrelated outputs.
- Preserve valid content.
- Rerun validation after repair.
- Remaining uncertainty must be visible in review files.

# Stop conditions

- No validation target exists.
- Required source files are absent.
- Validation scripts are absent.
- Citations or formulas cannot be checked because required metadata is missing.
- Severe grounding issues require repair before continuing.

# Completion report

Report validation status, blocking issues, high-priority fixes, minor fixes, files written, and the recommended next skill after repair or approval.
