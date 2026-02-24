---
description: Run full 9-domain data center due diligence analysis on workspace documents
argument-hint: "<data room folder path (optional — defaults to workspace root)>"
---

# Due Diligence Analysis

Analyze the data center opportunity documents in your workspace.

## Instructions

1. Identify the target folder. If a path was provided: use `$ARGUMENTS`. Otherwise, scan the current workspace root for document files.

2. Check for a prior session checkpoint. If `_dd_status.json` exists in the target folder, read it. If the file is less than 24 hours old and `phase` is "routing", skip to domain agent dispatch (Phase 3). If `phase` is "inventory", skip to categorization. If the file is older than 24 hours, discard it and start fresh.

3. Run the file discovery bash block below to list all document files by type.

4. If no documents are found, inform the user clearly and stop.

5. Display a summary table grouped by file type with counts.

6. Write `_dd_inventory.json` to the target folder with the full file listing.

7. Write `_dd_status.json` checkpoint.

8. Proceed to document categorization and routing (see Domain Categorization section below).

## Orchestration Notes

This command orchestrates the full due diligence workflow. Full instructions are also available in the orchestrator skill. The workflow performs document discovery, creates a structured inventory, categorizes documents by domain, and routes them to domain agents. Future phases will dispatch 9 domain agents (Power, Connectivity, Water/Cooling, Land/Zoning, Ownership, Environmental, Commercials, Natural Gas, Market Comparables), synthesize findings with a Risk Assessment agent, and generate a scored Executive Summary with a Pursue / Proceed with Caution / Pass verdict.

Dispatch pattern: Parallel — 9 domain agents run concurrently via the Task tool. Sequential fallback is retained if parallel encounters issues (see Phase 1 smoke test results in STATE.md).

## Workspace File Discovery

Use bash to find all document files in the target folder and count them by type:

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
IMG_COUNT=$(echo "$ALL_FILES" | grep -iE "\.(jpg|jpeg|png)$" | wc -l | tr -d ' ')
OTHER_COUNT=$(echo "$ALL_FILES" | grep -iE "\.(csv|txt|eml)$" | wc -l | tr -d ' ')
TOTAL_COUNT=$(echo "$ALL_FILES" | grep -c . || echo 0)

echo "--- File Discovery Results ---"
echo "PDF:   $PDF_COUNT"
echo "DOCX:  $DOCX_COUNT"
echo "XLSX:  $XLSX_COUNT"
echo "PPTX:  $PPTX_COUNT"
echo "Images (JPG/JPEG/PNG): $IMG_COUNT"
echo "Other (CSV/TXT/EML):   $OTHER_COUNT"
echo "Total: $TOTAL_COUNT"
```

Display results to the user as a summary table grouped by file type with counts only. Do NOT list individual filenames in chat output — the detailed listing lives in `_dd_inventory.json`.

## Document Inventory

After file discovery, write a structured JSON inventory to disk. This file is consumed by domain agents in Phase 3 and must be written BEFORE any agent dispatch (INGEST-05 requirement).

```bash
TARGET_FOLDER="${ARGUMENTS:-$(pwd)}"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Build file list as JSON array (handle spaces in filenames)
FILE_LIST_JSON=$(echo "$ALL_FILES" | while IFS= read -r f; do
  [ -z "$f" ] && continue
  printf '"%s",' "$f"
done | sed 's/,$//')

cat > "$TARGET_FOLDER/_dd_inventory.json" << INVENTORY_EOF
{
  "generated": "$TIMESTAMP",
  "workspace_folder": "$TARGET_FOLDER",
  "total_files": $TOTAL_COUNT,
  "file_types": {
    "pdf": $PDF_COUNT,
    "docx": $DOCX_COUNT,
    "xlsx": $XLSX_COUNT,
    "pptx": $PPTX_COUNT,
    "images": $IMG_COUNT,
    "other": $OTHER_COUNT
  },
  "files": [$FILE_LIST_JSON],
  "domains": {},
  "uncategorized": [],
  "status": "inventory_complete"
}
INVENTORY_EOF
echo "Inventory written to $TARGET_FOLDER/_dd_inventory.json"
```

The `domains` and `uncategorized` fields start empty — they are populated during the categorization step.

## Native Document Reading

Claude Cowork reads all document types natively — no Python conversion pipeline needed:

- **PDF files:** Use the Read tool directly. Claude extracts text content from text-based PDFs.
- **DOCX files:** Use the Read tool. Claude reads Word documents and extracts text content.
- **XLSX files:** Use the Read tool. Claude reads spreadsheet data as structured content.
- **PPTX files:** Use the Read tool. Claude reads slide content as text.
- **Images (JPG, JPEG, PNG):** Use the Read tool. Claude's vision capabilities interpret image content visually.
- **Scanned PDFs:** If a PDF returns very little or no text via Read, it may be a scanned document. Use the Read tool — Claude's multimodal vision will interpret the page images directly.
- **Text files (.csv, .txt, .eml):** Use the Read tool. These are read as plain text.

For categorization purposes, read only the first page or first ~500 words of each document to determine its domain. Do NOT read entire documents during categorization — preserve context window for domain agents in Phase 3.

## Domain Categorization

After inventory is written, categorize each file into one of the 9 domain buckets. Use a two-pass approach to conserve context window:

### Pass 1: Filename and Path Heuristics

For each file in the inventory, check the filename and parent directory name against domain keyword sets. This pass is fast and requires no file reading.

Domain keyword sets for filename matching (case-insensitive):

| Domain | Keywords |
|--------|----------|
| power | utility, substation, transformer, MW, megawatt, electrical, grid, voltage, redundancy, UPS, generator, switchgear, power purchase, PPA |
| connectivity | fiber, carrier, latency, bandwidth, network, ISP, peering, dark fiber, lit services, cross-connect, route diversity, meet-me, telecom |
| water-cooling | cooling, water, chiller, HVAC, airflow, temperature, humidity, PUE, WUE, cooling tower, mechanical |
| land-zoning | zoning, parcel, entitlement, setback, easement, lot, acre, building permit, land use, variance, conditional use, survey, plat |
| ownership | deed, title, lien, mortgage, LLC, owner, entity, beneficial, encumbrance, UCC, litigation, corporate |
| environmental | contamination, hazardous, flood, seismic, Phase I, Phase II, remediation, brownfield, EPA, environmental impact, ESA |
| commercials | lease, rent, NNN, CAM, tenant, escalation, term, option, pricing, rate, cost, revenue, EBITDA, financial, pro forma, LOI |
| natural-gas | gas, pipeline, natural gas, BTU, therms, generation, turbine, fuel, backup power |
| market-comparables | comparable, market rate, transaction, sale, acquisition, benchmark, competitor, vacancy, comp |

If a filename matches keywords from exactly one domain, assign it. If it matches multiple domains, assign to the domain with the most keyword hits. If no keywords match, mark as "needs content inspection" for Pass 2.

### Pass 2: Content Inspection (only for unmatched files)

For files that could not be categorized by filename alone, read the first page or first ~500 words using the Read tool. Apply the same keyword matching against the extracted content.

If a scanned PDF or image returns no text, use Claude's vision to inspect the first page — look for letterheads, logos, table headers, or other visual cues that indicate the domain.

If content inspection still doesn't yield a clear domain match, mark the file as "uncategorized" with reason "No domain keywords matched".

### Categorization Output

After both passes complete:

1. Display to chat (summary only per user decision):
```
Documents categorized:
- Power: X files
- Connectivity: X files
- Water & Cooling: X files
- Land & Zoning: X files
- Ownership: X files
- Environmental: X files
- Commercials: X files
- Natural Gas: X files
- Market Comparables: X files
- Uncategorized: X files [list filenames if any]
```

2. Each file assigned to exactly ONE domain or uncategorized — no duplicates.

## Document Routing

After categorization, prepare routing metadata for Phase 3 agent dispatch.

### Batch Splitting

For each domain bucket, check if the file count exceeds 20 (the per-chat platform limit). If so, split into sequential batches of max 20 files each.

```bash
# Batch splitting logic (orchestrator implements this during Phase 3 dispatch)
BATCH_SIZE=20
for domain in power connectivity water-cooling land-zoning ownership environmental commercials natural-gas market-comparables; do
  DOMAIN_COUNT=$(jq -r ".domains.\"$domain\".count // 0" "$TARGET_FOLDER/_dd_inventory.json")
  if [ "$DOMAIN_COUNT" -gt "$BATCH_SIZE" ]; then
    BATCHES=$(( (DOMAIN_COUNT + BATCH_SIZE - 1) / BATCH_SIZE ))
    echo "$domain: $DOMAIN_COUNT files -> $BATCHES batches"
  else
    echo "$domain: $DOMAIN_COUNT files -> 1 batch"
  fi
done
```

### Update Inventory JSON

After categorization and batch assignment, update `_dd_inventory.json` with the routing metadata. For each domain:

```json
"domains": {
  "power": {
    "files": ["/path/to/file1.pdf", "/path/to/file2.xlsx"],
    "count": 2,
    "batches": [
      {"batch": 1, "files": ["/path/to/file1.pdf", "/path/to/file2.xlsx"]}
    ]
  }
}
```

For uncategorized files:
```json
"uncategorized": [
  {"path": "/path/to/mystery.pdf", "reason": "No domain keywords matched"}
]
```

Update the `status` field from `"inventory_complete"` to `"routing_complete"`.

### Routing Checkpoint

After routing metadata is written, update `_dd_status.json`:

```bash
TARGET_FOLDER="${ARGUMENTS:-$(pwd)}"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
CATEGORIZED_COUNT=$(jq '[.domains[].count] | add // 0' "$TARGET_FOLDER/_dd_inventory.json")
UNCATEGORIZED_COUNT=$(jq '.uncategorized | length' "$TARGET_FOLDER/_dd_inventory.json")
cat > "$TARGET_FOLDER/_dd_status.json" << EOF
{
  "phase": "routing",
  "files_found": $TOTAL_COUNT,
  "files_categorized": $CATEGORIZED_COUNT,
  "files_uncategorized": $UNCATEGORIZED_COUNT,
  "inventory_file": "$TARGET_FOLDER/_dd_inventory.json",
  "timestamp": "$TIMESTAMP"
}
EOF
echo "Routing checkpoint written."
```

If a session resumes and `_dd_status.json` shows `"phase": "routing"`, skip directly to Phase 3 domain agent dispatch — the inventory and routing are already complete.

### Automatic Dispatch

Per user decision: no confirmation prompt. After routing completes, the orchestrator proceeds directly to domain agent dispatch (Phase 3). The user's mental model is "one command does everything."

## Session Resilience

After file discovery and inventory write complete, write a status checkpoint to the workspace folder:

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
echo "Checkpoint written to $TARGET_FOLDER/_dd_status.json"
```

If `_dd_status.json` already exists when the command starts, check how old it is:

```bash
TARGET_FOLDER="${ARGUMENTS:-$(pwd)}"
STATUS_FILE="$TARGET_FOLDER/_dd_status.json"
if [ -f "$STATUS_FILE" ]; then
  FILE_AGE_SECONDS=$(( $(date +%s) - $(date -r "$STATUS_FILE" +%s) ))
  if [ "$FILE_AGE_SECONDS" -lt 86400 ]; then
    echo "Found prior session checkpoint ($(( FILE_AGE_SECONDS / 60 )) minutes old)"
    cat "$STATUS_FILE"
    PHASE=$(cat "$STATUS_FILE" | grep -o '"phase"[[:space:]]*:[[:space:]]*"[^"]*"' | grep -o '"[^"]*"$' | tr -d '"')
    if [ "$PHASE" = "routing" ]; then
      echo "Routing complete. Proceeding to domain agent dispatch."
    elif [ "$PHASE" = "inventory" ]; then
      echo "Inventory complete. Proceeding to categorization."
    fi
  else
    echo "Prior checkpoint is older than 24 hours — starting fresh."
    rm "$STATUS_FILE"
  fi
fi
```

## Parallel Dispatch Smoke Test

**This section is a Phase 1 validation test — do not run this section during normal due diligence.** The smoke test validates whether Cowork supports parallel sub-agent dispatch (Task tool). Run this only when explicitly testing dispatch architecture.

### Smoke Test Instructions

Dispatch two stub sub-agents. Attempt to use the Task tool to run both simultaneously:

**Sub-agent A task:** Run this bash command, then write the output file:
```bash
sleep 5
TIMESTAMP_A=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "Agent A completed at: $TIMESTAMP_A" > "${ARGUMENTS:-$(pwd)}/agent-a-done.txt"
echo "Agent A done: $TIMESTAMP_A"
```

**Sub-agent B task:** Run this bash command, then write the output file:
```bash
sleep 5
TIMESTAMP_B=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "Agent B completed at: $TIMESTAMP_B" > "${ARGUMENTS:-$(pwd)}/agent-b-done.txt"
echo "Agent B done: $TIMESTAMP_B"
```

### Analyzing Results

After both agents complete, read both output files and compare the timestamps:

```bash
TARGET_FOLDER="${ARGUMENTS:-$(pwd)}"
echo "=== Smoke Test Results ==="
echo ""
echo "Agent A output:"
cat "$TARGET_FOLDER/agent-a-done.txt" 2>/dev/null || echo "MISSING: agent-a-done.txt"
echo ""
echo "Agent B output:"
cat "$TARGET_FOLDER/agent-b-done.txt" 2>/dev/null || echo "MISSING: agent-b-done.txt"
```

Interpret results:
- If both timestamps are within 2 seconds of each other: **PARALLEL CONFIRMED** — Task tool dispatched both agents concurrently
- If agent-b-done.txt timestamp is 5+ seconds after agent-a-done.txt: **SEQUENTIAL CONFIRMED** — agents ran one at a time
- If Task tool errored on dispatch attempt: **TASK TOOL UNAVAILABLE** — sequential-only architecture required

Report the exact timestamps and interpretation to the user.

### Sequential Fallback Validation

After the parallel dispatch test (regardless of result), validate sequential execution works correctly:

```bash
TARGET_FOLDER="${ARGUMENTS:-$(pwd)}"
# Sequential Agent A
sleep 5
TIMESTAMP_A=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "Sequential Agent A completed at: $TIMESTAMP_A" > "$TARGET_FOLDER/seq-agent-a-done.txt"
echo "Sequential A done: $TIMESTAMP_A"

# Sequential Agent B (runs after A)
sleep 5
TIMESTAMP_B=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "Sequential Agent B completed at: $TIMESTAMP_B" > "$TARGET_FOLDER/seq-agent-b-done.txt"
echo "Sequential B done: $TIMESTAMP_B"

echo ""
echo "=== Sequential Fallback Results ==="
cat "$TARGET_FOLDER/seq-agent-a-done.txt"
cat "$TARGET_FOLDER/seq-agent-b-done.txt"
echo "Sequential fallback: CONFIRMED WORKING"
```

Both `seq-agent-a-done.txt` and `seq-agent-b-done.txt` should exist with timestamps ~5 seconds apart, confirming the sequential path works.
