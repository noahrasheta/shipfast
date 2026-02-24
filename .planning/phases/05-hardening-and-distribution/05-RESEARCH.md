# Phase 5: Hardening and Distribution - Research

**Researched:** 2026-02-24
**Domain:** Claude Cowork plugin robustness, large data room stress-testing, non-technical README authoring
**Confidence:** MEDIUM — Cowork platform specifics verified via web search (multiple sources), architecture analysis from direct code review, README patterns from established guidance

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
No locked decisions — user deferred all implementation choices to Claude.

### Claude's Discretion
- **Stress test strategy** — How to simulate and validate 50+ file data rooms, what failure modes to test (context budget overflow, agent timeouts, corrupted/empty files, mixed file types), and what fallback behaviors to implement
- **README tone and depth** — Level of detail, formatting approach (screenshots vs text), reader assumptions, troubleshooting coverage
- **Error messaging UX** — What users see when failures occur mid-run, progress reporting, retry behavior, graceful degradation messaging
- **Install validation** — Definition of "clean machine" test, validation steps, inline troubleshooting vs separate FAQ

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| INFRA-04 | Plugin includes clear README with setup instructions a non-technical user can follow | README structure patterns, Cowork install flow mechanics, non-technical language guidelines |
</phase_requirements>

---

## Summary

Phase 5 has two separable workstreams: (1) hardening the plugin to survive large data rooms without context exhaustion or silent failure, and (2) shipping a README that lets a non-technical user install and run the plugin without any external help. These are independent tasks — hardening is code/orchestration changes, README is documentation.

The existing architecture already handles the hardest part of large data rooms: each domain agent runs in its own isolated context window (sub-agents in Cowork each get independent 200K token budgets), so 50 files spread across 9 domains never creates a single overflowing context. The real hardening work is defensive: what happens when an individual agent produces a bad output (too small, malformed, missing), and how does the user know what's happening during a 30-45 minute run on a large data room.

The README is well-understood territory. Cowork plugin installation has a confirmed non-technical path: download ZIP, open Cowork, click "+" in the plugin panel, drag ZIP in, click Upload. The README must describe this without any terminal commands, git references, or technical jargon. The success criteria ("no external help") means the README must be self-contained — every question a confused user might have should be answered in the document.

**Primary recommendation:** Split into two plans — Plan 05-01 for hardening (defensive error handling, better progress feedback, stress test script), Plan 05-02 for README authoring and install validation walkthrough.

---

## Standard Stack

No new libraries are required for this phase. The entire deliverable is:
- Modifications to existing Markdown files (orchestrator command, agent files)
- A new `README.md` file in `dc-due-diligence-desktop/`
- A new `STRESS_TEST.md` or similar test procedure document

### Core (Already in place)
| Component | Purpose | Status |
|-----------|---------|--------|
| Checkpoint system (`_dd_status.json`) | Session resilience — resume interrupted runs | Built in Phase 2 |
| Per-agent resume check (> 500 bytes) | Skip already-complete agents on retry | Built in Phase 3 |
| Sub-agent isolated contexts | Each domain agent has its own 200K token budget | Cowork architecture |
| 20-file batch ceiling | Prevents any single agent from exceeding platform file limit | Built in Phase 2 |

### No new installs needed
This phase adds no dependencies. Do not install packages, tools, or SDKs.

---

## Architecture Patterns

### Recommended File Structure After Phase 5

```
dc-due-diligence-desktop/
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   └── [12 agent files — unchanged from Phase 4]
├── commands/
│   └── due-diligence.md     # Modified: improved error UX, progress feedback
├── skills/
│   └── due-diligence/
│       └── SKILL.md         # Minor update: remove "Future Capabilities (Phase 5)" stub
└── README.md                # NEW: plain-language install and usage guide
```

### Pattern 1: Defensive Agent Output Validation

**What:** After each agent completes (domain and synthesis), validate the output file exists and is substantive before continuing. Currently the orchestrator checks `> 500 bytes`, which is the right approach — extend it to surface explicit user-visible messages when an agent's output is missing or suspiciously small.

**When to use:** After Wave 1 completes (before dispatching Wave 2), and after each synthesis agent completes.

**Example — enhanced completion check:**
```bash
# After Wave 1 completes
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
  echo "Warning: $((9 - COMPLETE_COUNT)) domain agents did not produce output."
  echo "Affected domains:$FAILED_DOMAINS"
  echo "Proceeding to synthesis with available reports."
  echo "Missing domains will be scored as Low in the Executive Summary."
fi
```

**Why this matters:** Synthesis agents (Risk Assessment, Executive Summary) already handle missing reports gracefully (SYNTH-05 is implemented). The gap is that the orchestrator currently doesn't tell the user *which* agents failed or why. Adding this surfacing removes the "silent failure" concern.

### Pattern 2: Pre-Dispatch File Count Warning

**What:** Before dispatching Wave 1, calculate the total file count. If it exceeds 50, display an estimated duration warning so the user isn't surprised by a long run.

**When to use:** Always, after routing completes and before agent dispatch.

**Example:**
```bash
TARGET_FOLDER="${ARGUMENTS:-$(pwd)}"
TOTAL_FILES=$(jq '.total_files' "$TARGET_FOLDER/_dd_inventory.json" 2>/dev/null || echo 0)
DOMAINS_WITH_FILES=$(jq '[.domains | to_entries[] | select(.value.count > 0)] | length' "$TARGET_FOLDER/_dd_inventory.json" 2>/dev/null || echo 9)

if [ "$TOTAL_FILES" -gt 50 ]; then
  echo ""
  echo "Large data room detected: $TOTAL_FILES files across $DOMAINS_WITH_FILES domains."
  echo "Estimated run time: 30-45 minutes. Claude will display progress as agents complete."
  echo ""
fi
```

### Pattern 3: README Structure for Non-Technical Users

**What:** A README written for a reader who knows what a data center is but has never used a terminal, never heard of Git, and may not know what a "plugin" is beyond "something you add to make software do more things."

**Sections (in order):**
1. What this does (2-3 plain sentences)
2. What you need before starting (Claude Desktop with Cowork, paid plan, a folder of documents)
3. How to install (numbered steps with concrete UI actions, no terminal)
4. How to use it (what to type, what to expect)
5. What the output looks like (so they know what success looks like)
6. Troubleshooting (3-5 specific problems with answers in plain language)

**Anti-patterns to avoid in the README:**
- Saying "run this command" or showing any `$` shell prompt
- Saying "clone the repo" or "git clone"
- Using terms like "terminal," "bash," "path," "CLI," "API," "token," "context window"
- Assuming the user knows what a ZIP file is (say "compressed folder" and tell them to double-click it)
- Linking to GitHub for installation (they're not developers)

### Pattern 4: ZIP Distribution Validation

**What:** The ZIP file has a known-working structure (validated in Phase 1). The hardening task is to verify the ZIP is correctly built and that the README's install steps match what a fresh Cowork install actually shows.

**Known install flow (MEDIUM confidence — from multiple web sources, consistent with STATE.md Phase 1 validation):**
1. User downloads the ZIP file (from wherever it's hosted — email, Notion, Dropbox link)
2. User opens Claude Desktop, clicks "Cowork" tab
3. User clicks "+" icon in the sidebar > "Plugins"
4. User drags the ZIP into the Cowork interface and clicks "Upload"
5. Plugin activates and `/due-diligence` command becomes available

**Key finding from STATE.md:** "User has also validated ZIP plugin installation pattern with other plugins." — This means the ZIP structure is already confirmed to work. The Phase 5 task is to document the steps clearly, not to re-engineer the install mechanism.

### Anti-Patterns to Avoid

- **Adding a progress bar or polling loop:** Cowork's Task tool sub-agents run asynchronously — the orchestrator cannot poll their progress mid-run. Surface completion status at the join point (after Wave 1 joins), not during.
- **Re-engineering the resume system:** The existing `_dd_status.json` + per-agent > 500 byte check is correct. Do not add a new checkpoint format or layer.
- **Splitting agents further for "context safety":** Sub-agents already have isolated contexts. Splitting domain agents into smaller pieces adds complexity without benefit.
- **Trying to make DOCX generation work without pandoc:** The existing graceful fallback (markdown-only with user message) is the correct pattern. Do not add a Python script or alternative converter.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Context overflow protection | Per-file token counting, truncation logic | Cowork's sub-agent isolation | Each sub-agent has its own 200K window; orchestrator doesn't hold file content |
| Progress during agent run | Polling loops, status files written by agents | Post-completion validation check at Wave join | Task tool sub-agents run independently; orchestrator waits at join |
| File type detection | Custom MIME type library | Existing filename extension matching (already built) | Extension matching is sufficient and already tested |
| README screenshots | Build a screenshot pipeline | Plain text with clear step descriptions | Screenshots go stale as Cowork UI evolves; text descriptions stay accurate |

**Key insight:** The hardening work here is defensive messaging, not new mechanism design. Every critical failure mode already has a recovery path — the gap is surfacing those paths to the user clearly.

---

## Common Pitfalls

### Pitfall 1: Conflating Orchestrator Context with Sub-Agent Context

**What goes wrong:** Assuming the orchestrator's context window fills up as 50+ files are processed, causing the whole run to fail.
**Why it happens:** Intuition from sequential processing — in serial code, reading 50 files would fill memory. In Cowork's Task tool architecture, each sub-agent has its own isolated 200K token context. The orchestrator only holds the inventory JSON and agent dispatch logic.
**How to avoid:** Don't add token-counting or file-splitting beyond the existing 20-file batch ceiling. The architecture is already correct.
**Warning signs:** If you find yourself writing token estimation logic in the orchestrator, stop — you're solving the wrong problem.

### Pitfall 2: README Written for the Wrong Reader

**What goes wrong:** README includes terminal commands, technical setup steps, or assumes familiarity with developer tooling.
**Why it happens:** The author (Claude) is a developer by training. Non-technical users have entirely different mental models.
**How to avoid:** Write the README to someone who can use Microsoft Word and double-click files, but has never opened Terminal. Test every instruction: "Could someone do this step with zero developer context?"
**Warning signs:** Any sentence that starts with "Run...", "Install...", "Configure...", "Add to your PATH..." is wrong.

### Pitfall 3: Treating "Agent Timeout" as Silent

**What goes wrong:** An agent runs too long (large file set, slow web search) and produces no output. The orchestrator proceeds to synthesis, which scores that domain as Low. User never knows why.
**Why it happens:** Cowork's Task tool has execution limits that aren't surfaced to the orchestrator on completion — the report file simply won't exist.
**How to avoid:** The post-Wave-1 validation check (Pattern 1 above) surfaces this explicitly. Make sure the message tells the user they can re-run `/due-diligence` and the checkpoint system will retry only the failed agents.
**Warning signs:** User reports "the verdict seems wrong" or "Power is scored Low but we know the power is fine" — this is often a failed/missing agent report.

### Pitfall 4: README Install Steps Don't Match Current Cowork UI

**What goes wrong:** README says "click the Plugins icon" but Cowork's UI uses a "+" button, or the modal says "Add Plugin" not "Upload."
**Why it happens:** UI labels in preview software change frequently. The README is written from documentation, not from testing the actual UI.
**How to avoid:** The README install steps should be tested against the actual Cowork desktop app before finalizing. If exact button labels aren't certain, use descriptions rather than quoted labels: "look for the add/upload option" rather than "click 'Upload Plugin'."
**Warning signs:** Multiple support questions about "I don't see the button you described."

### Pitfall 5: Stress Test With Artificial Files Misses Real Failure Modes

**What goes wrong:** Create 50 `.txt` files filled with lorem ipsum, run the plugin, it works — but real data rooms with 50 scanned PDFs or large Excel files behave differently.
**Why it happens:** Synthetic test data doesn't replicate the actual token pressure from vision processing or dense spreadsheet content.
**How to avoid:** The stress test procedure should specify realistic file types (a mix of PDFs, DOCX, XLSX). The most important failure modes to validate are: (1) a domain with zero files assigned, (2) a domain with > 20 files (triggers batch splitting), (3) a file that produces a very small agent report (resume check threshold).

---

## Code Examples

### Checking Agent Output Completeness After Wave 1

```bash
# Source: Derived from existing resume check pattern in due-diligence.md
TARGET_FOLDER="${ARGUMENTS:-$(pwd)}"
FAILED_DOMAINS=""
COMPLETE_COUNT=0
for domain in power connectivity water-cooling land-zoning ownership environmental commercials natural-gas market-comparables; do
  REPORT="$TARGET_FOLDER/research/${domain}-report.md"
  SIZE=$(stat -f%z "$REPORT" 2>/dev/null || echo 0)
  if [ "$SIZE" -gt 500 ]; then
    COMPLETE_COUNT=$((COMPLETE_COUNT + 1))
  else
    FAILED_DOMAINS="$FAILED_DOMAINS $domain"
  fi
done

if [ -n "$FAILED_DOMAINS" ]; then
  echo ""
  echo "Note: The following domains produced no report:$FAILED_DOMAINS"
  echo "This can happen when an agent runs out of time or encounters an error."
  echo "These domains will be marked as unavailable in the Executive Summary."
  echo "To retry, run /due-diligence again — completed domains will be skipped automatically."
fi
echo "$COMPLETE_COUNT of 9 domain reports complete. Proceeding to synthesis."
```

### Large Data Room Warning (pre-dispatch)

```bash
# Source: New pattern for Phase 5 — insert before Wave 1 dispatch
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

### README Install Section Template (plain language)

```markdown
## Installing the Plugin

**Step 1: Get the plugin file**

You should have received a file called something like `dc-due-diligence-desktop.zip`.
Save it somewhere you can find it — your Downloads folder is fine.

**Step 2: Open Claude Desktop**

Open the Claude app on your Mac. Click "Cowork" at the top of the window to switch to Cowork mode.

**Step 3: Add the plugin**

Click the "+" button on the left side of the screen, then choose "Plugins."
Look for an option to upload or add your own plugin.
Drag the `.zip` file into the window that appears, then click the button to confirm.

The plugin will install in a few seconds. You should see "Due Diligence" appear in your plugin list.

**Step 4: Connect your documents folder**

Before running an analysis, click "Work in a folder" and choose the folder on your computer
that contains the broker documents. Claude will be able to read those files during the analysis.
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Single-agent sequential file processing | Parallel sub-agents with isolated contexts | Cowork architecture (Jan 2026) | 50+ file data rooms are feasible; each domain runs in its own context |
| Plugin distribution via developer CLI | ZIP drag-and-drop upload in Cowork UI | Cowork plugin launch (Jan 30, 2026) | Non-technical users can install without terminal |
| Silent context truncation | Explicit error on overflow (Sonnet 3.7+) | Mid-2024 Claude model update | Agent failures are visible, not silent |

**Deprecated/outdated:**
- Python venv install for document conversion: NOT applicable here — the desktop plugin uses Claude's native document reading (no Python at all). The README must NOT mention Python, venv, or API keys. This is the CLI plugin's pattern, not the desktop plugin's.
- MCP tool configuration for web search: NOT required. All agents use built-in WebSearch/WebFetch.

---

## Open Questions

1. **Exact Cowork plugin upload UI labels**
   - What we know: ZIP drag-and-drop upload is confirmed by multiple sources; the flow is "+ > Plugins > upload/drag"
   - What's unclear: Exact button labels ("Upload Plugin"? "Add Plugin"? "Install"?) in the current Cowork UI — these change during preview
   - Recommendation: Write README with UI description language ("look for an option to upload your own plugin") rather than exact button label quotes, so it survives minor UI changes. The planner should flag this as a step to verify against the actual app.

2. **Cowork on Windows**
   - What we know: Cowork launched on Windows (per VentureBeat article, 2026). The shell commands in the orchestrator use `stat -f%z` which is macOS-specific.
   - What's unclear: Whether the user base for this plugin includes Windows users
   - Recommendation: The README can note "Mac app" in its prerequisites. If Windows support becomes a requirement, `stat -f%z` needs a cross-platform replacement. Out of scope for Phase 5 per REQUIREMENTS.md ("Claude Desktop Mac app only").

3. **Stress test with real data room**
   - What we know: The architecture handles 50+ files correctly in theory (batch ceiling, sub-agent isolation)
   - What's unclear: Actual end-to-end behavior on a 50+ file data room — the plugin has not been tested at this scale
   - Recommendation: The stress test plan should include a step that creates a realistic synthetic data room (50 mixed-type files) and runs the full pipeline. Success criteria: all agents complete, checkpoint survives if interrupted, and the Executive Summary reflects available data.

---

## Sources

### Primary (HIGH confidence)
- Direct code review of `dc-due-diligence-desktop/commands/due-diligence.md` — full orchestrator flow
- Direct code review of `dc-due-diligence-desktop/skills/due-diligence/SKILL.md` — capability list
- `.planning/STATE.md` — accumulated project decisions and validations (ZIP install confirmed, parallel dispatch confirmed)
- `.planning/REQUIREMENTS.md` — INFRA-04 requirement definition and scope boundaries

### Secondary (MEDIUM confidence)
- [Claude Help Center — Understanding usage and length limits](https://support.claude.com/en/articles/11647753-understanding-usage-and-length-limits) — 200K token context window confirmed
- [Claude Help Center — Uploading files to Claude](https://support.claude.com/en/articles/8241126-uploading-files-to-claude) — 20 files per chat, 30MB per file limits
- [Claude Blog — Customize Cowork with plugins](https://claude.com/blog/cowork-plugins) — "upload your own plugin" capability confirmed, launched Jan 30, 2026
- [Alex McFarland Substack — Plugins walkthrough](https://alexmcfarland.substack.com/p/plugins-are-here-for-claude-cowork) — "drag a zip file into Cowork" install pattern confirmed
- [WebSearch result summary] — Cowork sub-agents each have independent contexts, auto-compaction at 95% capacity
- [claudecowork.im complete guide](https://claudecowork.im/blog/claude-cowork-plugins-complete-guide) — "Upload plugin" option in Cowork desktop confirmed

### Tertiary (LOW confidence)
- [claudecodeplugins.io](https://claudecodeplugins.io/cowork/) — "Copy plugin folder into `.claude/plugins/`" install variant — this appears to be an unofficial guide and the method differs from the official ZIP drag-and-drop; do not use in README
- Estimated run times for large data rooms (30-45 minutes) — derived from known agent count and web research behavior; not measured empirically

---

## Metadata

**Confidence breakdown:**
- Standard stack (no new deps): HIGH — confirmed by code review; nothing to install
- Architecture patterns (hardening): MEDIUM — defensive patterns derived from existing code and known failure modes; specific failure behavior in Cowork not directly testable here
- Cowork install flow: MEDIUM — confirmed by multiple web sources and STATE.md validation; exact UI labels uncertain
- README patterns: HIGH — plain-language documentation principles are well-established
- Pitfalls: MEDIUM — derived from code review + platform behavior patterns; not all empirically tested

**Research date:** 2026-02-24
**Valid until:** 2026-03-24 for architecture patterns (stable); 2026-03-03 for Cowork UI specifics (fast-moving preview platform)
