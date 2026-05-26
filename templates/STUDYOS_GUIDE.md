# StudyOS Guide

StudyOS is a guided study-material workflow for one course. It keeps your original course files protected, copies approved material into `inputs/`, then helps an agent build inventory, batch notes, validation reports, and final review outputs step by step.

## Folder Structure

- `subject.yaml` stores the course setup: subject name, level, language, exam type, raw source path, processing settings, requested outputs, validation settings, and model routing.
- `inputs/` contains copied course files after import. Treat these files as read-only.
- `working/inventory/` contains the import plan, course inventory, and batch plan.
- `working/digests/` contains source digests for processed batches.
- `working/learning-cores/` contains the learning core for each processed batch.
- `working/visual-notes/` contains visual-analysis notes only when charts, diagrams, tables, or images matter.
- `working/validation/` contains validation handoff notes when needed.
- `outputs/` contains generated study outputs.
- `review/` contains validation reports, weak points, unresolved questions, and progress tracking.
- `study-os/config/` contains StudyOS reference guides and configuration files.
- `study-os/scripts/` contains local scripts used by the skills.
- `study-os/skills/`, `.agents/skills/`, and `.claude/skills/` contain the installed skill instructions.
- `study-os/state/` contains local state such as the SQLite database and run logs.

## Protected Files

The original raw course folder configured at `subject.yaml` -> `raw_source.path` is read-only. StudyOS must never move, rename, delete, or modify anything there.

Files under `inputs/` are imported copies. After import, StudyOS treats them as read-only and processes them by reading only.

Generated files live under `working/`, `outputs/`, `review/`, and `study-os/state/`.

## Skill Commands

- `study-os-import-sources` scans the configured raw source folder read-only. In proposal mode it writes `working/inventory/import_plan.md`. In execute mode it copies approved files into `inputs/` and writes `working/inventory/import_log.md`.
- `study-os-inventory` scans `inputs/`, creates `working/inventory/course_inventory.md`, and creates `working/inventory/batch_plan.md`.
- `study-os-process-batch` processes one planned batch. It creates a digest, a learning core, and the configured batch outputs.
- `study-os-validate` validates a processed batch with deterministic checks and, when configured, LLM review. It writes reports under `review/` and `working/validation/`.
- `study-os-process-course` processes remaining planned batches sequentially. It validates each batch before moving to the next and stops on severe issues.
- `study-os-synthesize` creates final course-level outputs after batches have been processed and validated.

## Recommended Workflow

1. Run `study-os-import-sources` in proposal mode.
2. Review `working/inventory/import_plan.md`.
3. Run `study-os-import-sources` in execute mode when the import plan is acceptable.
4. Run `study-os-inventory`.
5. Run `study-os-process-batch` for one batch to test quality.
6. Run `study-os-validate` for that batch.
7. Run `study-os-process-course` for remaining batches.
8. Run `study-os-synthesize` when the course is processed and validated.

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
