---
name: study-os-synthesize
description: Create final StudyOS course synthesis only after batch artifacts and validation reports exist, using learning cores and validated outputs as the basis.
---

# StudyOS Synthesize

Use this skill only when the user asks for final course-level synthesis or final review materials after batch processing and validation.

## Scope

Synthesis is the final stage of v1. It may work across batches, but only from existing StudyOS artifacts. It should not replace batch processing or validation.

Keep v1 lean. Do not add Graphify, hooks, subagents, Anki export, Obsidian export, dashboards, or web apps.

## Preflight

Before synthesis, confirm:

- `subject.yaml` exists;
- `working/inventory/batch_plan.md` exists;
- included batches have digests in `working/digests/`;
- included batches have learning cores in `working/learning-cores/`;
- included batches have requested outputs under `outputs/`;
- validation reports exist under `review/`;
- unresolved questions and weak points have been reviewed.

If any preflight item is missing, stop and report:

- what is missing;
- why synthesis cannot continue;
- which skill to run first.

Use this guidance:

- Missing `subject.yaml` or `study-os/`: run `study-os-install` first.
- Missing batch plan: run `study-os-inventory` first.
- Missing digests, learning cores, or batch outputs: run `study-os-process-batch` or `study-os-process-course` first.
- Missing validation reports: run `study-os-validate` first.

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
