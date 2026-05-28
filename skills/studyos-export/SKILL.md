---
name: studyos-export
description: Export StudyOS unmerged and merged study-facing Markdown outputs to polished PDF deliverables.
---

# Purpose

Convert StudyOS study-facing Markdown outputs into polished, readable, student-friendly exports with LaTeX-friendly formatting.

The skill exports both:

- unmerged batch-level outputs
- merged full-course outputs

It does not rewrite, reinterpret, summarize, or improve the source content. It preserves the existing Markdown content and source references.

# When to use

Use after the desired `studyos-batch`, `studyos-course`, or `studyos-merge` outputs exist and have acceptable validation status.

# Preflight checks

- Confirm at least one exportable study-facing Markdown output exists.
- If merged outputs are missing, export only unmerged outputs and warn.
- If unmerged outputs are missing, export only merged outputs and warn.
- If no exportable outputs exist, stop and tell the user to run `studyos-batch`, `studyos-course`, or `studyos-merge` first.
- Confirm `study-os/scripts/export_outputs.py` exists.
- Create export directories if they are missing.

# Reads

Unmerged batch-level outputs:

- `outputs/notes/Batch_*.md`
- `outputs/formulas/Batch_*.md`
- `outputs/questions/Batch_*.md`

Merged full-course outputs:

- `outputs/notes/full_course_notes.md`
- `outputs/formulas/full_formula_sheet.md`
- `outputs/questions/full_exam_practice_questions.md`

# Writes

Unmerged exports:

- `exports/pdf/unmerged/notes/`
- `exports/pdf/unmerged/formulas/`
- `exports/pdf/unmerged/questions/`

Merged exports:

- `exports/pdf/merged/`

Export log:

- `study-os/state/export-log.md`

# Workflow

1. Run:

   ```sh
   python3 study-os/scripts/export_outputs.py --root .
   ```

2. Review the completion report for exported unmerged files, exported merged files, skipped files, failures, export format, and output location.
3. If the script reports HTML fallback, tell the user that PDF generation dependencies were unavailable and the HTML files are print-ready.

# Export rules

- Export only the explicit study-facing output paths listed in this skill.
- Do not export internal analysis files.
- Do not export review, validation, or debug files unless the user explicitly requests a custom export outside this default skill.
- Do not modify files under `outputs/`.
- Preserve source references exactly as written.
- Preserve LaTeX expressions; use PDF tooling when available and MathJax-backed HTML fallback when PDF tooling is unavailable.
- Keep dependencies minimal.
- Do not add dashboard, Anki, or external app integrations.

# Output-specific formatting

The exporter applies output-specific presentation styling without changing content:

- notes: readable sections, definitions, examples, exam angles
- formulas: compact formula review, variables, assumptions, common mistakes
- questions: grouped practice, difficulty cues, expected answers

# PDF dependency behavior

The exporter prefers PDF when `pandoc` and a LaTeX PDF engine are available. If PDF generation dependencies are unavailable, it writes clean print-ready HTML under the same export folders and reports the fallback.

# Stop conditions

- No eligible outputs exist.
- The export script is missing.
- Explicit PDF-only export is requested but PDF tooling is unavailable.

# Completion report

Report:

- exported unmerged files
- exported merged files
- skipped files
- failed files
- export format
- output location
- whether PDF generation fell back to HTML
