# StudyOS Course Core

StudyOS is a VS Code-based full-course study-material pipeline.

It turns raw university course material into structured study outputs through a lean, batch-based workflow.

## Target workflow

raw course folder / unsorted/
→ sort files into inputs/
→ inventory
→ conceptual batch plan
→ process all batches sequentially
→ validate each batch
→ repair if needed
→ synthesize final outputs

Raw files may initially exist directly in the course root or in unsorted/. Before inventory, files are sorted into inputs/ through a reviewed sorting plan. After sorting, inputs/ is read-only.

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

- study-os-sort-inputs
- improved conceptual batch planning
- study-os-process-course

v1.1 extends v1 without changing the core output model. It adds safe intake sorting, stronger conceptual batch planning, and a course-level runner that processes batches in order.

### study-os-sort-inputs

- Detect raw files in the course root and unsorted/.
- Create a sorting plan before moving files.
- Sort approved files into inputs/ subfolders.
- Leave inputs/ read-only after sorting.

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

- raw course root: possible initial location for unsorted source files
- unsorted/: optional intake area for raw source files before sorting
- inputs/: sorted raw course material, read-only after sorting
- working/: intermediate digests and learning cores
- outputs/: final study material
- review/: weak points, validation, unresolved questions
- study-os/: scripts, skills, config, state

## Rules

- Sort raw files safely through a sorting plan before moving them into inputs/.
- Never modify files in inputs/ after sorting.
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

- study-os-sort-inputs
- study-os-inventory with improved conceptual batch planning
- study-os-process-course

## v1 testing philosophy

Build step by step.

Each step must be tested before moving forward.

One prompt = one task = one test = one commit.
