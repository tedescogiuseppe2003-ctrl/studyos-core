---
name: study-os-install
description: Install or repair the StudyOS v1 folder structure and local support files for one subject folder while preserving inputs and existing user work.
---

# StudyOS Install

Use this skill when setting up StudyOS in a subject folder, repairing a partial installation, or checking whether the local StudyOS structure is complete.

This skill is mostly reference documentation for the installing agent. Before StudyOS is installed, local workspace skills may not exist yet, so the agent should use the core repository installer directly.

## Scope

StudyOS v1 is a local folder pipeline:

raw source folder -> import plan -> copy into `inputs/` -> inventory -> batch plan -> `working/digests/` -> `working/learning-cores/` -> `outputs/` -> `review/validation` -> final synthesis

Keep v1 lean. Do not add Graphify, hooks, subagents, Anki export, Obsidian export, dashboards, or web apps.

Installation is setup only. Do not import, classify, summarize, process, validate, or synthesize course material during installation.

## Setup Wizard Behavior

When the user asks something like "Install StudyOS in this folder using ~/Developer/studyos-core", act as a small setup wizard:

1. Identify the target folder as the current workspace unless the user names another target.
2. Use the named core repo, usually `~/Developer/studyos-core`.
3. Check whether the target already has enough information in `subject.yaml`.
4. Ask only for missing essential setup information.
5. Run the core installer.
6. Initialize the database if the installer did not already do so.
7. Fill `subject.yaml` from the setup answers.
8. Leave original files and imported files untouched.
9. Point the user to `STUDYOS_GUIDE.md` and the first skill to run.

Ask for these values only when they are missing:

- subject name;
- raw/original course folder path;
- course level, for example Bachelor or Master;
- language of course material;
- exam type: written, oral, project, or mixed;
- desired outputs:
  - master notes,
  - formula sheets,
  - flashcards,
  - exam questions,
  - cheat sheets,
  - study plan,
  - final review pack;
- whether original files must be treated as read-only, default yes;
- whether StudyOS should copy files into `inputs/`, default yes.

Defaults:

- `raw_source.mode`: `read_only`
- `raw_source.copy_strategy`: `copy_into_inputs`
- `processing.mode`: `manual_guided`
- `processing.batch_strategy`: `conceptual_batches`
- `processing.process_incrementally`: `true`
- `processing.require_validation`: `true`
- `processing.allow_parallel_batches`: `false`
- `graphify.enabled`: `false`

The user should not need to manually edit `subject.yaml` unless they want to.

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

## Must Not Write

- Never modify files inside `inputs/`.
- Never modify the original raw source folder.
- Never overwrite existing user-edited files unless the user explicitly asks for overwrite behavior.
- Do not create digests, learning cores, study outputs, validation reports, final packs, or synthesis artifacts.
- Do not import files into `inputs/` during installation.

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
3. Ask the setup wizard questions for missing values only.
4. Run `python3 <core-repo>/scripts/install_studyos.py <target-folder>`.
5. Fill `subject.yaml` from the setup answers without changing raw course files.
6. Confirm SQLite state exists at `study-os/state/studyos.sqlite`.
7. Report:
   - target path,
   - directories created,
   - files copied,
   - files skipped because they already existed,
   - `subject.yaml` fields filled,
   - guide files installed,
   - any missing source files in the core repo.

## Quality Bar

- Installation must be idempotent.
- Existing student/course work must be preserved.
- `inputs/` is raw course material and is always read-only after directory creation.
