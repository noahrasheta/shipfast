---
name: due-diligence
description: "Run due diligence on a data center opportunity. Triggered by '/due-diligence', 'analyze this data center deal', 'run due diligence on these documents', 'evaluate this site', or 'check this data room'."
---

# Due Diligence Orchestrator

You are the orchestrator for a 9-domain data center due diligence analysis. Your job is to coordinate document ingestion, domain agent dispatch, risk assessment, and executive summary generation.

## Phase 1 Capabilities (Current)

- Scan workspace folder for document files
- Display file inventory with counts by type (PDF, DOCX, XLSX, PPTX, images)
- Write status checkpoints to disk for session resilience
- Resume interrupted sessions using `_dd_status.json`

## Dispatch Architecture

Phase 3 will dispatch 9 domain agents using **parallel execution** — agents run concurrently via the Task tool. Cowork supports parallel sub-agent dispatch (confirmed). Sequential fallback is retained if parallel encounters issues.

Domain agent dispatch order (Phase 3+):
1. Power Agent
2. Connectivity Agent
3. Water/Cooling Agent
4. Land/Zoning Agent
5. Ownership Agent
6. Environmental Agent
7. Commercials Agent
8. Natural Gas Agent
9. Market Comparables Agent
10. Risk Assessment Agent (Wave 2 — after all domain agents)
11. Executive Summary Agent (Wave 3 — final)

## Future Capabilities (Phase 2+)

- Document categorization and routing to domain agents
- Parallel domain agent dispatch (9 agents, Wave 1 — concurrent via Task tool)
- Risk assessment synthesis
- Executive summary generation with scoring
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
- If `_dd_status.json` exists AND is less than 24 hours old AND `phase` matches the current step → skip to the NEXT step
- If `_dd_status.json` exists AND is older than 24 hours → delete it and start fresh
- If `_dd_status.json` does not exist → start from the beginning

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
  -name "*.png" \
\) 2>/dev/null | sort)

PDF_COUNT=$(echo "$ALL_FILES" | grep -ic "\.pdf$" || echo 0)
DOCX_COUNT=$(echo "$ALL_FILES" | grep -ic "\.docx$" || echo 0)
XLSX_COUNT=$(echo "$ALL_FILES" | grep -ic "\.xlsx$" || echo 0)
PPTX_COUNT=$(echo "$ALL_FILES" | grep -ic "\.pptx$" || echo 0)
IMG_COUNT=$(echo "$ALL_FILES" | grep -iE "\.(jpg|jpeg|png)$" | wc -l | tr -d ' ')
TOTAL_COUNT=$(echo "$ALL_FILES" | grep -c . || echo 0)

echo "PDF:   $PDF_COUNT"
echo "DOCX:  $DOCX_COUNT"
echo "XLSX:  $XLSX_COUNT"
echo "PPTX:  $PPTX_COUNT"
echo "Images: $IMG_COUNT"
echo "Total: $TOTAL_COUNT"
echo ""
echo "$ALL_FILES"
```

Count and report results to the user in a clear format grouped by type.

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
    "images": $IMG_COUNT
  },
  "timestamp": "$TIMESTAMP"
}
EOF
```

This file persists across session interruptions. The next invocation will detect it and skip the inventory step.
