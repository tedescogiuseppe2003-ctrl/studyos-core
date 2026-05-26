---
name: study-os-sort-inputs
description: Safely sort raw course files from the course root or unsorted/ into approved inputs/ subfolders through a reviewed sorting plan.
---

# StudyOS Sort Inputs

Use this skill before `study-os-inventory` when raw course files are still in the course root or `unsorted/`.

This skill has two modes:

1. Proposal mode creates `working/inventory/sorting_plan.md` and does not move files.
2. Execute mode reads the approved `working/inventory/sorting_plan.md`, moves only approved files, and creates `working/inventory/sorting_log.md`.

## Scope

Sort intake files only. Do not process course material, generate study outputs, summarize content, or invent file contents.

Keep v1.1 lean. Do not add Graphify, hooks, subagents, Anki export, Obsidian export, dashboards, or web apps.

## Source Locations

Scan only:

- the course root;
- `unsorted/`.

Ignore:

- `.git/`
- `study-os/`
- `working/`
- `outputs/`
- `review/`
- `inputs/`
- `.agents/`
- `.claude/`
- `__pycache__/`
- `.DS_Store` files

Do not recursively scan ignored folders even if they appear inside `unsorted/`.

## Destination Folders

Files may be proposed or moved only into these folders:

- `inputs/slides/`
- `inputs/readings/`
- `inputs/notes/`
- `inputs/exercises/`
- `inputs/exams/`
- `inputs/transcripts/`
- `inputs/miscellaneous/`

Preserve original file extensions. Use clean filenames only when useful, such as removing obvious download prefixes, duplicate counters, or unsafe characters.

## Proposal Mode

Use proposal mode when the user asks to sort, inspect, classify, plan, prepare intake, or create a sorting plan without explicitly approving execution.

Proposal mode may read:

- filenames and paths in the course root and `unsorted/`;
- minimal file metadata needed for classification;
- a small skim of file contents only when filename and metadata are insufficient.

Proposal mode may write:

- `working/inventory/sorting_plan.md`

Proposal mode must not:

- modify files;
- move files;
- rename files;
- delete files;
- write inside `inputs/`;
- generate digests, learning cores, study outputs, validation reports, or synthesis artifacts.

For each discovered raw file, add one row to `working/inventory/sorting_plan.md` with:

- current path;
- proposed destination folder;
- proposed clean filename if useful;
- confidence: `high`, `medium`, or `low`;
- reason;
- action: `move`, `skip`, or `needs review`.

If uncertain, use `confidence: low` and either propose `inputs/miscellaneous/` or mark `action: needs review`.

## Execute Mode

Use execute mode only when the user explicitly asks to execute, apply, or run an approved sorting plan.

Execute mode may read:

- `working/inventory/sorting_plan.md`;
- source files referenced by approved `move` rows only enough to confirm they exist;
- destination paths only enough to prevent collisions.

Execute mode may write:

- files moved into approved `inputs/` destination folders;
- `working/inventory/sorting_log.md`.

Execute mode must not:

- move any file not listed in `working/inventory/sorting_plan.md`;
- move rows marked `skip` or `needs review`;
- delete files;
- overwrite destination files;
- change file contents;
- process course material;
- generate study outputs.

Before moving each file:

1. Confirm the source path exists and is outside ignored folders.
2. Confirm the destination folder is one of the approved `inputs/` subfolders.
3. Confirm the destination filename preserves the original extension.
4. Confirm the destination path does not already exist.
5. If any check fails, skip the file and record the reason in `sorting_log.md`.

## Classification Guidance

Classify conservatively from filenames, folder names, extensions, and minimal skimming when needed.

- Slides: lecture slides, decks, presentation exports, files named like slides, lecture deck, `L01`, `Lecture 1`, or similar.
- Readings: articles, papers, book chapters, required or optional readings, textbook extracts.
- Notes: instructor notes, student notes, summaries, handwritten notes, lecture notes when not clearly slide decks.
- Exercises: problem sets, tutorials, labs, assignments, worksheets, solution practice, exercise sheets.
- Exams: past exams, mock exams, quizzes, midterms, finals, exam solutions.
- Transcripts: lecture transcripts, subtitles, captions, recorded lecture text.
- Miscellaneous: files that are relevant but do not clearly fit another destination.

When a file appears unrelated to the course or should remain in place, mark `action: skip` with a clear reason.

## Sorting Plan Format

Create `working/inventory/sorting_plan.md` with this structure:

```markdown
# Sorting Plan

Generated: YYYY-MM-DD
Mode: proposal

## Summary

- Files scanned:
- Proposed moves:
- Needs review:
- Skipped:

## Plan

| Current path | Proposed destination folder | Proposed clean filename | Confidence | Reason | Action |
|---|---|---|---|---|---|
```

Use relative paths from the course root. Leave `Proposed clean filename` blank when the original filename should be preserved.

## Sorting Log Format

Create `working/inventory/sorting_log.md` during execute mode with this structure:

```markdown
# Sorting Log

Executed: YYYY-MM-DD
Plan: working/inventory/sorting_plan.md

## Summary

- Moved:
- Skipped:
- Failed:

## Log

| Source | Destination | Status | Reason |
|---|---|---|---|
```

Record every planned `move` row, including skipped or failed rows.

## Workflow

### Proposal mode workflow

1. Run from the course root unless the user supplies another root.
2. Ensure `working/inventory/` exists.
3. Scan only the course root and `unsorted/`, excluding ignored folders and `.DS_Store` files.
4. Classify each discovered raw file conservatively.
5. Skim only enough content to classify when path, filename, and metadata are insufficient.
6. Write `working/inventory/sorting_plan.md`.
7. Report the plan path, scanned count, proposed moves, skipped files, and files needing review.

### Execute mode workflow

1. Run from the course root unless the user supplies another root.
2. Read `working/inventory/sorting_plan.md`.
3. Create approved destination folders if missing.
4. For each row with `action: move`, validate source and destination safety checks.
5. Move valid files without overwriting anything.
6. Skip invalid, missing, conflicting, low-confidence unapproved, `skip`, or `needs review` rows.
7. Write `working/inventory/sorting_log.md`.
8. Report moved count, skipped count, failed count, and log path.

## Quality Bar

- Proposal mode is non-destructive.
- Execute mode is driven only by the approved sorting plan.
- No files are deleted.
- No destination files are overwritten.
- File contents are never modified.
- Uncertain files are handled conservatively.
- `inputs/` contains only sorted raw course material after execution.
