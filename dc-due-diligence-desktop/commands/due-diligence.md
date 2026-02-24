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

This command orchestrates the full due diligence workflow. Full instructions are also available in the orchestrator skill. The workflow performs document discovery, creates a structured inventory, categorizes documents by domain, routes them to domain agents, synthesizes findings with Risk Assessment, Executive Summary, and Client Summary agents, and generates Word document deliverables.

Dispatch pattern:
- **Wave 1 (Parallel):** 9 domain agents run concurrently via the Task tool
- **Wave 2 (Sequential):** Risk Assessment agent reads all 9 domain reports
- **Wave 3 (Sequential):** Executive Summary agent scores all 10 reports, then Client Summary agent produces external document
- **Post-processing:** Convert final reports to Word (.docx) format using pandoc

Sequential fallback is retained if parallel dispatch encounters issues (see Phase 1 smoke test results in STATE.md).

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

## Domain Agent Dispatch (Phase 3)

After routing is complete, dispatch all 9 domain agents to analyze their assigned documents.

### Research Folder Creation

```bash
TARGET_FOLDER="${ARGUMENTS:-$(pwd)}"
mkdir -p "$TARGET_FOLDER/research"
echo "Research folder ready: $TARGET_FOLDER/research"
```

### Resume Check

Before dispatching agents, check which reports already exist and skip those domains:

```bash
TARGET_FOLDER="${ARGUMENTS:-$(pwd)}"
echo "=== Checking for existing domain reports ==="
DISPATCH_LIST=""
SKIP_COUNT=0
DISPATCH_COUNT=0
for domain in power connectivity water-cooling land-zoning ownership environmental commercials natural-gas market-comparables; do
  REPORT="$TARGET_FOLDER/research/${domain}-report.md"
  REPORT_SIZE=$(stat -f%z "$REPORT" 2>/dev/null || echo 0)
  if [ "$REPORT_SIZE" -gt 500 ]; then
    echo "SKIP: $domain (report exists, ${REPORT_SIZE} bytes)"
    SKIP_COUNT=$((SKIP_COUNT + 1))
  else
    echo "DISPATCH: $domain"
    DISPATCH_LIST="$DISPATCH_LIST $domain"
    DISPATCH_COUNT=$((DISPATCH_COUNT + 1))
  fi
done
echo ""
echo "Dispatching $DISPATCH_COUNT agents, skipping $SKIP_COUNT with existing reports"
```

## Pre-Dispatch Data Room Assessment

Before dispatching agents, check the data room size and display a warning if the analysis will take significant time:

```bash
TARGET_FOLDER="${ARGUMENTS:-$(pwd)}"
TOTAL_FILES=$(jq '.total_files // 0' "$TARGET_FOLDER/_dd_inventory.json" 2>/dev/null || echo 0)
if [ "$TOTAL_FILES" -gt 30 ]; then
  BATCHED_DOMAINS=$(jq '[.domains | to_entries[] | select(.value.count > 20)] | length' "$TARGET_FOLDER/_dd_inventory.json" 2>/dev/null || echo 0)
  echo "Data room size: $TOTAL_FILES files."
  if [ "$BATCHED_DOMAINS" -gt 0 ]; then
    echo "$BATCHED_DOMAINS domain(s) have more than 20 files and will run in multiple passes."
  fi
  echo "Estimated completion: 20-40 minutes depending on file complexity and web research."
  echo ""
fi
```

If total_files is 30 or fewer, no warning is displayed and the pipeline proceeds at normal speed.

### Parallel Agent Dispatch

For each domain that needs to run:

1. Read the agent file at `agents/{domain}-agent.md`
2. Pass the agent file content as the task description to the Task tool
3. Replace `${WORKSPACE_FOLDER}` in the agent content with the actual target folder path (agents cannot inherit variables across Task tool boundaries)
4. Dispatch all agents that need to run simultaneously using parallel Task tool calls
5. Each agent writes its report to `research/{domain}-report.md` when complete

**Domain agent files:**
- `agents/power-agent.md` -- Power infrastructure, capacity, interconnection
- `agents/connectivity-agent.md` -- Fiber carriers, route diversity, carrier neutrality
- `agents/water-cooling-agent.md` -- Water supply, cooling design, scarcity risk
- `agents/land-zoning-agent.md` -- Zoning compliance, permits, entitlements
- `agents/ownership-agent.md` -- Ownership verification, title, middleman detection
- `agents/environmental-agent.md` -- Hazard risk, compliance, contamination
- `agents/commercials-agent.md` -- Financial terms, lease structure, pricing
- `agents/natural-gas-agent.md` -- Gas supply, pipeline access, on-site generation
- `agents/market-comparables-agent.md` -- Comparable transactions, market rates, competition

**Synthesis agent files (Wave 2/3 — dispatched after all domain agents complete):**
- `agents/risk-assessment-agent.md` -- Cross-domain risk synthesis (Wave 2)
- `agents/executive-summary-agent.md` -- Scored executive summary with verdict (Wave 3a)
- `agents/client-summary-agent.md` -- External-facing client summary (Wave 3b)

### Progress Feedback

Before dispatch, display a status table showing which agents will run vs. skip:

```
Domain Agent Status:
| Domain | Status | Reason |
|--------|--------|--------|
| Power | DISPATCH | No existing report |
| Connectivity | SKIP | Report exists (2,450 bytes) |
...
```

After all agents complete, display a completion summary:

```bash
TARGET_FOLDER="${ARGUMENTS:-$(pwd)}"
echo "=== Domain Agent Results ==="
COMPLETE_COUNT=0
FAILED_DOMAINS=""
for domain in power connectivity water-cooling land-zoning ownership environmental commercials natural-gas market-comparables; do
  REPORT="$TARGET_FOLDER/research/${domain}-report.md"
  SIZE=$(stat -f%z "$REPORT" 2>/dev/null || echo 0)
  if [ "$SIZE" -gt 500 ]; then
    echo "  $domain: Complete (${SIZE} bytes)"
    COMPLETE_COUNT=$((COMPLETE_COUNT + 1))
  else
    echo "  $domain: MISSING or incomplete"
    FAILED_DOMAINS="$FAILED_DOMAINS $domain"
  fi
done

if [ -n "$FAILED_DOMAINS" ]; then
  echo ""
  echo "Warning: $((9 - COMPLETE_COUNT)) domain agent(s) did not produce a report."
  echo "Affected domains:$FAILED_DOMAINS"
  echo "These domains will be marked as unavailable in the Executive Summary."
  echo "To retry failed domains only, run /due-diligence again — completed reports will be kept."
fi
echo ""
echo "$COMPLETE_COUNT of 9 domain reports complete. Proceeding to synthesis."
```

If any domains failed, display the warning message above. Then proceed to synthesis regardless — synthesis agents handle missing reports gracefully (SYNTH-05).

### Analysis Checkpoint

After all domain agents finish (or are skipped), update the checkpoint:

```bash
TARGET_FOLDER="${ARGUMENTS:-$(pwd)}"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
REPORTS_COMPLETE=$(ls "$TARGET_FOLDER/research/"*-report.md 2>/dev/null | wc -l | tr -d ' ')
cat > "$TARGET_FOLDER/_dd_status.json" << EOF
{
  "phase": "analysis",
  "reports_complete": $REPORTS_COMPLETE,
  "timestamp": "$TIMESTAMP"
}
EOF
echo "Analysis checkpoint written: $REPORTS_COMPLETE reports complete"
```

### Synthesis Checkpoint

After each synthesis agent completes, update the checkpoint with synthesis progress:

```bash
TARGET_FOLDER="${ARGUMENTS:-$(pwd)}"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Check synthesis progress
RA_DONE=false
ES_DONE=false
CS_DONE=false
[ $(stat -f%z "$TARGET_FOLDER/research/risk-assessment-report.md" 2>/dev/null || echo 0) -gt 500 ] && RA_DONE=true
[ $(stat -f%z "$TARGET_FOLDER/EXECUTIVE_SUMMARY.md" 2>/dev/null || echo 0) -gt 500 ] && ES_DONE=true
[ $(stat -f%z "$TARGET_FOLDER/CLIENT_SUMMARY.md" 2>/dev/null || echo 0) -gt 500 ] && CS_DONE=true

cat > "$TARGET_FOLDER/_dd_status.json" << EOF
{
  "phase": "synthesis",
  "reports_complete": $(ls "$TARGET_FOLDER/research/"*-report.md 2>/dev/null | wc -l | tr -d ' '),
  "risk_assessment_complete": $RA_DONE,
  "executive_summary_complete": $ES_DONE,
  "client_summary_complete": $CS_DONE,
  "timestamp": "$TIMESTAMP"
}
EOF
```

## Synthesis Agent Dispatch (Phase 4)

After all 9 domain agents complete, dispatch the synthesis agents sequentially. Each synthesis agent reads reports from the workspace folder and writes its output to disk.

### Wave 2: Risk Assessment

The Risk Assessment agent reads all 9 domain reports and identifies cross-cutting risks.

**Resume check:** If `research/risk-assessment-report.md` exists and is > 500 bytes, skip this agent.

```bash
TARGET_FOLDER="${ARGUMENTS:-$(pwd)}"
REPORT="$TARGET_FOLDER/research/risk-assessment-report.md"
REPORT_SIZE=$(stat -f%z "$REPORT" 2>/dev/null || echo 0)
if [ "$REPORT_SIZE" -gt 500 ]; then
  echo "SKIP: Risk Assessment (report exists, ${REPORT_SIZE} bytes)"
else
  echo "DISPATCH: Risk Assessment agent"
fi
```

If dispatch is needed:
1. Read `agents/risk-assessment-agent.md`
2. Replace `${WORKSPACE_FOLDER}` with the actual target folder path
3. Dispatch as a Task tool call (single agent, not parallel)
4. Wait for completion before proceeding to Wave 3

### Wave 3a: Executive Summary

The Executive Summary agent reads all 10 reports (9 domain + risk assessment), applies the scoring rubric, and produces the Pursue / Proceed with Caution / Pass verdict.

**Resume check:** If `EXECUTIVE_SUMMARY.md` exists in the workspace root and is > 500 bytes, skip this agent.

```bash
TARGET_FOLDER="${ARGUMENTS:-$(pwd)}"
REPORT="$TARGET_FOLDER/EXECUTIVE_SUMMARY.md"
REPORT_SIZE=$(stat -f%z "$REPORT" 2>/dev/null || echo 0)
if [ "$REPORT_SIZE" -gt 500 ]; then
  echo "SKIP: Executive Summary (report exists, ${REPORT_SIZE} bytes)"
else
  echo "DISPATCH: Executive Summary agent"
fi
```

If dispatch is needed:
1. Read `agents/executive-summary-agent.md`
2. Replace `${WORKSPACE_FOLDER}` with the actual target folder path
3. Dispatch as a Task tool call
4. Wait for completion before proceeding to Wave 3b

### Wave 3b: Client Summary

The Client Summary agent reads the executive summary and research reports, then produces an external-facing document for the deal presenter.

**Resume check:** If `CLIENT_SUMMARY.md` exists in the workspace root and is > 500 bytes, skip this agent.

```bash
TARGET_FOLDER="${ARGUMENTS:-$(pwd)}"
REPORT="$TARGET_FOLDER/CLIENT_SUMMARY.md"
REPORT_SIZE=$(stat -f%z "$REPORT" 2>/dev/null || echo 0)
if [ "$REPORT_SIZE" -gt 500 ]; then
  echo "SKIP: Client Summary (report exists, ${REPORT_SIZE} bytes)"
else
  echo "DISPATCH: Client Summary agent"
fi
```

If dispatch is needed:
1. Read `agents/client-summary-agent.md`
2. Replace `${WORKSPACE_FOLDER}` with the actual target folder path
3. Dispatch as a Task tool call
4. Wait for completion

## DOCX Generation

After all synthesis agents complete, convert final reports to Word format using pandoc. This step runs as post-processing — it does not require a sub-agent.

```bash
TARGET_FOLDER="${ARGUMENTS:-$(pwd)}"
mkdir -p "$TARGET_FOLDER/output"

if command -v pandoc &> /dev/null; then
  echo "Converting reports to Word format..."

  if [ -f "$TARGET_FOLDER/EXECUTIVE_SUMMARY.md" ]; then
    pandoc -f markdown -t docx -o "$TARGET_FOLDER/output/executive-summary.docx" "$TARGET_FOLDER/EXECUTIVE_SUMMARY.md"
    echo "Created: output/executive-summary.docx"
  fi

  if [ -f "$TARGET_FOLDER/CLIENT_SUMMARY.md" ]; then
    pandoc -f markdown -t docx -o "$TARGET_FOLDER/output/client-summary.docx" "$TARGET_FOLDER/CLIENT_SUMMARY.md"
    echo "Created: output/client-summary.docx"
  fi

  if [ -f "$TARGET_FOLDER/research/risk-assessment-report.md" ]; then
    pandoc -f markdown -t docx -o "$TARGET_FOLDER/output/risk-assessment.docx" "$TARGET_FOLDER/research/risk-assessment-report.md"
    echo "Created: output/risk-assessment.docx"
  fi
else
  echo ""
  echo "Note: pandoc not found. Word document generation skipped."
  echo "Install pandoc for DOCX output: brew install pandoc"
  echo "Markdown reports are available in the workspace folder."
fi
```

## Completion UX

After DOCX generation (or after Client Summary if pandoc is unavailable), display the completion output.

The orchestrator must:
1. Read the first few lines of `EXECUTIVE_SUMMARY.md` to extract the verdict from the `**Verdict:**` line
2. Extract 3-4 bullet points from the Key Strengths and Critical Concerns sections
3. Display in this format:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 VERDICT: [Pursue / Proceed with Caution / Pass]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Key Highlights:
• [Strength or concern 1]
• [Strength or concern 2]
• [Strength or concern 3]
• [Strength or concern 4]

Deliverables:
• [TARGET_FOLDER]/output/executive-summary.docx
• [TARGET_FOLDER]/output/client-summary.docx
• [TARGET_FOLDER]/output/risk-assessment.docx
• [TARGET_FOLDER]/EXECUTIVE_SUMMARY.md
• [TARGET_FOLDER]/CLIENT_SUMMARY.md
• [TARGET_FOLDER]/research/risk-assessment-report.md

9 domain reports available in: [TARGET_FOLDER]/research/
```

If DOCX files were not generated (no pandoc), omit the `.docx` lines from the deliverables list and show only the markdown files.

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
    if [ "$PHASE" = "synthesis" ]; then
      echo "Synthesis phase. Checking for incomplete synthesis reports."
    elif [ "$PHASE" = "analysis" ]; then
      echo "Analysis phase. Checking for incomplete reports."
    elif [ "$PHASE" = "routing" ]; then
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
