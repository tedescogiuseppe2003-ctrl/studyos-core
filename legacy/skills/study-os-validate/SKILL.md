---
name: study-os-validate
description: Validate one StudyOS batch with deterministic checks and LLM review for grounding, clarity, recall quality, exam usefulness, and weak points.
---

# StudyOS Validate

Use this skill after a batch has been processed or when the user asks to inspect StudyOS output quality.

## Scope

Validate by batch, not across the full course, unless the user explicitly asks for course-level validation. Validation reports problems and recommends focused fixes. It does not rewrite outputs unless the user asks for fixes or the validation task explicitly includes making corrections.

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

- Run deterministic checks as `script`.
- Use `audit` or `balanced` for normal validation, depending on configured validation depth and exam relevance.
- Use `audit` plus `deep` for formula issues, visual issues, source-grounding issues, hallucination detection, inconsistent derivations, or exam-critical validation failures.
- Use `balanced` for ordinary clarity, formatting, active-recall quality, and output-completeness review when source grounding is straightforward.
- Do not use `deep` for mechanical report formatting or script output summarization.
- Check output length and rigor against the configured quality mode in `output-standards.yaml`.

## Preflight Checks

Before validation, confirm:

- `outputs/` contains generated files, or both `working/digests/` and `working/learning-cores/` contain processed batch files;
- `study-os/scripts/validate_outputs.py` exists;
- `study-os/scripts/validate_citations.py` exists;
- `study-os/scripts/validate_formulas.py` exists.

If any required preflight item is missing, stop immediately and warn:

`Cannot validate yet. Process at least one batch first.`

Also explain:

- Missing: name the missing generated outputs, processed digest/core files, or validation script.
- Why blocked: validation needs generated batch artifacts to inspect and deterministic scripts to check structure, citations, and formulas.
- Run first: run `study-os-process-batch` for at least one planned batch; run `study-os-install` or sync/reinstall StudyOS first if validation scripts are missing.
- Expected afterward: `outputs/` should contain generated batch outputs, or `working/digests/` and `working/learning-cores/` should contain processed batch files, and all three validation scripts should exist under `study-os/scripts/`.

## May Read

- `PROJECT_BRIEF.md` when working in the core repo.
- Installed subject configuration:
  - `subject.yaml`
  - `workflow.yaml`
  - `output-standards.yaml`
- Inventory and batch plan:
  - `working/inventory/course_inventory.md`
  - `working/inventory/batch_plan.md`
- Relevant batch raw sources under `inputs/`.
- Relevant batch intermediate files:
  - `working/digests/`
  - `working/learning-cores/`
  - `working/visual-notes/`
- Relevant batch outputs under `outputs/`.
- Existing review files:
  - `review/validation-report.md`
  - `review/source-coverage.md`
  - `review/formula_validation_report.md`
  - `review/weak-points.md`
  - `review/unresolved-questions.md`
- Validation scripts under `study-os/scripts/` or the core repo `scripts/`.

## May Write

- `review/validation-report.md`
- `review/source-coverage.md`
- `review/formula_validation_report.md`
- `working/validation/` notes when useful.
- `study-os/state/studyos.sqlite` validation status when applicable.

## Must Not Write

- Never modify files inside `inputs/`.
- Do not rewrite `outputs/` unless the user explicitly asks for fixes or the validation request includes applying clear corrections.
- Do not synthesize final course material.
- Do not hide validation failures to make the report pass.

## Deterministic Validation

Run or reproduce these checks before the LLM review:

1. Output structure:
   - required folders exist,
   - required output category folders exist,
   - existing output files are non-empty,
   - expected batch output categories are present after processing.
2. Citations:
   - working files and outputs contain source references,
   - cited `inputs/` filenames exist somewhere under `inputs/`,
   - suspicious placeholders or vague references are reported,
   - normal pipeline references such as `working/learning-cores/...` are not treated as raw source citations.
3. Formulas:
   - formula sheets exist when the batch contains formulas,
   - each formula entry includes:
     - `Formula:`
     - `Variables:`
     - `Assumptions:`
     - `Use when:`
     - `Interpretation:`
     - `Common mistake:`
     - `Source:`

Write deterministic reports to:

- `review/validation-report.md`
- `review/source-coverage.md`
- `review/formula_validation_report.md`

When doing a final combined validation report, preserve or summarize the deterministic results in `review/validation-report.md`.

## LLM Review

After deterministic checks, perform a human-quality review against the relevant source files, digest, learning core, and outputs.

Review these areas:

- source grounding: every substantive claim is supported by a source, digest, or learning core;
- source-type handling: slides, notes, exercises, readings, exams, transcripts, and miscellaneous files were used according to their roles;
- formula quality: formulas are correct for the stated assumptions and include variables, assumptions, interpretation, use cases, mistakes, and source;
- conceptual clarity: explanations are precise, not circular, and distinguish similar concepts;
- active recall quality: flashcards force retrieval rather than passive recognition;
- exam usefulness: exam questions reflect definitions, explanations, calculations, exercises, and likely exam tasks;
- output budgets: master notes, flashcard counts, exam-question counts, and formula-sheet depth match the selected quality mode or document a justified exception;
- missing weak points: uncertainty, conventions, unsupported gaps, and common mistakes are recorded.

The LLM review must use all relevant batch sources, including slides, notes, exercises, readings, and transcripts assigned to the batch.

## Repair Before Regenerate

Validation should recommend targeted repair before regeneration.

When validation finds issues and correction is in scope:

- patch only affected sections or files;
- preserve valid content and valid source references;
- do not regenerate unrelated outputs;
- rerun validation after repair or record the exact targeted re-check;
- mark remaining uncertainty clearly in the report and affected artifact.

Recommend full regeneration only when targeted repair cannot make the affected artifact trustworthy, such as missing source coverage across the artifact, unsupported conceptual structure, or pervasive formula inconsistency.

## Report Format

Write `review/validation-report.md` with this order:

1. title, timestamp, root, and batch reviewed,
2. issues first, ordered by severity,
3. deterministic validation summary,
4. LLM review by category,
5. decision:
   - pass,
   - pass with warnings,
   - needs targeted content improvement,
   - blocked,
6. recommended next fixes.

Each issue should include:

- severity,
- area,
- finding,
- evidence with file paths,
- recommended fix.

## Workflow

1. Identify the batch and expected artifacts.
2. Confirm digest exists before learning core and learning core exists before outputs.
3. Run deterministic validation scripts when available.
4. Read deterministic reports.
5. Read all relevant batch sources and generated artifacts.
6. Perform LLM review.
7. Write or update `review/validation-report.md`.
8. Do not edit outputs unless explicitly instructed.
9. Report final status and the report path.

## Quality Bar

- Findings are specific and actionable.
- Reports distinguish deterministic failures from content-quality issues.
- Source coverage includes all relevant assigned source types.
- `inputs/` remains read-only.
