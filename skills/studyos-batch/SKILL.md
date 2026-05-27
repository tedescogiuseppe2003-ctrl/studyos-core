---
name: studyos-batch
description: Process one planned StudyOS batch into digest, learning core, and configured study outputs.
---

# Purpose

Process one conceptual batch at a time using assigned sources, creating grounded batch-level study material.

# When to use

Use after `studyos-plan` when the user selects a specific planned batch to process.

# Preflight checks

- `analysis/inventory/course_inventory.md` exists.
- `analysis/inventory/batch_plan.md` exists.
- The selected batch exists and has assigned source files.
- Assigned source files exist under `inputs/`.
- Stop if previous blocking validation issues remain for this batch.

# Reads

- `subject.yaml`
- `analysis/inventory/course_inventory.md`
- `analysis/inventory/batch_plan.md`
- assigned batch sources under `inputs/`
- relevant prior validation or weak-point notes

# Writes

- source digest under `analysis/batches/`
- learning core under `analysis/batches/`
- configured batch outputs under `outputs/`
- visual notes under `analysis/visual/`, when relevant
- updates to `review/weak-points.md` and `review/unresolved-questions.md`

# Workflow

1. Confirm the selected batch and assigned sources.
2. Read the assigned sources and create a source digest with source coverage.
3. Screen diagrams, charts, tables, screenshots, and formulas according to configured depth.
4. Create the learning core from the digest.
5. Generate requested batch outputs: notes, formulas, flashcards, questions, cheat sheets, or study-plan fragments.
6. Record weak points, unresolved questions, and source coverage.
7. Stop and recommend validation.

# Model routing and efficiency

- Use fast reasoning for formatting, simple extraction, and obvious source roles.
- Use deeper reasoning for dense theory, formulas, visual interpretation, derivations, and exam-critical integration.
- Avoid rereading unrelated batches.

# Quality rules

- Every substantive claim must trace back to assigned sources.
- Digest comes before learning core; learning core comes before outputs.
- Exercises support practice and weak-point extraction by default, not standalone theory notes.
- Formula outputs include assumptions and source provenance when configured.
- Visual material is not ignored when it carries examinable content.

# Stop conditions

- Selected batch is missing or ambiguous.
- Assigned sources are missing.
- Required source content is unreadable.
- Grounding, formula, or visual uncertainty is too high to produce reliable outputs.

# Completion report

Report the processed batch, sources used, files written, weak points, unresolved questions, and the next recommended skill: `studyos-validate`.
