# StudyOS Course Core

StudyOS is a VS Code-based full-course study-material pipeline.

It turns raw university course material into structured study outputs through a lean, manual, step-by-step workflow.

## Final installation and setup UX

The user opens an existing course folder in VS Code. That folder becomes the StudyOS workspace.

The course folder may already contain raw course files before StudyOS is installed. Any pre-existing course files are treated as original raw source files.

Original raw source files must never be moved, renamed, deleted, overwritten, or modified. StudyOS may read them and, when the user agrees, copy them into `inputs/` for processing.

The StudyOS core repo lives outside the course folder, usually at:

`~/Developer/studyos-core`

The user does not manually edit the core repo during normal use. The agent installs StudyOS into the currently open course folder using the external core repo.

Typical user request:

`Install StudyOS in this folder using ~/Developer/studyos-core.`

Immediately after installation, before importing or processing any files, the agent must inspect the folder name and visible raw course files, then propose a complete `subject.yaml` setup using reasonable defaults.

The user should not manually edit `subject.yaml` unless they want to.

## Proposal-first setup

The setup proposal happens immediately after installation and before import, inventory, batch planning, validation, or output generation.

The final install UX is:

1. User opens an existing course folder in VS Code.
2. User asks: `Install StudyOS in this folder using ~/Developer/studyos-core.`
3. Agent installs StudyOS from the external core repo.
4. Agent initializes or confirms local StudyOS state.
5. Agent syncs latest scripts, skills, and config.
6. Agent inspects the folder name and visible raw course files read-only.
7. Agent proposes a complete `subject.yaml` setup.
8. Agent asks the user to approve the setup or request modifications.
9. Agent fills `subject.yaml` only after user approval.
10. Agent stops without importing, inventorying, planning, validating, or processing material.

The proposal must include:

- subject name
- course level: Bachelor / Master / PhD / Other
- language of course material
- exam type: written / oral / project / mixed / unknown
- raw/original course folder path
- whether original files are read-only, default yes
- whether StudyOS should copy files into `inputs/`, default yes
- desired outputs:
  - master notes
  - formula sheets
  - flashcards
  - exam questions
  - cheat sheets
  - study plan
  - final review pack
- quality/depth mode:
  - economy
  - standard
  - rigorous
- visual handling depth:
  - minimal
  - standard
  - rigorous
- formula handling depth:
  - normal
  - rigorous
- validation depth:
  - structural only
  - standard
  - rigorous audit

The agent should infer defaults from the folder name and visible files. It should not ask setup questions one by one unless the proposed setup is impossible to infer.

Technical or formula-heavy subjects should default to rigorous setup. This includes finance, risk management, statistics, econometrics, mathematics, derivatives, portfolio theory, quantitative methods, and similar courses.

Standard defaults are appropriate for non-technical courses unless visible files or the folder name suggest higher rigor.

After presenting the proposal, the agent asks:

`Do you approve this setup, or do you want modifications?`

If the user requests modifications, the agent updates the proposal and asks again. These approved setup values are stored in `subject.yaml`. The installing agent writes the file automatically only after approval.

After installation and approved setup, the user manually calls StudyOS skills step by step. StudyOS does not add a master orchestration skill or automatic course runner.

## Installed course structure

```text
course-folder/
├── STUDYOS_GUIDE.md
├── subject.yaml
├── AGENTS.md
├── CLAUDE.md
│
├── inputs/
│   ├── slides/
│   ├── readings/
│   ├── notes/
│   ├── exercises/
│   ├── exams/
│   ├── transcripts/
│   └── miscellaneous/
│
├── analysis/
│   ├── inventory/
│   ├── batches/
│   ├── visual/
│   ├── validation/
│   └── state/
│
├── outputs/
│   ├── notes/
│   ├── formulas/
│   ├── flashcards/
│   ├── questions/
│   ├── cheat-sheets/
│   ├── study-plan/
│   └── final-pack/
│
├── exports/
│   └── pdf/
│       ├── unmerged/
│       └── merged/
│
├── review/
│   ├── weak-points.md
│   ├── unresolved-questions.md
│   ├── visual-issues.md
│   ├── source-coverage.md
│   ├── validation-report.md
│   └── progress-tracker.md
│
└── study-os/
    ├── scripts/
    ├── skills/
    └── config/
```

## Quality and depth modes

`economy` mode is faster, uses fewer tokens, creates lighter notes, performs minimal visual checks, and is suitable for low-stakes review.

`standard` mode is the default. It balances precision and efficiency, includes inventory, conceptual batch planning, source analysis, output generation, validation, and visual screening.

`rigorous` mode is slower and more precise. It uses deeper formula handling, stronger validation, and deeper visual analysis when relevant. It is suitable for exam-critical technical courses.

Visual handling depth controls how aggressively StudyOS inspects diagrams, charts, tables, screenshots, and other visual course material.

Formula handling depth controls how carefully StudyOS extracts, checks, cites, and audits mathematical or technical formulas.

Validation depth controls how deeply StudyOS checks structure, citations, completeness, formula provenance, stale outputs, weak points, and unresolved questions.

Quality modes, model routing, and targeted repair remain part of the system.

## Final user-facing skills

- `studyos-import`
- `studyos-plan`
- `studyos-batch`
- `studyos-validate`
- `studyos-course`
- `studyos-merge`
- `studyos-export`

There is no master orchestration skill. The user manually calls these skills one step at a time after installation and setup approval.

Visual screening is integrated into `studyos-batch`, `studyos-course`, and `studyos-validate`. It is not a separate user-facing skill.

`studyos-merge` replaces the older full-course consolidation concept. StudyOS should use merge language for full-course consolidation.

## Target workflow

existing course folder opened in VS Code
-> install StudyOS from external core repo
-> initialize local StudyOS state
-> sync latest scripts, skills, and config
-> inspect folder name and visible raw files
-> propose complete setup
-> ask user to approve or modify
-> fill `subject.yaml` after approval
-> user manually calls `studyos-import`
-> import proposal
-> approved copy into `inputs/`
-> inventory
-> first conceptual batch plan
-> user manually calls `studyos-plan` to refine the conceptual batch plan
-> user manually calls `studyos-batch` for one batch at a time
-> user manually calls `studyos-validate` after each batch or repair pass
-> user manually calls `studyos-course` for course-level outputs
-> user manually calls `studyos-merge` for merged full-course outputs
-> user manually calls `studyos-export` for unmerged and merged PDF exports

After setup, the user manually calls individual StudyOS skills step by step. StudyOS does not add a master orchestration skill or automatic course runner.

## Current v1 core

v1 assumes approved course material is copied into `inputs/` before processing begins.

inputs/
-> `studyos-import`
-> analysis/inventory/
-> analysis/batches/
-> analysis/visual/
-> analysis/validation/
-> outputs/
-> review/
-> `studyos-course`
-> `studyos-merge`
-> `studyos-export`

## Source import model

- The raw/original course folder path is stored in `subject.yaml` under `raw_source.path`.
- The original raw source folder may be the same folder the user opened in VS Code.
- StudyOS scans the original source folder read-only.
- StudyOS creates an import proposal before copying files.
- StudyOS copies approved files into `inputs/` subfolders when the user chooses the default copy strategy.
- StudyOS never moves, deletes, renames, overwrites, or modifies original source files.
- StudyOS never overwrites destination files during import.
- After import, `inputs/` is treated as read-only for processing.

`studyos-import` merges import and inventory work:

- import proposal
- approved import execution
- inventory
- first conceptual batch plan

## Conceptual batch planning

- Batches must represent conceptual topics, lectures, or modules.
- `studyos-import` creates the first conceptual batch plan from the copied inputs and inventory.
- `studyos-plan` refines the conceptual batch plan before batch processing.
- Exercises, readings, transcripts, notes, and exams usually support conceptual batches.
- Exercises should not normally become standalone master-note batches.
- Standalone exercise batches are only appropriate when they are explicitly tutorial/conceptual material or no related conceptual batch can be identified.

## Outputs and exports

Batch-level outputs are written under `outputs/` as unmerged material. These preserve the batch structure and are useful for review, repair, and incremental study.

Course-level and merged outputs are also written under `outputs/`, including consolidated notes, formulas, flashcards, questions, cheat sheets, study plans, and the final review pack.

`studyos-export` exports both forms:

- unmerged batch-level PDF exports to `exports/pdf/unmerged/`
- merged full-course PDF exports to `exports/pdf/merged/`

Unmerged exports should preserve batch boundaries. Merged exports should represent the cleaned, consolidated full-course result produced by `studyos-merge`.

## Main folders

- StudyOS workspace: the existing course folder opened in VS Code
- original raw source files: pre-existing course material, always treated as read-only
- external StudyOS core repo: source of installer, templates, skills, and scripts, usually `~/Developer/studyos-core`
- `inputs/`: imported raw course material copied from the original source, read-only after import
- `analysis/`: inventory, batch plans, visual analysis, validation records, and processing state
- `outputs/`: batch-level, course-level, and merged study material
- `exports/`: exported deliverables, including unmerged and merged PDFs
- `review/`: weak points, unresolved questions, visual issues, source coverage, validation reports, and progress tracking
- `study-os/`: scripts, skills, and config
- `subject.yaml`: course configuration filled from the approved setup proposal

## Rules

- The existing course folder becomes the StudyOS workspace.
- Treat pre-existing course files as original raw source files.
- Analyze the original raw source folder read-only.
- Import raw files safely through an import proposal before copying them into `inputs/`.
- Copy only approved files into `inputs/`.
- Never move, delete, rename, overwrite, or modify files in the original raw source folder.
- Never overwrite destination files during import.
- Never modify files in `inputs/` after import.
- After installation, infer and propose a complete setup from the folder name and visible raw files.
- Ask the user to approve or modify the proposed setup.
- Store approved setup values in `subject.yaml`.
- Fill `subject.yaml` only after user approval.
- Do not import, inventory, plan, validate, or process material during installation.
- Process material by conceptual batch, not all at once.
- Batches should represent topics, lectures, or modules.
- Use exercises, readings, transcripts, notes, and exams as supporting sources when they belong to a conceptual batch.
- Do not create separate master notes for exercise files attached to conceptual batches.
- Create source analysis before final outputs.
- Create learning-oriented batch outputs before merged course outputs.
- Merged full-course outputs must be based on validated batch and course outputs.
- Use source references.
- Track weak points and unresolved questions.
- Validate outputs after each batch.
- Repair blocking validation issues before continuing to later batches.
- Use visual analysis according to the configured visual handling depth inside batch, course, and validation skills.
- Use formula handling according to the configured formula handling depth.
- Use validation according to the configured validation depth.
- Preserve the manual skill-by-skill workflow after setup.
- Do not add a master orchestration skill.
- Do not add Graphify yet.
- Do not add hooks yet.
- Do not add Anki export yet.
- Do not add dashboards or web apps.

## Explicitly out of scope for now

- master orchestration skill
- Graphify
- hooks
- Anki
- dashboard

## v1 testing philosophy

Build step by step.

Each step must be tested before moving forward.

One prompt = one task = one test = one commit.
