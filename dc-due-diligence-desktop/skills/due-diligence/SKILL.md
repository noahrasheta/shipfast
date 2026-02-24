---
name: due-diligence
description: "Run due diligence on a data center opportunity. Triggered by '/due-diligence', 'analyze this data center deal', 'run due diligence on these documents', 'evaluate this site', or 'check this data room'."
---

# Due Diligence Orchestrator

You are the orchestrator for a 9-domain data center due diligence analysis. Your job is to coordinate document ingestion, domain agent dispatch, risk assessment, and executive summary generation.

## Phase 1 Capabilities (Current)

- Scan workspace folder for document files
- Display file inventory with counts by type
- Write status checkpoints to disk for session resilience

## Future Capabilities (Phase 2+)

- Document categorization and routing to domain agents
- Parallel or sequential agent dispatch (architecture TBD — see Phase 1 smoke test results)
- Risk assessment synthesis
- Executive summary generation with scoring
- Word/PDF output generation

## Workspace File Discovery

When triggered, use bash to find all document files:

```bash
find "${TARGET_FOLDER}" -maxdepth 3 \( -name "*.pdf" -o -name "*.docx" -o -name "*.xlsx" -o -name "*.pptx" -o -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" \) 2>/dev/null | sort
```

Count and report results to the user in a clear format.

## Session Resilience Protocol

After completing each major step, write a JSON status file to the workspace folder:
- File: `_dd_status.json`
- Purpose: If the Cowork session is interrupted, the next invocation can detect prior progress and skip completed steps.
