# StudyOS Guide

StudyOS is a guided study-material workflow for one course. It keeps original course files protected, copies approved material into `inputs/`, then helps an agent build inventory, batch outputs, validation reports, merged study material, and PDF exports step by step.

## Normal Installation UX

Before installation, this course folder may not have local StudyOS skills yet. Installation is done through the external StudyOS core repo, usually `~/Developer/studyos-core`.

Normal request:

> Install StudyOS in this folder using ~/Developer/studyos-core.

The installing agent runs the external core installer, initializes or confirms the database, runs core sync, inspects the folder name and visible raw course files read-only, proposes a complete setup, asks for approval or modifications, fills `subject.yaml` only after approval, creates or updates this guide, and stops.

Installation/setup does not import files, run inventory, create a batch plan, validate, process, merge, or export material.

## Setup Proposal After Installation

The proposal includes subject name, course level, material language, exam type, raw source folder path, read-only original files, copy-into-inputs strategy, fixed default outputs, quality/depth mode, visual handling depth, formula handling depth, and validation depth.

Default study-facing outputs are notes, formulas, and exam practice questions. Flashcards, cheat sheets, study plans, and final review packs are not default outputs anymore; they are deprecated and disabled by default. Fewer outputs means higher quality and better focus on complete notes, display-LaTeX formulas, source coverage, visual coverage, and exam-quality practice questions.

The agent asks:

> Do you approve this setup, or do you want modifications?

The agent fills `subject.yaml` only after approval.

## Folder Structure

- `inputs/` contains approved copied course files after import. Treat these files as read-only processing inputs, not as editable working files.
- `analysis/` contains process evidence: import plans, inventory, first-pass and refined batch plans, repair logs, source digests, learning cores, visual notes, validation records, and processing state.
- `outputs/` contains reduced-scope study-facing Markdown outputs: notes, formula sheets, and exam practice questions.
- `exports/pdf/unmerged/` contains batch-level exports grouped by output category.
- `exports/pdf/merged/` contains consolidated full-course exports.
- `review/` contains validation reports, weak points, unresolved questions, source coverage, and progress tracking.
- `study-os/` contains installed scripts, skills, config guides, and local state.

## Protected Files

The original raw course folder configured at `subject.yaml` -> `raw_source.path` is read-only. StudyOS must never move, rename, delete, overwrite, or modify anything there.

Import copies approved files into `inputs/`. Files under `inputs/` are also treated as read-only after import.

Import is copy-only. It never moves raw files, never deletes raw files, never renames raw files, never edits raw files, and never overwrites an existing destination file in `inputs/`. If a destination already exists, the import plan must propose a safe alternate action or stop for user review.

## Skill Commands

- `python3 study-os/scripts/studyos.py status` reports the current workspace state and next recommended manual skill.
- `python3 study-os/scripts/studyos.py doctor` checks local readiness without modifying files.
- `studyos-import` proposes safe import, stops for approval, executes approved copy actions, then creates inventory and the first-pass batch plan from metadata.
- `studyos-plan` refines that first-pass plan into conceptual lectures, topics, modules, or tutorials before processing.
- `studyos-batch` processes one selected conceptual batch into digest, learning core, complete notes, formula sheet when relevant, exam practice questions, review updates, and integrated visual screening.
- `studyos-validate` validates batch, course, repaired, or merged outputs.
- `studyos-course` processes remaining planned or unprocessed batches sequentially, validates each batch before continuing, and reports processed, skipped, and stopped batches.
- `studyos-merge` merges validated batch outputs into consolidated full-course notes, formula sheet, and exam practice questions.
- `studyos-export` exports unmerged and merged study-facing deliverables to PDF when possible, with clean print-ready HTML fallback.

## Recommended Workflow

1. Install StudyOS from the external core repo.
2. Approve the setup proposal so the agent can write `subject.yaml`.
3. Run `studyos-import` proposal mode to create `analysis/inventory/import_plan.md`, review and approve the import plan, then let import copy approved files into `inputs/`, create `analysis/inventory/course_inventory.md`, and create the first-pass `analysis/inventory/batch_plan.md`.
4. Run `studyos-plan` to refine conceptual batches, source assignments, dependencies, and any `Unassigned / needs review` entries.
5. Run `studyos-batch` for one selected conceptual batch.
6. Run `studyos-validate`.
7. Run `studyos-course` if you want remaining planned or unprocessed batches processed sequentially with validation after each batch.
8. Run `studyos-merge` when batch outputs are processed and validated.
9. Run `studyos-export`.

You may optionally run `python3 study-os/scripts/studyos.py status` or `python3 study-os/scripts/studyos.py doctor` between steps.

Review `analysis/inventory/import_plan.md` before import execute. Do not continue with execute mode unless the proposed copies are acceptable.

`studyos-import` full flow runs proposal first if no plan exists, then stops for approval. It must not silently execute without an approved plan.

## Quality And Model Routing

Quality mode is stored in `subject.yaml` and interpreted with `study-os/config/output-standards.yaml`.

- `economy` is faster and lighter. Use it for low-stakes review or when you only need compact outputs.
- `standard` is the default. It balances coverage, source traceability, visual screening, and validation cost.
- `rigorous` is slower and deeper. Use it for technical, formula-heavy, or exam-critical courses.

Model routing is configured in `study-os/config/model-routing.yaml`.

- `fast` is for metadata, inventory, classification, and formatting.
- `balanced` is for normal digests, learning cores, explanations, and standard question generation.
- `deep` is for formulas, difficult concepts, exam questions, essential visual analysis, and merge work.
- `audit` is for validation, citation checks, formula checks, coverage review, and unsupported-claim detection.

Use the deeper tier only for the affected section when repairing validation issues. Do not regenerate unrelated outputs just to fix one finding.

## Agent-Driven Optimization

StudyOS is intentionally agent-driven. Scripts handle safe mechanical work: install, sync, import proposal, approved copy, inventory, deterministic validation, and export. The agent handles the judgment-heavy work: reading sources, deciding what matters, extracting concepts, analyzing formulas and visuals, writing notes, creating exam practice, repairing validation findings, and merging the course.

The agent should optimize time and tokens only after output quality and exhaustive assigned-input coverage are protected:

- read inventory, batch plan, filenames, headings, slide titles, tables of contents, and obvious formula/exam signals before full source reads
- fully cover every assigned primary source and every assigned supporting source
- use selective reading only when Source Coverage can justify a source as duplicate, irrelevant, unreadable, or deferred
- spend saved effort on complete notes, formula correctness, essential visuals, exam-quality questions, and validation repair
- use deeper reasoning only for difficult concepts, formulas, notation conflicts, essential visuals, exam integration, and final merge decisions
- repair affected sections instead of regenerating unrelated valid work
- write long outputs when long outputs are required to preserve all unique concepts, examples, caveats, assumptions, formulas, visuals, and exam signals

StudyOS treats "perfect output" as an operational quality target, not a promise of impossible certainty: complete assigned-source coverage, no known unsupported claims, display-quality formulas, clear expected answers, visible unresolved uncertainty, and no high or blocking validation findings.

## Common Missing-Step Warnings

- Missing `subject.yaml` or `study-os/`: install StudyOS first.
- Missing `raw_source.path`: complete approved setup before importing.
- Missing import plan: run `studyos-import` proposal mode.
- Empty `inputs/`: run `studyos-import` proposal mode, approve the plan, then run execute mode.
- Missing `batch_plan.md`: run `studyos-import` inventory mode, then `studyos-plan`.
- Random file-level or exercise-only batches in `batch_plan.md`: run `studyos-plan` before processing.
- Missing digest, learning core, notes, formulas when relevant, or questions: run `studyos-batch`.
- Missing validation reports: run `studyos-validate`.
- Missing merged outputs: run `studyos-merge`.

When a preflight warning appears, stop the current skill and do exactly the recommended prerequisite. Do not bypass warnings by manually creating placeholder files. If the warning mentions blocking validation, repair the affected output, rerun `studyos-validate`, and continue only after the blocking issue is cleared or explicitly recorded as unresolved by the user.

## Output Locations

- Batch digests: `analysis/batches/<batch>_digest.md`
- Batch learning cores: `analysis/batches/<batch>_learning_core.md`
- Batch visual notes: `analysis/visual/<batch>_visual_notes.md` when visual findings exist
- Validation notes: `analysis/validation/`
- Notes: `outputs/notes/`
- Formula sheets: `outputs/formulas/`
- Exam questions: `outputs/questions/`
- Unmerged exports: `exports/pdf/unmerged/notes/`, `exports/pdf/unmerged/formulas/`, and `exports/pdf/unmerged/questions/`
- Merged exports: `exports/pdf/merged/`

Batch output files use these names:

- Notes: `outputs/notes/<batch>.md`
- Formula sheets: `outputs/formulas/<batch>_formulas.md` when formulas exist or are relevant
- Exam questions: `outputs/questions/<batch>_questions.md`

Merged full-course output files use these names:

- Notes: `outputs/notes/full_course_notes.md`
- Formula sheet: `outputs/formulas/full_formula_sheet.md`
- Exam practice questions: `outputs/questions/full_exam_practice_questions.md`

`studyos-batch` updates `review/weak-points.md`, `review/unresolved-questions.md`, and `review/visual-issues.md` when visual issues exist.

Batch notes are exhaustive complete study notes, not summaries. Each batch notes file includes Scope, Core Notes, Definitions, Examples, Formula Intuition, Exam Relevance, Common Mistakes, Weak Points, and Source References. Formula sheets require readable display LaTeX and include assumptions, intuition, common mistakes, and source references. Exam practice questions replace flashcards as the active-recall and practice layer, using exercises for practice prompts and weak-point discovery rather than fake theory summaries. Outputs may be long; length is acceptable when it reflects complete assigned-input coverage.

`studyos-batch` does not create flashcards, cheat sheets, study plans, final review packs, or deprecated output folders for those formats. Fewer outputs should mean deeper attention to notes, formulas, questions, source coverage, and visual coverage.

## Course Processing

`studyos-course` reads `subject.yaml`, `analysis/inventory/batch_plan.md`, optional `analysis/inventory/processing_queue.md`, `analysis/batches/`, `outputs/`, and `review/`. It requires files under `inputs/` and stops if the batch plan is missing.

If no validated batch exists yet, the agent warns:

> Recommended: process and validate one batch manually before full course processing.

The skill identifies planned, unprocessed, stale, or previously failed batches and processes them one batch at a time using `studyos-batch` semantics. For each batch, final outputs are limited to notes, formula sheets when relevant, and exam practice questions. Digest, learning core, visual notes, validation files, and review files remain internal process evidence.

Each batch is validated with `studyos-validate` semantics before the next batch starts. Minor localized issues may be repaired and revalidated. Blocking validation issues, missing assigned sources, ambiguous ordering, insufficient source coverage, insufficient formula quality, insufficient notes depth, or unresolved essential visual coverage stop processing.

Default processing is sequential. Safe parallel processing is allowed only when configured in `subject.yaml`; dependent batches must not be parallelized, digest and learning-core work for the same batch must not be parallelized, and merged validation is required before downstream work continues.

The completion report lists batches processed, batches skipped, blocking issues and stopped batch if any, notes/formula sheets/exam practice questions created, validation status, unresolved issues, files written, and the recommended next skill: `studyos-merge`.

## Merge Outputs

`studyos-merge` reads validated learning cores from `analysis/batches/*_learning_core.md`, batch outputs from `outputs/notes/Batch_*.md`, `outputs/formulas/Batch_*_formulas.md`, and `outputs/questions/Batch_*_questions.md`, plus `review/weak-points.md`, `review/unresolved-questions.md`, `review/visual-issues.md`, and `review/validation-report.md`.

Merge does not mean concatenate. The skill consolidates duplicate concepts, harmonizes notation, deduplicates formulas, identifies dependencies, preserves source references, preserves repaired batch-note depth, prioritizes weak points inside the relevant notes and questions, includes unresolved issues where relevant, includes likely exam questions, and carries exam-relevant visual findings.

Merged full-course outputs are limited to:

- `outputs/notes/full_course_notes.md`
- `outputs/formulas/full_formula_sheet.md`
- `outputs/questions/full_exam_practice_questions.md`

`studyos-merge` must not create `full_flashcards.md`, `final_cheat_sheet.md`, `full_course_study_plan.md`, `final_review_pack.md`, or any substitute for those removed outputs.

Merged notes should preserve batch-level completeness, add transitions, include a dependency map, and build a progressive course-level learning flow. Merged formula sheets should use display LaTeX, include notation and formula indexes, deduplicate formulas, and retain variables, assumptions, interpretation, mistakes, and sources. Merged exam practice questions should be grouped by topic and difficulty, include expected answers, and add integrated exam-style questions where useful.

The completion report lists merged outputs created, unresolved issues included, validation or audit recommendations, and the recommended next skill: `studyos-export`.

## Export Outputs

`studyos-export` reads only study-facing Markdown outputs and writes polished exports. It does not export internal analysis files, validation reports, review/debug files, or raw sources by default.

Unmerged batch-level inputs:

- `outputs/notes/Batch_*.md`
- `outputs/formulas/Batch_*_formulas.md`
- `outputs/questions/Batch_*_questions.md`

Unmerged exports are written by category under:

- `exports/pdf/unmerged/notes/`
- `exports/pdf/unmerged/formulas/`
- `exports/pdf/unmerged/questions/`

Merged full-course inputs:

- `outputs/notes/full_course_notes.md`
- `outputs/formulas/full_formula_sheet.md`
- `outputs/questions/full_exam_practice_questions.md`

Merged exports are written to `exports/pdf/merged/`.

Run:

```sh
python3 study-os/scripts/export_outputs.py --root .
```

`export_outputs.py` is the only normal export script installed in this workspace. The deprecated `export_final_pack.py` compatibility wrapper is not installed by default.

The exporter preserves content and source references. It exports unmerged and merged PDFs for notes, formulas, and exam practice questions only; flashcards, cheat sheets, study plans, final review packs, internal analysis files, and review/debug files are skipped by default. It prefers PDF when `pandoc` and a LaTeX PDF engine are available. If those dependencies are unavailable, it writes print-ready HTML with MathJax support and reports the fallback in `study-os/state/export-log.md`.

## Integrated Visual Screening

Visual screening is part of `studyos-batch`, `studyos-course`, and `studyos-validate`. There is no separate visual skill.

Every batch with slides, PDFs, or images must include Visual Coverage in the digest. If no essential visuals exist, the digest says so explicitly. Essential visuals include formulas, definitions, charts, tables, rankings, benchmark values, model diagrams, process diagrams, and summary visual slides.

`studyos-validate` checks Visual Coverage again. Essential visuals must be analyzed in `analysis/visual/` or explicitly carried into `review/visual-issues.md` or `review/unresolved-questions.md`.

## Validation Outputs

`studyos-validate` reads `analysis/batches/`, `analysis/visual/`, `outputs/`, `review/`, `inputs/`, and `subject.yaml`. It writes validation detail under `analysis/validation/` and review reports under `review/`.

Validation focuses only on the final study-facing outputs: notes, formula sheets, and exam practice questions. It does not require flashcards, cheat sheets, study plans, or final review packs. It also checks internal quality-support files: each processed batch digest, learning core, source coverage, and visual coverage.

For notes, validation checks file existence, non-empty content, required sections, approximate depth in standard or rigorous mode, source references, visual findings when relevant, and whether the file looks like complete study notes rather than a compressed summary. Validation should fail notes that are short because they omit assigned-source concepts, examples, caveats, formulas, assumptions, visuals, or exam signals.

For formulas, validation checks that relevant formula sheets exist, Formula Index and Notation sections are present, display LaTeX is used, formulas are not inline-code/plain-ASCII only, and each formula has Formula, Variables, Assumptions, Use when, Interpretation, Common mistake, and Source fields.

For questions, validation checks expected answers, topic or concept grouping, conceptual and exam-style prompts, formula/application questions for formula-heavy batches, exercise-derived practice where assigned, and source or topic references.

For internal support, validation checks Source Coverage in digests, Visual Coverage when relevant, learning cores that preserve enough digest depth, and unresolved visual/formula issues tracked in review files. It also compares assigned primary and supporting sources in `analysis/inventory/batch_plan.md` against each batch digest Source Coverage table. Every assigned source must be listed with status `used`, `partially used`, `unreadable`, `irrelevant`, `duplicate`, or `deferred`; non-use statuses require a concrete reason.

Expected validation reports:

- `review/validation-report.md`
- `review/source-coverage.md`
- `review/visual-issues.md` when visual issues exist
- `review/unresolved-questions.md` when unresolved questions remain

Validation uses severity levels `low`, `medium`, `high`, and `blocking`. Blocking issues stop downstream merge or export until repaired.

The completion report includes notes status, formulas status, questions status, source coverage status, visual coverage status, blocking issues, and a recommended repair target.

## Repair Before Regenerate

When validation finds issues, repair only the affected sections or files. Preserve valid content, do not regenerate unrelated outputs, rerun validation after repair, and leave remaining uncertainty clearly marked.
