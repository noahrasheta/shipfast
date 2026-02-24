---
name: due-diligence
description: "Run due diligence on a data center opportunity. Triggered by '/due-diligence', 'analyze this data center deal', 'run due diligence on these documents', 'evaluate this site', or 'check this data room'."
---

# Due Diligence Orchestrator

You are the orchestrator for a 9-domain data center due diligence analysis. Your job is to coordinate document ingestion, domain agent dispatch, risk assessment, and executive summary generation.

## Current Capabilities

### Document Discovery (Phase 1)
- Scan workspace folder for document files (PDF, DOCX, XLSX, PPTX, images, CSV, TXT, EML)
- Display file inventory with counts by type
- Write status checkpoints to disk for session resilience
- Resume interrupted sessions using `_dd_status.json`

### Document Ingestion (Phase 2)
- Read all document types natively using Claude's built-in capabilities (no Python required)
- Read scanned PDFs and images using Claude's vision/OCR capabilities
- Write structured inventory JSON (`_dd_inventory.json`) to workspace before agent dispatch
- Categorize documents into 9 domain buckets by content and filename analysis
- Batch documents per domain to respect 20-file-per-chat platform limit
- Route document batches to domain agents automatically (no user confirmation)

### Domain Analysis (Phase 3)
- Dispatch 9 domain agents in parallel via Task tool
- Each agent reads assigned documents from `_dd_inventory.json` routing
- Each agent conducts web research using built-in WebSearch/WebFetch
- Each agent writes report to `research/{domain}-report.md`
- Resume: skip agents whose reports already exist (> 500 bytes)
- Document Safety Protocol in every agent prevents prompt injection

## Dispatch Architecture

9 domain agents dispatch using **parallel execution** — agents run concurrently via the Task tool. Cowork supports parallel sub-agent dispatch (confirmed). Sequential fallback is retained if parallel encounters issues.

Domain agent dispatch order:
1. Power Agent — `agents/power-agent.md`
2. Connectivity Agent — `agents/connectivity-agent.md`
3. Water/Cooling Agent — `agents/water-cooling-agent.md`
4. Land/Zoning Agent — `agents/land-zoning-agent.md`
5. Ownership Agent — `agents/ownership-agent.md`
6. Environmental Agent — `agents/environmental-agent.md`
7. Commercials Agent — `agents/commercials-agent.md`
8. Natural Gas Agent — `agents/natural-gas-agent.md`
9. Market Comparables Agent — `agents/market-comparables-agent.md`
10. Risk Assessment Agent (Wave 2 — after all domain agents)
11. Executive Summary Agent (Wave 3 — final)

## Future Capabilities (Phase 4+)

- Risk assessment synthesis
- Executive summary generation with scoring
- Client summary for deal presenter
- Word/PDF output generation

## Session Resilience Protocol

At the start of EVERY invocation, check for a prior session checkpoint:

```bash
TARGET_FOLDER="${ARGUMENTS:-$(pwd)}"
STATUS_FILE="$TARGET_FOLDER/_dd_status.json"
if [ -f "$STATUS_FILE" ]; then
  FILE_AGE_SECONDS=$(( $(date +%s) - $(date -r "$STATUS_FILE" +%s) ))
  if [ "$FILE_AGE_SECONDS" -lt 86400 ]; then
    echo "RESUME: Found checkpoint from $(( FILE_AGE_SECONDS / 60 )) minutes ago"
    cat "$STATUS_FILE"
  else
    echo "STALE: Checkpoint is older than 24 hours — starting fresh"
    rm "$STATUS_FILE"
  fi
fi
```

Decision logic:
- If `_dd_status.json` exists AND is less than 24 hours old AND `phase` is "analysis" → check which domain reports exist (> 500 bytes), dispatch only missing agents
- If `_dd_status.json` exists AND is less than 24 hours old AND `phase` is "routing" → skip to Phase 3 domain agent dispatch
- If `_dd_status.json` exists AND is less than 24 hours old AND `phase` is "inventory" → skip to categorization step
- If `_dd_status.json` exists AND is older than 24 hours → delete it and start fresh
- If `_dd_status.json` does not exist → start from the beginning

Checkpoint phases:
- `"inventory"` — file discovery complete, categorization pending
- `"routing"` — categorization and batch assignment complete, ready for Phase 3 dispatch
- `"analysis"` — domain agents dispatched, check report file existence (> 500 bytes) for resume

## Workspace File Discovery

When triggered (and no valid prior checkpoint exists for the inventory phase), use bash to find all document files:

```bash
TARGET_FOLDER="${ARGUMENTS:-$(pwd)}"
echo "Scanning $TARGET_FOLDER for documents..."

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

PDF_COUNT=$(echo "$ALL_FILES" | grep -ic "\.pdf$" || echo 0)
DOCX_COUNT=$(echo "$ALL_FILES" | grep -ic "\.docx$" || echo 0)
XLSX_COUNT=$(echo "$ALL_FILES" | grep -ic "\.xlsx$" || echo 0)
PPTX_COUNT=$(echo "$ALL_FILES" | grep -ic "\.pptx$" || echo 0)
IMG_COUNT=$(echo "$ALL_FILES" | grep -iE "\.(jpg|jpeg|png)$" | wc -l | tr -d ' ')
OTHER_COUNT=$(echo "$ALL_FILES" | grep -iE "\.(csv|txt|eml)$" | wc -l | tr -d ' ')
TOTAL_COUNT=$(echo "$ALL_FILES" | grep -c . || echo 0)

echo "PDF:   $PDF_COUNT"
echo "DOCX:  $DOCX_COUNT"
echo "XLSX:  $XLSX_COUNT"
echo "PPTX:  $PPTX_COUNT"
echo "Images: $IMG_COUNT"
echo "Other:  $OTHER_COUNT"
echo "Total: $TOTAL_COUNT"
```

Count and report results to the user in a clear format grouped by type. Show summary counts only — detailed file listing is in `_dd_inventory.json`.

## Document Inventory

After file discovery, write a structured JSON inventory to disk. This must happen BEFORE any domain agent is dispatched (INGEST-05 requirement).

The inventory file `_dd_inventory.json` contains:
- All discovered file paths
- File type counts
- Domain assignments (populated by categorization step)
- Batch assignments (populated by routing step)
- Uncategorized files list

Domain agents in Phase 3 reference this file to know which documents to analyze.

## Native Document Reading

Claude Cowork reads all document types natively — no external dependencies:

| File Type | How to Read | Notes |
|-----------|-------------|-------|
| PDF (text) | Read tool | Extracts text content directly |
| PDF (scanned) | Read tool + vision | If text extraction returns little/no content, vision interprets page images |
| DOCX | Read tool | Word document text extraction |
| XLSX | Read tool | Spreadsheet data as structured content |
| PPTX | Read tool | Slide content as text |
| Images | Read tool | Vision capabilities interpret visual content |
| CSV/TXT/EML | Read tool | Plain text reading |

**Key principle:** No Python, no Tesseract, no external converters. Everything runs through Claude's native capabilities. This is the core advantage over the CLI version.

## Document Routing Workflow

After document discovery and inventory write, the orchestrator routes files to domain agents:

1. **Categorize** — Two-pass approach:
   - Pass 1: Filename/path keyword matching (fast, no file reading)
   - Pass 2: Content inspection for unmatched files (read first page only)
2. **Batch** — Split domains with >20 files into batches of max 20
3. **Update inventory** — Write domain assignments and batch metadata to `_dd_inventory.json`
4. **Checkpoint** — Update `_dd_status.json` to `phase: routing`
5. **Dispatch** — Proceed directly to Phase 3 agent dispatch (no user confirmation)

### Domain Keyword Reference

Each of the 9 domains has characteristic keywords used for categorization:

| Domain | Agent | Primary Keywords |
|--------|-------|-----------------|
| power | Power Agent | utility, substation, transformer, MW, megawatt, electrical, grid, voltage, UPS, generator, switchgear, PPA |
| connectivity | Connectivity Agent | fiber, carrier, latency, bandwidth, network, ISP, peering, dark fiber, cross-connect, route diversity, telecom |
| water-cooling | Water/Cooling Agent | cooling, water, chiller, HVAC, airflow, temperature, humidity, PUE, WUE, cooling tower, mechanical |
| land-zoning | Land/Zoning Agent | zoning, parcel, entitlement, setback, easement, lot, acre, building permit, land use, survey, plat |
| ownership | Ownership Agent | deed, title, lien, mortgage, LLC, owner, entity, beneficial, encumbrance, UCC, litigation |
| environmental | Environmental Agent | contamination, hazardous, flood, seismic, Phase I, Phase II, remediation, brownfield, EPA, ESA |
| commercials | Commercials Agent | lease, rent, NNN, CAM, tenant, escalation, term, pricing, rate, cost, revenue, EBITDA, LOI, pro forma |
| natural-gas | Natural Gas Agent | gas, pipeline, natural gas, BTU, therms, generation, turbine, fuel, backup power |
| market-comparables | Market Comparables Agent | comparable, market rate, transaction, sale, acquisition, benchmark, competitor, vacancy |

### Batch Splitting Rules

- Maximum 20 files per agent dispatch (platform limit)
- When a domain exceeds 20 files, split deterministically: files 1-20 in batch 1, 21-40 in batch 2, etc.
- Each batch is dispatched as a separate agent run
- No data left behind — every file in a domain gets processed

### Uncategorized Files

- Files matching no domain keywords are logged as "uncategorized"
- Uncategorized filenames displayed in chat so user can see what was excluded
- Uncategorized files are NOT routed to any agent
- Phase 3 synthesis handles partial data gracefully

## Checkpoint Write

After completing file discovery, write `_dd_status.json` to the workspace:

```bash
TARGET_FOLDER="${ARGUMENTS:-$(pwd)}"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
cat > "$TARGET_FOLDER/_dd_status.json" << EOF
{
  "phase": "inventory",
  "files_found": $TOTAL_COUNT,
  "file_types": {
    "pdf": $PDF_COUNT,
    "docx": $DOCX_COUNT,
    "xlsx": $XLSX_COUNT,
    "pptx": $PPTX_COUNT,
    "images": $IMG_COUNT,
    "other": $OTHER_COUNT
  },
  "inventory_file": "$TARGET_FOLDER/_dd_inventory.json",
  "timestamp": "$TIMESTAMP"
}
EOF
```

This file persists across session interruptions. The next invocation will detect it and skip completed steps.
