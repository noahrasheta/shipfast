---
name: due-diligence
description: "Run due diligence on a data center opportunity. Triggered by '/due-diligence <folder-path>', 'analyze this data center deal', 'run due diligence', or 'evaluate this site'. Analyzes broker documents across 9 domains (power, connectivity, water/cooling, zoning, ownership, environmental, commercials, natural gas, market comparables), synthesizes cross-domain risks, and produces a scored executive summary with a Pursue / Proceed with Caution / Pass verdict."
version: "0.1.0"
---

# Due Diligence Orchestrator

You are the orchestrator for the data center due diligence workflow. Your job is to take a folder of opportunity documents and coordinate the full analysis pipeline: 9 domain research agents running in parallel, followed by a Risk Assessment agent that synthesizes findings across all domains, and finally an Executive Summary Generator that scores each category and delivers a verdict.

## What You're Given

The user invokes `/due-diligence <folder-path>` with a path to an opportunity folder containing documents (PDFs, spreadsheets, Word docs, images, etc.).

Folder path provided: `${ARGUMENTS}`

## Your Workflow

Execute the following phases in order. Each phase must complete successfully before proceeding to the next.

### Phase 1: Input Validation and Setup

1. **Validate input:**
   - Check if `${ARGUMENTS}` is provided. If not, respond: "Please provide a folder path: `/due-diligence <folder-path>`"
   - Convert relative paths to absolute paths using Bash: `realpath "<path>"`
   - Verify the folder exists and is a directory using Bash: `test -d "<absolute-path>" && echo "exists" || echo "not found"`
   - If folder doesn't exist, respond: "Folder not found: `<path>`. Please check the path and try again."

2. **Locate the plugin directory:**

   Determine `PLUGIN_DIR` once here and reuse it in all subsequent phases. Use `${CLAUDE_PLUGIN_ROOT}` if available, otherwise fall back to filesystem discovery:
   ```bash
   if [ -n "${CLAUDE_PLUGIN_ROOT}" ]; then
     PLUGIN_DIR="${CLAUDE_PLUGIN_ROOT}"
   else
     PLUGIN_DIR=$(find "$HOME/.claude/plugins" -maxdepth 4 -name "plugin.json" -path "*/dc-due-diligence/*" 2>/dev/null | head -1 | xargs dirname | xargs dirname)
   fi
   echo "PLUGIN_DIR=$PLUGIN_DIR"
   ```
   - If `PLUGIN_DIR` is empty, tell the user: "Could not locate the dc-due-diligence plugin. Make sure it's installed and that `setup.sh` has been run."
   - Store `PLUGIN_DIR` for use in Phase 2 (conversion pipeline) and Phase 4 (agent spawning).

3. **Report to user:**
   ```
   Processing documents in <folder-name>...
   ```

### Phase 2: Document Processing

1. **Check for existing converted documents:**

   Before running the conversion pipeline, check if conversion has already been completed:
   ```bash
   test -f "<absolute-folder-path>/_converted/manifest.json" && echo "manifest exists" || echo "no manifest"
   ```

   If a manifest already exists, read it and check how many files converted successfully. If at least one file converted successfully, **skip the conversion pipeline** and report:
   ```
   Found existing converted documents (<N> files). Skipping conversion.
   ```

   If no manifest exists, proceed with the conversion pipeline below.

2. **Run the conversion pipeline:**

   Use the `PLUGIN_DIR` resolved in Phase 1 to run the pipeline:
   ```bash
   "$PLUGIN_DIR/.venv/bin/python3" -m converters.pipeline "<absolute-folder-path>"
   ```
   - The pipeline automatically prints a detailed status report
   - Wait for the pipeline to complete (it will exit with code 0 on success, non-zero on failure)

3. **Check pipeline result:**
   - If pipeline exits with non-zero code, stop workflow and report:
     ```
     Document processing failed. Please check the error messages above and ensure:
     - All files are readable and not corrupted
     - The Python environment has required packages installed
     - You have sufficient disk space for converted files
     ```
   - If successful, verify that `<folder>/_converted/manifest.json` exists
   - Read the manifest to confirm at least one file was successfully converted

4. **Handle empty results:**
   - If manifest shows 0 successfully converted files, stop workflow and report:
     ```
     No documents could be processed. The folder may contain only unsupported file types or all conversions failed. Please check the status report above.
     ```

### Phase 3: Research Subfolder Setup

1. **Create the research output directory:**
   ```bash
   mkdir -p "<absolute-folder-path>/research"
   ```

2. **Verify creation:**
   - Check that the directory was created successfully
   - If creation fails, stop workflow and report the error

### Phase 4: Parallel Agent Orchestration

This phase runs in two waves:
- **Wave 1**: 9 domain research agents that analyze broker documents (run in parallel)
- **Wave 2**: 1 Risk Assessment agent that reads all 9 domain reports (runs after Wave 1 completes)

#### Wave 1: Domain Research Agents (Parallel)

1. **Prepare agent context:**
   - Read the manifest at `<folder>/_converted/manifest.json`
   - Note the absolute folder path to pass to each agent
   - Prepare to substitute `${OPPORTUNITY_FOLDER}` in each agent definition with the absolute path
   - **Plugin directory:** Use the `PLUGIN_DIR` resolved in Phase 1. Pass this path to each agent as `${PLUGIN_DIR}` when spawning them so agents can find templates.
   - **Web research:** Agents have access to WebSearch, WebFetch, and MCP servers (firecrawl, exa, tavily) for independent verification. No additional configuration needed.

2. **Spawn all 9 domain agents in parallel:**

   Use the Task tool to spawn these 9 agents **in a single message** (make 9 Task tool calls in one response block). In each agent's prompt, include: "The opportunity folder is: `<absolute-folder-path>`. The plugin directory is: `<PLUGIN_DIR>`."

   - **Power Agent**: `dc-due-diligence:power-agent`
     - Expected output: `<folder>/research/power-report.md`
   - **Connectivity Agent**: `dc-due-diligence:connectivity-agent`
     - Expected output: `<folder>/research/connectivity-report.md`
   - **Water & Cooling Agent**: `dc-due-diligence:water-cooling-agent`
     - Expected output: `<folder>/research/water-cooling-report.md`
   - **Land, Zoning & Entitlements Agent**: `dc-due-diligence:land-zoning-agent`
     - Expected output: `<folder>/research/land-zoning-report.md`
   - **Ownership & Control Agent**: `dc-due-diligence:ownership-agent`
     - Expected output: `<folder>/research/ownership-report.md`
   - **Environmental Agent**: `dc-due-diligence:environmental-agent`
     - Expected output: `<folder>/research/environmental-report.md`
   - **Commercials Agent**: `dc-due-diligence:commercials-agent`
     - Expected output: `<folder>/research/commercials-report.md`
   - **Natural Gas Agent**: `dc-due-diligence:natural-gas-agent`
     - Expected output: `<folder>/research/natural-gas-report.md`
   - **Market Comparables Agent**: `dc-due-diligence:market-comparables-agent`
     - Expected output: `<folder>/research/market-comparables-report.md`

3. **Report progress to user:**
   ```
   Launching 9 domain research agents in parallel...

   Agents running:
   1. Power -- analyzing electrical infrastructure, utility interconnection, grid capacity
   2. Connectivity -- analyzing fiber carriers, route diversity, network infrastructure
   3. Water & Cooling -- analyzing water supply, cooling design, scarcity risk
   4. Land, Zoning & Entitlements -- analyzing zoning compliance, permits, building status
   5. Ownership & Control -- analyzing property ownership, background, litigation
   6. Environmental -- analyzing natural hazards, compliance, contamination risk
   7. Commercials -- analyzing deal terms, costs, lease structure, financial terms
   8. Natural Gas -- analyzing gas supply, pipeline access, generation feasibility
   9. Market Comparables -- analyzing comparable transactions, market rates, competition

   This may take several minutes. Each agent reads the converted documents, conducts web research using WebSearch and WebFetch tools, and produces a detailed research report.
   ```

4. **Wait for all 9 agents to complete.**

#### Wave 2: Risk Assessment Agent (Sequential)

After all 9 domain agents have completed:

1. **Check which domain reports were produced:**

   Before spawning the Risk Assessment agent, verify which domain reports exist:
   ```bash
   for report in power connectivity water-cooling land-zoning ownership environmental commercials natural-gas market-comparables; do
     test -f "<folder>/research/${report}-report.md" && echo "OK ${report}" || echo "MISSING ${report}"
   done
   ```

2. **Spawn the Risk Assessment agent:**

   Use the Task tool to spawn the Risk Assessment agent. In the prompt, include the opportunity folder path and the plugin directory path.

   - **Risk Assessment Agent**: `dc-due-diligence:risk-assessment-agent`
     - Expected output: `<folder>/research/risk-assessment-report.md`

3. **Report progress:**
   ```
   Domain research complete. Launching Risk Assessment agent to synthesize cross-domain findings...

   Domain reports available: <N>/9
   [If any missing: "Missing: <list of missing domains>"]

   The Risk Assessment agent reads all domain reports and identifies cross-cutting risks, deal-breakers, and compound risks that individual agents cannot see.
   ```

4. **Wait for the Risk Assessment agent to complete.**

### Phase 5: Output Validation and Gap Detection

After all 10 agents have completed:

1. **Verify all output files exist:**

   ```bash
   test -f "<folder>/research/power-report.md" && echo "OK Power" || echo "MISSING Power"
   test -f "<folder>/research/connectivity-report.md" && echo "OK Connectivity" || echo "MISSING Connectivity"
   test -f "<folder>/research/water-cooling-report.md" && echo "OK Water & Cooling" || echo "MISSING Water & Cooling"
   test -f "<folder>/research/land-zoning-report.md" && echo "OK Land & Zoning" || echo "MISSING Land & Zoning"
   test -f "<folder>/research/ownership-report.md" && echo "OK Ownership" || echo "MISSING Ownership"
   test -f "<folder>/research/environmental-report.md" && echo "OK Environmental" || echo "MISSING Environmental"
   test -f "<folder>/research/commercials-report.md" && echo "OK Commercials" || echo "MISSING Commercials"
   test -f "<folder>/research/natural-gas-report.md" && echo "OK Natural Gas" || echo "MISSING Natural Gas"
   test -f "<folder>/research/market-comparables-report.md" && echo "OK Market Comparables" || echo "MISSING Market Comparables"
   test -f "<folder>/research/risk-assessment-report.md" && echo "OK Risk Assessment" || echo "MISSING Risk Assessment"
   ```

2. **Check file sizes:**

   For each existing file, verify it's substantial (> 500 bytes for a real research report):

   ```bash
   for file in "<folder>/research/"*-report.md; do
     if [ -f "$file" ]; then
       size=$(wc -c < "$file")
       name=$(basename "$file")
       if [ "$size" -lt 500 ]; then
         echo "WARNING: ${name} is very small (${size} bytes) - may be incomplete"
       else
         echo "OK: ${name} (${size} bytes)"
       fi
     fi
   done
   ```

3. **Content validation for each report:**

   For each report file, verify it contains the required template sections:

   ```bash
   for file in "<folder>/research/"*-report.md; do
     if [ -f "$file" ]; then
       name=$(basename "$file")
       missing=""
       grep -qE "GREEN|YELLOW|RED" "$file" || missing="${missing} status-indicator"
       grep -q "Confidence Score:" "$file" || missing="${missing} confidence-score"
       grep -q "## Executive Summary" "$file" || missing="${missing} executive-summary"
       grep -q "## Findings" "$file" || missing="${missing} findings"
       grep -q "## Risks" "$file" || missing="${missing} risks"
       grep -q "## Recommendations" "$file" || missing="${missing} recommendations"
       grep -q "## Research Methodology" "$file" || missing="${missing} methodology"
       if [ -z "$missing" ]; then
         echo "VALID: ${name} - all required sections present"
       else
         echo "INCOMPLETE: ${name} - missing:${missing}"
       fi
     fi
   done
   ```

4. **Track completion status:**

   Build a summary of results:
   - **Complete**: File exists, > 500 bytes, all required sections present
   - **Incomplete**: File exists but missing sections or very small
   - **Failed**: File does not exist

### Phase 6: Executive Summary Generation

After validation is complete, generate the executive summary that scores all 10 categories and determines the overall verdict.

1. **Check if enough reports exist to generate a summary:**

   At least 3 domain reports must be present (Complete or Incomplete) to produce a meaningful executive summary. If fewer than 3 reports exist, skip this phase and note:
   ```
   Too few research reports available to generate an executive summary. Only <N>/10 reports were produced.
   Review individual reports in: <folder>/research/
   ```

2. **Spawn the Executive Summary Generator agent:**

   Use the Task tool to spawn the Executive Summary Generator. In the prompt, include the opportunity folder path and the plugin directory path.

   - **Executive Summary Generator**: `dc-due-diligence:executive-summary-agent`
     - Expected output: `<folder>/EXECUTIVE_SUMMARY.md`

3. **Report progress:**
   ```
   Research reports validated. Generating executive summary with scored categories and overall verdict...

   The Executive Summary Generator reads all 10 research reports, applies the scoring rubric, normalizes terminology, resolves data conflicts, and produces a single stakeholder-ready document.
   ```

4. **Wait for the Executive Summary Generator to complete.**

5. **Validate the executive summary was produced:**

   ```bash
   test -f "<folder>/EXECUTIVE_SUMMARY.md" && echo "OK Executive Summary" || echo "MISSING Executive Summary"
   ```

   If the file exists, check that it contains the required sections:
   ```bash
   file="<folder>/EXECUTIVE_SUMMARY.md"
   missing=""
   grep -q "## At a Glance" "$file" || missing="${missing} at-a-glance"
   grep -q "## Key Strengths" "$file" || missing="${missing} key-strengths"
   grep -q "## Critical Concerns" "$file" || missing="${missing} critical-concerns"
   grep -q "## Detailed Category Scores" "$file" || missing="${missing} detailed-scores"
   grep -q "## Detailed Findings" "$file" || missing="${missing} detailed-findings"
   grep -q "## Recommended Next Steps" "$file" || missing="${missing} next-steps"
   grep -qE "Pursue|Proceed with Caution|Pass" "$file" || missing="${missing} verdict"
   if [ -z "$missing" ]; then
     echo "VALID: EXECUTIVE_SUMMARY.md - all required sections present"
   else
     echo "INCOMPLETE: EXECUTIVE_SUMMARY.md - missing:${missing}"
   fi
   ```

6. **Handle executive summary failure:**
   - If the file was not created, note the failure but continue to results reporting. The individual research reports are still valuable.
   - If the file exists but is incomplete, note which sections are missing.

### Phase 7: Results Reporting

1. **Report completion summary:**

   ```
   Due diligence analysis complete.

   Research Reports:
   [For each of the 10 domains, show status:]
   [Complete]  Power -- <folder>/research/power-report.md
   [Complete]  Connectivity -- <folder>/research/connectivity-report.md
   [Complete]  Water & Cooling -- <folder>/research/water-cooling-report.md
   [Complete]  Land, Zoning & Entitlements -- <folder>/research/land-zoning-report.md
   [Complete]  Ownership & Control -- <folder>/research/ownership-report.md
   [Complete]  Environmental -- <folder>/research/environmental-report.md
   [Complete]  Commercials -- <folder>/research/commercials-report.md
   [Complete]  Natural Gas -- <folder>/research/natural-gas-report.md
   [Complete]  Market Comparables -- <folder>/research/market-comparables-report.md
   [Complete]  Risk Assessment -- <folder>/research/risk-assessment-report.md

   [If any incomplete or failed, show those with appropriate status markers]

   Summary: <N>/10 reports completed, <M> incomplete, <F> failed
   All reports saved to: <absolute-folder-path>/research/
   ```

2. **Report executive summary status:**

   If the executive summary was generated successfully:
   ```
   Executive Summary: <folder>/EXECUTIVE_SUMMARY.md
   Verdict: [Pursue / Proceed with Caution / Pass]
   ```

   Read the verdict line from the executive summary and display it prominently. This is the single most important output of the entire workflow.

   If the executive summary was not generated:
   ```
   Executive summary could not be generated. Review individual research reports for findings.
   ```

3. **If any agents failed or produced incomplete output:**

   ```
   Some research domains require attention:

   [For each incomplete/failed domain:]
   - [Domain]: [Reason -- "report not generated", "missing required sections: X, Y", etc.]
     Manual review recommended for this domain.
   ```

4. **Provide overview of findings:**

   Read each completed report's Status Indicator and Confidence Score, then present a quick summary table:

   ```
   Quick Overview:

   Domain                    Status    Confidence
   ──────────────────────────────────────────────
   Power                     [indicator]   [score]%
   Connectivity              [indicator]   [score]%
   Water & Cooling           [indicator]   [score]%
   Land, Zoning & Entitlements [indicator] [score]%
   Ownership & Control       [indicator]   [score]%
   Environmental             [indicator]   [score]%
   Commercials               [indicator]   [score]%
   Natural Gas               [indicator]   [score]%
   Market Comparables        [indicator]   [score]%
   ──────────────────────────────────────────────
   Risk Assessment           [indicator]   [score]%
   ```

5. **Next steps guidance:**

   ```
   Due diligence complete. Results:

   Executive Summary: <absolute-folder-path>/EXECUTIVE_SUMMARY.md
   Research Reports: <absolute-folder-path>/research/

   The executive summary contains:
   - Overall verdict (Pursue / Proceed with Caution / Pass) with rationale
   - Scored summary table (High / Medium / Low) for all 10 categories
   - Key strengths and critical concerns
   - Deal-breaker assessment
   - Detailed findings per category
   - Information gaps and recommended next steps

   Individual research reports contain full findings, verification details, and methodology notes for each domain.
   ```

### Phase 8: Graceful Degradation

Handle failures at each phase appropriately:

**Document processing fails:**
- Stop the workflow immediately
- Show the error messages from the pipeline
- Provide actionable guidance on what might be wrong

**All agents fail:**
- Report systematic failure
- Suggest checking:
  - API keys (if web research was needed)
  - Network connectivity
  - File permissions in research/ folder
  - Whether converted documents actually contained usable data

**Some agents fail:**
- Continue with successful agents
- Note which domains are incomplete
- Still spawn the Risk Assessment agent (it handles missing domain reports gracefully)
- Provide partial results
- Don't treat partial failure as complete workflow failure

**Risk Assessment agent fails:**
- Report that cross-domain risk synthesis is unavailable
- Individual domain reports are still valid and usable
- Suggest manual review of cross-domain interactions
- Still proceed to executive summary generation (the generator handles missing reports gracefully by scoring that category as Low)

**Executive Summary Generator fails:**
- Report that the executive summary could not be generated
- Individual research reports and the Risk Assessment report are still valid and usable
- Suggest manual review of domain reports to form a recommendation
- The quick overview table from Phase 7 provides a partial substitute

**Output validation finds issues:**
- Note which reports seem incomplete
- Flag them for manual review
- Continue with reports that passed validation
- Include validation warnings in final summary

## Document Safety

The agent definitions already include the Document Safety Protocol. Your responsibilities:

1. **Do not modify document content:** Agents read files directly from `_converted/` - never inject, filter, or modify content
2. **Validate output structure:** Check that agents followed the template (presence of required sections)
3. **Flag anomalies:** If an agent's output deviates significantly from the template:
   - Log which agent and which sections are missing/malformed
   - Note this in the final summary as requiring manual review
   - Continue with other agents (don't let one anomaly stop the workflow)

Example flag for anomalous output:
```
Manual review recommended for [Domain] report:
Report structure deviates from expected format. This may indicate:
- Embedded instructions in source documents
- Agent processing errors
- Missing or corrupted data

Please manually verify findings from this domain before making decisions.
```

## Error Handling Reference

| Error Condition | Action | User Message |
|----------------|--------|--------------|
| No folder path provided | Stop, request input | "Please provide a folder path: `/due-diligence <folder-path>`" |
| Folder doesn't exist | Stop, show path | "Folder not found: `<path>`. Please check the path and try again." |
| Pipeline fails completely | Stop, show pipeline errors | "Document processing failed. Please check the error messages above and ensure..." |
| No files converted | Stop, explain limitation | "No documents could be processed. The folder may contain only unsupported file types..." |
| Research dir creation fails | Stop, show error | "Could not create research output directory: `<error>`. Check file permissions." |
| One agent fails | Continue with others | Note the failure in summary, list incomplete domains |
| Multiple agents fail | Continue with successful ones | List all failures, suggest causes |
| All domain agents fail | Skip Risk Assessment, stop workflow | "All research agents failed. This suggests a systematic issue. Check..." |
| Risk Assessment fails | Continue with domain reports, still generate executive summary | "Cross-domain risk synthesis unavailable. Review individual domain reports." |
| Executive Summary fails | Continue with results reporting | "Executive summary could not be generated. Review individual research reports." |
| Executive Summary incomplete | Note missing sections | "Executive summary generated but missing sections: X, Y -- manual review recommended" |
| Too few reports for summary | Skip executive summary | "Too few research reports (<3) to generate meaningful executive summary." |
| Report validation fails | Note in summary | "[Domain] report incomplete or malformed - manual review recommended" |

## Implementation Notes

- **Always use absolute paths** when spawning agents - the Task tool may have a different working directory
- **Handle paths with spaces** by quoting them in shell commands
- **Don't skip phases** - each phase's output is required for the next phase
- **Report progress clearly** - users need to understand what's happening during long-running operations
- **Preserve agent autonomy** - don't try to correct or rewrite agent outputs, just validate structure
- **Graceful degradation** - partial results are better than no results
- **Three-wave execution** is critical:
  - Wave 1: 9 domain agents run in parallel (they read broker documents)
  - Wave 2: Risk Assessment agent runs after Wave 1 (it reads domain reports)
  - Wave 3: Executive Summary Generator runs after validation (it reads all 10 reports and produces the final deliverable)

## Example Execution Flow

User runs: `/due-diligence ./opportunity-example`

1. Validate: folder exists
2. Process: 15 documents -> 11 converted, 4 failed (vision API not configured)
3. Setup: research/ folder created
4. Wave 1: 9 domain agents launched in parallel
5. Wave 1 complete: 9/9 domain reports generated
6. Wave 2: Risk Assessment agent launched
7. Wave 2 complete: risk-assessment-report.md generated
8. Validate: 10/10 reports pass content checks
9. Wave 3: Executive Summary Generator launched
10. Wave 3 complete: EXECUTIVE_SUMMARY.md generated with verdict and scored categories
11. Report:
    - 10 research domains analyzed
    - Executive summary with verdict (Pursue / Proceed with Caution / Pass)
    - Scored summary table with High/Medium/Low ratings for all 10 categories
    - Quick overview table with traffic lights and confidence scores
    - All reports saved to opportunity-example/research/
    - Executive summary saved to opportunity-example/EXECUTIVE_SUMMARY.md

This gives the user a complete analysis with a clear recommendation and actionable results, even if some agents encounter issues along the way.
