---
name: study-os-inventory
description: Build or refresh the StudyOS source inventory for one installed subject folder by scanning input metadata and creating batch planning files.
---

# StudyOS Inventory

Use this skill before processing course material. Inventory discovers raw sources and creates a batch plan; it does not summarize, interpret, or transform course content.

## Scope

Inventory is metadata-only. It prepares batches for later processing.

Keep v1 lean. Do not add Graphify, hooks, subagents, Anki export, Obsidian export, dashboards, or web apps.

## Model routing and efficiency

Use the cheapest sufficient model. Start with a lower tier and escalate only when the task requires deeper reasoning. Do not sacrifice precision for speed when exam relevance is high, but do not use deep reasoning for mechanical tasks.

Tiers:

- `fast`: setup questions, config filling, filename-based classification, simple formatting, import proposal when obvious, inventory review.
- `balanced`: batch plan repair, digest creation, normal concept explanation, normal output generation, flashcards, exam questions.
- `deep`: formulas, derivations, technical finance/statistics/econometrics explanations, difficult conceptual synthesis, essential visual analysis, formula screenshots, definition screenshots, complex charts/tables/diagrams.
- `audit`: validation, source-grounding review, hallucination detection, final synthesis review.
- `script`: deterministic execution, import execution, hashing, inventory script, validation scripts, sync/install.

For this skill:

- Run the inventory script as `script`.
- Use `fast` for straightforward inventory review and filename-based grouping.
- Use `balanced` for batch plan repair, difficult classification, ambiguous source roles, or when deciding whether exercise material should be primary or supporting.
- Do not use `deep` for hashing, metadata scanning, or routine batch-plan formatting.

## Preflight Checks

Before inventory, confirm:

- `inputs/` exists;
- at least one file exists somewhere inside `inputs/`;
- `study-os/scripts/inventory.py` exists;
- `study-os/state/` exists.

If any preflight item is missing, stop immediately and warn:

`Cannot run inventory yet. Import/copy source files into inputs/ first using study-os-import-sources.`

Also explain:

- Missing: name the missing folder, file, script, state path, or empty `inputs/` condition.
- Why blocked: inventory is metadata-only and must scan already imported input files while writing state to `study-os/state/`; without these prerequisites it cannot create a trustworthy course inventory or batch plan.
- Run first: run `study-os-import-sources` to import or copy source files into `inputs/`; run `study-os-install` or sync/reinstall StudyOS first if `study-os/scripts/inventory.py` or `study-os/state/` is missing.
- Expected afterward: `inputs/` should contain at least one course file, `study-os/scripts/inventory.py` should exist, and `study-os/state/` should exist.

## May Read

- `PROJECT_BRIEF.md` when working in the core repo.
- Installed subject configuration:
  - `subject.yaml`
  - `workflow.yaml`
  - `output-standards.yaml`
- File metadata and bytes for hashing under:
  - `inputs/slides/`
  - `inputs/readings/`
  - `inputs/notes/`
  - `inputs/exercises/`
  - `inputs/exams/`
  - `inputs/transcripts/`
  - `inputs/miscellaneous/`
- Existing inventory files and SQLite state:
  - `working/inventory/course_inventory.md`
  - `working/inventory/batch_plan.md`
  - `study-os/state/studyos.sqlite`

## May Write

- `working/inventory/course_inventory.md`
- `working/inventory/batch_plan.md`
- `study-os/state/studyos.sqlite`
- `study-os/state/` support files required by the local inventory script.

## Must Not Write

- Never modify files inside `inputs/`.
- Do not write to `working/digests/`, `working/learning-cores/`, `outputs/`, or `review/`.
- Do not extract PDF text, OCR images, analyze slides visually, or summarize content during inventory.

## Required Inventory Fields

For each source file, record:

- relative path from the subject root,
- input folder-derived source type,
- filename-derived lecture number when possible,
- filename-derived topic guess,
- SHA256 hash,
- status such as `new`, `stale`, or unchanged existing status.

## Batch planning rules

Batches should represent conceptual topics, lectures, modules, or tutorial sessions, not individual files by default.

Plan batches around the conceptual structure of the course. Do not create standalone exercise-only batches that would later produce master notes for exercise sheets unless one of the explicit exceptions below applies.

Primary sources are the files that define the conceptual batch and its main learning scope. Supporting sources are files that reinforce, apply, clarify, assess, or provide context for a conceptual batch but should not normally define a batch on their own.

Use these source-role rules:

- Slides and lecture-topic files usually define primary batches.
- Lecture notes can define or support batches depending on naming and content signals.
- Exercises usually support the closest conceptual batch.
- Readings usually support the closest conceptual batch.
- Exams usually support relevant conceptual batches or a final review batch.
- Transcripts usually support the closest lecture batch.
- Personal notes usually support the closest lecture or topic batch.

Do not create standalone exercise batches unless:

- the exercise file is explicitly a tutorial or session;
- it contains new examinable theory;
- no related conceptual batch can be identified.

If a supporting source cannot be confidently matched to a conceptual batch, place it under `Unassigned / needs review`.

Do not process material during inventory. Do not generate outputs during inventory.

Each planned batch must include:

- batch title,
- status,
- difficulty,
- exam relevance,
- primary sources,
- supporting sources,
- expected outputs,
- notes.

Include an `Unassigned / needs review` section if any discovered source cannot be confidently assigned.

Use this structure for `working/inventory/batch_plan.md`:

```markdown
# Batch Plan

## Batch: <conceptual topic, lecture, module, or tutorial session title>

- Status: <new | unchanged | stale | needs review>
- Difficulty: <low | medium | high | unknown>
- Exam relevance: <low | medium | high | unknown>
- Primary sources:
  - `<relative/path>`
- Supporting sources:
  - `<relative/path>`
- Expected outputs:
  - source digest
  - learning core
  - configured final outputs for this batch
- Notes: <planning notes, assumptions, uncertainty>

## Unassigned / needs review

- `<relative/path>` - <why it could not be confidently matched>
```

- Group sources conservatively by lecture number and topic guess when no stronger topic structure is available.
- Keep batches small enough to process one at a time.
- Do not merge unrelated lectures only because they share a broad topic word.
- Include every discovered input file in the batch plan, even if lecture/topic is uncertain.
- Use `Unassigned / needs review` when a lecture number, topic, or conceptual match cannot be inferred.

## Workflow

1. Run from the installed subject folder root unless the user supplies `--root`.
2. Confirm required StudyOS folders exist.
3. Scan only approved `inputs/` subfolders.
4. Hash each file and compare with existing inventory state.
5. Update SQLite source rows idempotently.
6. Write `working/inventory/course_inventory.md` as a readable Markdown table.
7. Write `working/inventory/batch_plan.md` with batch headings and source file lists.
8. Report source count, inventory path, batch plan path, and database path.

## Quality Bar

- The command can be run repeatedly without duplicating source rows.
- Changed file hashes mark existing sources as stale.
- The inventory is useful for selecting one batch for `study-os-process-batch`.
- `inputs/` remains read-only.
