---
description: Run full 9-domain data center due diligence analysis on workspace documents
argument-hint: "<data room folder path (optional — defaults to workspace root)>"
---

# Due Diligence Analysis

Analyze the data center opportunity documents in your workspace.

## Instructions

1. Identify the target folder. If a path was provided: use `$ARGUMENTS`. Otherwise, scan the current workspace root for document files.

2. Check for a prior session checkpoint. If `_dd_status.json` exists in the target folder, read it. If the file is less than 24 hours old and `phase` is "inventory", report that a prior inventory was found and use it. If the file is older than 24 hours, discard it and start fresh.

3. Run the file discovery bash block below to list all document files by type.

4. If no documents are found, inform the user clearly and stop.

5. Display a summary table grouped by file type with counts.

6. Write `_dd_status.json` to the target folder with the discovery results.

7. [Phase 1 stub] Report that the document inventory is complete. Full domain agent dispatch will be added in Phase 2+.

## Orchestration Notes

This command orchestrates the full due diligence workflow. Full instructions are also available in the orchestrator skill. For Phase 1, the workflow performs document discovery and inventory. Future phases will dispatch 9 domain agents (Power, Connectivity, Water/Cooling, Land/Zoning, Ownership, Environmental, Commercials, Natural Gas, Market Comparables), synthesize findings with a Risk Assessment agent, and generate a scored Executive Summary with a Pursue / Proceed with Caution / Pass verdict.

## Workspace File Discovery

Use bash to find all document files in the target folder and count them by type:

```bash
TARGET_FOLDER="${ARGUMENTS:-$(pwd)}"
echo "Scanning $TARGET_FOLDER for documents..."

# Find all document files
ALL_FILES=$(find "$TARGET_FOLDER" -maxdepth 3 \( \
  -name "*.pdf" -o \
  -name "*.docx" -o \
  -name "*.xlsx" -o \
  -name "*.pptx" -o \
  -name "*.jpg" -o \
  -name "*.jpeg" -o \
  -name "*.png" \
\) 2>/dev/null | sort)

# Count by type
PDF_COUNT=$(echo "$ALL_FILES" | grep -ic "\.pdf$" || echo 0)
DOCX_COUNT=$(echo "$ALL_FILES" | grep -ic "\.docx$" || echo 0)
XLSX_COUNT=$(echo "$ALL_FILES" | grep -ic "\.xlsx$" || echo 0)
PPTX_COUNT=$(echo "$ALL_FILES" | grep -ic "\.pptx$" || echo 0)
IMG_COUNT=$(echo "$ALL_FILES" | grep -iE "\.(jpg|jpeg|png)$" | wc -l | tr -d ' ')
TOTAL_COUNT=$(echo "$ALL_FILES" | grep -c . || echo 0)

echo "--- File Discovery Results ---"
echo "PDF:   $PDF_COUNT"
echo "DOCX:  $DOCX_COUNT"
echo "XLSX:  $XLSX_COUNT"
echo "PPTX:  $PPTX_COUNT"
echo "Images (JPG/JPEG/PNG): $IMG_COUNT"
echo "Total: $TOTAL_COUNT"
echo ""
echo "Files found:"
echo "$ALL_FILES"
```

Display results to the user in a clear table grouped by type.

## Session Resilience

After file discovery completes, write a status checkpoint to the workspace folder:

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
    echo "Using prior inventory. To rescan, delete $STATUS_FILE and re-run."
  else
    echo "Prior checkpoint is older than 24 hours — starting fresh."
    rm "$STATUS_FILE"
  fi
fi
```
