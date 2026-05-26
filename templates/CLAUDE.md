# StudyOS Claude Code Instructions

You are working inside a StudyOS v1 course workspace.

## Standing Rules

- Keep the implementation lean and course-focused.
- Treat `raw_source.path` as an external read-only source folder.
- Do not modify `inputs/`; treat raw course material as read-only.
- Work batch by batch.
- Treat batches as conceptual lectures, topics, or modules whenever possible.
- Use exercises as supporting practice sources unless they are explicitly tutorial or conceptual batches.
- Do not create separate master notes for an exercise file attached to a conceptual batch.
- Produce source digests before learning cores.
- Produce learning cores before final outputs.
- Ensure final outputs are derived from learning cores.
- Include source references for course claims.
- Record weak points and unresolved questions.
- Validate after each batch before synthesis.
- Use visual analysis only when a chart, table, diagram, or image is important to understanding the material.

## Installation Setup

When installing StudyOS into a course folder, behave like a setup wizard. Ask only for missing essentials, fill `subject.yaml` automatically, initialize the database, and do not import or process course files during installation.

Essential setup fields are subject name, raw source folder path, course level, course-material language, exam type, desired outputs, whether original files are read-only, and whether StudyOS should copy files into `inputs/`. Default to read-only originals and copying into `inputs/`.

After installation, point the user to `STUDYOS_GUIDE.md` and continue only when the user chooses the next skill.

## v1 Exclusions

- No Graphify.
- No hooks.
- No subagents.
- No optional modules.
- No Anki export.
- No Obsidian export.
- No dashboards or web apps.

## Expected Flow

Follow `templates/workflow.yaml`:

1. `install`
2. `import_sources`
3. `inventory`
4. `process_batch`
5. `validate`
6. `synthesize`

Prefer small, testable edits. Keep generated study material traceable to sources.
