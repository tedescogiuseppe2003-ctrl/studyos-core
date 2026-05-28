# StudyOS Codex Instructions

You are working inside a StudyOS v1 course workspace.

## Standing Rules

- Keep StudyOS v1 lean.
- Treat `raw_source.path` as an external read-only source folder.
- Never modify files in `inputs/`.
- Process course material by batch.
- Treat batches as conceptual lectures, topics, or modules whenever possible.
- Use exercises as supporting practice sources unless they are explicitly tutorial or conceptual batches.
- Do not create separate note outputs for an exercise file attached to a conceptual batch.
- Create source digests before learning cores.
- Create learning cores before final outputs.
- Base final outputs on learning cores.
- Use source references for course claims.
- Track weak points and unresolved questions.
- Validate outputs after each batch.
- Use integrated visual screening in `studyos-batch`, `studyos-course`, and `studyos-validate` when charts, tables, diagrams, or images carry important course content.

## Installation Setup

When installing StudyOS into a course folder, use the external core repo, usually `~/Developer/studyos-core`. Install and sync local scripts, skills, and config, inspect the folder name and visible raw course files read-only, propose a complete setup, ask the user to approve or modify it, write `subject.yaml` only after approval, and stop.

Essential setup fields are subject name, raw source folder path, course level, course-material language, exam type, the fixed default outputs, quality mode, visual handling depth, formula handling depth, validation depth, whether original files are read-only, and whether StudyOS should copy files into `inputs/`. Default to read-only originals and copy-only import into `inputs/`.

The setup proposal should include only these default study-facing outputs: notes, formulas, and exam practice questions. Do not ask whether to generate flashcards, cheat sheets, study plans, or final review packs during setup; those are deprecated and disabled.

After installation, point the user to `STUDYOS_GUIDE.md` and continue only when the user chooses the next skill. Do not import, inventory, plan, process, validate, merge, or export during installation/setup.

## Folder Semantics

- `inputs/` contains approved copied raw material and is read-only after import.
- `analysis/` contains import plans, inventory, batch plans, digests, learning cores, visual notes, validation details, and state.
- `outputs/` contains study-facing Markdown outputs.
- `exports/pdf/unmerged/` contains batch-level exports.
- `exports/pdf/merged/` contains consolidated full-course exports.
- `review/` contains weak points, unresolved questions, source coverage, visual issues, validation reports, and progress tracking.

## v1 Scope

- Do not add Graphify.
- Do not add hooks.
- Do not add subagents.
- Do not add optional modules.
- Do not add Anki export.
- Do not add Obsidian export.
- Do not add dashboards or web apps.

## Workflow

Use the v1 workflow in `templates/workflow.yaml`:

1. `studyos-import`
2. `studyos-plan`
3. `studyos-batch`
4. `studyos-validate`
5. `studyos-course`
6. `studyos-merge`
7. `studyos-export`

Keep each change small and test the current step before moving forward.
