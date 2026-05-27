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

Apply the configured quality mode from `output-standards.yaml` when deciding output size:

- `economy`: prefer compact outputs and essential formulas only.
- `standard`: use the normal balanced output budgets.
- `rigorous`: expand only where completeness, exam risk, formulas, or dense source material require it.

## Preflight Checks

Before processing a batch, confirm:

- `working/inventory/course_inventory.md` exists;
- `working/inventory/batch_plan.md` exists;
- `working/inventory/batch_plan.md` contains at least one planned batch;
- `inputs/` contains files;
- the selected batch exists in `working/inventory/batch_plan.md`;
- every assigned source for the selected batch exists under `inputs/`.

If any required preflight item is missing, stop immediately and warn:

`Cannot process a batch yet. Run study-os-inventory first.`

Also explain:

- Missing: name the missing inventory file, batch plan, planned batch, input files, selected batch, or assigned source path.
- Why blocked: batch processing must be grounded in the inventory and batch plan, and it cannot safely read or cite sources that are absent from `inputs/`.
- Run first: run `study-os-inventory` after importing files; run `study-os-import-sources` first if `inputs/` is empty or assigned source files are missing.
- Expected afterward: `working/inventory/course_inventory.md`, `working/inventory/batch_plan.md`, at least one planned batch, and the selected batch source files under `inputs/` should exist.

Also warn before processing, without hard-blocking unless the user chooses to stop:

- If `working/inventory/batch_plan.md` has an `Unassigned / needs review` section with files, warn that some sources have not been confidently attached to a conceptual batch and may need inventory review before processing.
- If the selected batch has only exercise sources and is not explicitly marked tutorial, conceptual, or equivalent course instruction, warn that normal master notes should not be created by default and that the batch lacks a primary conceptual source.

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

Source-type handling:

- Slides are the primary theory source when assigned as core lecture material. Extract definitions, formulas, diagrams, charts, tables, professor emphasis, and visually essential content that may be tested or needed to understand the concept.
- Notes provide professor emphasis, personal doubts, traps, clarifications, caveats, and likely exam warnings. Integrate these into weak points and the learning core.
- Exercises must not be summarized as theory by default. Convert them into practice questions, extract repeated problem types, update weak points, and connect them to relevant formulas and concepts.
- Readings provide relevant theory, definitions, assumptions, limitations, and deeper explanations. Do not over-summarize readings unless the material is exam-relevant; connect useful reading material to the batch concepts.
- Exams provide exam patterns, likely question types, answer expectations, recurring assessment angles, and final-review signals. Connect these to exam questions and final-review notes.
- Transcripts provide explanations, examples, emphasis, professor-style phrasing, and spoken clarifications.
- Miscellaneous sources must be classified by role before use. If the role is uncertain, flag the uncertainty in the batch digest.
- Primary sources define the conceptual core of the batch.
- Supporting sources must still be used, but they must support the batch concept rather than become unrelated standalone outputs.

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
- batch processing plan,
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
## Batch Processing Plan

- Sources:
- Primary sources:
- Supporting sources:
- Priority:
- Complexity:
- Formula risk:
- Visual risk:
- Outputs needed:
- Recommended model tier:
- Potential issues:
```

Use the plan to set depth, source priorities, visual screening effort, formula handling, and output budgets before generating outputs.

The digest must also include this required section:

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

Respect the configured output length budget:

- `economy`: master notes 800-1200 words per batch, 15-25 flashcards per batch, 5-10 exam questions per batch, and only essential formulas.
- `standard`: master notes 1200-2200 words per batch, 25-45 flashcards per batch, 8-18 exam questions per batch, and all important formulas.
- `rigorous`: master notes as long as needed for completeness, 40-70 flashcards per batch when exam-heavy, 15-30 exam questions per batch, and formulas with assumptions, derivations, and common mistakes.

If a source set cannot fit the selected budget without losing exam-critical material, preserve correctness and flag the reason for exceeding the budget.

## Repair Before Regenerate

When validation finds issues in a processed batch:

- patch only the affected digest, learning-core, output, weak-point, unresolved-question, or validation sections;
- preserve valid content and source references;
- do not regenerate unrelated outputs;
- rerun validation after the repair or record the exact targeted re-check performed;
- mark remaining uncertainty clearly instead of smoothing it over.

## Lazy Visual Analysis

Use visual analysis only when a chart, table, diagram, equation image, or slide visual contains testable information that is not captured in text. If visual analysis is skipped, note why only when the decision affects the batch.

## Workflow

1. Read the batch plan and identify the requested batch.
2. List every assigned source file.
3. Classify the batch as conceptual, tutorial/conceptual exercise-only, or ordinary exercise-only.
4. Identify primary sources and supporting sources.
5. Read and check all assigned sources.
6. Create or update the source digest, including the required `Batch Processing Plan` and `Source Coverage` table.
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
