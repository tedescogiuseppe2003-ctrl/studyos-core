# StudyOS Claude Code Instructions

You are working inside a StudyOS v1 course workspace.

## Standing Rules

- Keep the implementation lean and course-focused.
- Keep StudyOS agent-driven: scripts handle installation, import, inventory, deterministic validation, and export; the agent handles source judgment, extraction, repair, and merging.
- Treat `raw_source.path` as an external read-only source folder.
- Do not modify `inputs/`; treat raw course material as read-only.
- Work batch by batch.
- Treat batches as conceptual lectures, topics, or modules whenever possible.
- Use exercises as supporting practice sources unless they are explicitly tutorial or conceptual batches.
- Do not create separate note outputs for an exercise file attached to a conceptual batch.
- Produce source digests before learning cores.
- Produce learning cores before final outputs.
- Ensure final outputs are derived from learning cores.
- Create only notes, formulas, and exam practice questions as default student-facing outputs.
- Treat notes as complete study notes, not summaries.
- Use display LaTeX for formulas.
- Treat exam practice questions as the active-recall/practice layer instead of flashcards.
- Include source references for course claims.
- Record weak points and unresolved questions.
- Validate after each batch before course-level and merged outputs.
- Use integrated visual screening in `studyos-batch`, `studyos-course`, and `studyos-validate` when a chart, table, diagram, or image is important to understanding the material.

## Agent Efficiency And Quality

- Output quality is the highest priority. Time and token optimization are useful only when they preserve exhaustive coverage and soundness.
- Optimize time and tokens by reading metadata, inventories, headings, slide titles, tables of contents, and obvious formula/exam signals before full source reads.
- Fully cover every assigned primary source and every assigned supporting source. Use selective reading only when the Source Coverage table can justify that a source is duplicate, irrelevant, unreadable, or deferred.
- Outputs may be long. Do not shorten notes, formulas, or exam answers by omitting unique input concepts, examples, caveats, assumptions, formulas, visuals, or exam signals.
- Spend saved tokens on complete notes, formula correctness, essential visuals, exam-quality practice questions, and validation repair.
- Use deeper reasoning only for hard concepts, formulas, notation conflicts, essential visuals, exam integration, and final merge decisions.
- Prefer targeted repair over broad regeneration. Preserve valid digest, learning-core, and output sections.
- Treat "perfect" as an operational target: no known unsupported claims, complete assigned-source coverage, display-quality formulas, clear expected answers, visible unresolved uncertainty, and no high or blocking validation findings.
- Validation and final review must fail outputs that are short because they dropped assigned-input coverage.

## Installation Setup

When installing StudyOS into a course folder, use the external core repo, usually `~/Developer/studyos-core`. Install and sync local scripts, skills, and config, inspect the folder name and visible raw course files read-only, propose a complete setup, ask the user to approve or modify it, write `subject.yaml` only after approval, and stop.

Essential setup fields are subject name, raw source folder path, course level, course-material language, exam type, the fixed default outputs, quality mode, visual handling depth, formula handling depth, validation depth, whether original files are read-only, and whether StudyOS should copy files into `inputs/`. Default to read-only originals and copy-only import into `inputs/`.

The setup proposal should include only these default study-facing outputs: notes, formulas, and exam practice questions. Do not ask whether to generate flashcards, cheat sheets, study plans, or final review packs during setup; those are not default outputs anymore and are deprecated/disabled. The reduced scope is intentional because fewer outputs means higher quality and better focus.

After installation, point the user to `STUDYOS_GUIDE.md` and continue only when the user chooses the next skill. Do not import, inventory, plan, process, validate, merge, or export during installation/setup.

## Folder Semantics

- `inputs/` contains approved copied raw material and is read-only after import.
- `analysis/` contains import plans, inventory, batch plans, digests, learning cores, visual notes, validation details, and state.
- `outputs/` contains study-facing Markdown outputs: notes, formula sheets, and exam practice questions.
- `analysis/` and `review/` are important internal quality-support areas, but they are not student-facing outputs and are not exported by default.
- `exports/pdf/unmerged/` contains batch-level exports.
- `exports/pdf/merged/` contains consolidated full-course exports.
- `review/` contains weak points, unresolved questions, source coverage, visual issues, validation reports, and progress tracking.

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

1. Install StudyOS.
2. Approve setup.
3. `studyos-import`
4. `studyos-plan`
5. `studyos-batch`
6. `studyos-validate`
7. `studyos-course`
8. `studyos-merge`
9. `studyos-export`

Prefer small, testable edits. Keep generated study material traceable to sources.
