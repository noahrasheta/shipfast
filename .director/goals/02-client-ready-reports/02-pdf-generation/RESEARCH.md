# Step Research: PDF Generation

**Researched:** 2026-02-20
**Step:** PDF generation
**Domain:** Python markdown-to-PDF conversion
**Confidence:** HIGH

## Reuse Metadata

_This section is used by the smart reuse check to determine if re-research is warranted. Populate all fields._

- **Step scope:** Build a markdown-to-PDF conversion pipeline in Python and wire it into the due diligence orchestrator to generate polished PDFs of both the executive summary and client-facing summary. Markdown versions are preserved alongside PDFs.
- **Locked decisions:** Markdown-to-PDF conversion pipeline approach (not WeasyPrint or reportlab directly); both executive summary and client-facing summary get PDF versions; Python 3.11+ runtime; markdown versions preserved for AI workflows.
- **Flexible decisions:** Specific Python markdown-to-PDF library -- user said "markdown to PDF" approach but no specific library preference.
- **Onboarding research used:** Yes -- referenced existing library solutions recommendation and note that Python infrastructure for document processing already exists in `dc-due-diligence/converters/`.
- **Inputs checksum:** step=pdf-generation locked=markdown-to-pdf-pipeline,dual-output,python311 flexible=library

## User Decisions

### Locked (researched deeply)

- **Markdown-to-PDF conversion pipeline:** The locked approach is a Python pipeline that converts markdown to PDF via an intermediate HTML step. This is the correct architecture for this project: the agents already produce markdown output files (`executive-summary.md`, `client-summary.md`), and the pipeline should read those files and write `.pdf` siblings. The pipeline should be a standalone Python script (following the pattern of `converters/pipeline.py`) that takes a markdown file path, converts it, and writes a PDF alongside it. The orchestrator calls this script after agent output is finalized.

- **Both executive summary and client-facing summary get PDF versions:** Two PDF files need to be generated per run: `executive-summary.pdf` and `client-summary.pdf`. The pipeline should accept either a specific file path or auto-detect these two files in the research output folder. The simplest integration point is at the end of the orchestrator skill, after the Executive Summary Generator agent writes its output.

- **Markdown versions preserved:** PDFs are additive -- do not replace or delete the `.md` files. The orchestrator should write the `.md` first (existing behavior), then invoke the PDF converter on it. File naming convention: `executive-summary.pdf` alongside `executive-summary.md` in the same directory.

- **Python 3.11+ runtime:** All three library candidates support Python 3.10+, so Python 3.11 is not a constraint. The library should integrate with the existing `dc-due-diligence` package, added as a dependency in `pyproject.toml`. The `.venv` created by `setup.sh` will handle installation automatically on first use.

### Flexible (comparative recommendations)

- **Markdown-to-PDF library:** Recommend **markdown-pdf** (version 1.13.1, February 2026) because it is a direct, zero-friction solution: install one package, call the API with markdown text, get a PDF. No system-level dependencies, no separate HTML step to manage, no Pango/Gtk library requirements. It uses `markdown-it-py` for parsing and `PyMuPDF` for rendering -- both pure Python with wheels available. Supports tables, images, custom CSS, multi-page, TOC from headings, hyperlinks, and page breaks -- everything this step needs. Licensed under AGPL-3.0, which is acceptable for internal tooling.

  **Alternative 1: WeasyPrint (v68.1)** is the most polished renderer with excellent CSS Paged Media support and the best typography of any Python option. However, it requires Pango as a system library (`brew install weasyprint` on macOS, system packages on Linux). This is a significant friction point: it breaks the self-contained Python install story and requires documentation changes. The markdown step would also need `mistune` or `markdown-it-py` separately since WeasyPrint only accepts HTML. Recommend against for this project unless print quality becomes a priority requirement.

  **Alternative 2: md2pdf (v3.1.0)** is a convenient CLI/library wrapper around WeasyPrint with Jinja template support and PyMdown extensions. Has the same system dependency problem as WeasyPrint (it depends on it), plus adds another abstraction layer. More complexity, same Pango requirement. Not recommended.

### Deferred (not researched)

- None explicitly deferred per user decisions.

## Recommended Approach

Build a thin `generate_pdf.py` module in the existing `dc-due-diligence/converters/` package (following the established converter pattern). The module accepts a markdown file path and writes a PDF to the same directory. The `markdown-pdf` library handles the full conversion pipeline internally: markdown text is parsed to HTML by `markdown-it-py`, then rendered to PDF by `PyMuPDF`. Custom CSS is passed to the `Section` constructor to style the output for a professional, readable look -- larger heading fonts, better table borders, sensible margins.

Add `markdown-pdf` to `pyproject.toml` dependencies. Wire the PDF generator into the orchestrator skill (`skills/due-diligence/SKILL.md`) as a final step after the Executive Summary Generator agent finishes. The orchestrator instructs Claude Code to call the PDF generator on both output files. The generator writes `executive-summary.pdf` and `client-summary.pdf` alongside their markdown versions. No changes to the existing agent pipeline, only addition at the tail of the orchestrator.

CSS customization is the main design task: executive summary gets a denser layout with more heading weight (internal data center report look); client summary gets a cleaner, more spaced layout with branding-friendly margins (external deliverable look). Both should use `markdown-pdf`'s custom CSS parameter. A reasonable default CSS can be stored in `dc-due-diligence/templates/pdf-styles/` as separate files so they can be adjusted without touching code.

## Stack for This Step

| Library/Tool | Version | Purpose | Why |
|--------------|---------|---------|-----|
| markdown-pdf | >=1.13.1 | Markdown-to-PDF conversion | Direct markdown-to-PDF with no system deps, pure Python wheels, tables + CSS support |
| markdown-it-py | (transitive via markdown-pdf) | Markdown parsing to HTML | Pulled in automatically; no separate install needed |
| PyMuPDF | >=1.27.1 (transitive) | HTML-to-PDF rendering | Included via markdown-pdf; no system-level library required |

Note: `PyMuPDF` and `markdown-pdf` are both AGPL-3.0 licensed. For internal tooling used within Data Canopy (not redistributed as a library), this is acceptable. If the plugin is ever published as a marketplace plugin for third-party use, the AGPL license requires users to either comply with AGPL or obtain a commercial Artifex license for PyMuPDF.

## Architecture Patterns

### Converter Module Pattern

**What:** A new `generate_pdf.py` in `converters/` that follows the same structural pattern as `pdf.py`, `word.py`, etc. -- a callable function that takes a `Path` and returns a result object. The module is not a `BaseConverter` subclass (it produces PDF _output_, not markdown output), but follows the same error handling conventions.

**When:** Called from the orchestrator after agent output is written to disk.

**Example:**
```python
"""
PDF generation from markdown output files.

Converts markdown reports produced by the due diligence agent pipeline
into polished PDF documents, preserving the original markdown files.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from markdown_pdf import MarkdownPdf, Section


# Load CSS from templates directory.
_TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "pdf-styles"


@dataclass
class PdfResult:
    source_path: Path
    output_path: Path | None
    success: bool
    error: str | None = None


def generate_pdf(
    markdown_path: str | Path,
    style: str = "executive",
) -> PdfResult:
    """Convert a markdown file to a PDF in the same directory.

    Parameters
    ----------
    markdown_path:
        Path to the source .md file.
    style:
        One of "executive" or "client" -- selects the CSS stylesheet.

    Returns
    -------
    PdfResult
        Result with output_path pointing to the generated .pdf file.
    """
    source = Path(markdown_path).resolve()
    if not source.exists():
        return PdfResult(source, None, False, f"File not found: {source}")

    output = source.with_suffix(".pdf")
    css_file = _TEMPLATE_DIR / f"{style}.css"
    css = css_file.read_text(encoding="utf-8") if css_file.exists() else ""

    try:
        text = source.read_text(encoding="utf-8")
        pdf = MarkdownPdf(toc_level=2)
        pdf.add_section(Section(text, toc=True), user_css=css)
        pdf.meta["title"] = source.stem.replace("-", " ").title()
        pdf.save(str(output))
    except Exception as exc:
        return PdfResult(source, None, False, str(exc))

    return PdfResult(source, output, True)
```

### Orchestrator Tail Integration

**What:** The orchestrator skill calls the PDF generator as a final, sequential step after the Executive Summary Generator agent has written its output. This keeps the existing agent pipeline unchanged.

**When:** At the end of the orchestrator's final wave, after confirming both `executive-summary.md` and `client-summary.md` exist.

**Example (in SKILL.md orchestrator instructions):**
```
## Wave 3 Completion

After the Executive Summary Generator writes its output:

1. Verify both files exist:
   - `[opportunity-folder]/research/executive-summary.md`
   - `[opportunity-folder]/research/client-summary.md`

2. Run the PDF generator on both files:
   ```bash
   python -c "
   import sys
   sys.path.insert(0, 'dc-due-diligence')
   from converters.generate_pdf import generate_pdf
   r1 = generate_pdf('[opportunity-folder]/research/executive-summary.md', style='executive')
   r2 = generate_pdf('[opportunity-folder]/research/client-summary.md', style='client')
   print('Executive PDF:', r1.output_path, '| Success:', r1.success)
   print('Client PDF:', r2.output_path, '| Success:', r2.success)
   "
   ```

3. Report PDF paths in the final output summary.
```

### CSS Styling Pattern

**What:** Two CSS files in `dc-due-diligence/templates/pdf-styles/` control the look of each document type. Keeping CSS external means style changes don't require code edits.

**When:** Always -- even the default styling should live in CSS files, not hardcoded strings.

**Example (`templates/pdf-styles/executive.css`):**
```css
/* Executive Summary -- internal, dense, data-forward */
body {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-size: 10pt;
    line-height: 1.5;
    color: #1a1a1a;
    margin: 0;
    padding: 0;
}
h1 { font-size: 18pt; font-weight: 700; border-bottom: 2px solid #333; padding-bottom: 4px; }
h2 { font-size: 13pt; font-weight: 600; margin-top: 16pt; }
h3 { font-size: 11pt; font-weight: 600; color: #444; }
table { border-collapse: collapse; width: 100%; margin: 8pt 0; }
th { background: #2c3e50; color: white; padding: 6pt 8pt; text-align: left; }
td { border: 1px solid #ccc; padding: 5pt 8pt; }
tr:nth-child(even) { background: #f5f5f5; }
code { background: #f0f0f0; padding: 1px 4px; font-family: monospace; font-size: 9pt; }
```

## Don't Hand-Roll

| Problem | Existing Solution | Why Not Build It |
|---------|-------------------|------------------|
| Markdown table rendering | markdown-pdf handles via markdown-it-py | Table parsing has many edge cases (escaped pipes, colspan, alignment); the pipeline already validates these work in the library |
| HTML-to-PDF layout engine | PyMuPDF (via markdown-pdf) | Page layout with proper text reflow, image embedding, and PDF spec compliance is thousands of lines of spec-compliant code |
| Unicode and CJK text in PDFs | PyMuPDF's built-in font handling | Font embedding, glyph mapping, and right-to-left text handling are notoriously tricky; let the library do it |
| Page breaks and TOC generation | markdown-pdf Section + toc_level parameter | Manual page break tracking requires understanding the render tree; markdown-pdf's `Section` class handles page boundaries and bookmark generation |

## Pitfalls

### AGPL License Exposure on Distribution

**What goes wrong:** Both `markdown-pdf` and `PyMuPDF` are AGPL-3.0 licensed. If the `dc-due-diligence` plugin is ever published to the shipfast.cc marketplace or distributed to third parties as a plugin, any user who receives it must also receive the source under AGPL -- or purchase a commercial license from Artifex for PyMuPDF.

**How to avoid:** For internal Data Canopy use, AGPL compliance is simple (the source is already available). For marketplace distribution, either (a) evaluate whether WeasyPrint (BSD-licensed) is worth the Pango system dependency for the cleaner license, or (b) require a PyMuPDF commercial license note in plugin documentation. Document this explicitly in `dc-due-diligence/README.md` when adding the dependency.

### Pango/System Library Trap with WeasyPrint

**What goes wrong:** If the decision is later switched to WeasyPrint, it silently works on machines that happen to have Pango installed (e.g., developer machines with `brew install weasyprint`) but breaks on clean machines or CI environments where Pango is absent. The Python import succeeds; the failure only surfaces at render time with a cryptic `OSError`.

**How to avoid:** Stick with `markdown-pdf` for its zero-system-dependency design. If WeasyPrint is chosen for any reason, document the system dependency in `setup.sh` with an explicit `brew install weasyprint` step, and add a preflight check in the PDF generator that tests WeasyPrint import before the pipeline runs.

### Image Path Resolution

**What goes wrong:** The executive summary markdown files may include relative image references (e.g., `![](../charts/power-capacity.png)`). `markdown-pdf` resolves image paths relative to the current working directory, not the markdown file's location. If the script is called from a different working directory, images silently disappear from the PDF with no error.

**How to avoid:** Set the `root` parameter on `Section` to the markdown file's parent directory: `Section(text, root=str(source.parent))`. This tells `markdown-pdf` where to resolve relative paths. Always call the generator with absolute paths.

### Large Reports Causing Memory Pressure

**What goes wrong:** The executive summary for a complex data center deal can be 20-40 pages of dense markdown including tables and scoring rubrics. `PyMuPDF` (via `markdown-pdf`) loads the full document into memory at once. For very large reports (100+ pages), this can cause slow generation or OOM on memory-constrained machines.

**How to avoid:** For this project, 20-40 pages is well within normal operating range -- no action needed. If reports grow significantly, the `Section`-based API allows splitting a single markdown into multiple sections with controlled page breaks, reducing peak memory.

### Missing Output Directory

**What goes wrong:** If the `research/` subdirectory doesn't exist when the PDF generator is called (e.g., the orchestrator creates output files in a different location than expected), `MarkdownPdf.save()` raises a `FileNotFoundError` with a confusing message that points to the PDF path, not the missing directory.

**How to avoid:** In `generate_pdf()`, ensure the output directory exists before calling `pdf.save()`: `output.parent.mkdir(parents=True, exist_ok=True)`. This is defensive and consistent with how the existing pipeline creates `_converted/` directories.

### Orchestrator Timing: PDF Must Run After Agents Complete

**What goes wrong:** If the PDF generation is wired into the orchestrator incorrectly -- for example, if the orchestrator task spawns agents and then immediately tries to generate PDFs without waiting for agent output -- the markdown files won't exist yet and the PDF generator will fail silently or raise a file-not-found error.

**How to avoid:** PDF generation is a sequential tail step. In the SKILL.md orchestrator, explicitly verify that the markdown output files exist before invoking the generator. Use a conditional check pattern and surface any failure in the final summary output rather than allowing silent failures.

## Code Examples

### Basic Usage

```python
from converters.generate_pdf import generate_pdf
from pathlib import Path

# Generate executive summary PDF
result = generate_pdf(
    "/path/to/opportunity/research/executive-summary.md",
    style="executive",
)
if result.success:
    print(f"PDF written: {result.output_path}")
else:
    print(f"PDF generation failed: {result.error}")

# Generate client summary PDF
result = generate_pdf(
    "/path/to/opportunity/research/client-summary.md",
    style="client",
)
```

### Adding to pyproject.toml

```toml
[project]
dependencies = [
    "pdfplumber>=0.11.0",
    "openpyxl>=3.1.0",
    "pyxlsb>=1.0.10",
    "python-docx>=1.1.0",
    "python-pptx>=1.0.0",
    "anthropic>=0.40.0",
    "Pillow>=10.0.0",
    "markdown-pdf>=1.13.1",   # <-- add this
]
```

### Generating Both PDFs from the Orchestrator Context

```python
"""Example of how the orchestrator triggers PDF generation after agents finish."""
import subprocess
import sys
from pathlib import Path

def generate_report_pdfs(opportunity_folder: str) -> None:
    research_dir = Path(opportunity_folder) / "research"
    exec_md = research_dir / "executive-summary.md"
    client_md = research_dir / "client-summary.md"

    # Only generate if the markdown files exist.
    for md_path, style in [(exec_md, "executive"), (client_md, "client")]:
        if md_path.exists():
            from converters.generate_pdf import generate_pdf
            result = generate_pdf(md_path, style=style)
            if result.success:
                print(f"  PDF: {result.output_path}")
            else:
                print(f"  PDF failed for {md_path.name}: {result.error}")
        else:
            print(f"  Skipping PDF: {md_path.name} not found")
```

## Conflicts with User Decisions

| Decision | Conflict | Severity | Recommendation |
|----------|----------|----------|---------------|
| "markdown to PDF approach" (not WeasyPrint or reportlab directly) | markdown-pdf uses PyMuPDF under the hood, which is AGPL-3.0. This is a transitive license concern, not a technical conflict. | MEDIUM | Acceptable for internal use; document the AGPL dependency in README. For marketplace distribution, evaluate WeasyPrint (BSD) or commercial PyMuPDF license. |

## Quality Gate

Before considering this file complete, verify:
- [x] Every locked decision has deep investigation findings
- [x] Every flexible area has 2-3 ranked options with tradeoffs
- [x] Deferred items are listed but NOT researched
- [x] Don't Hand-Roll section present (populated or explicitly empty)
- [x] Conflicts section present (populated or explicitly "No conflicts")
- [x] Reuse Metadata section has all fields populated
- [x] Confidence level reflects actual source quality
