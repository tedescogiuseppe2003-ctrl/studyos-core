---
name: studyos-plan
description: Refine the initial StudyOS conceptual batch plan before batch processing.
---

# Purpose

Review and improve `analysis/inventory/batch_plan.md` so batches represent coherent course concepts and have the right supporting sources.

# When to use

Use after `studyos-import` creates the first inventory and batch plan, and before `studyos-batch` starts processing.

# Preflight checks

- `analysis/inventory/course_inventory.md` exists.
- `analysis/inventory/batch_plan.md` exists.
- Referenced source files exist under `inputs/`.
- Stop if source files need to be edited or moved.

# Reads

- `subject.yaml`
- `analysis/inventory/course_inventory.md`
- `analysis/inventory/batch_plan.md`
- filenames and metadata under `inputs/`

# Writes

- updated `analysis/inventory/batch_plan.md`
- optional planning notes under `analysis/inventory/`
- `review/unresolved-questions.md` for planning uncertainties

# Workflow

1. Read the inventory and current batch plan.
2. Identify batches that are too broad, too narrow, duplicated, file-type based, or missing supporting sources.
3. Merge, split, rename, or reorder batches when this improves conceptual coherence.
4. Attach exercises, readings, notes, transcripts, and exams to the relevant conceptual batches where possible.
5. Keep truly ambiguous files in an explicit needs-review section.
6. Summarize the final processing order.

# Model routing and efficiency

- Use fast reasoning for simple renames, ordering, and obvious source attachment.
- Use deeper reasoning for technical courses, mixed lecture/exercise material, or unclear module boundaries.
- Do not read full source contents unless metadata and filenames are insufficient.

# Quality rules

- Batches represent concepts, lectures, modules, or tutorial themes.
- Exercises should not become standalone master-note batches unless they are explicitly conceptual or have no related conceptual batch.
- Every planned batch lists its assigned sources.
- Uncertainty is preserved rather than hidden.

# Stop conditions

- Inventory or batch plan is missing.
- Referenced input files are absent.
- The plan cannot be made reliable without user clarification.

# Completion report

Report changed batch names, merged/split batches, unassigned sources, unresolved planning questions, and the next recommended skill: `studyos-batch`.
