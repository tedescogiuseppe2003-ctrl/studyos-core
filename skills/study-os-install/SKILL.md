---
name: study-os-install
description: Install or repair the StudyOS v1 folder structure and local support files for one subject folder while preserving inputs and existing user work.
---

# StudyOS Install

Use this skill when setting up StudyOS in a subject folder, repairing a partial installation, or checking whether the local StudyOS structure is complete.

This skill is reference guidance for install behavior. Before StudyOS is installed, local workspace skills may not exist yet, so the agent must use the external core repository directly.

## Scope

StudyOS v1 is a local folder pipeline:

raw source folder -> import plan -> copy into `inputs/` -> inventory -> batch plan -> `working/digests/` -> `working/learning-cores/` -> `outputs/` -> `review/validation` -> final synthesis

Keep v1 lean. Do not add Graphify, hooks, subagents, Anki export, Obsidian export, dashboards, or web apps.

Installation is setup only. Do not import, inventory, classify, summarize, process, validate, or synthesize course material during installation.

## Setup Wizard Behavior

When the user asks something like "Install StudyOS in this folder using ~/Developer/studyos-core", act as a small setup wizard:

1. Identify the target folder as the current workspace unless the user names another target.
2. Use the user-provided core repo path, or `~/Developer/studyos-core` when the user does not provide one.
3. Read `PROJECT_BRIEF.md` from the external core repo.
4. Run `python3 <core-repo>/scripts/install_studyos.py <target-folder>`.
5. Run `python3 <core-repo>/scripts/sync_studyos.py <target-folder>`.
6. Confirm `study-os/state/studyos.sqlite` exists. Initialize it by running `python3 <core-repo>/scripts/init_db.py` from the target folder only if it is missing.
7. Ask setup questions for missing values.
8. Fill `subject.yaml` from the setup answers.
9. Create or update `STUDYOS_GUIDE.md`, preserving any existing course-specific notes unless the user asks for replacement.
10. Stop.

Never run an installed workspace copy of `install_studyos.py`. The installer is core-only. If an old `study-os/scripts/install_studyos.py` exists, ignore it and run sync from the external core repo so the deprecated copy is removed.

Ask for these setup values when they are missing:

- Subject name
- Course level
- Course material language
- Exam type
- Original/raw course folder path
- Desired outputs:
  - master notes
  - formula sheets
  - flashcards
  - exam questions
  - cheat sheets
  - study plan
  - final review pack
- Quality/depth mode: economy, standard, rigorous
- Visual handling depth: minimal, standard, rigorous
- Formula handling depth: normal, rigorous
- Validation depth: structural only, standard, rigorous audit
- Confirmation that original files are read-only
- Confirmation that StudyOS copies files into `inputs/`

Defaults:

- `raw_source.mode`: `read_only`
- `raw_source.copy_strategy`: `copy_into_inputs`
- `processing.quality_mode`: `standard`
- `processing.batch_strategy`: `lecture_or_topic`
- `processing.process_incrementally`: `true`
- `processing.require_validation`: `true`
- `processing.allow_parallel_batches`: `false`
- `analysis_depth.visual_handling`: `standard`
- `analysis_depth.formula_handling`: `normal`
- `analysis_depth.validation_depth`: `standard`
- `graphify.enabled`: `false`

The user should not need to manually edit `subject.yaml` unless they want to.

After setup, tell the user that the next step is manual and skill-by-skill, starting with `study-os-import-sources` when they are ready. Do not run that skill for them during installation.

## May Read

- The core repo files needed for installation:
  - `PROJECT_BRIEF.md`
  - `templates/`
  - `scripts/`
  - `skills/`
- The target subject folder structure.
- Existing target config files, scripts, skills, and state files only to decide whether they already exist.

## May Write

- Missing target directories under:
  - `inputs/`
  - `working/`
  - `outputs/`
  - `review/`
  - `study-os/`
  - `.agents/skills/`
  - `.claude/skills/`
- Missing copied files from:
  - `templates/`
  - `scripts/` into `study-os/scripts/`
  - `skills/` into `study-os/skills/`, `.agents/skills/`, and `.claude/skills/`
- `subject.yaml` after installation, using the setup answers.
- `study-os/state/studyos.sqlite` only when initializing missing state.
- `STUDYOS_GUIDE.md` to create or update setup guidance.

## Must Not Write

- Never modify files inside `inputs/`.
- Never modify the original raw source folder.
- Never overwrite existing user-edited files unless the user explicitly asks for overwrite behavior.
- Do not create digests, learning cores, study outputs, validation reports, final packs, or synthesis artifacts.
- Do not import files into `inputs/` during installation.
- Do not create `working/inventory/import_plan.md`, `course_inventory.md`, or `batch_plan.md` during installation.

## Required Directories

Ensure these directories exist:

- `inputs/slides`
- `inputs/readings`
- `inputs/notes`
- `inputs/exercises`
- `inputs/exams`
- `inputs/transcripts`
- `inputs/miscellaneous`
- `working/inventory`
- `working/digests`
- `working/learning-cores`
- `working/visual-notes`
- `working/validation`
- `outputs/master-notes`
- `outputs/formula-sheets`
- `outputs/flashcards`
- `outputs/exam-questions`
- `outputs/cheat-sheets`
- `outputs/study-plan`
- `outputs/final-review-pack`
- `outputs/assets`
- `review`
- `study-os/config`
- `study-os/state`
- `study-os/scripts`
- `study-os/skills`
- `.agents/skills`
- `.claude/skills`

## Installed Guides

Ensure these files exist after installation:

- `STUDYOS_GUIDE.md`
- `study-os/config/SKILLS_GUIDE.md`

## Workflow

1. Read `PROJECT_BRIEF.md` from the core repo.
2. Confirm the target subject folder path.
3. Confirm the external core repo path, defaulting to `~/Developer/studyos-core`.
4. Run `python3 <core-repo>/scripts/install_studyos.py <target-folder>`.
5. Run `python3 <core-repo>/scripts/sync_studyos.py <target-folder>`.
6. Confirm SQLite state exists at `study-os/state/studyos.sqlite`.
7. Ask the setup wizard questions for missing values.
8. Fill `subject.yaml` from the setup answers without changing raw course files.
9. Create or update `STUDYOS_GUIDE.md`, preserving any existing course-specific notes unless the user asks for replacement.
10. Report:
   - target path,
   - directories created,
   - files copied,
   - files skipped because they already existed,
   - `subject.yaml` fields filled,
   - guide files installed,
   - any missing source files in the core repo,
   - that installation/setup is complete and no import, inventory, or processing was run.
11. Stop. Do not continue into import or inventory.

## Quality Bar

- Installation must be idempotent.
- Existing student/course work must be preserved.
- `inputs/` is raw course material and is always read-only after directory creation.
- Setup ends before any course-material workflow begins.
