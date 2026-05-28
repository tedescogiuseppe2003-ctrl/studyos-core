# StudyOS Core

StudyOS core is installed and synced from the external core repository, usually `~/Developer/studyos-core`.

## Normal Installation UX

The user opens an existing course folder in VS Code and asks:

> Install StudyOS in this folder using ~/Developer/studyos-core.

The agent runs `scripts/install_studyos.py`, initializes or confirms the database, runs `scripts/sync_studyos.py`, inspects the folder name and visible raw course files read-only, proposes a complete `subject.yaml` setup, asks for approval or modifications, fills `subject.yaml` only after approval, creates or updates `STUDYOS_GUIDE.md`, and stops.

Installation/setup does not import, inventory, plan, validate, process, merge, or export course material.

## Installed User-Facing Skills

Fresh installs and syncs install only these final skill names:

- `studyos-import`
- `studyos-plan`
- `studyos-batch`
- `studyos-validate`
- `studyos-course`
- `studyos-merge`
- `studyos-export`

There is no normal user workflow skill for installation and no master orchestration skill.

`studyos-merge` is the installed full-course consolidation skill.

## Normal User Workflow

After the setup proposal is approved and written to `subject.yaml`, use skills manually:

1. `studyos-import`
2. `studyos-plan`
3. `studyos-batch`
4. `studyos-validate`
5. `studyos-course`
6. `studyos-merge`
7. `studyos-export`

`studyos-import` is the combined import and inventory skill. It first writes `analysis/inventory/import_plan.md` from a read-only scan of `raw_source.path`, stops for approval, copies approved files into `inputs/` without moving originals or overwriting destinations, then writes `analysis/inventory/course_inventory.md` and `analysis/inventory/batch_plan.md`.

`studyos-plan` refines the first batch plan into conceptual batches. `studyos-batch` processes one selected batch. `studyos-validate` checks outputs and guides targeted repair. `studyos-course` processes remaining planned batches with validation after each batch. Visual screening is integrated into batch, course, and validation work; it is not a separate skill.

`studyos-merge` reads validated batch learning cores and batch outputs, then writes the final full-course structure:

- `outputs/notes/full_course_notes.md`
- `outputs/formulas/full_formula_sheet.md`
- `outputs/questions/full_exam_practice_questions.md`

Merge does not mean concatenate: it consolidates duplicate concepts, harmonizes notation, deduplicates formulas, identifies dependencies, preserves source references, prioritizes weak points, includes unresolved questions, includes likely exam questions, and carries exam-relevant visual findings.

`studyos-export` converts study-facing Markdown outputs into polished student deliverables. It exports unmerged batch outputs from `outputs/notes/Batch_*.md`, `outputs/formulas/Batch_*_formulas.md`, and `outputs/questions/Batch_*_questions.md` into category folders under `exports/pdf/unmerged/`. It exports merged full-course outputs into `exports/pdf/merged/`.

The export script is:

```sh
python3 study-os/scripts/export_outputs.py --root .
```

PDF is preferred when `pandoc` and a LaTeX PDF engine are available. If PDF dependencies are unavailable, the exporter writes print-ready HTML and reports the fallback. Flashcards, cheat sheets, study plans, final review packs, internal `analysis/`, `review/`, validation, and debug files are not exported by default.

## Installed Course Folder

A StudyOS course folder is self-explaining after install:

- `inputs/` contains approved copied course files. Originals stay protected at `subject.yaml` -> `raw_source.path`; import is copy-only and never moves, deletes, renames, overwrites, or edits raw files.
- `analysis/` contains working evidence: import plans, inventory, conceptual batch plans, batch digests, learning cores, visual notes, validation details, and processing state.
- `outputs/` contains reduced-scope study-facing Markdown outputs: notes, formula sheets, and exam practice questions.
- `exports/pdf/unmerged/` contains batch-level exports by category.
- `exports/pdf/merged/` contains consolidated full-course exports.
- `review/` contains weak points, unresolved questions, source coverage, visual issues, validation reports, and progress tracking.
- `study-os/` contains local scripts, installed skills, config, and state synced from the external core repo.

Quality modes are `economy`, `standard`, and `rigorous`. Economy is lighter and faster, standard is the default, and rigorous uses deeper formula, visual, and validation handling for exam-critical or technical courses. Model routing uses fast models for simple metadata work, balanced models for normal generation, deep models for formulas and merging, and audit models for validation.

If a preflight warning appears, stop and fix the missing prerequisite instead of forcing the current step. Common fixes are approving the setup, approving the import plan, running import before planning, running plan before batch processing, validating before merge, or repairing blocking validation findings before export.

## Install A New Subject

Run the installer from the core repo:

```sh
cd ~/Developer/studyos-core
python3 scripts/install_studyos.py ~/StudyOS-Test/TestCourse
```

The installer creates the subject folder structure, copies templates, copies course-local scripts into `study-os/scripts/`, installs final skills into `study-os/skills/`, `.agents/skills/`, and `.claude/skills/`, and initializes `study-os/state/studyos.sqlite`.

`install_studyos.py` is core-only and is not copied into installed subject folders.

After install, run sync from the same external core repo:

```sh
cd ~/Developer/studyos-core
python3 scripts/sync_studyos.py ~/StudyOS-Test/TestCourse
```

The installing agent then proposes setup and fills `subject.yaml` only after user approval.

## Sync An Existing Subject

Run sync from the core repo:

```sh
cd ~/Developer/studyos-core
python3 scripts/sync_studyos.py ~/StudyOS-Test/TestCourse
```

Sync updates course-local scripts in `study-os/scripts/`, replaces installed final skill folders in `study-os/skills/`, `.agents/skills/`, and `.claude/skills/`, removes old installed StudyOS skill folders, and updates `study-os/config/SKILLS_GUIDE.md`.

Sync does not touch raw course files or generated study work in `inputs/`, `outputs/`, `analysis/`, `review/`, `subject.yaml`, or `.git/`. It writes a sync log to `study-os/state/sync-log.md`.

Never run an old installed copy such as `study-os/scripts/install_studyos.py`. If one exists from an earlier install, `sync_studyos.py` removes it.

## Install Stops Before Course Work

During installation/setup, do not run any skill or script that imports, inventories, plans, summarizes, validates, processes, merges, or exports course material.
