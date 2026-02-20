# Step 2: PDF generation

## What This Delivers

Both the executive summary and client-facing summary are available as polished PDFs, ready to share via email or print. Markdown versions are preserved for AI workflows and internal use.

## Tasks

- [ ] Task 1: Build markdown-to-PDF conversion pipeline
- [ ] Task 2: Wire PDF generation into orchestrator for both summaries

## Needs First

Needs the client-facing summary built from Step 1, so both documents are ready for PDF conversion.

## Decisions

### Locked
- Markdown-to-PDF conversion pipeline (not direct PDF rendering with WeasyPrint or reportlab)
- Both executive summary and client-facing summary get PDF versions
- Markdown versions preserved alongside PDFs for AI workflows

### Flexible
- Specific Python markdown-to-PDF library -- research recommends `markdown-pdf` for zero system dependencies and pure Python wheels; alternatives include WeasyPrint (better print quality but requires Pango system library) and md2pdf (also requires Pango)
