---
name: studyos-plan
description: Refine the first-pass StudyOS batch plan into conceptual lectures, topics, modules, or tutorials before processing.
---

# Purpose

`studyos-plan` refines the first-pass `analysis/inventory/batch_plan.md` created by `studyos-import`.

The import inventory pass is metadata-first: it scans copied files under `inputs/`, writes `analysis/inventory/course_inventory.md`, and creates an initial batch plan from filenames, folders, lecture numbers, and simple topic keywords. This skill is the manual planning pass that turns that first draft into a reliable conceptual processing plan.

The goal is that batches represent conceptual lectures, topics, modules, or tutorials, not random individual files or file-type buckets.

# When to use

Use after `studyos-import` has created:

- `analysis/inventory/course_inventory.md`
- `analysis/inventory/batch_plan.md`

Use before any `studyos-batch`, `studyos-course`, validation, merge, or export work.

# Preflight checks

Before changing the plan, confirm:

- `analysis/inventory/course_inventory.md` exists.
- `analysis/inventory/batch_plan.md` exists.
- `subject.yaml` exists.
- `inputs/` exists and contains at least one file.
- Files referenced by the inventory or plan exist under `inputs/`.

Stop and report the missing prerequisite if any required file is absent. Do not create invented source paths. Do not modify anything under `inputs/`.

# Reads

- `subject.yaml`
- `analysis/inventory/course_inventory.md`
- `analysis/inventory/batch_plan.md`
- filenames, paths, and visible metadata under `inputs/`

# Writes

- `analysis/inventory/batch_plan.md`
- `analysis/inventory/batch_plan_repair_log.md`
- `analysis/inventory/processing_queue.md`, if a separate execution order would make batch processing clearer

Do not write study outputs, digests, learning cores, summaries, flashcards, formulas, questions, validation reports, or exports.

# Model routing

- Use `balanced` by default.
- Use `deep` only for complex course structures, mixed lecture/tutorial numbering, technical prerequisite chains, or dependencies that cannot be inferred with ordinary metadata review.
- Do not process source material. Read full file contents only when filenames, folder placement, inventory metadata, and the current plan are insufficient to identify the conceptual boundary.

# Batch design rules

1. Slides and lecture-topic files usually define primary batches.
2. Exercises usually support the closest conceptual batch.
3. Readings usually support the closest conceptual batch.
4. Notes and transcripts support the closest lecture or topic.
5. Exams support final review or relevant conceptual batches.
6. Ordinary exercises should not become standalone master-note batches.
7. Standalone exercise or tutorial batches are allowed only when explicitly tutorial/conceptual, such as a named lab, recitation, methods tutorial, case tutorial, or problem-solving session.
8. Unclear files go under `Unassigned / needs review`.
9. Add dependencies where inferable from numbering, module sequence, prerequisites in titles, or obvious conceptual order.
10. Do not process, summarize, solve, validate, or transform course material.
11. Preserve every discovered input file somewhere in the plan: as a primary source, supporting source, or unassigned file.

# Refined batch plan format

Keep `analysis/inventory/batch_plan.md` as Markdown. Each conceptual batch must include:

```markdown
## Batch_<number>_<short_title>

Status: planned
Difficulty: low | medium | high | unknown
Exam relevance: low | medium | high | unknown
Depends on: none | Batch_<number>_<short_title>[, Batch_<number>_<short_title>]

### Primary sources

- `inputs/...`

### Supporting sources

- `inputs/...`

### Expected outputs

- source digest
- learning core
- configured final outputs for this batch

### Notes

Planning notes, assumptions, source assignment rationale, and uncertainty.
```

Keep this section when needed:

```markdown
## Unassigned / needs review

- `inputs/...` - reason it could not be confidently matched
```

# Planning workflow

1. Read `subject.yaml` to understand course level, exam type, quality mode, and expected outputs.
2. Read `analysis/inventory/course_inventory.md` and the current `analysis/inventory/batch_plan.md`.
3. Build a source coverage checklist from the inventory so every file is accounted for exactly once as primary, supporting, or unassigned.
4. Identify first-pass problems:
   - batches that are individual exercise files without conceptual scope
   - file-type buckets such as only readings or only exercises
   - duplicate lecture/topic batches
   - over-broad batches that combine unrelated concepts
   - missing supporting files
   - unclear or missing dependencies
5. Refine batches conservatively:
   - merge duplicate or fragmentary batches into a conceptual lecture/topic/module
   - split broad batches only when titles, numbering, or folder structure show separate concepts
   - rename batches to the clearest conceptual title
   - reorder batches into a sensible processing sequence
   - assign primary sources to the conceptual anchors
   - assign exercises, readings, notes, transcripts, and exams as supporting sources when a match is credible
6. Move uncertain files to `Unassigned / needs review` with a concrete reason.
7. Add or update `Depends on` for each batch.
8. Write the repaired `analysis/inventory/batch_plan.md`.
9. Write `analysis/inventory/batch_plan_repair_log.md` with:
   - batches created or refined
   - files reassigned
   - unassigned files
   - dependencies identified
   - warnings and assumptions
10. Optionally write `analysis/inventory/processing_queue.md` when the recommended execution order is not obvious from the batch headings alone.

# Repair log format

Use concise Markdown:

```markdown
# Batch Plan Repair Log

## Summary

- Batches created/refined: <count>
- Files reassigned: <count>
- Unassigned files: <count>
- Dependencies identified: <count>

## Changes

- <change>

## Unassigned Files

- `inputs/...` - <reason>

## Dependencies

- `<batch>` depends on `<batch>` - <reason>

## Warnings

- <warning or assumption>
```

# Stop conditions

Stop without rewriting the plan when:

- `course_inventory.md` is missing.
- `batch_plan.md` is missing.
- `inputs/` has no files.
- referenced source files are absent from `inputs/`.
- reliable refinement would require user clarification, not just conservative unassignment.

# Completion report

Report:

- batches created or refined
- files reassigned
- unassigned files
- dependencies identified
- warnings
- paths written
- next recommended skill: `studyos-batch`
