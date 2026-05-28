---
name: studyos-batch
description: Process one selected conceptual StudyOS batch into digest, learning core, complete notes, formula sheet when relevant, and exam practice questions.
---

# Purpose

Process one selected conceptual batch at a time using assigned sources, creating grounded batch-level study material with integrated visual screening.

The study-facing output set is deliberately reduced. This skill generates only complete notes, a formula sheet when formulas exist or are relevant, and exam practice questions. It must not generate flashcards, cheat sheets, study plans, final review packs, or any substitute for those removed outputs.

Output quality and exhaustive assigned-input coverage are the priority. Time and token optimization must never shorten or simplify outputs by omitting unique concepts, examples, caveats, assumptions, formulas, visuals, or exam signals from assigned sources. Long outputs are acceptable when long outputs are required for complete, sound study material.

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
- `outputs/formulas/<batch>_formulas.md` if formulas exist or are relevant
- `outputs/questions/<batch>_questions.md`
- `review/weak-points.md`
- `review/unresolved-questions.md`
- `review/visual-issues.md` if visual issues exist

Do not write:

- flashcards
- cheat sheets
- study plans
- final review packs
- any files under deprecated output folders for those formats

# Workflow

1. Run preflight checks.
2. Read the selected batch definition, assigned sources, and relevant existing review files.
3. Build a source-by-source reading plan from filenames, inventory metadata, headings, slide titles, tables of contents, abstracts, and obvious formula or exam signals.
4. Build a Source Coverage table before generating study outputs.
5. Fully read assigned primary sources. Read supporting sources selectively first, then escalate to full reading when they contain unique concepts, formulas, exam signals, corrections, essential examples, caveats, assumptions, or visuals. If selective reading cannot prove coverage, fully read the supporting source.
6. Extract and organize text content from assigned sources.
7. Perform visual screening internally for slides, PDFs, images, screenshots, diagrams, charts, and tables.
8. Perform targeted visual analysis for essential visuals.
9. Create `analysis/batches/<batch>_digest.md`.
10. Create `analysis/batches/<batch>_learning_core.md`.
11. Generate only the reduced study-facing outputs from the learning core:
   - complete notes
   - formula sheet when formulas exist or are relevant
   - exam practice questions
12. Update review files.
13. Stop and recommend validation.

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

All assigned sources must appear in Source Coverage as used, partially used, unreadable, irrelevant to the selected batch, duplicate, or deferred with a concrete reason. Do not silently omit assigned sources.

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

Exercises should feed exam practice questions, worked-answer expectations, common mistakes, and weak points. Do not convert exercise-only material into fake theory summaries unless the source itself contains conceptual explanations.

# Learning core requirements

The learning core must preserve enough depth to support complete notes. Do not over-compress into a summary outline.

The learning core should include:

- source-grounded concept map
- detailed explanations and dependencies
- definitions and assumptions
- formula derivations or intuition when available
- examples and exercise patterns
- exam-relevant answer expectations
- weak points, traps, and unresolved questions
- source references for each substantive block

# Required notes sections

`outputs/notes/<batch>.md` must be complete study notes, not a summary.

Every notes file must include:

- Scope
- Core Notes
- Definitions
- Examples
- Formula Intuition
- Exam Relevance
- Common Mistakes
- Weak Points
- Source References

Write enough detail for a student to study from the notes without reopening every source, while preserving source references and unresolved uncertainty. Formula Intuition is required even when no standalone formula sheet is produced; say explicitly when the batch has no formulas and explain any conceptual quantitative relationships.

Notes may be long. Do not compress them to fit an arbitrary length when assigned inputs contain distinct concepts, examples, caveats, assumptions, formulas, visuals, or exam signals that a student needs.

# Formula sheet requirements

Write `outputs/formulas/<batch>_formulas.md` when formulas, notation, quantitative assumptions, derivations, or formula-like rules exist or are relevant to the batch.

Formula sheets must use readable display LaTeX for important formulas, for example:

```latex
$$
R_p = \sum_{i=1}^{n} w_i R_i
$$
```

For each formula, include:

- name or purpose
- display LaTeX
- variable definitions
- assumptions or conditions
- intuition
- common mistakes
- source references

# Exam practice requirements

`outputs/questions/<batch>_questions.md` is the active-recall and practice layer for the batch.

Questions should include a mix of:

- conceptual recall
- definition checks
- formula application when relevant
- exercise-derived practice
- exam-style prompts
- common-mistake traps
- short expected answers or solution outlines
- source references

# Model routing and efficiency

- Use model routing from `subject.yaml` and `study-os/config/model-routing.yaml` when available.
- Use balanced reasoning for normal batches.
- Use deep reasoning for formula-heavy batches.
- Use deep reasoning only for the affected visual-essential sections when targeted visual analysis is required.
- Use balanced or deep reasoning for exam questions depending on difficulty and exam relevance.
- Repair affected sections before regenerating entire outputs.
- Avoid rereading unrelated batches.
- Spend saved effort from the reduced output set on deeper notes, better formula handling, stronger question quality, and source/visual coverage.
- Do not spend tokens planning or producing removed outputs.
- Use metadata-first reading to reduce wasted context, but do not let token savings reduce assigned-source coverage.
- Keep the digest compact for obvious or duplicated facts and detailed for definitions, formulas, assumptions, worked examples, exam signals, visual findings, source conflicts, and weak points.
- Escalate only the unclear section to deeper reasoning when possible.
- Reuse current digest, learning core, and validation findings for repairs; do not regenerate valid sections.
- Optimize by removing duplication and filler, not by omitting unique assigned-source content.

# Quality rules

- Every substantive claim must trace back to assigned sources.
- Digest comes before learning core; learning core comes before outputs.
- Exercises support practice and weak-point extraction by default, not standalone theory notes.
- Formula sheets include assumptions and source provenance.
- Visual screening is integrated and visual material is not ignored when it carries examinable content.
- Outputs must use `analysis/`, `outputs/`, and `review/` paths only.
- Notes must be complete study notes rather than summaries.
- Source Coverage and Visual Coverage are required in the digest.
- All assigned sources must be used or explicitly explained in Source Coverage.
- The reduced output set is fixed for this skill: notes, formulas when relevant, and questions.
- Before completion, check the outputs against the Source Coverage table and ensure no assigned source with status `used` or `partially used` is absent from notes, formulas when relevant, or questions when exam-relevant.
- If an output cannot be made sound from available evidence, mark the issue unresolved and stop before presenting it as complete.
- If notes or questions feel short, explicitly verify that they are short because the assigned inputs are small or duplicated, not because coverage was reduced.

# Stop conditions

- Selected batch is missing or ambiguous.
- Assigned sources are missing.
- Required source content is unreadable.
- Grounding, formula, or visual uncertainty is too high to produce reliable outputs.

# Completion report

Report:

- files created or updated
- sources used
- assigned sources not used and why
- visuals analyzed
- unresolved issues
- recommended next skill: `studyos-validate`
