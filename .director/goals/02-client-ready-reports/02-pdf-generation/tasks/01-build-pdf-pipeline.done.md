# Task: Build markdown-to-PDF conversion pipeline

## What To Do

Create a `generate_pdf.py` module in the dc-due-diligence converters directory that converts markdown files to styled PDF documents. Research recommends `markdown-pdf` for zero system dependencies and pure Python wheels. Create separate CSS stylesheets for the executive summary and client summary to control their visual presentation.

## Why It Matters

Executives and deal presenters expect PDF documents they can forward, print, or archive. The markdown versions remain for AI workflows, but the PDF is the human-facing deliverable.

## Size

**Estimate:** medium

New Python module following the existing converter pattern, plus CSS stylesheets for document styling. Needs testing with actual markdown output to ensure proper rendering of tables, headings, and lists.

## Done When

- [x] generate_pdf.py module exists in dc-due-diligence/converters/
- [x] Converts markdown input to styled PDF output
- [x] CSS stylesheets in templates/pdf-styles/ control document appearance
- [x] Tables, headings, lists, and emphasis render correctly in PDF
- [x] No system-level dependencies required (pure Python)

## Needs First

Nothing -- this can be built alongside the client summary work, using existing executive summary markdown for testing.
