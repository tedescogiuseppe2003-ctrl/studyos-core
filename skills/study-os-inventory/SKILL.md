---
name: study-os-inventory
description: Build or refresh the StudyOS source inventory for one installed subject folder by scanning input file metadata, updating SQLite, and creating inventory planning files.
---

# StudyOS Inventory

Use this skill to run the inventory step before any batch processing.

## Workflow

1. Run from the installed subject folder root.
2. Scan only the approved `inputs/` subfolders.
3. Record source metadata: relative path, folder-derived file type, SHA256 hash, filename-derived lecture number when possible, and filename-derived topic guess.
4. Update `study-os/state/studyos.sqlite` idempotently, using the source path as the stable identity.
5. Mark an existing source `stale` when its hash changed.
6. Write `working/inventory/course_inventory.md`.
7. Write `working/inventory/batch_plan.md`.

## Guardrails

- Do not read or summarize course content beyond hashing file bytes.
- Do not modify anything in `inputs/`.
- Do not extract PDFs or perform visual analysis during inventory.
- Do not generate digests, learning cores, study outputs, validation outputs, or synthesis.
- Inventory prepares batches; it does not process the whole course.
