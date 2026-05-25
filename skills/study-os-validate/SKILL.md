---
name: study-os-validate
description: Validate StudyOS batch outputs against their learning cores, source digests, and source references after processing.
---

# StudyOS Validate

Use this skill after a batch has been processed or when the user asks to inspect output quality.

## Workflow

1. Identify the batch to validate.
2. Check that source digests exist before learning cores, and learning cores exist before outputs.
3. Verify outputs are grounded in the batch learning cores and include source references.
4. Check for missing topics, unsupported claims, weak points, unresolved questions, and citation problems.
5. Write validation notes or issues under `review/` or `working/validation/`.
6. Update SQLite validation status when applicable.
7. Recommend focused fixes for the same batch before moving on.

## Guardrails

- Validate by batch, not across the entire course.
- Treat `inputs/` as read-only.
- Do not rewrite course outputs unless the user asks for fixes.
- Use lazy visual analysis only when a visual source appears important to validation.
- Do not synthesize final course material during validation.
