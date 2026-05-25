---
name: study-os-install
description: Install or repair the StudyOS v1 folder structure and local support files for one subject folder while preserving inputs and existing user work.
---

# StudyOS Install

Use this skill when setting up StudyOS in a subject folder, repairing a partial installation, or checking whether the local StudyOS structure is complete.

## Scope

StudyOS v1 is a local folder pipeline:

`inputs/` -> inventory -> batch plan -> `working/digests/` -> `working/learning-cores/` -> `outputs/` -> `review/validation` -> final synthesis

Keep v1 lean. Do not add Graphify, hooks, subagents, Anki export, Obsidian export, dashboards, or web apps.

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
- `study-os/state/studyos.sqlite` only when initializing missing state.

## Must Not Write

- Never modify files inside `inputs/`.
- Never overwrite existing user-edited files unless the user explicitly asks for overwrite behavior.
- Do not create digests, learning cores, study outputs, validation reports, final packs, or synthesis artifacts.

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

## Workflow

1. Read `PROJECT_BRIEF.md` from the core repo.
2. Confirm the target subject folder path.
3. Create missing required directories.
4. Copy templates, scripts, and skills without overwriting existing files.
5. Initialize SQLite state if the installed workflow requires it and the database is missing.
6. Report:
   - target path,
   - directories created,
   - files copied,
   - files skipped because they already existed,
   - any missing source files in the core repo.

## Quality Bar

- Installation must be idempotent.
- Existing student/course work must be preserved.
- `inputs/` is raw course material and is always read-only after directory creation.
