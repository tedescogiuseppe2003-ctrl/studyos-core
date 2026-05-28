---
name: studyos-validate
description: Validate StudyOS batch, course, or merged outputs for structure, grounding, citations, formulas, and visual coverage.
---

# Purpose

Validate generated StudyOS material before more work builds on it. The final study-facing validation scope is limited to notes, formula sheets, and exam practice questions. Digest, learning core, source coverage, and visual coverage are checked as internal quality-support evidence.

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
2. Confirm preflight. Use `analysis/batches/` for batch-aware validation and `outputs/notes`, `outputs/formulas`, and `outputs/questions` for the only final study-facing outputs.
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

Do not require or validate removed final outputs: flashcards, cheat sheets, study plans, or final review packs.

## Notes

- Notes file exists when expected for a processed batch or merged course output.
- Notes are not empty.
- Required sections exist: Scope, Core Notes, Definitions, Examples, Formula Intuition, Exam Relevance, Common Mistakes, Weak Points, and Source References.
- Standard and rigorous modes warn when notes are approximately too short for the batch.
- Notes are complete study notes, not merely compressed summaries.
- Source references are present and usable.
- Exam-relevant visual findings are included when visual material is relevant.

## Formulas

- Formula sheet exists when formulas, notation, quantitative assumptions, or formula-like rules are relevant.
- Display LaTeX exists.
- Formulas are not only inline code or plain ASCII.
- Formula Index exists.
- Notation section exists.
- Each formula entry includes Formula, Variables, Assumptions, Use when, Interpretation, Common mistake, and Source.

## Questions

- Question file exists when expected.
- Expected answers, answer keys, or worked solutions are included.
- Questions are grouped by topic or concept.
- Questions include conceptual and exam-style prompts.
- Formula-heavy batches include formula/application/calculation questions.
- Assigned exercises are reflected as practice questions where relevant.
- Source references or topic references exist.

## Internal support

- Digest exists for processed batches and includes Source Coverage.
- Deterministically compare assigned primary and supporting sources in `analysis/inventory/batch_plan.md` against each batch digest Source Coverage table.
- Every assigned source must appear in Source Coverage with status `used`, `partially used`, `unreadable`, `irrelevant`, `duplicate`, or `deferred`.
- Sources marked `unreadable`, `irrelevant`, `duplicate`, or `deferred` require a concrete reason.
- Digest includes Visual Coverage when assigned sources include slides, PDFs, images, charts, tables, diagrams, or screenshots. If no essential visuals exist, it says so explicitly.
- Learning core exists and is not over-compressed relative to the digest.
- Source references are meaningful and resolve to `inputs/`.
- `review/source-coverage.md` exists after validation.
- Essential visuals are either analyzed in `analysis/visual/` or explicitly listed as unresolved in `review/visual-issues.md` or `review/unresolved-questions.md`.
- Unresolved visual or formula issues are tracked in review files.
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

Source Coverage validation must identify the batch, source path, source role, status, missing reason when applicable, severity, and recommended repair. Missing primary source coverage is high or blocking. Missing supporting source coverage is medium or high depending on role and exam relevance. Deferred without a reason is high. Duplicate or irrelevant with a clear reason is low or medium and should remain visible in `review/source-coverage.md`.

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

Report notes status, formulas status, questions status, source coverage status, visual coverage status, blocking issues, high-priority fixes, minor fixes, files written, and the recommended repair target. Recommend the next skill only after blocking issues are repaired or explicitly carried as unresolved.
