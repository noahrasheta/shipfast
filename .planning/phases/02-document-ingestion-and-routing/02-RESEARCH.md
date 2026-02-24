# Phase 2: Document Ingestion and Routing - Research

**Researched:** 2026-02-24
**Domain:** Document ingestion, categorization, and routing for Claude Cowork plugin
**Confidence:** HIGH

## Summary

Phase 2 transforms the Phase 1 file discovery stub into a full document ingestion pipeline. The orchestrator must: (1) read all document types natively using Claude's built-in capabilities (no Python, no external converters), (2) create a structured inventory file on disk before any agents run, (3) categorize each document into one of 9 domain buckets using content-aware heuristics, and (4) enforce a strict 20-file-per-agent-dispatch batch limit.

The key architectural insight is that Claude Cowork can natively read PDF, DOCX, XLSX, PPTX, and image files through its file reading capabilities — the Read tool handles structured document formats, and Claude's vision/multimodal capabilities handle scanned PDFs and images. This eliminates the Python conversion pipeline that the CLI version requires. The routing logic is straightforward keyword/content matching against the 9 established domains, with batching as a simple array-split operation.

**Primary recommendation:** Build the inventory as a JSON file (machine-readable for downstream agents), use content-sniffing plus filename heuristics for domain categorization, and implement batching as a deterministic split (files 1-20 in batch 1, 21-40 in batch 2, etc.) per domain.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Chat output shows summary counts only: total files, count per type (PDF, DOCX, XLSX, PPTX, images)
- Detailed inventory file also written to disk — agents can reference it, user can review later
- No confidence indicators on domain assignments — just assign the best-fit domain and move on
- Files that don't match any of the 9 domains are logged as "uncategorized" and skipped (not routed to any agent)
- Skipped/uncategorized files are listed in the chat output so the user can see what was excluded
- Text-based files (.csv, .txt, .eml) should be attempted for reading and categorization — don't ignore them just because they aren't the 5 primary types
- Supported primary types: PDF, DOCX, XLSX, PPTX, images (per INGEST requirements), plus text-based files as a best-effort extension
- When a domain has more than 20 files, split into multiple batches and run the domain agent multiple times — no data left behind
- No user confirmation step before agent dispatch — inventory -> categorize -> dispatch automatically (one command does it all)
- If an agent batch fails mid-run, retry once, then skip and continue with remaining domains (synthesis phase handles missing reports gracefully)
- CLI version dispatches all 9 domain agents in parallel — desktop version should do the same if Cowork supports it (Phase 1 confirmed parallel dispatch available; sequential fallback retained)
- The user's mental model is "one command does everything" — no pauses or confirmation prompts during the ingestion/routing phase
- Keep chat output clean and minimal — the detailed routing info lives in the inventory file, not the conversation

### Claude's Discretion
- Inventory file format (JSON vs markdown vs other) — pick what works best for downstream agent consumption
- Domain categorization rules — how files get matched to the 9 domains (keyword matching, content inspection, folder name signals, etc.)
- Whether to use folder/directory names as categorization hints
- Batch progress verbosity in chat (per-batch updates vs domain-level only)

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| INGEST-01 | Orchestrator reads PDF files from workspace folder using Cowork's native file reading | Claude's Read tool handles PDF natively — no conversion needed. Read each PDF to extract text content for categorization. |
| INGEST-02 | Orchestrator reads DOCX, XLSX, PPTX files from workspace folder using native file reading | Claude's Read tool handles Office documents natively in Cowork. XLSX files are read as structured data. PPTX slides are read as text content. |
| INGEST-03 | Orchestrator reads scanned PDFs and images using Claude's native vision/OCR capabilities | Claude's multimodal vision reads images and scanned PDFs directly. Use the Read tool on image files — Claude interprets them visually. For scanned PDFs, Read tool + vision capabilities extract text from page images. |
| INGEST-04 | Orchestrator handles data rooms with 50+ files by batching or routing documents across agents to stay within the 20-file-per-chat platform limit | Deterministic batch splitting: for each domain bucket, split files into groups of max 20. Each batch becomes a separate agent dispatch. Domain agent runs once per batch, producing partial reports that are concatenated or the final batch produces the complete report incorporating all prior batch findings. |
| INGEST-05 | Orchestrator creates a document inventory/index of all files in the data room before dispatching agents | JSON inventory file written to workspace folder containing: file paths, types, sizes, domain assignments, batch assignments. Written before any agent dispatch. Downstream agents reference this file to know which documents to analyze. |
</phase_requirements>

## Standard Stack

### Core
| Component | Purpose | Why Standard |
|-----------|---------|--------------|
| Claude Read tool | Native file reading for all document types | Built into Cowork — reads PDF, DOCX, XLSX, PPTX, images without any external dependencies |
| Claude Vision | OCR/reading of scanned PDFs and images | Built into Claude's multimodal capabilities — no Python, no Tesseract, no external OCR |
| Bash (find/jq) | File discovery and JSON manipulation | Available in Cowork sandbox, used in Phase 1 already |
| JSON | Inventory file format | Machine-readable, parseable by both bash (jq) and Claude, downstream agents can consume directly |

### Supporting
| Component | Purpose | When to Use |
|-----------|---------|-------------|
| Bash arrays | Batch splitting logic | When a domain has >20 files, split into deterministic batches |
| grep/awk | Content keyword extraction | Quick domain categorization from file names and shallow content inspection |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| JSON inventory | Markdown inventory | Markdown is human-readable but harder for agents to parse programmatically; JSON wins for machine consumption |
| Content-based categorization | Filename-only categorization | Filename-only is faster but misses documents with generic names; content sniffing is more accurate |
| Deterministic batch split | Priority-based batching | Priority batching adds complexity without clear benefit when all files in a domain are equally important |

## Architecture Patterns

### Recommended Orchestrator Flow
```
1. File Discovery (bash find — reuse Phase 1 logic, expanded)
   ↓
2. Content Sniffing (Read first page/section of each file)
   ↓
3. Domain Categorization (keyword matching against 9 domains)
   ↓
4. Batch Assignment (split domains with >20 files)
   ↓
5. Write Inventory JSON to disk
   ↓
6. Display summary to user (counts only)
   ↓
7. Update _dd_status.json checkpoint
   ↓
[Phase 3 picks up here with agent dispatch]
```

### Pattern 1: Two-Pass Categorization
**What:** First pass uses filename and path heuristics (fast, no file reading). Second pass reads file content for files that couldn't be categorized by name alone.
**When to use:** Always — reduces unnecessary file reads for obviously-named documents.
**Example:**
```
Pass 1 (filename): "Power_Infrastructure_Assessment.pdf" → Power domain (obvious)
Pass 1 (filename): "Site_Report_2024.pdf" → Unknown (generic name)
Pass 2 (content):  Read first ~500 words of "Site_Report_2024.pdf" → mentions "fiber routes", "carrier diversity" → Connectivity domain
```

### Pattern 2: Domain Keyword Dictionary
**What:** Each of the 9 domains has a set of characteristic keywords. Score each document against all 9 keyword sets, assign to highest-scoring domain.
**When to use:** For the categorization step — provides deterministic, reproducible assignments.
**Example keyword sets:**
```
Power: utility, substation, transformer, MW, megawatt, electrical, grid, voltage, redundancy, UPS, generator, switchgear, power purchase
Connectivity: fiber, carrier, latency, bandwidth, network, ISP, peering, dark fiber, lit services, cross-connect, route diversity, meet-me
Water/Cooling: cooling, water, chiller, HVAC, airflow, temperature, humidity, PUE, WUE, cooling tower, water source, reclamation
Land/Zoning: zoning, parcel, entitlement, setback, easement, lot, acre, building permit, land use, variance, conditional use
Ownership: deed, title, lien, mortgage, LLC, owner, entity, beneficial, encumbrance, UCC, litigation
Environmental: contamination, hazardous, flood, seismic, Phase I, Phase II, remediation, brownfield, EPA, environmental impact
Commercials: lease, rent, NNN, CAM, tenant, escalation, term, option, pricing, rate, $/kW, cost, revenue, EBITDA
Natural Gas: gas, pipeline, natural gas, BTU, therms, generation, turbine, fuel, backup power
Market Comparables: comparable, market rate, transaction, sale, acquisition, benchmark, competitor, pricing, vacancy
```

### Pattern 3: Inventory JSON Structure
**What:** Structured JSON that downstream agents can parse.
**Example:**
```json
{
  "generated": "2026-02-24T10:00:00Z",
  "workspace_folder": "/path/to/data-room",
  "total_files": 47,
  "file_types": {
    "pdf": 25,
    "docx": 10,
    "xlsx": 8,
    "pptx": 2,
    "images": 2,
    "other": 0
  },
  "domains": {
    "power": {
      "files": ["path/to/file1.pdf", "path/to/file2.xlsx"],
      "count": 2,
      "batches": 1
    },
    "connectivity": {
      "files": ["path/to/file3.pdf"],
      "count": 1,
      "batches": 1
    }
  },
  "uncategorized": [
    {"path": "path/to/mystery.pdf", "reason": "No domain keywords matched"}
  ],
  "batching": {
    "power": [
      {"batch": 1, "files": ["file1.pdf", "file2.xlsx"]}
    ]
  }
}
```

### Anti-Patterns to Avoid
- **Reading every file fully for categorization:** Waste of context window. Read only what's needed — filename first, then first page/section if filename isn't enough.
- **Hardcoding file paths:** Use the workspace folder path from $ARGUMENTS and build paths dynamically.
- **Ignoring text-based files:** Per user decision, .csv, .txt, .eml should be attempted. Extend the find command beyond the 5 primary types.
- **Writing inventory after agent dispatch:** INGEST-05 explicitly requires inventory BEFORE dispatch. This is a hard ordering constraint.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| PDF text extraction | Custom PDF parser | Claude's native Read tool | Cowork reads PDFs natively; no external tools needed |
| OCR for scanned docs | Tesseract/Python OCR | Claude's vision capabilities | Multimodal model reads images directly; zero dependencies |
| JSON generation | String concatenation | jq or heredoc templates | Proper JSON escaping handles special characters in filenames |
| File type detection | Custom MIME type logic | File extension matching | Data room files follow standard naming; extension is reliable |

**Key insight:** The desktop version's biggest advantage over CLI is zero external dependencies. Claude Cowork reads everything natively — don't reintroduce Python for any document handling.

## Common Pitfalls

### Pitfall 1: Context Window Exhaustion During Categorization
**What goes wrong:** Reading 50+ full documents to categorize them burns the entire context window before agents even start.
**Why it happens:** Naive approach reads every file completely to determine its domain.
**How to avoid:** Two-pass approach — filename heuristics first (free), content sniffing only for unknowns (read first page only). Keep categorization lightweight.
**Warning signs:** Claude starts summarizing or losing track of earlier files during categorization.

### Pitfall 2: Inventory File Written Too Late
**What goes wrong:** Agent dispatch starts before inventory is persisted. If session crashes mid-dispatch, inventory is lost.
**Why it happens:** Trying to optimize by combining inventory write with dispatch.
**How to avoid:** Strict ordering — write inventory JSON to disk, THEN update _dd_status.json checkpoint, THEN start Phase 3 dispatch. Requirement INGEST-05 enforces this explicitly.
**Warning signs:** _dd_status.json says "routing" but no inventory file exists on disk.

### Pitfall 3: Batch Split Creates Uneven Workloads
**What goes wrong:** One domain gets 45 files split into 3 batches while 8 other domains have 1-3 files each.
**Why it happens:** Real data rooms are often power- or commercials-heavy.
**How to avoid:** Accept it — uneven distribution is the reality of data rooms. The batching exists to respect the 20-file limit, not to balance workloads. Each batch runs as a separate agent dispatch regardless.
**Warning signs:** N/A — this is expected behavior, not a bug.

### Pitfall 4: Text-Based Files (.csv, .txt, .eml) Silently Dropped
**What goes wrong:** The find command only matches the 5 primary types, so CSV/TXT/EML files are never discovered.
**Why it happens:** Phase 1's find command was intentionally limited to primary types.
**How to avoid:** Extend the find command to include .csv, .txt, .eml (and potentially .msg, .html). Per user decision, these are best-effort extensions.
**Warning signs:** User notices files in the data room that don't appear in the inventory.

### Pitfall 5: Domain Assignment Ambiguity
**What goes wrong:** A document about "power purchase agreement pricing" could match both Power and Commercials domains.
**Why it happens:** Real documents span multiple domains.
**How to avoid:** Assign to the FIRST matching domain by priority (or highest keyword score). Per user decision, no confidence indicators — just pick the best fit and move on. If a document is genuinely multi-domain, the domain agents' web research and cross-referencing will compensate.
**Warning signs:** Same document appearing in multiple domain buckets (a bug if it happens — each file should be assigned to exactly one domain or uncategorized).

### Pitfall 6: Scanned PDF vs Text PDF Detection
**What goes wrong:** Attempting text extraction on a scanned PDF returns empty/garbage, but the orchestrator doesn't realize it's scanned.
**Why it happens:** Read tool returns empty for image-only PDFs.
**How to avoid:** If Read returns very little text for a PDF, treat it as a scanned document and use vision capabilities. The categorization pass should handle this gracefully — if text extraction yields nothing useful, try vision on the first page.
**Warning signs:** PDF files showing up as "uncategorized" because no keywords were extracted.

## Code Examples

### Extended File Discovery (Phase 2 expansion of Phase 1 logic)
```bash
TARGET_FOLDER="${ARGUMENTS:-$(pwd)}"
echo "Scanning $TARGET_FOLDER for documents..."

# Find all document files including text-based extensions
ALL_FILES=$(find "$TARGET_FOLDER" -maxdepth 3 \( \
  -name "*.pdf" -o \
  -name "*.docx" -o \
  -name "*.xlsx" -o \
  -name "*.pptx" -o \
  -name "*.jpg" -o \
  -name "*.jpeg" -o \
  -name "*.png" -o \
  -name "*.csv" -o \
  -name "*.txt" -o \
  -name "*.eml" \
\) ! -path "*/_converted/*" ! -path "*/research/*" ! -name "_dd_*" 2>/dev/null | sort)

# Count by type
PDF_COUNT=$(echo "$ALL_FILES" | grep -ic "\.pdf$" || echo 0)
DOCX_COUNT=$(echo "$ALL_FILES" | grep -ic "\.docx$" || echo 0)
XLSX_COUNT=$(echo "$ALL_FILES" | grep -ic "\.xlsx$" || echo 0)
PPTX_COUNT=$(echo "$ALL_FILES" | grep -ic "\.pptx$" || echo 0)
IMG_COUNT=$(echo "$ALL_FILES" | grep -iEc "\.(jpg|jpeg|png)$" || echo 0)
OTHER_COUNT=$(echo "$ALL_FILES" | grep -iEc "\.(csv|txt|eml)$" || echo 0)
TOTAL_COUNT=$(echo "$ALL_FILES" | grep -c . || echo 0)
```

### Inventory JSON Generation
```bash
# After categorization is complete, write inventory JSON
cat > "$TARGET_FOLDER/_dd_inventory.json" << 'INVENTORY_EOF'
{
  "generated": "$TIMESTAMP",
  "workspace_folder": "$TARGET_FOLDER",
  "total_files": $TOTAL_COUNT,
  ...
}
INVENTORY_EOF
```

### Batch Splitting Logic
```bash
# For a domain with N files, create batches of max 20
BATCH_SIZE=20
DOMAIN_FILES=("${POWER_FILES[@]}")  # example
TOTAL=${#DOMAIN_FILES[@]}
BATCHES=$(( (TOTAL + BATCH_SIZE - 1) / BATCH_SIZE ))

for ((b=0; b<BATCHES; b++)); do
  START=$((b * BATCH_SIZE))
  BATCH_FILES=("${DOMAIN_FILES[@]:$START:$BATCH_SIZE}")
  echo "Batch $((b+1))/$BATCHES: ${#BATCH_FILES[@]} files"
done
```

## State of the Art

| Old Approach (CLI version) | Current Approach (Desktop) | When Changed | Impact |
|---------------------------|---------------------------|--------------|--------|
| Python conversion pipeline (pdf2text, docx2text, etc.) | Claude native Read + Vision | Phase 2 design | Zero external dependencies — non-technical user never touches Python |
| manifest.json from Python converter | _dd_inventory.json from orchestrator bash/Claude | Phase 2 design | Inventory is richer (includes domain assignments and batching info) |
| All files passed to all agents | Files routed to domain-specific agents with batching | Phase 2 design | Respects 20-file-per-chat limit; agents only see relevant documents |

**Deprecated/outdated:**
- Python `converters.pipeline` — not used in desktop version; replaced by native file reading
- `_converted/manifest.json` — replaced by `_dd_inventory.json` written by the orchestrator

## Open Questions

1. **Content sniffing depth for categorization**
   - What we know: Reading the first page/section of a document is usually sufficient for domain categorization
   - What's unclear: Exactly how much content Claude needs to read to reliably categorize — is filename + first 500 words enough, or do some documents need more?
   - Recommendation: Start with filename heuristics + first page read for unknowns. If uncategorized rate is too high in testing, increase sniffing depth.

2. **Multi-batch domain agent behavior**
   - What we know: When a domain has >20 files, we split into batches and dispatch the agent multiple times
   - What's unclear: How the domain agent should handle being called with batch 2 of 3 — does it need context from batch 1's findings? Or does each batch produce an independent partial report that gets merged?
   - Recommendation: Each batch is independent. The agent produces a report per batch. The final batch's report or a merge step combines findings. This is a Phase 3 concern (domain agent design) but affects how we structure the batch metadata in the inventory.

3. **Session checkpoint granularity**
   - What we know: _dd_status.json tracks phase completion (Phase 1 uses "inventory" phase)
   - What's unclear: Should Phase 2 add a separate checkpoint for "categorization" vs "inventory_written" vs "ready_for_dispatch"?
   - Recommendation: Add a "routing" phase to _dd_status.json. If session resumes and routing is complete, skip directly to Phase 3 dispatch. Checkpoint written after inventory JSON is persisted.

## Sources

### Primary (HIGH confidence)
- Phase 1 codebase: `dc-due-diligence-desktop/commands/due-diligence.md` — existing file discovery logic
- Phase 1 codebase: `dc-due-diligence-desktop/skills/due-diligence/SKILL.md` — orchestrator pattern
- CLI version: `dc-due-diligence/skills/due-diligence/SKILL.md` — full orchestration pipeline reference
- CLI version: `dc-due-diligence/agents/*.md` — 9 domain agent definitions (domain keyword vocabulary)
- Project requirements: `.planning/REQUIREMENTS.md` — INGEST-01 through INGEST-05 specifications
- Phase 2 context: `.planning/phases/02-document-ingestion-and-routing/02-CONTEXT.md` — user decisions

### Secondary (MEDIUM confidence)
- Claude Cowork capabilities — native file reading for PDF, DOCX, XLSX, PPTX confirmed by Phase 1 research and user experience
- Claude multimodal vision — image and scanned PDF reading confirmed by model capabilities

### Tertiary (LOW confidence)
- None — all research findings verified from primary or secondary sources

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all tools are built into Claude Cowork (Read, Vision, Bash)
- Architecture: HIGH — follows established CLI orchestration pattern adapted for Cowork constraints
- Pitfalls: HIGH — derived from CLI version experience and Phase 1 learnings

**Research date:** 2026-02-24
**Valid until:** 2026-03-24 (stable domain — no fast-moving dependencies)
