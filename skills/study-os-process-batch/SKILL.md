---
name: study-os-process-batch
description: Process one StudyOS batch by creating source digests, learning cores, and batch outputs grounded in all relevant assigned sources.
---

# StudyOS Process Batch

Use this skill when the user asks to process a specific batch from `working/inventory/batch_plan.md`.

## Scope

Process one batch at a time. The output order is mandatory:

1. source digest,
2. learning core,
3. batch-specific study outputs.

Keep v1 lean. Do not add Graphify, hooks, subagents, Anki export, Obsidian export, dashboards, or web apps.

## May Read

- `PROJECT_BRIEF.md` when working in the core repo.
- Installed subject configuration:
  - `subject.yaml`
  - `workflow.yaml`
  - `output-standards.yaml`
  - `model-routing.yaml`
- Inventory and batch plan:
  - `working/inventory/course_inventory.md`
  - `working/inventory/batch_plan.md`
  - `study-os/state/studyos.sqlite`
- All relevant source files assigned to the selected batch, including:
  - slides,
  - notes,
  - exercises,
  - readings,
  - transcripts,
  - exams,
  - miscellaneous sources when assigned.
- Existing batch artifacts for the same batch when updating or continuing work.

## May Write

- `working/digests/`
- `working/learning-cores/`
- `working/visual-notes/` only when lazy visual analysis is needed.
- `outputs/master-notes/`
- `outputs/formula-sheets/`
- `outputs/flashcards/`
- `outputs/exam-questions/`
- `outputs/cheat-sheets/`
- `outputs/study-plan/`
- `review/weak-points.md`
- `review/unresolved-questions.md`
- `working/validation/` notes only when needed for handoff.
- `study-os/state/studyos.sqlite` processing status when applicable.

## Must Not Write

- Never modify files inside `inputs/`.
- Do not create final course synthesis or final review packs during batch processing.
- Do not process the whole course unless the user explicitly selects multiple batches.
- Do not hide unsupported claims; record weak points and unresolved questions.

## Required Source Use

Use all relevant sources assigned to the batch. Do not rely only on slides when notes, exercises, readings, or transcripts are assigned.

For each batch, explicitly check every assigned source file. The digest must include a `Source coverage` section listing every assigned source and what was extracted from it. If a source contributes nothing, explain why.

For every assigned source:

- include it in the source digest or explicitly state why it has no usable content,
- carry its important facts, examples, definitions, formulas, practice prompts, and warnings into the learning core,
- cite it in downstream outputs when its content is used.

Special handling:

- Slides often provide definitions and structure.
- Notes often provide instructor emphasis, caveats, and likely exam warnings.
- Exercises provide practice formats and exam-useful task types.
- Readings provide deeper explanation and formal definitions.
- Transcripts provide spoken clarifications and examples.

## Batch Type Rules

A batch should normally represent a conceptual lecture, topic, or module.

Primary sources usually include slides, lecture notes, or core readings. Supporting sources usually include exercises, exams, transcripts, personal notes, and supplementary readings.

When exercises are assigned to a conceptual batch:

- integrate them into exam questions,
- create practice tasks when useful,
- update weak points with recurring mistakes or fragile skills,
- do not create separate master notes for the exercise file.

If a batch contains only exercises:

- do not automatically create master notes,
- create an exercise practice file instead, unless the batch is explicitly marked as a tutorial or conceptual batch,
- flag the batch for review if its topic is unclear.

## Digest Requirements

Create one batch digest in `working/digests/`.

The digest must include:

- batch name and scope,
- complete source list,
- source coverage,
- key topics,
- definitions,
- formulas,
- examples and exercises,
- instructor emphasis or caveats,
- weak points,
- unresolved questions,
- source references.

The digest must include this required section:

```markdown
## Source coverage

| Source | Used? | What was extracted | If not used, why |
|---|---|---|---|
```

Every assigned source file must appear in that table. Use `yes`, `partial`, or `no` in `Used?`.

Keep the digest faithful to sources. Do not add unsupported teaching material here.

## Learning Core Requirements

Create one learning core in `working/learning-cores/` based on the digest.

The learning core must include:

- learning objectives,
- core concepts,
- explanations,
- connections between topics,
- worked examples when sources support them,
- formulas and notation,
- common mistakes,
- exam-relevant points,
- weak points,
- unresolved questions,
- source references.

The learning core may synthesize across sources, but every substantive claim must be traceable to the digest or a cited source.

## Output Requirements

Create only the batch outputs requested by the workflow or user. Typical v1 outputs are:

- master notes,
- formula sheets,
- flashcards,
- exam questions,
- cheat sheets,
- study plans.

Each output must:

- be based on the learning core,
- include source references,
- preserve unresolved-question markers where uncertainty remains,
- include weak points when relevant,
- be specific to the batch,
- avoid vague filler.

Formula sheet entries must include:

- `Formula:`
- `Variables:`
- `Assumptions:`
- `Use when:`
- `Interpretation:`
- `Common mistake:`
- `Source:`

## Lazy Visual Analysis

Use visual analysis only when a chart, table, diagram, equation image, or slide visual contains testable information that is not captured in text. If visual analysis is skipped, note why only when the decision affects the batch.

## Workflow

1. Read the batch plan and identify the requested batch.
2. List every assigned source file.
3. Read all relevant assigned sources.
4. Create or update the source digest.
5. Create or update the learning core from the digest.
6. Create requested outputs from the learning core.
7. Update `review/weak-points.md` and `review/unresolved-questions.md`.
8. Run deterministic validation scripts when available or tell the user exactly which validation remains.
9. Report changed files and any unresolved issues.

## Quality Bar

- Digest before learning core; learning core before outputs.
- All relevant assigned sources are represented.
- Outputs are directly usable for studying, active recall, and exam preparation.
- `inputs/` remains read-only.
