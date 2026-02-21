# Task: Wire PDF generation into orchestrator for both summaries

## What To Do

Add PDF generation as a final step in the orchestrator skill, running after the client summary agent completes. It should convert both the executive summary markdown and the client-facing summary markdown to PDF, writing the PDF files alongside the markdown versions in the opportunity folder.

## Why It Matters

This is the last step in the pipeline -- the one that produces the deliverables people actually send. Running it at the end ensures all content is finalized before conversion.

## Size

**Estimate:** small

A Python script invocation in the orchestrator after Wave 4. The PDF conversion module already exists from the previous task; this just wires it into the pipeline.

## Done When

- [x] Orchestrator triggers PDF generation after all agent waves complete
- [x] Executive summary PDF is generated alongside the markdown version
- [x] Client summary PDF is generated alongside the markdown version
- [x] PDF files are named clearly (e.g., executive-summary.pdf, client-summary.pdf)

## Needs First

Needs the markdown-to-PDF pipeline built and the client summary agent wired into the orchestrator.
