---
name: study-os-install
description: Install or repair the StudyOS v1 folder structure and local support files for one subject folder while preserving any existing course inputs and user work.
---

# StudyOS Install

Use this skill when setting up StudyOS in a subject folder or checking that an installation is complete.

## Workflow

1. Confirm the target subject folder.
2. Create missing StudyOS directories for `inputs/`, `working/`, `outputs/`, `review/`, and `study-os/`.
3. Copy StudyOS scripts, skills, and templates without overwriting existing user-edited files.
4. Initialize `study-os/state/studyos.sqlite` if needed.
5. Report what was created, copied, skipped, or already present.

## Guardrails

- Treat `inputs/` as read-only course material. Create missing input directories, but do not edit, delete, rename, summarize, or transform files inside them.
- Do not process course content during installation.
- Do not create digests, learning cores, outputs, validation results, or final synthesis during installation.
- Keep v1 focused on the local folder pipeline only.
