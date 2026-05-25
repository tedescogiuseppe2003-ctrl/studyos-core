---
name: study-os-synthesize
description: Create final StudyOS synthesis only after batches have inventories, digests, learning cores, outputs, and validation results.
---

# StudyOS Synthesize

Use this skill only for final course-level synthesis after batch work already exists.

## Preconditions

- Inventory and batch plan exist.
- Relevant batches have source digests.
- Relevant batches have learning cores.
- Requested outputs have been validated or validation gaps are known.

## Workflow

1. Review existing batch plans, learning cores, outputs, validation notes, weak points, and unresolved questions.
2. Identify which batches are ready for synthesis and which remain blocked.
3. Create final synthesis artifacts only from learning cores, validated outputs, and recorded validation findings.
4. Preserve source references and unresolved-question markers.
5. Place final artifacts in the appropriate `outputs/` location.
6. Report remaining gaps instead of inventing missing material.

## Guardrails

- This is the only skill that may work across the whole course, and only after batch artifacts exist.
- Treat `inputs/` as read-only.
- Do not base final outputs directly on raw inputs when learning cores are available.
- Do not skip validation findings.
- Use lazy visual analysis only when existing notes show that a visual source matters.
