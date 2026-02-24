# Phase 4: Synthesis and Document Output - Context

**Gathered:** 2026-02-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Port the Risk Assessment, Executive Summary, and Client Summary agents from the CLI plugin to the Cowork desktop plugin. Generate final deliverables as Word (.docx) files. The scoring rubric, tier framework, and agent logic already exist in the CLI version and should be adapted for the Cowork environment (no Python, native file reading, Cowork path conventions). PDF output is not needed.

</domain>

<decisions>
## Implementation Decisions

### Document Output Format
- Primary output format is Word (.docx) alongside markdown
- PDF generation is not needed -- Word is the final deliverable format
- Claude has discretion on the Word generation approach (pandoc if available, raw XML assembly, or whatever works most reliably in the Cowork environment at runtime)
- Visual polish: clean and readable with proper headings, tables, bold/italic -- standard Word formatting, no custom branding or color palette required

### Output File Organization
- Final deliverables go in an `output/` subfolder within the opportunity folder (not the root)
- Three Word files in output/: Executive Summary (.docx), Client Summary (.docx), Risk Assessment (.docx)
- Markdown versions of all reports remain in research/ as they do now
- Domain reports (9 agents) stay as markdown in research/ -- not converted to Word

### Completion UX
- When the full pipeline finishes, the orchestrator shows the verdict (Pursue / Proceed with Caution / Pass) prominently
- Below the verdict, show 3-4 key highlights from the Executive Summary (strengths and concerns)
- Below the highlights, print the file paths to all generated deliverables
- Print paths only -- no attempt to auto-open folders or files

### Claude's Discretion
- Word generation mechanism (pandoc vs. raw XML vs. other approach) -- pick the most reliable option
- Scoring rubric delivery method (embed in agent file vs. read from templates/ directory)
- How synthesis agents reference paths in the Cowork plugin environment
- How to handle session interruption during synthesis wave (checkpoint strategy)
- Graceful degradation when domain reports are missing -- the CLI agents already handle this, adapt as needed

</decisions>

<specifics>
## Specific Ideas

- The CLI version's 3 synthesis agents (risk-assessment-agent.md, executive-summary-agent.md, client-summary-agent.md) are the reference implementation -- port their logic, scoring rubric, and tiered framework
- The scoring rubric at dc-due-diligence/templates/scoring-rubric.md defines the exact High/Medium/Low criteria and verdict logic (Pursue / Proceed with Caution / Pass)
- The client summary template at dc-due-diligence/templates/client-summary-template.md defines the external-facing document structure
- The existing desktop orchestrator (SKILL.md) already references Wave 2 (Risk Assessment) and Wave 3 (Executive Summary) in its dispatch architecture -- Client Summary should be added to Wave 3
- "If we can do the word document, we won't need the pdf at all" -- PDF is explicitly not a deliverable

</specifics>

<deferred>
## Deferred Ideas

- PDF output generation -- user confirmed not needed if Word works
- Branded/styled document output matching CLI CSS templates -- deferred unless explicitly requested later

</deferred>

---

*Phase: 04-synthesis-and-document-output*
*Context gathered: 2026-02-24*
