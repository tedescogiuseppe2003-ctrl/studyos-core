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

## Model routing and efficiency

Use the cheapest sufficient model. Start with a lower tier and escalate only when the task requires deeper reasoning. Do not sacrifice precision for speed when exam relevance is high, but do not use deep reasoning for mechanical tasks.

Tiers:

- `fast`: setup questions, config filling, filename-based classification, simple formatting, import proposal when obvious, inventory review.
- `balanced`: batch plan repair, digest creation, normal concept explanation, normal output generation, flashcards, exam questions.
- `deep`: formulas, derivations, technical finance/statistics/econometrics explanations, difficult conceptual synthesis, essential visual analysis, formula screenshots, definition screenshots, complex charts/tables/diagrams.
- `audit`: validation, source-grounding review, hallucination detection, final synthesis review.
- `script`: deterministic execution, import execution, hashing, inventory script, validation scripts, sync/install.

For this skill:

- Use `balanced` for a normal batch: digest creation, learning core creation, normal explanations, and normal output generation.
- Use `deep` for formula-heavy batches, derivations, technical finance/statistics/econometrics material, difficult conceptual synthesis, and any exam-critical precision issue.
- Use `deep` only for affected visuals in visual-essential batches, such as formula screenshots, definition screenshots, or complex charts/tables/diagrams. Do not escalate the entire batch automatically when only one visual needs deeper analysis.
- Use `fast` or `balanced` for flashcards depending on conceptual difficulty and exam relevance.
- Use `balanced` for normal exam questions and `deep` for difficult, formula-heavy, or high-stakes exam questions.
- Use `script` for deterministic validation scripts or status updates run during the workflow.

## Preflight

Before processing a batch, confirm:

- `subject.yaml` exists;
- `study-os/` exists;
- `working/inventory/course_inventory.md` exists;
- `working/inventory/batch_plan.md` exists;
- the requested batch exists in `batch_plan.md`;
- every assigned source for the requested batch exists under `inputs/`.

If any preflight item is missing, stop and report:

- what is missing;
- why batch processing cannot continue;
- which skill to run first.

Use this guidance:

- Missing `subject.yaml` or `study-os/`: run `study-os-install` first.
- Missing or empty `inputs/`: run `study-os-import-sources` first.
- Missing inventory or batch plan: run `study-os-inventory` first.
- Missing assigned source files: repair the import plan or rerun import before processing.

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

Check all sources assigned to the batch and use all relevant content. Do not rely only on slides when notes, exercises, readings, or transcripts are assigned.

For each batch, explicitly check every assigned source file. No assigned source may be silently ignored. The digest must include a `Source Coverage` table listing every assigned source, its role, whether it was used, what was extracted from it, and why it was not used if applicable.

For every assigned source:

- include it in the source digest or explicitly state why it has no usable content,
- carry its important facts, examples, definitions, formulas, practice prompts, and warnings into the learning core when they support the batch concept,
- cite it in downstream outputs when its content is used.

Special handling:

- Primary sources define the conceptual core of the batch.
- Supporting sources must still be used, but they must support the batch concept rather than become unrelated standalone outputs.
- Slides often provide definitions, sequence, notation, and lecture structure.
- Exercises contribute exam questions, practice tasks, weak points, recurring mistakes, and fragile skills.
- Readings contribute theory, formal definitions, assumptions, limitations, and deeper explanations.
- Notes contribute professor emphasis, doubts, traps, caveats, and likely exam warnings.
- Transcripts contribute explanations, examples, emphasis, and spoken clarifications.
- Exams contribute likely exam patterns, task formats, and recurring assessment angles.
- Miscellaneous assigned sources must be checked and either mapped to the learning core or explained as unused.

## Batch Type Rules

A batch should normally represent a conceptual lecture, topic, or module.

Primary sources define the conceptual core. They usually include slides, lecture notes, core readings, or any source explicitly marked as the main lecture/topic/module material.

Supporting sources must still be used, but only in service of the conceptual core. They usually include exercises, exams, transcripts, personal notes, and supplementary readings.

Every downstream output must be based on the learning core. The learning core must be grounded in the conceptual core and supported by the assigned supporting sources.

When exercises are assigned to a conceptual batch:

- integrate them into exam questions,
- create practice tasks when useful,
- update weak points with recurring mistakes or fragile skills,
- do not create separate master notes for the exercise file.

If a batch contains only exercises and is not explicitly marked as a tutorial or conceptual batch:

- do not create normal master notes by default,
- create or update `outputs/exam-questions/`,
- create practice tasks,
- update `review/weak-points.md`,
- flag the batch for review in `review/unresolved-questions.md` or `working/validation/` as appropriate,
- explain that the batch lacks a primary conceptual source.

Only create master notes for an exercise-only batch when the batch plan explicitly marks it as tutorial, conceptual, or equivalent course instruction. Ordinary exercise-only batches must not produce standalone master notes.

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
## Source Coverage

| Source | Role | Used? | What was extracted | If not used, why |
|---|---|---|---|---|
```

Every assigned source file must appear in that table. Use `primary` or `supporting` in `Role`, with a short qualifier when useful, such as `supporting - exercises` or `primary - lecture slides`. Use `yes`, `partial`, or `no` in `Used?`.

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
3. Classify the batch as conceptual, tutorial/conceptual exercise-only, or ordinary exercise-only.
4. Identify primary sources and supporting sources.
5. Read and check all assigned sources.
6. Create or update the source digest, including the required `Source Coverage` table.
7. Create or update the learning core from the digest.
8. Create requested outputs from the learning core, applying the exercise-only restrictions above.
9. Update `review/weak-points.md` and `review/unresolved-questions.md`.
10. Run deterministic validation scripts when available or tell the user exactly which validation remains.
11. Report changed files and any unresolved issues.

## Quality Bar

- Digest before learning core; learning core before outputs.
- All assigned sources are checked and represented in the digest.
- If any assigned source is not used, the digest explains why.
- Primary sources define the conceptual core; supporting sources support that core.
- Ordinary exercise-only batches do not produce normal master notes by default.
- Outputs are directly usable for studying, active recall, and exam preparation.
- `inputs/` remains read-only.
