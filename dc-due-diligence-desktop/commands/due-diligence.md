---
description: Run full 9-domain data center due diligence analysis on workspace documents
argument-hint: "<data room folder path (optional — defaults to workspace root)>"
---

# Due Diligence Analysis

Analyze the data center opportunity documents in your workspace.

## Instructions

1. Identify the target folder. If a path was provided: use `$ARGUMENTS`. Otherwise, scan the current workspace root for document files.

2. List all document files found (PDF, DOCX, XLSX, PPTX, JPG, PNG) and display the count to the user.

3. If no documents are found, inform the user and stop.

4. [Phase 1 stub] Report that the document inventory is complete. Full domain agent dispatch will be added in Phase 2+.

## Orchestration Notes

This command orchestrates the full due diligence workflow. Full instructions are also available in the orchestrator skill. For Phase 1, the workflow performs document discovery and inventory. Future phases will dispatch 9 domain agents (Power, Connectivity, Water/Cooling, Land/Zoning, Ownership, Environmental, Commercials, Natural Gas, Market Comparables), synthesize findings with a Risk Assessment agent, and generate a scored Executive Summary with a Pursue / Proceed with Caution / Pass verdict.

## Workspace File Discovery

Use bash to find all document files in the target folder:

```bash
TARGET_FOLDER="${ARGUMENTS:-$(pwd)}"
echo "Scanning $TARGET_FOLDER for documents..."
find "$TARGET_FOLDER" -maxdepth 3 \( \
  -name "*.pdf" -o \
  -name "*.docx" -o \
  -name "*.xlsx" -o \
  -name "*.pptx" -o \
  -name "*.jpg" -o \
  -name "*.jpeg" -o \
  -name "*.png" \
\) 2>/dev/null | sort

COUNT=$(find "$TARGET_FOLDER" -maxdepth 3 \( \
  -name "*.pdf" -o -name "*.docx" -o -name "*.xlsx" \
  -o -name "*.pptx" -o -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" \
\) 2>/dev/null | wc -l | tr -d ' ')
echo "Found $COUNT documents"
```

Display results to the user in a clear format grouped by type.

## Session Resilience

After each major step, write a status checkpoint to the workspace folder so progress survives session interruptions:
- Write `_dd_status.json` with `{"phase": "inventory", "files_found": <count>, "timestamp": "<ISO>"}` after file discovery completes.
