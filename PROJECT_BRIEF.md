# StudyOS Course Core v1

StudyOS is a VS Code-based full-course study-material pipeline.

It processes university course material by batch and transforms raw sources into structured study outputs.

## Core pipeline

inputs/
→ inventory
→ batch plan
→ working/digests/
→ working/learning-cores/
→ outputs/
→ review/validation
→ final synthesis

## Main folders

- inputs/: raw course material, read-only
- working/: intermediate digests and learning cores
- outputs/: final study material
- review/: weak points, validation, unresolved questions
- study-os/: scripts, skills, config, state

## Rules

- Never modify files in inputs/.
- Process material by batch, not all at once.
- Create source digests before final outputs.
- Create learning cores before final outputs.
- Final outputs must be based on learning cores.
- Use source references.
- Track weak points and unresolved questions.
- Validate outputs after each batch.
- Use lazy visual analysis only when charts, tables, diagrams, or images are important.
- Do not add Graphify in v1.
- Do not add subagents in v1.
- Do not add hooks in v1.
- Do not add Anki export in v1.
- Do not add Obsidian export in v1.
- Do not add dashboards or web apps in v1.

## v1 skills

- study-os-install
- study-os-inventory
- study-os-process-batch
- study-os-validate
- study-os-synthesize

## v1 testing philosophy

Build step by step.

Each step must be tested before moving forward.

One prompt = one task = one test = one commit.