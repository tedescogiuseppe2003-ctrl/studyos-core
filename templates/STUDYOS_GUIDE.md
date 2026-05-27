# StudyOS Guide

StudyOS is a guided study-material workflow for one course. It keeps your original course files protected, copies approved material into `inputs/`, then helps an agent build inventory, batch notes, validation reports, and final review outputs step by step.

## Normal Installation UX

Before installation, this course folder may not have local StudyOS skills yet. Installation is done through the external StudyOS core repo, usually `~/Developer/studyos-core`.

Normal request:

> Install StudyOS in this folder using ~/Developer/studyos-core.

The installing agent runs the external core installer, runs core sync, confirms the database exists, asks setup questions, fills `subject.yaml`, creates or updates this guide, and stops.

The setup questions the agent should ask are:

- Subject name.
- Course level: Bachelor, Master, PhD, or Other.
- Language of the course material.
- Exam type: written, oral, project, mixed, or unknown.
- Raw/original course folder path.
- Whether original files are read-only, default yes.
- Whether StudyOS should copy files into `inputs/`, default yes.
- Desired outputs: master notes, formula sheets, flashcards, exam questions, cheat sheets, study plan, and final review pack.
- Quality/depth mode: `economy`, `standard`, or `rigorous`.
- Visual handling depth: minimal, standard, or rigorous.
- Formula handling depth: normal or rigorous.
- Validation depth: structural only, standard, or rigorous audit.

The user should not manually edit `subject.yaml` unless desired. Installation/setup does not import files, run inventory, or process course material.

## Quality Modes And Output Budgets

Quality mode controls analysis depth, output size, and rigor.

- `economy` is faster and compact: master notes are about 800-1200 words per batch, flashcards 15-25, exam questions 5-10, and formula sheets include only essential formulas.
- `standard` is the default balance: master notes are about 1200-2200 words per batch, flashcards 25-45, exam questions 8-18, and formula sheets include all important formulas.
- `rigorous` prioritizes completeness for exam-heavy or technical material: master notes are as long as needed, flashcards can reach 40-70 per exam-heavy batch, exam questions 15-30, and formula sheets include formulas, assumptions, derivations, and common mistakes.

Visual handling depth, formula handling depth, and validation depth further adjust rigor. Higher depth means more careful source screening and validation, especially for diagrams, charts, tables, formulas, assumptions, and exam-critical details.

## subject.yaml

`subject.yaml` stores the course setup answers and processing configuration. It contains the subject name, course level, material language, exam type, requested outputs, quality/depth mode, visual handling depth, formula handling depth, validation depth, model routing, and `raw_source.path` for the original course folder.

The user normally does not edit this file manually. The installing agent fills it from the setup answers before import, inventory, or processing.

## Folder Structure

- `inputs/` contains copied course files after import. Treat these files as read-only.
- `working/` contains intermediate artifacts, including import plans, course inventory, batch plans, source digests, learning cores, visual-analysis notes, and validation handoff notes.
- `outputs/` contains generated study outputs.
- `review/` contains validation reports, weak points, unresolved questions, and progress tracking.
- `study-os/` contains installed StudyOS scripts, skills, config guides, local state such as the SQLite database, and run logs.

## Protected Files

The original raw course folder configured at `subject.yaml` -> `raw_source.path` is read-only. StudyOS must never move, rename, delete, overwrite, or modify anything there.

Import copies approved files into `inputs/`. Original raw files stay where they are and are never changed.

Files under `inputs/` are imported copies. After import, StudyOS treats them as read-only and processes them by reading only.

Generated files live under `working/`, `outputs/`, `review/`, and `study-os/state/`.

## Skill Commands

- `python3 study-os/scripts/studyos.py status` reports the current StudyOS workspace state and the next recommended manual skill. It does not import, inventory, process, validate, synthesize, or modify files.
- `python3 study-os/scripts/studyos.py doctor` checks local readiness, installed folders/scripts/skills/config, and obvious stale setup issues. It does not modify files.
- `study-os-import-sources` scans the configured raw source folder read-only. In proposal mode it writes `working/inventory/import_plan.md`. In execute mode it copies approved files into `inputs/` and writes `working/inventory/import_log.md`.
- `study-os-inventory` scans `inputs/`, creates `working/inventory/course_inventory.md`, and creates `working/inventory/batch_plan.md`.
- `study-os-process-batch` processes one planned batch. It creates a digest, a learning core, and the configured batch outputs.
- `study-os-validate` validates a processed batch with deterministic checks and, when configured, LLM review. It writes reports under `review/` and `working/validation/`.
- `study-os-process-course` processes remaining planned batches sequentially only when the user explicitly asks for that skill. It validates each batch before moving to the next and stops on severe issues.
- `study-os-synthesize` creates final course-level outputs after batches have been processed and validated.

## Source-Type Processing

`study-os-process-batch` uses source roles to avoid wasting time and to keep outputs consistent.

- Slides are usually the primary theory source and are screened for definitions, formulas, diagrams, charts, tables, professor emphasis, and visually essential content.
- Notes contribute professor emphasis, doubts, traps, clarifications, caveats, and weak points.
- Exercises are converted into practice questions, repeated problem types, weak points, and links to formulas or concepts instead of being summarized as theory by default.
- Readings contribute relevant theory, definitions, assumptions, limitations, and deeper explanations without over-summarizing unless exam-relevant.
- Exams contribute exam patterns, likely question types, answer expectations, and final-review signals.
- Transcripts contribute explanations, examples, emphasis, professor-style phrasing, and spoken clarifications.
- Miscellaneous sources are classified by role before use; uncertain roles are flagged in the batch digest.

## Recommended Workflow

After installation/setup, call skills manually one step at a time:

1. Optionally run `python3 study-os/scripts/studyos.py status` or `python3 study-os/scripts/studyos.py doctor` to inspect readiness.
2. Run `study-os-import-sources` in proposal mode.
3. Run `study-os-import-sources` in execute mode when the import plan is acceptable.
4. Run `study-os-inventory`.
5. Run `study-os-process-batch` for one batch to test quality.
6. Run `study-os-validate` for that batch.
7. Run `study-os-process-course` if you want remaining batches processed sequentially.
8. Run `study-os-synthesize` when the course is processed and validated.

Review `working/inventory/import_plan.md` before import execute. Do not continue with execute mode unless the proposed copies are acceptable.

## If A Skill Warns That A Previous Step Is Missing

Stop and run the missing earlier skill. The warning should name what is missing, why the current skill cannot continue, and which skill to run first.

Common examples:

- Missing `subject.yaml` or `study-os/`: install StudyOS first.
- Missing `raw_source.path`: fill `subject.yaml` before importing.
- Missing import plan: run `study-os-import-sources` in proposal mode before execute mode.
- Empty `inputs/`: import sources before inventory.
- Missing `batch_plan.md`: run `study-os-inventory` before processing.
- Missing digest, learning core, or outputs: run `study-os-process-batch` before validation.
- Missing validation reports: run `study-os-validate` before synthesis.

## Output Locations

- Master notes: `outputs/master-notes/`
- Formula sheets: `outputs/formula-sheets/`
- Flashcards: `outputs/flashcards/`
- Exam questions: `outputs/exam-questions/`
- Cheat sheets: `outputs/cheat-sheets/`
- Study plans: `outputs/study-plan/`
- Final review packs: `outputs/final-review-pack/`

## Validation Report Locations

- Main validation report: `review/validation-report.md`
- Source coverage report: `review/source-coverage.md`
- Formula validation report: `review/formula_validation_report.md`
- Additional validation notes: `working/validation/`

## Restarting Or Rerunning Safely

Rerun steps in order from the earliest stale or missing artifact. Do not edit original raw source files and do not modify files in `inputs/`.

Safe reruns:

- Rerun import proposal to refresh `working/inventory/import_plan.md`.
- Rerun import execute to copy approved files that are not already present. Existing destination files are not overwritten.
- Rerun inventory after new files are copied into `inputs/`.
- Rerun one batch when its sources or outputs are stale.
- Rerun validation after repairing a batch.
- Rerun synthesis after all included batches are processed and validated.

## Repair Before Regenerate

When validation finds issues, repair only the affected sections or files. Preserve valid content, do not regenerate unrelated outputs, rerun validation after repair, and leave remaining uncertainty clearly marked.
