---
name: study-os-process-batch
description: Process one StudyOS batch at a time by creating source digests first, then learning cores, then batch-specific study outputs with source references.
---

# StudyOS Process Batch

Use this skill when the user asks to process a specific batch from `working/inventory/batch_plan.md`.

## Workflow

1. Identify the requested batch and its source files.
2. Confirm the batch exists in the inventory or SQLite state.
3. Create source digests for that batch in `working/digests/`.
4. Create learning cores for that batch in `working/learning-cores/`, based on the digests.
5. Create only the requested batch outputs in `outputs/`, based on the learning cores.
6. Preserve source references throughout digest, learning core, and output files.
7. Update SQLite status for processed batch artifacts when applicable.
8. Run or prepare validation for the batch after processing.

## Guardrails

- Process one batch at a time unless the user explicitly names multiple batches.
- Treat `inputs/` as read-only. Never edit, move, or delete source files.
- Digest before learning core; learning core before outputs.
- Do not create final synthesis during batch processing.
- Use lazy visual analysis only when charts, tables, diagrams, or images are important to the batch.
- Track weak points and unresolved questions instead of hiding uncertainty.
