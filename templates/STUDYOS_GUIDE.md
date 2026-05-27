# StudyOS Guide

StudyOS is a guided study-material workflow for one course. It keeps original course files protected, copies approved material into `inputs/`, then helps an agent build inventory, batch outputs, validation reports, merged study material, and PDF exports step by step.

## Normal Installation UX

Before installation, this course folder may not have local StudyOS skills yet. Installation is done through the external StudyOS core repo, usually `~/Developer/studyos-core`.

Normal request:

> Install StudyOS in this folder using ~/Developer/studyos-core.

The installing agent runs the external core installer, initializes or confirms the database, runs core sync, inspects the folder name and visible raw course files read-only, proposes a complete setup, asks for approval or modifications, fills `subject.yaml` only after approval, creates or updates this guide, and stops.

Installation/setup does not import files, run inventory, create a batch plan, validate, process, merge, or export material.

## Setup Proposal After Installation

The proposal includes subject name, course level, material language, exam type, raw source folder path, read-only original files, copy-into-inputs strategy, desired outputs, quality/depth mode, visual handling depth, formula handling depth, and validation depth.

The agent asks:

> Do you approve this setup, or do you want modifications?

The agent fills `subject.yaml` only after approval.

## Folder Structure

- `inputs/` contains copied course files after import. Treat these files as read-only.
- `analysis/` contains import plans, inventory, first-pass batch plans, source digests, learning cores, visual notes, validation records, and processing state.
- `outputs/` contains batch-level, course-level, and merged study outputs.
- `exports/pdf/unmerged/` and `exports/pdf/merged/` contain PDF exports.
- `review/` contains validation reports, weak points, unresolved questions, source coverage, and progress tracking.
- `study-os/` contains installed scripts, skills, config guides, and local state.

## Protected Files

The original raw course folder configured at `subject.yaml` -> `raw_source.path` is read-only. StudyOS must never move, rename, delete, overwrite, or modify anything there.

Import copies approved files into `inputs/`. Files under `inputs/` are also treated as read-only after import.

## Skill Commands

- `python3 study-os/scripts/studyos.py status` reports the current workspace state and next recommended manual skill.
- `python3 study-os/scripts/studyos.py doctor` checks local readiness without modifying files.
- `studyos-import` proposes safe import, stops for approval, executes approved copy actions, then creates inventory and the first conceptual batch plan.
- `studyos-plan` refines the conceptual batch plan.
- `studyos-batch` processes one planned batch into digest, learning core, and configured outputs.
- `studyos-validate` validates batch, course, repaired, or merged outputs.
- `studyos-course` processes remaining batches sequentially and creates course-level outputs.
- `studyos-merge` creates consolidated full-course outputs and the final review pack.
- `studyos-export` exports unmerged and merged PDF deliverables.

## Recommended Workflow

1. Optionally run `python3 study-os/scripts/studyos.py status` or `python3 study-os/scripts/studyos.py doctor`.
2. Run `studyos-import` proposal mode to create `analysis/inventory/import_plan.md`.
3. Review and approve the import plan.
4. Run `studyos-import` execute mode to copy approved files into `inputs/`.
5. Run `studyos-import` inventory mode to create `analysis/inventory/course_inventory.md` and `analysis/inventory/batch_plan.md`.
6. Run `studyos-plan`.
7. Run `studyos-batch` for one batch.
8. Run `studyos-validate`.
9. Run `studyos-course` if you want remaining batches processed sequentially.
10. Run `studyos-merge` when course outputs are processed and validated.
11. Run `studyos-export`.

Review `analysis/inventory/import_plan.md` before import execute. Do not continue with execute mode unless the proposed copies are acceptable.

`studyos-import` full flow runs proposal first if no plan exists, then stops for approval. It must not silently execute without an approved plan.

## Common Missing-Step Warnings

- Missing `subject.yaml` or `study-os/`: install StudyOS first.
- Missing `raw_source.path`: complete approved setup before importing.
- Missing import plan: run `studyos-import` proposal mode.
- Empty `inputs/`: run `studyos-import` proposal mode, approve the plan, then run execute mode.
- Missing `batch_plan.md`: run `studyos-import` inventory mode, then `studyos-plan`.
- Missing digest, learning core, or outputs: run `studyos-batch`.
- Missing validation reports: run `studyos-validate`.
- Missing merged outputs: run `studyos-merge`.

## Output Locations

- Notes: `outputs/notes/`
- Formula sheets: `outputs/formulas/`
- Flashcards: `outputs/flashcards/`
- Exam questions: `outputs/questions/`
- Cheat sheets: `outputs/cheat-sheets/`
- Study plans: `outputs/study-plan/`
- Final review packs: `outputs/final-pack/`
- Unmerged PDF exports: `exports/pdf/unmerged/`
- Merged PDF exports: `exports/pdf/merged/`

## Repair Before Regenerate

When validation finds issues, repair only the affected sections or files. Preserve valid content, do not regenerate unrelated outputs, rerun validation after repair, and leave remaining uncertainty clearly marked.
