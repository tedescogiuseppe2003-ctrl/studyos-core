---
name: studyos-batch
description: Process one selected conceptual StudyOS batch into digest, learning core, and configured study outputs.
---

# Purpose

Process one selected conceptual batch at a time using assigned sources, creating grounded batch-level study material with integrated visual screening.

# When to use

Use after `studyos-plan` when the user selects a specific planned batch to process.

There is no separate visual skill. Visual screening and targeted visual analysis happen inside this skill.

# Preflight checks

- `analysis/inventory/batch_plan.md` exists.
- The user has selected one batch, or the request clearly identifies one batch from `analysis/inventory/batch_plan.md`.
- `analysis/inventory/course_inventory.md` exists.
- At least one file exists under `inputs/`.
- The selected batch exists and has assigned source files under `inputs/`.
- Warn if the selected batch has only exercises and is not marked as tutorial or conceptual.
- Warn if `analysis/inventory/batch_plan.md` or `analysis/inventory/course_inventory.md` shows unassigned files.
- Stop if previous blocking validation issues remain for this batch.

# Reads

- `subject.yaml`
- `analysis/inventory/batch_plan.md`
- `analysis/inventory/course_inventory.md`
- assigned batch sources under `inputs/`
- existing review files when present:
  - `review/weak-points.md`
  - `review/unresolved-questions.md`
  - `review/visual-issues.md`

# Writes

- `analysis/batches/<batch>_digest.md`
- `analysis/batches/<batch>_learning_core.md`
- `analysis/visual/<batch>_visual_notes.md` if visual findings exist
- `outputs/notes/<batch>.md`
- `outputs/formulas/<batch>_formulas.md` if formulas exist
- `outputs/questions/<batch>_questions.md`
- `review/weak-points.md`
- `review/unresolved-questions.md`
- `review/visual-issues.md` if visual issues exist

# Workflow

1. Run preflight checks.
2. Read the selected batch definition, assigned sources, and relevant existing review files.
3. Build a Source Coverage table before generating study outputs.
4. Extract and organize text content from assigned sources.
5. Perform visual screening internally for slides, PDFs, images, screenshots, diagrams, charts, and tables.
6. Perform targeted visual analysis for essential visuals.
7. Create `analysis/batches/<batch>_digest.md`.
8. Create `analysis/batches/<batch>_learning_core.md`.
9. Generate batch outputs from the learning core.
10. Update review files.
11. Stop and recommend validation.

# Required digest sections

Every batch digest must include:

- Batch Processing Plan
- Source Coverage
- Visual Coverage
- Core extracted content
- Definitions
- Formulas
- Important tables/charts/diagrams
- Examples
- Weak points
- Unresolved questions
- Source references

# Visual coverage

Every batch that includes slides, PDFs, or images must include a `Visual Coverage` section in the digest.

If no essential visuals exist, say so explicitly.

Essential visuals include:

- formulas in images
- definitions in images
- charts
- tables
- rankings
- benchmark values
- model diagrams
- process diagrams
- summary visual slides

Write `analysis/visual/<batch>_visual_notes.md` only when visual findings exist. Write `review/visual-issues.md` only when unresolved or questionable visual issues exist.

# Source-type rules

- Slides: primary theory, definitions, formulas, visuals.
- Notes: emphasis, traps, doubts.
- Exercises: practice questions, weak points, exam patterns.
- Readings: theory, assumptions, definitions.
- Exams: exam patterns and answer expectations.
- Transcripts: examples and explanations.

# Model routing and efficiency

- Use model routing from `subject.yaml` and `study-os/config/model-routing.yaml` when available.
- Use balanced reasoning for normal batches.
- Use deep reasoning for formula-heavy batches.
- Use deep reasoning only for the affected visual-essential sections when targeted visual analysis is required.
- Use balanced or deep reasoning for exam questions depending on difficulty and exam relevance.
- Repair affected sections before regenerating entire outputs.
- Avoid rereading unrelated batches.

# Quality rules

- Every substantive claim must trace back to assigned sources.
- Digest comes before learning core; learning core comes before outputs.
- Exercises support practice and weak-point extraction by default, not standalone theory notes.
- Formula outputs include assumptions and source provenance when configured.
- Visual screening is integrated and visual material is not ignored when it carries examinable content.
- Outputs must use `analysis/`, `outputs/`, and `review/` paths only.

# Stop conditions

- Selected batch is missing or ambiguous.
- Assigned sources are missing.
- Required source content is unreadable.
- Grounding, formula, or visual uncertainty is too high to produce reliable outputs.

# Completion report

Report:

- files created or updated
- sources used
- visuals analyzed
- unresolved issues
- recommended next skill: `studyos-validate`
