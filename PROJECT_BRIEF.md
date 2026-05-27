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

Immediately after installation, before importing or processing any files, the agent must ask the setup questions below and fill `subject.yaml` automatically from the answers.

The user should not manually edit `subject.yaml` unless they want to.

## Setup questions

The setup wizard happens immediately after installation and before import, inventory, batch planning, or output generation.

The agent must ask for:

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

These setup answers are stored in `subject.yaml`. The installing agent writes the file automatically.

## Quality and depth modes

`economy` mode is faster, uses fewer tokens, creates lighter notes, performs minimal visual checks, and is suitable for low-stakes review.

`standard` mode is the default. It balances precision and efficiency, includes digest creation, learning-core creation, output generation, validation, and visual screening.

`rigorous` mode is slower and more precise. It uses deeper formula handling, stronger validation, and deeper visual analysis when relevant. It is suitable for exam-critical technical courses.

Visual handling depth controls how aggressively StudyOS inspects diagrams, charts, tables, screenshots, and other visual course material.

Formula handling depth controls how carefully StudyOS extracts, checks, cites, and audits mathematical or technical formulas.

Validation depth controls how deeply StudyOS checks structure, citations, completeness, formula provenance, stale outputs, weak points, and unresolved questions.

## Target workflow

existing course folder opened in VS Code
-> install StudyOS from external core repo
-> ask setup questions
-> fill `subject.yaml`
-> copy raw files into `inputs/` when approved
-> inventory
-> conceptual batch plan
-> manually process one batch or skill step at a time
-> validate each batch
-> repair if needed
-> synthesize final outputs

After setup, the user manually calls individual StudyOS skills step by step. StudyOS does not add a master orchestration skill or automatic course runner.

## Current v1 core

v1 assumes course material is available under `inputs/` before processing begins.

inputs/
-> inventory
-> batch plan
-> working/digests/
-> working/learning-cores/
-> outputs/
-> review/validation
-> final synthesis

## Source import model

- The raw/original course folder path is stored in `subject.yaml` under `raw_source.path`.
- The original raw source folder may be the same folder the user opened in VS Code.
- StudyOS scans the original source folder read-only.
- StudyOS creates an import plan before copying files.
- StudyOS copies approved files into `inputs/` subfolders when the user chooses the default copy strategy.
- StudyOS never moves, deletes, renames, overwrites, or modifies original source files.
- StudyOS never overwrites destination files during import.
- After import, `inputs/` is treated as read-only for processing.

## Conceptual batch planning

- Batches must represent conceptual topics, lectures, or modules.
- Exercises, readings, transcripts, notes, and exams usually support conceptual batches.
- Exercises should not normally become standalone master-note batches.
- Standalone exercise batches are only appropriate when they are explicitly tutorial/conceptual material or no related conceptual batch can be identified.

## Main folders

- StudyOS workspace: the existing course folder opened in VS Code
- original raw source files: pre-existing course material, always treated as read-only
- external StudyOS core repo: source of installer, templates, skills, and scripts, usually `~/Developer/studyos-core`
- `inputs/`: imported raw course material copied from the original source, read-only after import
- `working/`: intermediate digests and learning cores
- `outputs/`: final study material
- `review/`: weak points, validation, unresolved questions
- `study-os/`: scripts, skills, config, state
- `subject.yaml`: course configuration filled from setup answers

## Rules

- The existing course folder becomes the StudyOS workspace.
- Treat pre-existing course files as original raw source files.
- Analyze the original raw source folder read-only.
- Import raw files safely through an import plan before copying them into `inputs/`.
- Never move, delete, rename, overwrite, or modify files in the original raw source folder.
- Never overwrite destination files during import.
- Never modify files in `inputs/` after import.
- Ask all setup questions immediately after installation and before import or processing.
- Store setup answers in `subject.yaml`.
- Process material by conceptual batch, not all at once.
- Batches should represent topics, lectures, or modules.
- Use exercises, readings, transcripts, notes, and exams as supporting sources when they belong to a conceptual batch.
- Do not create separate master notes for exercise files attached to conceptual batches.
- Create source digests before final outputs.
- Create learning cores before final outputs.
- Final outputs must be based on learning cores.
- Use source references.
- Track weak points and unresolved questions.
- Validate outputs after each batch.
- Repair blocking validation issues before continuing to later batches.
- Use visual analysis according to the configured visual handling depth.
- Use formula handling according to the configured formula handling depth.
- Use validation according to the configured validation depth.
- Preserve the manual skill-by-skill workflow after setup.
- Do not add a master orchestration skill.
- Do not add Graphify yet.
- Do not add subagents yet.
- Do not add hooks yet.
- Do not add Anki export yet.
- Do not add Obsidian export yet.
- Do not add dashboards or web apps.

## v1 skills

- study-os-install
- study-os-import-sources
- study-os-inventory
- study-os-process-batch
- study-os-validate
- study-os-synthesize

## v1 testing philosophy

Build step by step.

Each step must be tested before moving forward.

One prompt = one task = one test = one commit.
