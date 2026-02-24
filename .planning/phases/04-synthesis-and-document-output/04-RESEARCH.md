# Phase 4: Synthesis and Document Output - Research

**Researched:** 2026-02-24
**Domain:** Agent porting (CLI to Cowork), document generation (Markdown to DOCX)
**Confidence:** HIGH

## Summary

Phase 4 ports three synthesis agents (Risk Assessment, Executive Summary, Client Summary) from the CLI plugin to the Cowork desktop plugin and adds Word (.docx) document generation for final deliverables. The agent porting follows the identical adaptation pattern established in Phase 3 (Plan 03-01 through 03-03): keep verbatim content (scoring rubric logic, tier framework, analysis workflow, output templates), replace path conventions (`OPPORTUNITY_FOLDER` to `WORKSPACE_FOLDER`, `PLUGIN_DIR` to inline references), remove Python/MCP dependencies, and add Cowork-specific task instructions (Read tool for file access, inventory-based reading).

Word document generation uses pandoc (confirmed installed at `/usr/local/bin/pandoc 3.8.2.1`) to convert the markdown reports to `.docx` format. Pandoc is the most reliable command-line tool for this conversion and is already available on the development machine. The orchestrator writes markdown first, then runs pandoc as a bash post-processing step. A fallback strategy exists: if pandoc is not available at runtime, the orchestrator can skip DOCX generation and inform the user that markdown-only output was produced.

**Primary recommendation:** Port the 3 synthesis agents using the Phase 3 adaptation pattern, embed the scoring rubric directly in the Executive Summary agent file (avoiding cross-file references that break in Cowork), and use pandoc for markdown-to-DOCX conversion with a graceful fallback.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Primary output format is Word (.docx) alongside markdown
- PDF generation is not needed -- Word is the final deliverable format
- Claude has discretion on the Word generation approach (pandoc if available, raw XML assembly, or whatever works most reliably in the Cowork environment at runtime)
- Visual polish: clean and readable with proper headings, tables, bold/italic -- standard Word formatting, no custom branding or color palette required
- Final deliverables go in an `output/` subfolder within the opportunity folder (not the root)
- Three Word files in output/: Executive Summary (.docx), Client Summary (.docx), Risk Assessment (.docx)
- Markdown versions of all reports remain in research/ as they do now
- Domain reports (9 agents) stay as markdown in research/ -- not converted to Word
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

### Deferred Ideas (OUT OF SCOPE)
- PDF output generation -- user confirmed not needed if Word works
- Branded/styled document output matching CLI CSS templates -- deferred unless explicitly requested later
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| SYNTH-01 | Risk Assessment agent reads all 9 domain reports and identifies cross-cutting risks | Port risk-assessment-agent.md using Phase 3 adaptation pattern; agent reads research/*.md files from workspace folder |
| SYNTH-02 | Executive Summary agent produces scored summary with Pursue / Proceed with Caution / Pass verdict | Port executive-summary-agent.md with embedded scoring rubric; reads all 10 reports (9 domain + risk assessment) |
| SYNTH-03 | Executive Summary applies the same scoring rubric and normalized category scores as the CLI version | Embed scoring rubric content directly in agent file (avoid cross-file template reads that may fail in Cowork) |
| SYNTH-04 | Client Summary agent produces external-facing report without internal scoring language | Port client-summary-agent.md with embedded client summary template structure |
| SYNTH-05 | Synthesis agents handle missing domain reports gracefully (continue with available data) | CLI agents already handle this (score missing domains as Low, note gaps); preserve this logic verbatim |
| OUTPUT-01 | All reports written to the workspace folder as files the user can access | Markdown in research/, Word in output/ subfolder |
| OUTPUT-02 | Final deliverables generated in Word (DOCX) format for easy editing | pandoc markdown-to-docx conversion; fallback to markdown-only if pandoc unavailable |
| OUTPUT-03 | Final deliverables also generated in PDF format for distribution | CONTEXT.md explicitly defers PDF -- user confirmed not needed. Requirement will be marked N/A or satisfied by noting Word can export to PDF natively |
| OUTPUT-04 | Markdown versions of all reports also available in workspace folder | Synthesis agents write markdown to research/ as primary output; DOCX is a secondary conversion |
</phase_requirements>

## Standard Stack

### Core

| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| pandoc | 3.8.2.1 | Markdown to DOCX conversion | Industry standard document converter; already installed on dev machine; handles tables, headings, bold/italic natively |
| Claude Cowork Task tool | native | Parallel agent dispatch | Confirmed working in Phase 1 smoke test; used for all 9 domain agents in Phase 3 |
| bash | native | Post-processing (pandoc invocation, file management) | Available in Cowork environment; used throughout Phases 1-3 |

### Supporting

| Tool | Purpose | When to Use |
|------|---------|-------------|
| mkdir -p | Create output/ subdirectory | Before writing DOCX files |
| stat -f%z | Check report file sizes for resume logic | Same pattern as Phase 3 domain agent resume |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pandoc | Raw Open XML assembly (unzip/edit XML/rezip) | Works without pandoc but extremely fragile, no table support, maintenance nightmare |
| pandoc | Claude Desktop native DOCX creation | Confirmed available in Claude.ai/Desktop web but NOT available inside Task tool subagents; unreliable for automated pipeline |
| pandoc | python-docx | Violates project constraint (no Python dependencies for non-technical user) |

**Recommendation:** pandoc with runtime availability check. If `which pandoc` fails, skip DOCX generation and display message: "Word document generation requires pandoc. Install with `brew install pandoc` or download from pandoc.org. Markdown reports are available in the research/ folder."

## Architecture Patterns

### Agent Porting Pattern (from Phase 3)

The Phase 3 adaptation pattern is well-established and must be followed exactly:

| Element | Keep Verbatim | Replace | Remove | Add |
|---------|---------------|---------|--------|-----|
| Safety Protocol | Yes | - | - | - |
| Analysis workflow/phases | Yes | - | - | - |
| Extraction categories | Yes | - | - | - |
| Scoring rubric logic | Yes | - | - | - |
| Tier framework | Yes | - | - | - |
| Output format template | Yes | - | - | - |
| Verification sources | Yes | - | - | - |
| `${OPPORTUNITY_FOLDER}` | - | `${WORKSPACE_FOLDER}` | - | - |
| `${PLUGIN_DIR}/templates/*` | - | Embed content inline | - | - |
| `_converted/manifest.json` | - | `_dd_inventory.json` | - | - |
| MCP tool references | - | - | Yes | - |
| Python dependency references | - | - | Yes | - |
| "Your Task" section | - | - | - | Cowork-specific Read tool instructions |

### Synthesis Wave Architecture

The orchestrator SKILL.md already references Wave 2 and Wave 3 placeholder structure. Phase 4 fills this in:

```
Wave 1: 9 domain agents (parallel) — COMPLETE (Phase 3)
Wave 2: Risk Assessment agent (sequential, reads all domain reports)
Wave 3: Executive Summary + Client Summary (sequential, ES first then CS)
```

Wave 3 ordering matters: Executive Summary must complete before Client Summary, because the Client Summary agent reads the Executive Summary as its primary input.

### Orchestrator Dispatch Pattern

The synthesis agents run sequentially, not in parallel, because each depends on the output of prior waves:

1. **Risk Assessment** (Wave 2): Reads 9 domain reports from `research/`, writes `research/risk-assessment-report.md`
2. **Executive Summary** (Wave 3a): Reads 10 reports (9 domain + risk assessment), writes `EXECUTIVE_SUMMARY.md` to workspace root
3. **Client Summary** (Wave 3b): Reads `EXECUTIVE_SUMMARY.md` + 10 research reports, writes `CLIENT_SUMMARY.md` to workspace root
4. **DOCX Generation** (Wave 4 / post-processing): Convert 3 markdown files to DOCX in `output/` subfolder

### Output File Layout

```
${WORKSPACE_FOLDER}/
├── research/
│   ├── power-report.md              (Phase 3, domain)
│   ├── connectivity-report.md       (Phase 3, domain)
│   ├── water-cooling-report.md      (Phase 3, domain)
│   ├── land-zoning-report.md        (Phase 3, domain)
│   ├── ownership-report.md          (Phase 3, domain)
│   ├── environmental-report.md      (Phase 3, domain)
│   ├── commercials-report.md        (Phase 3, domain)
│   ├── natural-gas-report.md        (Phase 3, domain)
│   ├── market-comparables-report.md (Phase 3, domain)
│   └── risk-assessment-report.md    (Phase 4, Wave 2)
├── EXECUTIVE_SUMMARY.md             (Phase 4, Wave 3a)
├── CLIENT_SUMMARY.md                (Phase 4, Wave 3b)
└── output/
    ├── executive-summary.docx       (Phase 4, post-processing)
    ├── client-summary.docx          (Phase 4, post-processing)
    └── risk-assessment.docx         (Phase 4, post-processing)
```

### Scoring Rubric Embedding Strategy

The CLI version's Executive Summary agent references `${PLUGIN_DIR}/templates/scoring-rubric.md` as a separate file read. In Cowork, cross-file template reads from within Task tool subagents are unreliable -- the agent may not be able to resolve `${PLUGIN_DIR}` paths because the plugin directory is not always available inside Task tool scope.

**Recommendation:** Embed the scoring rubric content directly into the executive-summary-agent.md file. The scoring rubric is ~8KB of structured content (tier definitions, criteria tables, verdict logic). Embedding it increases the agent file size but guarantees the agent always has access to its scoring methodology. This is the same pattern used for the Document Safety Protocol (embedded in every domain agent rather than referenced externally).

Similarly, embed the client summary template structure directly in the client-summary-agent.md file.

### Checkpoint Strategy for Synthesis Wave

Extend the existing `_dd_status.json` checkpoint with synthesis phase tracking:

```json
{
  "phase": "synthesis",
  "reports_complete": 9,
  "risk_assessment_complete": true,
  "executive_summary_complete": false,
  "client_summary_complete": false,
  "docx_complete": false,
  "timestamp": "2026-02-24T..."
}
```

Resume logic:
- If `risk_assessment_complete` is true and `research/risk-assessment-report.md` exists (> 500 bytes), skip to Executive Summary
- If `executive_summary_complete` is true and `EXECUTIVE_SUMMARY.md` exists (> 500 bytes), skip to Client Summary
- If `client_summary_complete` is true but `docx_complete` is false, skip to DOCX generation
- If all complete, skip to completion UX

### Completion UX Pattern

After all deliverables are generated, display:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 VERDICT: [Pursue / Proceed with Caution / Pass]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Key Highlights:
• [Strength 1 from Executive Summary]
• [Strength 2 from Executive Summary]
• [Concern 1 from Executive Summary]
• [Concern 2 from Executive Summary]

Deliverables:
• ${WORKSPACE_FOLDER}/output/executive-summary.docx
• ${WORKSPACE_FOLDER}/output/client-summary.docx
• ${WORKSPACE_FOLDER}/output/risk-assessment.docx
• ${WORKSPACE_FOLDER}/EXECUTIVE_SUMMARY.md
• ${WORKSPACE_FOLDER}/CLIENT_SUMMARY.md
• ${WORKSPACE_FOLDER}/research/risk-assessment-report.md

9 domain reports available in: ${WORKSPACE_FOLDER}/research/
```

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Markdown to DOCX | Custom Open XML builder | pandoc | pandoc handles tables, nested formatting, headings, bold/italic correctly; raw XML assembly misses edge cases |
| Scoring rubric | New rubric from scratch | Embed existing CLI scoring-rubric.md | CLI rubric is tested against real deals; changing it creates version drift |
| Tier framework | Alternative weighting scheme | Preserve CLI tier logic verbatim | Tier 1/2/3 framework is validated by domain experts |
| Client summary transformation | Simple text truncation | Full transformation logic from CLI agent | Client summary requires removing internal scoring, reframing tone, aggregating questions |
| Source document counting | New manifest format | Read `_dd_inventory.json` total_files field | Inventory already has the count; no manifest.json in Cowork (no `_converted/` pipeline) |

## Common Pitfalls

### Pitfall 1: Cross-File Template References Breaking in Cowork
**What goes wrong:** Agent file references `${PLUGIN_DIR}/templates/scoring-rubric.md` but the Task tool subagent cannot resolve `${PLUGIN_DIR}` to the plugin installation path.
**Why it happens:** Cowork plugin paths are managed by the platform and not always exposed to subagent contexts.
**How to avoid:** Embed all template content directly in agent files. The scoring rubric (~8KB), client summary template structure, and agent output template must all be inlined.
**Warning signs:** Agent reports "could not read file" or produces output without scoring.

### Pitfall 2: Executive Summary Before Risk Assessment
**What goes wrong:** Executive Summary agent runs before Risk Assessment completes, produces a summary missing the cross-domain risk synthesis.
**Why it happens:** Orchestrator dispatches both in parallel instead of sequentially.
**How to avoid:** Strictly sequential dispatch: Risk Assessment (Wave 2) must complete and its report verified before Executive Summary (Wave 3a) dispatch.
**Warning signs:** Executive Summary has empty or missing "Risk Assessment" section.

### Pitfall 3: Client Summary Exposing Internal Scoring
**What goes wrong:** Client Summary output contains tier labels (Tier 1, Tier 2), score labels (High/Medium/Low), confidence percentages, or agent names.
**Why it happens:** Agent transformation logic is complex; easy to miss internal terms.
**How to avoid:** The CLI client-summary-agent.md has a detailed exclusion checklist and quality review phase. Preserve this verbatim.
**Warning signs:** grep for "Tier 1|Tier 2|Tier 3|HIGH|MEDIUM|LOW|GREEN|YELLOW|RED|agent" in CLIENT_SUMMARY.md output.

### Pitfall 4: Source Document Count Using Wrong File
**What goes wrong:** CLI agents reference `_converted/manifest.json` for source document count, which does not exist in Cowork (no Python conversion pipeline).
**Why it happens:** Direct copy of CLI agent without adapting the manifest reference.
**How to avoid:** Replace manifest.json references with `_dd_inventory.json` total_files field, or use "the provided documents" fallback.
**Warning signs:** Agent reports "could not find manifest.json" or hardcodes a count.

### Pitfall 5: DOCX Generation Failing Silently
**What goes wrong:** pandoc is not installed on the end user's machine, DOCX files are never generated, user thinks pipeline is broken.
**Why it happens:** pandoc is a development dependency, not guaranteed on all machines.
**How to avoid:** Runtime check (`which pandoc`); if unavailable, display clear message and continue with markdown-only output. Never fail the entire pipeline because DOCX conversion fails.
**Warning signs:** `output/` directory empty or missing.

### Pitfall 6: Markdown Output Paths Not Matching CLI Conventions
**What goes wrong:** Executive Summary writes to `research/EXECUTIVE_SUMMARY.md` instead of workspace root.
**Why it happens:** Confusion between domain reports (go in research/) and synthesis reports (go in workspace root).
**How to avoid:** Explicit path specification:
- Risk Assessment: `${WORKSPACE_FOLDER}/research/risk-assessment-report.md` (in research/, same as domain reports)
- Executive Summary: `${WORKSPACE_FOLDER}/EXECUTIVE_SUMMARY.md` (workspace root)
- Client Summary: `${WORKSPACE_FOLDER}/CLIENT_SUMMARY.md` (workspace root)
**Warning signs:** Files in wrong location.

## Code Examples

### Pandoc Markdown to DOCX Conversion

```bash
# Convert a single markdown file to DOCX
pandoc -f markdown -t docx -o output/executive-summary.docx EXECUTIVE_SUMMARY.md

# With better table formatting
pandoc -f markdown -t docx --standalone -o output/executive-summary.docx EXECUTIVE_SUMMARY.md
```

### Runtime Pandoc Check with Fallback

```bash
TARGET_FOLDER="${WORKSPACE_FOLDER}"
mkdir -p "$TARGET_FOLDER/output"

if command -v pandoc &> /dev/null; then
  echo "Converting reports to Word format..."

  # Executive Summary
  if [ -f "$TARGET_FOLDER/EXECUTIVE_SUMMARY.md" ]; then
    pandoc -f markdown -t docx -o "$TARGET_FOLDER/output/executive-summary.docx" "$TARGET_FOLDER/EXECUTIVE_SUMMARY.md"
    echo "✓ executive-summary.docx"
  fi

  # Client Summary
  if [ -f "$TARGET_FOLDER/CLIENT_SUMMARY.md" ]; then
    pandoc -f markdown -t docx -o "$TARGET_FOLDER/output/client-summary.docx" "$TARGET_FOLDER/CLIENT_SUMMARY.md"
    echo "✓ client-summary.docx"
  fi

  # Risk Assessment
  if [ -f "$TARGET_FOLDER/research/risk-assessment-report.md" ]; then
    pandoc -f markdown -t docx -o "$TARGET_FOLDER/output/risk-assessment.docx" "$TARGET_FOLDER/research/risk-assessment-report.md"
    echo "✓ risk-assessment.docx"
  fi
else
  echo "⚠ pandoc not found. Word document generation skipped."
  echo "  Install pandoc: brew install pandoc"
  echo "  Markdown reports are available in the workspace folder."
fi
```

### Synthesis Agent Resume Check

```bash
TARGET_FOLDER="${WORKSPACE_FOLDER}"
echo "=== Checking synthesis progress ==="

# Risk Assessment
RA_SIZE=$(stat -f%z "$TARGET_FOLDER/research/risk-assessment-report.md" 2>/dev/null || echo 0)
if [ "$RA_SIZE" -gt 500 ]; then
  echo "SKIP: Risk Assessment (report exists, ${RA_SIZE} bytes)"
  RA_DONE=true
else
  echo "DISPATCH: Risk Assessment"
  RA_DONE=false
fi

# Executive Summary
ES_SIZE=$(stat -f%z "$TARGET_FOLDER/EXECUTIVE_SUMMARY.md" 2>/dev/null || echo 0)
if [ "$ES_SIZE" -gt 500 ]; then
  echo "SKIP: Executive Summary (report exists, ${ES_SIZE} bytes)"
  ES_DONE=true
else
  echo "DISPATCH: Executive Summary"
  ES_DONE=false
fi

# Client Summary
CS_SIZE=$(stat -f%z "$TARGET_FOLDER/CLIENT_SUMMARY.md" 2>/dev/null || echo 0)
if [ "$CS_SIZE" -gt 500 ]; then
  echo "SKIP: Client Summary (report exists, ${CS_SIZE} bytes)"
  CS_DONE=true
else
  echo "DISPATCH: Client Summary"
  CS_DONE=false
fi
```

## State of the Art

| Old Approach (CLI) | Current Approach (Cowork) | When Changed | Impact |
|---------------------|---------------------------|--------------|--------|
| `${PLUGIN_DIR}/templates/scoring-rubric.md` read at runtime | Embed scoring rubric in agent file | Phase 4 | Guarantees agent always has rubric; adds ~8KB to agent file |
| `${OPPORTUNITY_FOLDER}` path convention | `${WORKSPACE_FOLDER}` path convention | Phase 3 | Aligns with Cowork workspace model |
| `_converted/manifest.json` for doc count | `_dd_inventory.json` total_files field | Phase 2 | No Python conversion pipeline in Cowork |
| MCP tool references (Tavily, Exa, Firecrawl) | WebSearch/WebFetch only | Phase 3 | Cowork does not have MCP server configuration |
| Python pdf-to-html converter for output | pandoc markdown-to-docx | Phase 4 | No Python dependency; pandoc is simpler and more reliable |
| PDF output via wkhtmltopdf/Chrome headless | No PDF output (user decision) | Phase 4 | Simplified output pipeline |

## Open Questions

1. **Pandoc availability on end-user machines**
   - What we know: pandoc is installed on the development machine (v3.8.2.1). Cowork runs on macOS (Claude Desktop).
   - What's unclear: Whether typical Cowork users will have pandoc installed.
   - Recommendation: Runtime check with graceful fallback. The markdown reports are the primary output; DOCX is a convenience layer. Document pandoc installation in the plugin README (Phase 5 deliverable).

2. **Agent file size after embedding**
   - What we know: CLI executive-summary-agent.md is ~45KB. Scoring rubric is ~34KB. Combined would be ~79KB.
   - What's unclear: Whether a ~79KB agent file causes context window pressure in Cowork Task tool subagents.
   - Recommendation: Embed the essential scoring criteria (Quick Reference Table + Verdict Logic + Category Scoring, ~15KB) rather than the full rubric. The tier philosophy narrative and edge case discussions can be condensed. The full 34KB rubric is not needed if the scoring criteria and verdict rules are included.

3. **DOCX table rendering quality**
   - What we know: pandoc converts markdown tables to DOCX tables with standard formatting.
   - What's unclear: Whether complex tables (Executive Summary's detailed scoring tables) render cleanly.
   - Recommendation: Accept pandoc's default table rendering. The user specified "standard Word formatting, no custom branding" -- pandoc's defaults meet this requirement.

## Sources

### Primary (HIGH confidence)
- CLI plugin `dc-due-diligence/agents/risk-assessment-agent.md` -- full reference implementation (47KB)
- CLI plugin `dc-due-diligence/agents/executive-summary-agent.md` -- full reference implementation (45KB)
- CLI plugin `dc-due-diligence/agents/client-summary-agent.md` -- full reference implementation (22KB)
- CLI plugin `dc-due-diligence/templates/scoring-rubric.md` -- scoring criteria and verdict logic (34KB)
- CLI plugin `dc-due-diligence/templates/client-summary-template.md` -- client summary structure (15KB)
- Cowork desktop plugin `dc-due-diligence-desktop/agents/power-agent.md` -- Phase 3 adaptation pattern reference
- Cowork desktop plugin `dc-due-diligence-desktop/commands/due-diligence.md` -- current orchestrator
- Cowork desktop plugin `dc-due-diligence-desktop/skills/due-diligence/SKILL.md` -- current skill file

### Secondary (MEDIUM confidence)
- pandoc official documentation (pandoc.org) -- markdown-to-docx conversion confirmed
- Local pandoc installation verified: `/usr/local/bin/pandoc 3.8.2.1`
- Claude Desktop file creation capabilities confirmed via web search (October 2025 GA)

### Tertiary (LOW confidence)
- Claude Desktop native DOCX creation inside Task tool subagents -- unverified, assumed NOT available (conservative approach)

## Metadata

**Confidence breakdown:**
- Agent porting: HIGH - Exact same pattern as Phase 3, reference implementations available
- Scoring rubric integration: HIGH - Source material is complete and tested
- DOCX generation: HIGH - pandoc installed and verified, fallback strategy defined
- Orchestrator dispatch: HIGH - Sequential wave pattern is straightforward extension of Phase 3

**Research date:** 2026-02-24
**Valid until:** 2026-03-24 (stable domain, no fast-moving dependencies)
