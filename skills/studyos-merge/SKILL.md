---
name: studyos-merge
description: Merge validated StudyOS batch outputs into consolidated full-course study material.
---

# Purpose

Merge validated batch outputs into cleaned, consolidated full-course outputs.

Merge does not mean concatenate. The skill consolidates overlapping material, harmonizes notation, deduplicates formulas, identifies dependencies, preserves source references, and carries weak points and unresolved questions into the final study material.

# When to use

Use after relevant batches have been processed and validated, their learning cores exist, and the course is ready for full-course outputs.

# Preflight checks

- Validated batch outputs exist under `outputs/notes/`, `outputs/formulas/`, `outputs/flashcards/`, and `outputs/questions/`.
- Learning cores exist under `analysis/batches/*_learning_core.md`.
- `review/validation-report.md` exists and covers the included material.
- `review/weak-points.md` and `review/unresolved-questions.md` exist, even if empty.
- Warn if unresolved blocking issues exist and do not hide them in merged outputs.
- Stop if required learning cores, validated batch outputs, or the validation report are missing.

# Reads

- `subject.yaml`
- `analysis/inventory/batch_plan.md`
- `analysis/batches/*_learning_core.md`
- `outputs/notes/Batch_*.md`
- `outputs/formulas/Batch_*.md`
- `outputs/flashcards/Batch_*.md`
- `outputs/questions/Batch_*.md`
- `review/weak-points.md`
- `review/unresolved-questions.md`
- `review/validation-report.md`
- `review/source-coverage.md`
- `review/visual-issues.md` when present

# Writes

- `outputs/notes/full_course_notes.md`
- `outputs/formulas/full_formula_sheet.md`
- `outputs/flashcards/full_flashcards.md`
- `outputs/questions/full_question_bank.md`
- `outputs/cheat-sheets/final_cheat_sheet.md`
- `outputs/study-plan/full_course_study_plan.md`
- `outputs/final-pack/final_review_pack.md`

# Workflow

1. Select validated batch material to include.
2. Consolidate duplicate concepts and reconcile cross-batch terminology.
3. Harmonize notation, assumptions, dependencies, and prerequisites.
4. Deduplicate formulas and keep formula provenance and source references.
5. Prioritize weak points, unresolved questions, likely exam questions, and exam-relevant visual findings.
6. Create the full-course notes, formula sheet, flashcards, question bank, cheat sheet, study plan, and final review pack.
7. Include a final 7-day plan and a last-48-hour plan.
8. Recommend audit review of the final merged pack when validation depth or exam risk warrants it.

# Model routing and efficiency

- Use deep reasoning for rigorous mode.
- Use balanced or deep reasoning for standard mode, escalating to deep for formula consistency, dependencies, and exam-critical prioritization.
- Audit review is recommended for the final merged pack.
- Do not reread raw sources unless validated intermediates are insufficient.

# Quality rules

- Use merge language, not the older consolidation wording, in user-facing reports.
- Merged outputs are based on validated intermediates.
- Preserve traceability to sources and batches.
- Do not hide unresolved questions or weak points.
- Include unresolved questions in the merged outputs and final review pack.
- Include likely exam questions and answer expectations.
- Include key visual findings when exam-relevant.
- Final outputs should be cohesive full-course deliverables, not batch files pasted together.

# Stop conditions

- Required validated batch outputs are missing.
- Required learning cores are missing.
- `review/validation-report.md` is missing.
- Blocking validation issues make the requested merge unreliable.
- Source coverage is too incomplete to merge reliably.

# Completion report

Report merged outputs created, included batches/material, unresolved issues included, validation or audit recommendations, and the next recommended skill: `studyos-export`.
