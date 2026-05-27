---
name: study-os-import-sources
description: Safely classify external raw course files from subject.yaml raw_source.path and copy approved files into StudyOS inputs/ folders through a reviewed import plan.
---

# StudyOS Import Sources

Use this skill before `study-os-inventory` when course files live in an original source folder outside the StudyOS workspace.

This skill has two modes:

1. Proposal mode creates `working/inventory/import_plan.md` and does not copy, move, rename, delete, or modify files.
2. Execute mode reads the approved `working/inventory/import_plan.md`, copies only approved files into `inputs/`, and creates `working/inventory/import_log.md`.

## Scope

Import intake files only. Do not process course material, generate study outputs, summarize content, or invent file contents.

Keep v1.1 lean. Do not add Graphify, hooks, subagents, Anki export, Obsidian export, dashboards, or web apps.

## Model routing and efficiency

Use the cheapest sufficient model. Start with a lower tier and escalate only when the task requires deeper reasoning. Do not sacrifice precision for speed when exam relevance is high, but do not use deep reasoning for mechanical tasks.

Tiers:

- `fast`: setup questions, config filling, filename-based classification, simple formatting, import proposal when obvious, inventory review.
- `balanced`: batch plan repair, digest creation, normal concept explanation, normal output generation, flashcards, exam questions.
- `deep`: formulas, derivations, technical finance/statistics/econometrics explanations, difficult conceptual synthesis, essential visual analysis, formula screenshots, definition screenshots, complex charts/tables/diagrams.
- `audit`: validation, source-grounding review, hallucination detection, final synthesis review.
- `script`: deterministic execution, import execution, hashing, inventory script, validation scripts, sync/install.

For this skill:

- Proposal mode is `fast` when filenames, folder names, and extensions make the import destination obvious.
- Escalate proposal mode to `balanced` only when filenames are ambiguous and minimal content skimming is needed to classify course files.
- Execute mode is `script` only. Use deterministic checks and file operations, not reasoning-heavy review.
- Never use `deep` for import mechanics.

## Preflight

Before doing any import work, confirm:

- `subject.yaml` exists;
- `subject.yaml` contains `raw_source.path`;
- `raw_source.path` exists and is a directory;
- `study-os/` exists;
- `working/inventory/` exists or can be created.

If any preflight item is missing, stop and report:

- what is missing;
- why import cannot continue;
- which skill to run first.

Use this guidance:

- Missing `subject.yaml` or `study-os/`: run `study-os-install` first.
- Missing or invalid `raw_source.path`: fill `subject.yaml` from setup answers before importing.
- Missing `working/inventory/`: create it only if the StudyOS workspace is otherwise installed.

In execute mode, also confirm `working/inventory/import_plan.md` exists. If it is missing, stop and tell the user to run `study-os-import-sources` in proposal mode first.

## Source Location

Read the original raw source folder from:

- `subject.yaml` -> `raw_source.path`

The original source folder is read-only. Never write to it, rename anything in it, move anything from it, delete anything from it, or create helper files inside it.

Ignore system and hidden folders anywhere in the raw source tree, including:

- folders whose names begin with `.`
- `__pycache__/`
- `.DS_Store` files
- `Thumbs.db`
- `desktop.ini`

Do not recursively scan ignored folders.

If `raw_source.path` is the StudyOS workspace root because the user installed StudyOS into an existing course folder, also ignore StudyOS-managed paths:

- `inputs/`
- `working/`
- `outputs/`
- `review/`
- `study-os/`
- `.agents/`
- `.claude/`
- `subject.yaml`
- `AGENTS.md`
- `CLAUDE.md`
- `STUDYOS_GUIDE.md`
- `workflow.yaml`
- `output-standards.yaml`
- `model-routing.yaml`

## Destination Folders

Files may be proposed or copied only into these folders:

- `inputs/slides/`
- `inputs/readings/`
- `inputs/notes/`
- `inputs/exercises/`
- `inputs/exams/`
- `inputs/transcripts/`
- `inputs/miscellaneous/`

Preserve original file extensions. Use clean filenames only when useful, such as removing obvious download prefixes, duplicate counters, or unsafe characters.

## Proposal Mode

Use proposal mode when the user asks to import, inspect, classify, plan, prepare intake, or create an import plan without explicitly approving execution.

Proposal mode may read:

- `subject.yaml`;
- filenames and paths under `raw_source.path`;
- minimal file metadata needed for classification;
- a small skim of file contents only when filename and metadata are insufficient.

Proposal mode may write:

- `working/inventory/import_plan.md`

Proposal mode must not:

- modify the original source folder;
- copy files;
- move files;
- rename files;
- delete files;
- write inside `inputs/`;
- generate digests, learning cores, study outputs, validation reports, or synthesis artifacts.

For each discovered raw file, add one row to `working/inventory/import_plan.md` with:

- source path, preferably relative to `raw_source.path`;
- proposed destination folder;
- proposed clean filename if useful;
- confidence: `high`, `medium`, or `low`;
- reason;
- action: `copy`, `skip`, or `needs review`.

If uncertain, use `confidence: low` and either propose `inputs/miscellaneous/` or mark `action: needs review`.

## Execute Mode

Use execute mode only when the user explicitly asks to execute, apply, or run an approved import plan.

Execute mode may read:

- `subject.yaml`;
- `working/inventory/import_plan.md`;
- source files referenced by approved `copy` rows only enough to confirm they exist and copy them;
- destination paths only enough to prevent collisions.

Execute mode may write:

- copied files inside approved `inputs/` destination folders;
- `working/inventory/import_log.md`.

Execute mode must not:

- copy any file not listed in `working/inventory/import_plan.md`;
- copy rows marked `skip` or `needs review`;
- move files;
- delete files;
- overwrite destination files;
- change source file contents;
- write anywhere outside `inputs/` except `working/inventory/import_log.md`;
- process course material;
- generate study outputs.

Before copying each file:

1. Confirm the source path exists under `raw_source.path`.
2. Confirm the destination folder is one of the approved `inputs/` subfolders.
3. Confirm the destination filename preserves the original extension.
4. If the destination exists, append a numeric suffix.
5. If any safety check fails, skip the file and record the reason in `import_log.md`.

## Classification Guidance

Classify conservatively from filenames, folder names, extensions, and minimal skimming when needed.

- Slides: lecture slides, decks, presentation exports, files named like slides, lecture deck, `L01`, `Lecture 1`, or similar.
- Readings: articles, papers, book chapters, required or optional readings, textbook extracts.
- Notes: instructor notes, student notes, summaries, handwritten notes, lecture notes when not clearly slide decks.
- Exercises: problem sets, tutorials, labs, assignments, worksheets, solution practice, exercise sheets.
- Exams: past exams, mock exams, quizzes, midterms, finals, exam solutions.
- Transcripts: lecture transcripts, subtitles, captions, recorded lecture text.
- Miscellaneous: files that are relevant but do not clearly fit another destination.

When a file appears unrelated to the course or should not be imported, mark `action: skip` with a clear reason.

## Import Plan Format

Create `working/inventory/import_plan.md` with this structure:

```markdown
# Import Plan

Generated: YYYY-MM-DD
Mode: proposal
Raw source: /absolute/path/from/subject.yaml

## Summary

- Files scanned:
- Proposed copies:
- Needs review:
- Skipped:

## Plan

| Source path | Proposed destination folder | Proposed clean filename | Confidence | Reason | Action |
|---|---|---|---|---|---|
```

Use source paths relative to `raw_source.path` when practical. Leave `Proposed clean filename` blank when the original filename should be preserved.

## Import Log Format

Create `working/inventory/import_log.md` during execute mode with this structure:

```markdown
# Import Log

Executed: YYYY-MM-DD
Plan: working/inventory/import_plan.md

## Summary

- Copied:
- Skipped:
- Failed:

## Log

| Source | Destination | Status | Reason |
|---|---|---|---|
```

Record every planned `copy` row, including skipped or failed rows.

## Workflow

### Proposal mode workflow

1. Run from the StudyOS workspace root unless the user supplies another root.
2. Read `subject.yaml` and resolve `raw_source.path`.
3. Ensure `working/inventory/` exists.
4. Scan the raw source folder read-only, excluding system and hidden folders and files.
5. Classify each discovered raw file conservatively.
6. Skim only enough content to classify when path, filename, and metadata are insufficient.
7. Write `working/inventory/import_plan.md`.
8. Report the plan path, scanned count, proposed copies, skipped files, and files needing review.

### Execute mode workflow

1. Run from the StudyOS workspace root unless the user supplies another root.
2. Read `subject.yaml` and resolve `raw_source.path`.
3. Read `working/inventory/import_plan.md`.
4. Create approved destination folders if missing.
5. For each row with `action: copy`, validate source and destination safety checks.
6. Copy valid files without overwriting anything; append numeric suffixes for collisions.
7. Skip invalid, missing, conflicting, low-confidence unapproved, `skip`, or `needs review` rows.
8. Write `working/inventory/import_log.md`.
9. Report copied count, skipped count, failed count, and log path.

## Quality Bar

- Proposal mode is read-only against the original source folder.
- Execute mode is driven only by the approved import plan.
- No files are moved.
- No files are deleted.
- No destination files are overwritten.
- File contents are never modified.
- Uncertain files are handled conservatively.
- The original raw source folder remains unchanged.
