---
name: studyos-merge
description: Merge validated StudyOS batch outputs into the reduced full-course study output set.
---

# Purpose

Merge validated batch outputs into cleaned, consolidated full-course notes, formula sheet, and exam practice questions.

Merge does not mean concatenate. The skill consolidates overlapping material, harmonizes notation, deduplicates formulas, identifies dependencies, preserves source references, and carries weak points and unresolved questions into the final study material.

Merged output quality is more important than brevity. Full-course outputs may be long when the validated batch material requires it. Save length by deduplicating repeated explanations, not by dropping unique validated concepts, examples, caveats, assumptions, formulas, visuals, weak points, or exam signals.

# When to use

Use after relevant batches have been processed and validated, their learning cores exist, and the course is ready for the reduced full-course output set.

# Preflight checks

- Validated batch outputs exist under `outputs/notes/`, `outputs/formulas/`, and `outputs/questions/`.
- Learning cores exist under `analysis/batches/*_learning_core.md`.
- `review/validation-report.md` exists and covers the included material.
- `review/weak-points.md`, `review/unresolved-questions.md`, `review/visual-issues.md`, and `review/validation-report.md` exist, even if some are empty.
- Require validated batch outputs before merging.
- Warn if some batches are missing notes, formula sheets, or exam practice questions.
- Warn if validation has blocking issues, and do not hide those issues in merged outputs.
- Stop if required learning cores, validated batch outputs, or the validation report are missing.

# Reads

- `subject.yaml`
- `analysis/inventory/batch_plan.md`
- `analysis/batches/*_learning_core.md`
- `outputs/notes/Batch_*.md`
- `outputs/formulas/Batch_*_formulas.md`
- `outputs/questions/Batch_*_questions.md`
- `review/weak-points.md`
- `review/unresolved-questions.md`
- `review/visual-issues.md`
- `review/validation-report.md`

# Writes

- `outputs/notes/full_course_notes.md`
- `outputs/formulas/full_formula_sheet.md`
- `outputs/questions/full_exam_practice_questions.md`

# Does not write

- `outputs/questions/full_question_bank.md`
- `outputs/flashcards/full_flashcards.md`
- `outputs/cheatsheets/final_cheat_sheet.md`
- `outputs/study-plans/full_course_study_plan.md`
- `outputs/review/final_review_pack.md`
- Any other flashcards, cheat sheets, study plans, or final review packs

# Workflow

1. Select validated batch material to include.
2. Build a progressive course-level learning flow from prerequisites to advanced or integrated topics.
3. Consolidate duplicate concepts and reconcile cross-batch terminology without compressing away repaired batch depth.
4. Harmonize notation, assumptions, dependencies, and prerequisites across the course.
5. Deduplicate formulas while preserving formula provenance and source references.
6. Carry weak points into the relevant notes and questions instead of isolating them only in a review list.
7. Include unresolved issues where relevant and keep them visibly labeled.
8. Include exam-relevant visual findings from `review/visual-issues.md` in the affected notes or questions.
9. Create only the full-course notes, formula sheet, and exam practice questions.
10. Recommend audit review of the merged outputs when validation depth or exam risk warrants it.

# Model routing and efficiency

- Use deep reasoning for rigorous mode.
- Use balanced or deep reasoning for standard mode, escalating to deep for formula consistency, dependencies, and exam-critical prioritization.
- Audit review is recommended for the merged outputs.
- Do not reread raw sources unless validated intermediates are insufficient.
- Use validated learning cores and batch outputs as the main context to save tokens.
- Reread raw sources only for unresolved conflicts, missing provenance, formula ambiguity, visual uncertainty, or validation findings that cannot be repaired from intermediates.
- Merge in passes: dependency map first, duplicate concepts second, notation/formulas third, exam practice fourth, source-reference audit last.
- Prefer targeted repair of the affected merged section over regenerating all merged outputs.

# Quality rules

- Use merge language, not the older consolidation wording, in user-facing reports.
- Merged outputs are based on validated intermediates.
- Preserve traceability to sources and batches.
- Do not hide unresolved questions or weak points.
- Include unresolved questions where they affect concepts, formulas, assumptions, or exam preparation.
- Include likely exam questions and answer expectations.
- Include key visual findings when exam-relevant.
- Final outputs should be cohesive full-course deliverables, not batch files pasted together.
- Preserve the repaired depth and batch-level completeness of batch notes.
- Do not compress the merged notes into a short summary.
- Completeness beats brevity in merged outputs; save tokens by avoiding duplicated explanations, not by dropping unique source-grounded concepts.
- Do not mark the merge complete until every included batch has a visible contribution, a deduplicated counterpart, or an explicit reason for exclusion.
- Do not compress the full course into an executive summary or high-level review when the validated batch material contains detailed examinable content.

# Merged notes requirements

- Write `outputs/notes/full_course_notes.md`.
- Produce full-course study notes, not a summary or pasted batch bundle.
- Preserve batch-level completeness and repaired depth.
- Add transitions between topics.
- Include a dependency map.
- Consolidate duplicate concepts while preserving nuance and source references.
- Harmonize terminology and notation.
- Include weak points inside the relevant topic sections.
- Include unresolved issues and exam-relevant visual findings where they affect the material.

# Merged formula sheet requirements

- Write `outputs/formulas/full_formula_sheet.md`.
- Consolidate all formulas from validated batch formula sheets and learning cores.
- Deduplicate equivalent formulas.
- Use display LaTeX for every formula.
- Include a formula index and notation section.
- For each formula, include variables, assumptions, interpretation, common mistakes, and sources.
- Harmonize notation across the whole course and flag any unresolved notation conflicts.

# Merged exam practice questions requirements

- Write `outputs/questions/full_exam_practice_questions.md`.
- Combine and organize validated batch questions.
- Group questions by topic and difficulty.
- Include expected answers or solution outlines.
- Preserve source references.
- Include weak-point and common-trap questions where relevant.
- Add exam-style integrated questions where useful for cross-topic preparation.

# Stop conditions

- Required validated batch outputs are missing.
- Required learning cores are missing.
- `review/validation-report.md` is missing.
- Blocking validation issues make the requested merge unreliable.
- Source coverage is too incomplete to merge reliably.

# Completion report

Report:

- merged notes path: `outputs/notes/full_course_notes.md`
- merged formula sheet path: `outputs/formulas/full_formula_sheet.md`
- merged questions path: `outputs/questions/full_exam_practice_questions.md`
- included batches/material
- unresolved warnings, including missing batch outputs or blocking validation warnings
- validation or audit recommendations
- recommended next skill: `studyos-export`
