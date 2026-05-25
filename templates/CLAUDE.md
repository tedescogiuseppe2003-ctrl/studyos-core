# StudyOS Claude Code Instructions

You are working inside a StudyOS v1 course workspace.

## Standing Rules

- Keep the implementation lean and course-focused.
- Do not modify `inputs/`; treat raw course material as read-only.
- Work batch by batch.
- Produce source digests before learning cores.
- Produce learning cores before final outputs.
- Ensure final outputs are derived from learning cores.
- Include source references for course claims.
- Record weak points and unresolved questions.
- Validate after each batch before synthesis.
- Use visual analysis only when a chart, table, diagram, or image is important to understanding the material.

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
2. `inventory`
3. `process_batch`
4. `validate`
5. `synthesize`

Prefer small, testable edits. Keep generated study material traceable to sources.
