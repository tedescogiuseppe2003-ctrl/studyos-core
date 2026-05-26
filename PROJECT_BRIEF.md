# StudyOS Course Core

StudyOS is a VS Code-based full-course study-material pipeline.

It turns raw university course material into structured study outputs through a lean, batch-based workflow.

## Target workflow

raw source folder
→ import plan
→ copy into inputs/
→ inventory
→ conceptual batch plan
→ process all batches sequentially
→ validate each batch
→ repair if needed
→ synthesize final outputs

The original subject folder is always read-only. StudyOS analyzes it in place and copies classified files into a separate StudyOS workspace under `inputs/` through a reviewed import plan. After import, `inputs/` is read-only for processing.

## Current v1 core

v1 assumes course material is already arranged under inputs/.

inputs/
→ inventory
→ batch plan
→ working/digests/
→ working/learning-cores/
→ outputs/
→ review/validation
→ final synthesis

## Planned v1.1 upgrades

- study-os-import-sources
- improved conceptual batch planning
- study-os-process-course

v1.1 extends v1 without changing the core output model. It adds safe read-only source import, stronger conceptual batch planning, and a course-level runner that processes batches in order.

### study-os-import-sources

- Read the original raw source folder from `subject.yaml` under `raw_source.path`.
- Scan the original source folder read-only.
- Create an import plan before copying files.
- Copy approved files into `inputs/` subfolders.
- Never move, delete, rename, or modify original source files.
- Leave `inputs/` read-only after import.

### Improved conceptual batch planning

- Batches must represent conceptual topics, lectures, or modules.
- Exercises, readings, transcripts, notes, and exams usually support conceptual batches.
- Exercises should not normally become standalone master-note batches.
- Standalone exercise batches are only appropriate when they are explicitly tutorial/conceptual material or no related conceptual batch can be identified.

### study-os-process-course

- Read the conceptual batch plan.
- Process batches sequentially.
- Validate each batch before continuing.
- Repair a batch when validation finds blocking issues.
- Continue only after the current batch is acceptable.
- Synthesize final outputs after planned batches are processed and validated.

## Main folders

- original raw source folder: external course material folder, always read-only
- StudyOS workspace: separate working folder containing StudyOS config, inputs, working files, outputs, and review artifacts
- inputs/: imported raw course material copied from the original source, read-only after import
- working/: intermediate digests and learning cores
- outputs/: final study material
- review/: weak points, validation, unresolved questions
- study-os/: scripts, skills, config, state

## Rules

- Analyze the original raw source folder read-only.
- Import raw files safely through an import plan before copying them into `inputs/`.
- Never move, delete, rename, or modify files in the original raw source folder.
- Never overwrite destination files during import.
- Never modify files in `inputs/` after import.
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
- Use lazy visual analysis only when charts, tables, diagrams, or images are important.
- Do not add Graphify yet.
- Do not add subagents yet.
- Do not add hooks yet.
- Do not add Anki export yet.
- Do not add Obsidian export yet.
- Do not add dashboards or web apps.

## v1 skills

- study-os-install
- study-os-inventory
- study-os-process-batch
- study-os-validate
- study-os-synthesize

## v1.1 planned skills

- study-os-import-sources
- study-os-inventory with improved conceptual batch planning
- study-os-process-course

## v1 testing philosophy

Build step by step.

Each step must be tested before moving forward.

One prompt = one task = one test = one commit.
