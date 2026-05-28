#!/usr/bin/env python3
"""Export StudyOS study-facing Markdown outputs to PDF or print-ready fallbacks."""

from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


UNMERGED_CATEGORIES = ("notes", "formulas", "questions")
EXPORT_BASE = Path("exports/pdf")
STATE_LOG = Path("study-os/state/export-log.md")


@dataclass(frozen=True)
class ExportSpec:
    source: Path
    destination_directory: Path
    output_type: str
    category: str
    title: str


@dataclass
class ExportResult:
    source: Path
    destination: Path | None
    output_type: str
    category: str
    status: str
    detail: str = ""


MERGED_OUTPUTS = (
    (
        Path("outputs/notes/full_course_notes.md"),
        "notes",
        "Full Course Notes",
    ),
    (
        Path("outputs/formulas/full_formula_sheet.md"),
        "formulas",
        "Full Formula Sheet",
    ),
    (
        Path("outputs/questions/full_exam_practice_questions.md"),
        "questions",
        "Full Exam Practice Questions",
    ),
)


TEMPLATE_SUBTITLES = {
    "notes": "Readable sections, definitions, examples, and exam angles",
    "formulas": "Compact formula review with variables, assumptions, and mistakes",
    "questions": "Topic-grouped practice with difficulty and answer expectations",
}


CSS = """
@page {
  margin: 18mm 15mm;
}

:root {
  color-scheme: light;
  --ink: #1f2933;
  --muted: #5d6b78;
  --line: #d8dee5;
  --panel: #f6f8fa;
  --accent: #126b6f;
  --accent-soft: #e6f4f1;
}

body {
  margin: 0;
  color: var(--ink);
  background: white;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  font-size: 11.5pt;
  line-height: 1.55;
}

main {
  max-width: 920px;
  margin: 0 auto;
  padding: 28px 32px 44px;
}

.cover {
  border-bottom: 2px solid var(--accent);
  margin-bottom: 24px;
  padding-bottom: 14px;
}

.kicker {
  color: var(--accent);
  font-size: 9pt;
  font-weight: 700;
  letter-spacing: .04em;
  text-transform: uppercase;
}

h1 {
  margin: 6px 0 8px;
  font-size: 26pt;
  line-height: 1.12;
}

.subtitle,
.meta {
  color: var(--muted);
}

h2 {
  margin-top: 26px;
  border-bottom: 1px solid var(--line);
  padding-bottom: 4px;
  font-size: 18pt;
}

h3 {
  margin-top: 20px;
  font-size: 14pt;
}

h4 {
  margin-top: 16px;
  font-size: 12pt;
}

p,
ul,
ol,
table,
pre,
blockquote {
  margin-top: 0;
  margin-bottom: 12px;
}

a {
  color: var(--accent);
}

code {
  border: 1px solid var(--line);
  border-radius: 4px;
  background: var(--panel);
  padding: 0 3px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: .92em;
}

pre {
  overflow-x: auto;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: var(--panel);
  padding: 10px 12px;
}

pre code {
  border: 0;
  background: transparent;
  padding: 0;
}

blockquote {
  border-left: 4px solid var(--accent);
  background: var(--accent-soft);
  margin-left: 0;
  padding: 8px 14px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  border: 1px solid var(--line);
  padding: 6px 8px;
  vertical-align: top;
}

th {
  background: var(--panel);
  font-weight: 700;
}

.formulas h2,
.formulas h3 {
  break-after: avoid;
}

.questions h3 {
  border-left: 4px solid var(--accent);
  padding-left: 8px;
}

.source-path {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 9pt;
}

@media print {
  main {
    max-width: none;
    padding: 0;
  }

  a {
    color: inherit;
    text-decoration: none;
  }
}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Export StudyOS batch-level and merged Markdown outputs to PDFs. "
            "Falls back to print-ready HTML when PDF tooling is unavailable."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Installed subject folder root. Defaults to the current directory.",
    )
    parser.add_argument(
        "--format",
        choices=("auto", "pdf", "html", "markdown"),
        default="auto",
        help="Export format. auto prefers PDF and falls back to HTML.",
    )
    return parser.parse_args()


def relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def slug_title(path: Path) -> str:
    return path.stem.replace("_", " ").replace("-", " ").strip().title()


def collect_unmerged(root: Path) -> list[ExportSpec]:
    specs: list[ExportSpec] = []
    for category in UNMERGED_CATEGORIES:
        source_directory = root / "outputs" / category
        destination_directory = root / EXPORT_BASE / "unmerged" / category
        for source in sorted(source_directory.glob("Batch_*.md")):
            specs.append(
                ExportSpec(
                    source=source,
                    destination_directory=destination_directory,
                    output_type="unmerged",
                    category=category,
                    title=slug_title(source),
                )
            )
    return specs


def collect_merged(root: Path) -> list[ExportSpec]:
    specs: list[ExportSpec] = []
    for relative_source, category, title in MERGED_OUTPUTS:
        source = root / relative_source
        if not source.is_file():
            continue
        specs.append(
            ExportSpec(
                source=source,
                destination_directory=root / EXPORT_BASE / "merged",
                output_type="merged",
                category=category,
                title=title,
            )
        )
    return specs


def ensure_export_directories(root: Path) -> None:
    for category in UNMERGED_CATEGORIES:
        (root / EXPORT_BASE / "unmerged" / category).mkdir(parents=True, exist_ok=True)
    (root / EXPORT_BASE / "merged").mkdir(parents=True, exist_ok=True)


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def pdf_engine() -> str | None:
    for engine in ("xelatex", "lualatex", "pdflatex", "tectonic"):
        if command_exists(engine):
            return engine
    return None


def can_write_pdf() -> tuple[bool, str]:
    if not command_exists("pandoc"):
        return False, "pandoc is not installed"
    engine = pdf_engine()
    if engine is None:
        return False, "pandoc is installed but no LaTeX PDF engine was found"
    return True, engine


def can_use_pandoc_html() -> bool:
    return command_exists("pandoc")


def destination_for(spec: ExportSpec, extension: str) -> Path:
    return spec.destination_directory / f"{spec.source.stem}.{extension}"


def run_pandoc_pdf(spec: ExportSpec, destination: Path, root: Path, engine: str) -> None:
    metadata = f"title={spec.title}"
    command = [
        "pandoc",
        str(spec.source),
        "--from",
        "markdown+tex_math_dollars+pipe_tables",
        "--pdf-engine",
        engine,
        "--metadata",
        metadata,
        "--variable",
        "geometry:margin=18mm",
        "--variable",
        "fontsize=11pt",
        "--output",
        str(destination),
    ]
    subprocess.run(command, cwd=root, check=True, capture_output=True, text=True)


def run_pandoc_html(spec: ExportSpec, destination: Path, root: Path) -> None:
    body = subprocess.run(
        [
            "pandoc",
            str(spec.source),
            "--from",
            "markdown+tex_math_dollars+pipe_tables",
            "--to",
            "html5",
            "--mathjax",
        ],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    write_html_document(spec, destination, body, root)


def inline_markdown(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", escaped)
    return escaped


def simple_markdown_to_html(markdown: str) -> str:
    lines = markdown.splitlines()
    html_lines: list[str] = []
    in_code = False
    in_ul = False
    in_ol = False
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            html_lines.append(f"<p>{inline_markdown(' '.join(paragraph))}</p>")
            paragraph.clear()

    def close_lists() -> None:
        nonlocal in_ul, in_ol
        if in_ul:
            html_lines.append("</ul>")
            in_ul = False
        if in_ol:
            html_lines.append("</ol>")
            in_ol = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("```"):
            flush_paragraph()
            close_lists()
            if in_code:
                html_lines.append("</code></pre>")
                in_code = False
            else:
                html_lines.append("<pre><code>")
                in_code = True
            continue

        if in_code:
            html_lines.append(html.escape(line))
            continue

        if not stripped:
            flush_paragraph()
            close_lists()
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading:
            flush_paragraph()
            close_lists()
            level = len(heading.group(1))
            html_lines.append(
                f"<h{level}>{inline_markdown(heading.group(2))}</h{level}>"
            )
            continue

        if stripped.startswith(">"):
            flush_paragraph()
            close_lists()
            html_lines.append(f"<blockquote>{inline_markdown(stripped[1:].strip())}</blockquote>")
            continue

        unordered = re.match(r"^[-*]\s+(.+)$", stripped)
        if unordered:
            flush_paragraph()
            if in_ol:
                html_lines.append("</ol>")
                in_ol = False
            if not in_ul:
                html_lines.append("<ul>")
                in_ul = True
            html_lines.append(f"<li>{inline_markdown(unordered.group(1))}</li>")
            continue

        ordered = re.match(r"^\d+[.)]\s+(.+)$", stripped)
        if ordered:
            flush_paragraph()
            if in_ul:
                html_lines.append("</ul>")
                in_ul = False
            if not in_ol:
                html_lines.append("<ol>")
                in_ol = True
            html_lines.append(f"<li>{inline_markdown(ordered.group(1))}</li>")
            continue

        paragraph.append(stripped)

    flush_paragraph()
    close_lists()
    if in_code:
        html_lines.append("</code></pre>")
    return "\n".join(html_lines)


def write_html_document(spec: ExportSpec, destination: Path, body: str, root: Path) -> None:
    subtitle = TEMPLATE_SUBTITLES.get(spec.category, "Polished StudyOS export")
    class_name = spec.category.replace("_", "-")
    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(spec.title)}</title>
  <script>
    window.MathJax = {{
      tex: {{ inlineMath: [['$', '$'], ['\\\\(', '\\\\)']], displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']] }},
      svg: {{ fontCache: 'global' }}
    }};
  </script>
  <script async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
  <style>{CSS}</style>
</head>
<body>
  <main class="{html.escape(class_name)}">
    <section class="cover">
      <div class="kicker">StudyOS {html.escape(spec.output_type)} export</div>
      <h1>{html.escape(spec.title)}</h1>
      <div class="subtitle">{html.escape(subtitle)}</div>
      <div class="meta source-path">Source: {html.escape(relative(spec.source, root))}</div>
    </section>
    {body}
  </main>
</body>
</html>
"""
    destination.write_text(document, encoding="utf-8")


def write_simple_html(spec: ExportSpec, destination: Path, root: Path) -> None:
    markdown = spec.source.read_text(encoding="utf-8", errors="replace")
    write_html_document(spec, destination, simple_markdown_to_html(markdown), root)


def write_print_markdown(spec: ExportSpec, destination: Path, root: Path) -> None:
    source_text = spec.source.read_text(encoding="utf-8", errors="replace")
    destination.write_text(
        "\n".join(
            (
                f"# {spec.title}",
                "",
                f"StudyOS {spec.output_type} export",
                f"Source: `{relative(spec.source, root)}`",
                "",
                source_text,
            )
        ),
        encoding="utf-8",
    )


def export_one(
    spec: ExportSpec,
    root: Path,
    requested_format: str,
    pdf_ready: bool,
    pdf_detail: str,
) -> ExportResult:
    spec.destination_directory.mkdir(parents=True, exist_ok=True)
    pdf_failure_detail = ""

    if requested_format in ("auto", "pdf") and pdf_ready:
        destination = destination_for(spec, "pdf")
        try:
            run_pandoc_pdf(spec, destination, root, pdf_detail)
            return ExportResult(spec.source, destination, spec.output_type, spec.category, "exported")
        except subprocess.CalledProcessError as error:
            pdf_failure_detail = error.stderr.strip() or str(error)
            if requested_format == "pdf":
                return ExportResult(spec.source, None, spec.output_type, spec.category, "failed", pdf_failure_detail)

    if requested_format == "pdf":
        return ExportResult(spec.source, None, spec.output_type, spec.category, "failed", pdf_detail)

    if requested_format == "markdown":
        destination = destination_for(spec, "print.md")
        write_print_markdown(spec, destination, root)
        return ExportResult(spec.source, destination, spec.output_type, spec.category, "exported")

    destination = destination_for(spec, "html")
    try:
        if can_use_pandoc_html():
            run_pandoc_html(spec, destination, root)
        else:
            write_simple_html(spec, destination, root)
    except (OSError, subprocess.CalledProcessError):
        write_simple_html(spec, destination, root)
    detail = "PDF failed; wrote HTML fallback" if pdf_failure_detail else ""
    return ExportResult(spec.source, destination, spec.output_type, spec.category, "exported", detail)


def skipped_missing_merged(root: Path) -> list[ExportResult]:
    skipped: list[ExportResult] = []
    for relative_source, category, _title in MERGED_OUTPUTS:
        source = root / relative_source
        if source.is_file():
            continue
        skipped.append(
            ExportResult(source, None, "merged", category, "skipped", "missing merged output")
        )
    return skipped


def write_log(
    root: Path,
    results: list[ExportResult],
    warnings: list[str],
    export_format: str,
) -> Path:
    log_path = root / STATE_LOG
    log_path.parent.mkdir(parents=True, exist_ok=True)

    def section(title: str, rows: list[ExportResult]) -> list[str]:
        lines = [f"## {title}", ""]
        if not rows:
            lines.extend(["- None", ""])
            return lines
        for row in rows:
            destination = relative(row.destination, root) if row.destination else "none"
            detail = f" ({row.detail})" if row.detail else ""
            lines.append(
                f"- {row.status}: `{relative(row.source, root)}` -> `{destination}`{detail}"
            )
        lines.append("")
        return lines

    exported = [row for row in results if row.status == "exported"]
    skipped = [row for row in results if row.status == "skipped"]
    failed = [row for row in results if row.status == "failed"]
    warning_lines = [f"- {warning}" for warning in warnings] or ["- None"]

    lines = [
        "# StudyOS Export Log",
        "",
        f"- Timestamp: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        f"- Export format: {export_format}",
        f"- Output root: `{relative(root / EXPORT_BASE, root)}`",
        "",
        "## Warnings",
        "",
        *warning_lines,
        "",
        *section("Exported Files", exported),
        *section("Skipped Files", skipped),
        *section("Failed Files", failed),
    ]
    log_path.write_text("\n".join(lines), encoding="utf-8")
    return log_path


def infer_export_format(results: list[ExportResult], fallback: str) -> str:
    suffixes = {
        row.destination.suffix.lower()
        for row in results
        if row.status == "exported" and row.destination is not None
    }
    if suffixes == {".pdf"}:
        return "pdf"
    if suffixes == {".html"}:
        return "html"
    if suffixes == {".md"}:
        return "markdown"
    if suffixes:
        return "mixed"
    return fallback


def print_completion(
    root: Path,
    results: list[ExportResult],
    warnings: list[str],
    export_format: str,
    log_path: Path,
) -> None:
    exported_unmerged = [
        row for row in results if row.status == "exported" and row.output_type == "unmerged"
    ]
    exported_merged = [
        row for row in results if row.status == "exported" and row.output_type == "merged"
    ]
    skipped = [row for row in results if row.status == "skipped"]
    failed = [row for row in results if row.status == "failed"]

    print("StudyOS export complete")
    print(f"Export format: {export_format}")
    print(f"Output location: {root / EXPORT_BASE}")
    print(f"Export log: {log_path}")
    print("")

    def print_rows(title: str, rows: list[ExportResult]) -> None:
        print(title)
        if not rows:
            print("  - None")
            return
        for row in rows:
            destination = relative(row.destination, root) if row.destination else "none"
            detail = f" ({row.detail})" if row.detail else ""
            print(f"  - {relative(row.source, root)} -> {destination}{detail}")

    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"  - {warning}")
    print_rows("Exported unmerged files:", exported_unmerged)
    print_rows("Exported merged files:", exported_merged)
    print_rows("Skipped files:", skipped)
    print_rows("Failed files:", failed)


def main() -> int:
    args = parse_args()
    root = args.root.expanduser().resolve()

    ensure_export_directories(root)
    unmerged_specs = collect_unmerged(root)
    merged_specs = collect_merged(root)

    warnings: list[str] = []
    if not unmerged_specs:
        warnings.append(
            "No unmerged Batch_*.md outputs found; exporting merged outputs only."
        )
    if not merged_specs:
        warnings.append(
            "No merged full-course outputs found; exporting unmerged outputs only."
        )
    elif len(merged_specs) < len(MERGED_OUTPUTS):
        missing_count = len(MERGED_OUTPUTS) - len(merged_specs)
        warnings.append(
            f"{missing_count} merged full-course output(s) are missing; exporting available merged outputs only."
        )

    if not unmerged_specs and not merged_specs:
        print(
            "No exportable StudyOS outputs found. Run studyos-batch, studyos-course, "
            "or studyos-merge first.",
            file=sys.stderr,
        )
        return 1

    pdf_ready, pdf_detail = can_write_pdf()
    if args.format == "auto":
        export_format = "pdf" if pdf_ready else "html"
        if not pdf_ready:
            warnings.append(
                f"PDF generation unavailable ({pdf_detail}); wrote print-ready HTML instead."
            )
    else:
        export_format = args.format

    results: list[ExportResult] = []
    for spec in [*unmerged_specs, *merged_specs]:
        results.append(export_one(spec, root, args.format, pdf_ready, pdf_detail))

    results.extend(skipped_missing_merged(root))

    export_format = infer_export_format(results, export_format)
    log_path = write_log(root, results, warnings, export_format)
    print_completion(root, results, warnings, export_format, log_path)

    return 1 if any(row.status == "failed" for row in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
