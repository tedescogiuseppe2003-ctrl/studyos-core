---
name: study-os-synthesize
description: Create final StudyOS course synthesis only after batch artifacts and validation reports exist, using learning cores and validated outputs as the basis.
---

# StudyOS Synthesize

Use this skill only when the user asks for final course-level synthesis or final review materials after batch processing and validation.

## Scope

Synthesis is the final stage of v1. It may work across batches, but only from existing StudyOS artifacts. It should not replace batch processing or validation.

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

- Use `balanced` or `deep` for normal synthesis depending on difficulty, formula density, and exam relevance.
- Use `deep` for difficult conceptual synthesis, technical formula integration, derivation-heavy material, and final exam-critical synthesis.
- Pair final exam-critical synthesis with an `audit` review for source grounding, hallucination detection, unresolved questions, and validation-report alignment.
- Use `balanced` for routine consolidation, deduplication, and normal final review packs when validation is clean.
- Use `script` only for deterministic status checks or file/state updates.

## Preflight Checks

Before synthesis, confirm:

- `working/learning-cores/` contains learning core files;
- `outputs/` contains batch outputs;
- `review/validation-report.md` exists;
- at least one validation pass appears to have been run, such as a validation report decision of `pass` or `pass with warnings`, a timestamped validation report entry, or an equivalent validation status in StudyOS state.

If any required preflight item is missing, stop immediately and warn:

`Cannot synthesize yet. Process and validate batches first.`

Also explain:

- Missing: name the missing learning cores, batch outputs, validation report, or validation-pass evidence.
- Why blocked: synthesis is a final-stage operation and must be based on processed learning cores, generated batch outputs, and validation results rather than raw or unvalidated material.
- Run first: run `study-os-process-batch` or `study-os-process-course`, then run `study-os-validate`.
- Expected afterward: `working/learning-cores/` should contain learning core files, `outputs/` should contain batch outputs, `review/validation-report.md` should exist, and at least one validation pass should be recorded.

## May Read

- `PROJECT_BRIEF.md` when working in the core repo.
- Installed subject configuration:
  - `subject.yaml`
  - `workflow.yaml`
  - `output-standards.yaml`
- Inventory and batch plan:
  - `working/inventory/course_inventory.md`
  - `working/inventory/batch_plan.md`
- Batch artifacts:
  - `working/digests/`
  - `working/learning-cores/`
  - `working/visual-notes/`
- Validated outputs:
  - `outputs/master-notes/`
  - `outputs/formula-sheets/`
  - `outputs/flashcards/`
  - `outputs/exam-questions/`
  - `outputs/cheat-sheets/`
  - `outputs/study-plan/`
- Review files:
  - `review/validation-report.md`
  - `review/source-coverage.md`
  - `review/formula_validation_report.md`
  - `review/weak-points.md`
  - `review/unresolved-questions.md`

Raw `inputs/` may be read only to resolve a citation or inspect a validation gap. Prefer learning cores and validated outputs as the synthesis basis.

## May Write

- `outputs/final-review-pack/`
- `outputs/master-notes/` only for explicitly requested course-level consolidated notes.
- `outputs/cheat-sheets/` only for explicitly requested course-level cheat sheets.
- `outputs/study-plan/` only for explicitly requested course-level plans.
- `review/` synthesis gap notes when final synthesis is blocked or incomplete.
- `study-os/state/studyos.sqlite` synthesis status when applicable.

## Must Not Write

- Never modify files inside `inputs/`.
- Do not rewrite batch digests, learning cores, or batch outputs unless the user explicitly asks for fixes.
- Do not invent missing material for unprocessed or unvalidated batches.
- Do not ignore unresolved questions or validation findings.

## Preconditions

Before synthesizing, confirm:

- `working/inventory/batch_plan.md` exists,
- relevant batches have digests,
- relevant batches have learning cores,
- relevant outputs exist,
- validation reports exist or validation gaps are explicitly known,
- weak points and unresolved questions have been reviewed.

If preconditions are missing, stop and report what must be processed or validated first.

## Synthesis Inputs

Use this priority order:

1. validated learning cores,
2. validated batch outputs,
3. validation reports and weak-point notes,
4. source digests,
5. raw inputs only for targeted clarification.

Do not base final course materials directly on raw sources when learning cores are available.

## Output Types

Possible final v1 artifacts:

- final review pack,
- course-level master notes,
- course-level formula sheet,
- course-level exam question set,
- course-level cheat sheet,
- study plan.

Only create the output types requested by the user or configured workflow.

## Required Final Output Qualities

Final synthesis must:

- preserve source references,
- mark unresolved questions clearly,
- carry forward weak points,
- integrate repeated concepts across batches,
- avoid duplicate explanations where one consolidated explanation is clearer,
- include exam-useful tasks when exercises or validation reports indicate them,
- avoid vague summaries unsupported by batch artifacts.

## Workflow

1. Identify requested final artifact type and course scope.
2. Check preconditions for all included batches.
3. Read learning cores, validated outputs, and review files.
4. Build a synthesis outline before writing final artifacts.
5. Create requested final artifacts under the appropriate `outputs/` folder.
6. Include source references and unresolved-question markers.
7. Write review notes for any blocked or incomplete sections.
8. Report created files and remaining gaps.

## Quality Bar

- Final artifacts are course-level, not just concatenated batch files.
- Validation findings influence the synthesis.
- Gaps remain visible instead of being smoothed over.
- `inputs/` remains read-only.
