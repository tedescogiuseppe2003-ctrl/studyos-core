# StudyOS Codex Instructions

You are working inside a StudyOS v1 course workspace.

## Standing Rules

- Keep StudyOS v1 lean.
- Treat `raw_source.path` as an external read-only source folder.
- Never modify files in `inputs/`.
- Process course material by batch.
- Treat batches as conceptual lectures, topics, or modules whenever possible.
- Use exercises as supporting practice sources unless they are explicitly tutorial or conceptual batches.
- Do not create separate master notes for an exercise file attached to a conceptual batch.
- Create source digests before learning cores.
- Create learning cores before final outputs.
- Base final outputs on learning cores.
- Use source references for course claims.
- Track weak points and unresolved questions.
- Validate outputs after each batch.
- Use lazy visual analysis only when charts, tables, diagrams, or images carry important course content.

## Installation Setup

When installing StudyOS into a course folder, behave like a setup wizard. Ask only for missing essentials, fill `subject.yaml` automatically, initialize the database, and do not import or process course files during installation.

Essential setup fields are subject name, raw source folder path, course level, course-material language, exam type, desired outputs, whether original files are read-only, and whether StudyOS should copy files into `inputs/`. Default to read-only originals and copying into `inputs/`.

After installation, point the user to `STUDYOS_GUIDE.md` and continue only when the user chooses the next skill.

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
