---
name: study-os-process-course
description: Process planned or unprocessed StudyOS batches sequentially, validating each batch before continuing and stopping on blocking course-level issues.
---

# StudyOS Process Course

Use this skill when the user asks to process all planned, unprocessed, or stale StudyOS batches for a subject.

This is a course-level orchestration skill. It must not process the full course as one giant batch. It loops through `working/inventory/batch_plan.md` and runs the batch workflow one batch at a time.

This skill is written as direct operating instructions for Codex or Claude Code in an installed StudyOS subject folder.

## Scope

Process batches sequentially from the existing batch plan. For each batch, use the `study-os-process-batch` workflow to create or update the digest, learning core, and configured batch outputs, then use the `study-os-validate` workflow before moving to the next batch.

Keep v1.1 lean. Do not add Graphify, hooks, subagents, Anki export, Obsidian export, dashboards, or web apps.

## May Read

- `PROJECT_BRIEF.md` when working in the core repo.
- Installed subject configuration:
  - `subject.yaml`
  - `study-os/config/workflow.yaml`
  - `study-os/config/output-standards.yaml`
  - `study-os/config/model-routing.yaml` when present.
- Inventory and batch planning:
  - `working/inventory/course_inventory.md`
  - `working/inventory/batch_plan.md`
  - `study-os/state/studyos.sqlite` when present.
- Existing intermediate artifacts:
  - `working/digests/`
  - `working/learning-cores/`
  - `working/visual-notes/`
  - `working/validation/`
- Existing outputs:
  - `outputs/master-notes/`
  - `outputs/formula-sheets/`
  - `outputs/flashcards/`
  - `outputs/exam-questions/`
  - `outputs/cheat-sheets/`
  - `outputs/study-plan/`
- Existing review files:
  - `review/weak-points.md`
  - `review/unresolved-questions.md`
  - `review/validation-report.md`
  - `review/source-coverage.md`
  - `review/formula_validation_report.md`
  - `review/progress-tracker.md`
- All source files assigned to the current batch under `inputs/`.

Read raw sources only for the current batch being processed or validated. Do not load unrelated course sources just because they exist.

## May Write

- `working/digests/`
- `working/learning-cores/`
- `outputs/master-notes/`
- `outputs/formula-sheets/`
- `outputs/flashcards/`
- `outputs/exam-questions/`
- `outputs/cheat-sheets/`
- `review/weak-points.md`
- `review/unresolved-questions.md`
- `review/validation-report.md`
- `review/progress-tracker.md`
- `study-os/state/run-log.md`

## Must Not Write

- Never modify files inside `inputs/`.
- Never modify raw source files.
- Do not write unrelated system files.
- Do not synthesize final course outputs during this skill.
- Do not skip validation to save time.
- Do not treat the course as a single combined source batch.
- Do not hide unsupported claims, inconsistent formulas, weak points, or unresolved questions.

## Batch Selection

Read `working/inventory/batch_plan.md` and identify batches whose status or artifacts indicate work is needed.

Process batches with statuses such as:

- `new`
- `planned`
- `unprocessed`
- `stale`
- `needs processing`
- `needs validation`
- `needs repair`
- missing status, when the batch otherwise appears planned and processable.

Skip batches only when the plan or review state clearly says they are already processed and validated, such as:

- `validated`
- `complete`
- `processed and validated`
- `skip`
- `blocked`, unless the user explicitly asks to retry.

If batch status is ambiguous, stop before processing and report the ambiguity. Do not guess when ambiguity could cause duplicate, skipped, or out-of-order processing.

## Required Per-Batch Loop

For each selected batch, complete this loop before considering the next batch:

1. Read the batch entry from `working/inventory/batch_plan.md`.
2. Confirm every assigned source file exists and is readable.
3. Confirm the batch has a clear conceptual scope, primary sources, supporting sources, and expected outputs.
4. Process the batch using the `study-os-process-batch` workflow:
   - create or update the source digest in `working/digests/`;
   - include the required `Source Coverage` table listing every assigned source;
   - create or update the learning core in `working/learning-cores/`;
   - create or update configured outputs under `outputs/`;
   - update weak points and unresolved questions.
5. Validate the batch using the `study-os-validate` workflow:
   - run deterministic checks when available;
   - review source grounding, formula quality, active recall quality, exam usefulness, and weak-point coverage;
   - update validation reports.
6. Decide whether to continue:
   - continue only if validation passes or passes with non-blocking warnings;
   - repair minor validation issues before continuing;
   - stop on severe validation issues.
7. Update `review/progress-tracker.md` and `study-os/state/run-log.md`.

Do not begin processing the next batch until the current batch has been processed, validated, and either accepted or repaired.

## Processing Requirements

For each batch:

- Use all assigned sources.
- Check every assigned source file explicitly.
- Preserve primary and supporting source roles from the batch plan.
- Do not create standalone master notes for ordinary exercise-only supporting material.
- Use lazy visual analysis only for important charts, tables, diagrams, equation images, or slide visuals with testable information not captured in text.
- Base final batch outputs on the learning core, not directly on raw sources.
- Preserve source references in digests, learning cores, and outputs.
- Carry weak points and unresolved questions forward.

Every digest must include:

```markdown
## Source Coverage

| Source | Role | Used? | What was extracted | If not used, why |
|---|---|---|---|---|
```

Every assigned source must appear in the table with `yes`, `partial`, or `no` in `Used?`.

## Output Requirements

Create or update only the configured or expected outputs for the batch.

Output requirements:

- Master notes must be based on the learning core and cite source references.
- Formula sheets must include required fields:
  - `Formula:`
  - `Variables:`
  - `Assumptions:`
  - `Use when:`
  - `Interpretation:`
  - `Common mistake:`
  - `Source:`
- Flashcards must use active recall, not passive recognition.
- Exam questions must include expected answers, and worked solutions or grading notes when useful.
- Cheat sheets must be compact, exam-oriented, and traceable to learning cores.
- Unresolved uncertainty must remain visible instead of being smoothed over.

## Validation Decisions

Classify validation findings before continuing.

Severe issues are blocking. Stop and report when any of these appear:

- missing source files;
- unreadable assigned files;
- severe validation failure;
- ambiguous batch plan;
- unsupported claims in outputs or learning cores;
- inconsistent formulas;
- source coverage missing assigned files;
- final outputs not based on the learning core;
- evidence that `inputs/` or raw source files would need modification.

Minor issues should be repaired before continuing, such as:

- missing or weak source references where the source is clear;
- incomplete formula fields with no formula inconsistency;
- weak flashcards that can be rewritten into active recall;
- exam questions missing expected answers;
- unclear weak-point wording;
- formatting or section-order problems.

After repairing minor issues, validate the same batch again or update the validation report with the targeted re-check. Do not continue on an unverified repair.

## Progress Tracking

Maintain `review/progress-tracker.md` with a course-level processing record:

```markdown
# Progress Tracker

Updated: YYYY-MM-DD

## Batch Status

| Batch | Status | Digest | Learning Core | Outputs | Validation | Notes |
|---|---|---|---|---|---|---|

## Current Stop Point

- Batch:
- Reason:
- Next action:
```

Append concise run entries to `study-os/state/run-log.md`:

```markdown
## YYYY-MM-DD HH:MM - study-os-process-course

- Batch:
- Action:
- Validation decision:
- Files changed:
- Stop or continue decision:
```

Use the local timezone when known.

## Workflow

1. Confirm the command is running from the subject root.
2. Read `subject.yaml`.
3. Read `working/inventory/course_inventory.md`.
4. Read `working/inventory/batch_plan.md`.
5. Read `study-os/config/workflow.yaml` and `study-os/config/output-standards.yaml`.
6. Review existing `working/`, `outputs/`, and `review/` artifacts to determine which batches are already complete, stale, blocked, or unprocessed.
7. Build an ordered processing queue from the batch plan.
8. Stop if the queue is ambiguous or if any selected batch references missing or unreadable source files.
9. For the first queued batch, run the per-batch loop.
10. Continue one batch at a time until the queue is empty or a stop condition appears.
11. After all queued batches are processed and validated, recommend running `study-os-synthesize`.

## Final Report

At the end of the run, report:

- batches processed;
- batches skipped;
- batch stopped on, if any;
- validation status;
- files created or updated;
- weak points found;
- unresolved questions;
- whether synthesis is safe to run next.

If processing stops early, include the exact blocker and the next repair action.

## Quality Bar

- Course-level processing is sequential orchestration, not one giant batch.
- Each batch is processed with `study-os-process-batch` semantics.
- Each batch is validated with `study-os-validate` semantics before moving on.
- Minor validation issues are repaired and rechecked.
- Severe validation issues stop the run.
- All assigned sources are used or explicitly accounted for.
- Every digest has complete `Source Coverage`.
- Final batch outputs are based on learning cores.
- Formula sheets, flashcards, and exam questions meet their required standards.
- `inputs/` and raw source files remain read-only.
