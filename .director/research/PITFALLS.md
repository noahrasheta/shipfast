# Pitfalls Research

**Analysis Date:** 2026-02-20
**Confidence:** HIGH (verified against official Claude Code documentation at code.claude.com; project-specific findings from direct codebase inspection)

## Critical Pitfalls

### Pitfall: Plugin Files Placed Inside .claude-plugin/ Instead of Plugin Root

**What goes wrong:**
Components like `commands/`, `agents/`, `skills/`, and `hooks/` end up inside the `.claude-plugin/` directory alongside `plugin.json`. The plugin loads without error but skills, agents, and hooks are silently missing -- nothing works as expected and there is no obvious error message.

**Why it happens:**
The naming `.claude-plugin/` implies "everything plugin-related goes here." New plugin authors assume it is the plugin's config directory and put all components inside it. The actual convention is the exact opposite: only `plugin.json` lives in `.claude-plugin/`, and everything else lives at the plugin root.

**How to avoid:**
The plugin root directory is the container. `.claude-plugin/` is a metadata subfolder for the manifest only. Every component directory (`skills/`, `agents/`, `hooks/`, `commands/`, `.mcp.json`, `.lsp.json`) must be a sibling of `.claude-plugin/`, not a child of it. Run `claude plugin validate ./<plugin-name>` after any structural change.

**Warning signs:**
Skills registered in `plugin.json` do not appear when running `/help`. Agents are missing from `/agents`. Debug output from `claude --debug` shows the plugin loaded but lists zero commands or agents.

---

### Pitfall: Hardcoded Absolute Paths in Agent and Hook Files

**What goes wrong:**
Agent Markdown files or hook scripts reference files using hardcoded absolute paths like `/Users/noah/.claude/plugins/cache/...` or relative paths like `../templates/`. When another user installs the plugin, or when Claude Code copies the plugin into its cache directory during installation, those paths are wrong. Agents fail to find reference files; hooks fail to execute scripts.

**Why it happens:**
During local development with `--plugin-dir`, the plugin runs in-place and absolute paths appear to work fine. The problem only surfaces after marketplace installation, when the plugin is copied to `~/.claude/plugins/cache/`. The cache path contains a version hash and differs per machine.

**How to avoid:**
Always use `${CLAUDE_PLUGIN_ROOT}` for any file reference inside a plugin. This token resolves to the plugin's actual installation directory at runtime, whether that is the local dev directory or the cache location. Never use `../` path traversal -- installed plugins cannot reference files outside their directory because only the plugin directory is copied to cache.

**Warning signs:**
Plugin works locally with `--plugin-dir` but breaks after `plugin install`. Agent output contains errors like "file not found" or "cannot read template." Hook scripts fail to execute. Any agent file containing a hardcode like `/Users/` or `~/` is a sign of this problem.

---

### Pitfall: Version Not Bumped After Changes -- Users Never See Updates

**What goes wrong:**
The plugin author pushes code changes to the repository but forgets to increment the `version` field in `plugin.json`. Existing users who run `/plugin update` see "already up to date" and get the old behavior. The version is the cache-busting mechanism -- if it does not change, Claude Code assumes the installed copy is current and skips the update.

**Why it happens:**
There is no CI check enforcing version bumps. When iterating quickly on agent prompts or skill logic, version management feels like overhead. For relative-path plugins within a monorepo marketplace, the version in `marketplace.json` is the source of truth, but if `plugin.json` also has a version field, `plugin.json` wins silently -- the marketplace version is ignored.

**How to avoid:**
Treat version bumps as required for any distributable change. For this project's structure (relative-path plugins inside the marketplace repo), set the version only in `marketplace.json` and omit the `version` field from `plugin.json` entirely -- or keep them synchronized. Document a release checklist: bump version, update CHANGELOG.md, push to the repo.

**Warning signs:**
Users report that changes are not visible after updating. The version field in `plugin.json` and `marketplace.json` contain different values. Commits that change agent or skill content do not also change any version field.

---

### Pitfall: Orchestrator Skill Forgets to Spawn All Agents in One Response Block

**What goes wrong:**
The orchestrator spawns parallel agents sequentially -- one Task tool call per response turn -- instead of issuing all Task calls in a single message. The agents run in series rather than in parallel, turning a 5-minute parallel job into a 45-minute sequential one. The user sees one agent complete, then another starts, and so on.

**Why it happens:**
The natural way to write instructions is "spawn agent A, wait, spawn agent B, wait..." Claude follows these step-by-step instructions literally unless the skill explicitly says "issue all Task calls in a single response block."

**How to avoid:**
In the skill instructions, explicitly state: "Make all N Task tool calls in a single response block." Provide a numbered list of agents to spawn and instruct the orchestrator to include all calls in one message. The dc-due-diligence skill already does this correctly for Wave 1 -- that pattern should be used for any parallel wave. Verify by watching whether the agents appear to start simultaneously in the UI.

**Warning signs:**
Parallel pipeline takes much longer than expected. The UI shows each agent completing fully before the next one appears. The skill description says "parallel" but execution is clearly sequential.

---

### Pitfall: Agent Context Starvation -- Too Much Content, Not Enough Specifics

**What goes wrong:**
An agent is given a vague task prompt like "analyze the opportunity folder" without the specific file paths it needs to read, the output file path it should write, or the template it should follow. The agent invents its own approach, writes output to the wrong location, uses a different format, or silently produces an empty file.

**Why it happens:**
In multi-agent pipelines, orchestrators often summarize the task in shorthand, assuming agents will figure out the specifics. Agents are stateless -- they receive only what is in their prompt and have no memory of prior agent runs or orchestrator context.

**How to avoid:**
Each agent invocation must include: the absolute path to the input data, the absolute path for the output file, and a reference to the template or format specification. The dc-due-diligence skill correctly passes `OPPORTUNITY_FOLDER` and `PLUGIN_DIR` to each agent. Use this as the template: never spawn an agent without specifying exactly where it reads from and where it writes to.

**Warning signs:**
Agent output files appear in unexpected locations. Agents produce output that does not match the expected template format. Validation checks fail because required sections are missing. Agents produce very short reports suggesting they could not find the input data.

---

### Pitfall: Loose Dependency Pins Break On Fresh Installs

**What goes wrong:**
The Python packages in `pyproject.toml` use loose lower-bound pins like `anthropic>=0.40.0`. Six months after initial development, a new user installs the plugin and gets `anthropic 1.0.0`, which has breaking changes to the client API. The converter pipeline fails on first run with an import error or unexpected keyword argument.

**Why it happens:**
Loose pins feel flexible and forward-compatible. Without a lockfile (`poetry.lock`, `requirements.txt` with pinned hashes), there is nothing to reproduce the exact environment that was tested. The `setup.sh` auto-creates a venv, but if it installs a newer incompatible version, the user gets a broken environment on first run with no clear error message.

**How to avoid:**
Add a `requirements.txt` with pinned versions, generated from the known-good development environment (`pip freeze > requirements.txt`). Use this file in `setup.sh` for installation. Alternatively, add `poetry.lock` and use `poetry install`. At minimum, use tighter pins like `anthropic>=0.40.0,<1.0.0` for any library with a track record of breaking changes between major versions.

**Warning signs:**
No lockfile present in the repo (confirmed in the current codebase). Users report installation errors that cannot be reproduced. The version of `anthropic` or `google-genai` installed in a fresh venv differs from what was used in development.

---

### Pitfall: Hardcoded Model Names Break When Models Are Deprecated

**What goes wrong:**
The vision converter hardcodes `claude-sonnet-4-20250514` as the model string. When Anthropic deprecates this model name (which happens regularly as newer models release), all vision-based PDF conversion fails with a model-not-found error. Because this is inside a try/except that returns `ExtractionResult(success=False)` on failure, the error is swallowed -- the user sees partial results with no clear explanation.

**Why it happens:**
At development time, you want a specific model. Putting it in code is fast. Updating it later requires tracking down every place it is hardcoded.

**How to avoid:**
Move model names to a configuration constant at the top of the file (e.g., `VISION_MODEL = "claude-sonnet-4-20250514"`). Better: move it to a config file or environment variable so users can override it without touching source code. Subscribe to Anthropic's model deprecation notices.

**Warning signs:**
The string `claude-sonnet-4-` appears in source code files rather than in a config file. Any error in conversion that results in `success=False` without a visible error message to the user.

---

### Pitfall: Three Files Must Be Updated Together -- Missing One Breaks the Catalog

**What goes wrong:**
A new plugin is added to the repo directory structure, but the developer forgets to update one of the three required files: `marketplace.json`, the `CLAUDE.md` Plugin Reference section, or the `README.md` summary table and detail section. The plugin exists in the file system but is not discoverable in the marketplace, or the documentation is stale.

**Why it happens:**
Three separate files need to be edited for every plugin addition. There is no automated check that enforces consistency between the directory structure and the catalog. This is a manually maintained registry -- it falls out of sync when process is skipped under time pressure.

**How to avoid:**
Add a checklist to CLAUDE.md: "When adding a new plugin, update these three files: ..." (already present). Consider adding a simple validation script that checks whether every directory containing a `.claude-plugin/plugin.json` has a corresponding entry in `marketplace.json`. Run this script as part of any CI check.

**Warning signs:**
A plugin directory exists at the repo root but has no matching entry in `.claude-plugin/marketplace.json`. Documentation in `README.md` references a plugin version or feature that differs from the actual plugin manifest.

---

## Common Shortcuts That Backfire

| Shortcut | Short-term Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Skipping version bump in `plugin.json` after code changes | Save one step per commit | Users never receive updates; cache is never invalidated | Never for published plugins |
| Using absolute paths instead of `${CLAUDE_PLUGIN_ROOT}` | Works instantly in local dev | Breaks on every other machine after installation | Never |
| No lockfile -- loose pip version pins | Flexible for experimentation | Fresh installs get untested dependency versions; production breaks silently | Never for plugins distributed to others |
| Single broad `SKILL.md` with all instructions inlined | Faster initial development | Hits the 500-line recommended limit; supporting reference files not loaded unless linked | Acceptable for simple skills; refactor when SKILL.md exceeds 500 lines |
| Putting version in both `plugin.json` and `marketplace.json` | Feels redundant-safe | `plugin.json` silently wins; marketplace version is ignored; users and authors confused about the truth | Never -- use one source of truth |
| Using relative paths like `../shared/` to share code across plugins | Avoids duplication | Breaks after marketplace installation because only the plugin dir is cached | Never -- use symlinks if sharing is required |
| Hardcoding model name in source | Fast at development time | Fails silently when model is deprecated | Never -- use a named constant at minimum |

## Things That Look Done But Aren't

- [ ] **Plugin published to marketplace:** Often missing a version bump -- verify that `version` in `plugin.json` or `marketplace.json` was incremented since the last release, and that a `CHANGELOG.md` entry exists
- [ ] **Parallel agent wave implemented:** Often appears parallel but runs sequentially -- verify by checking that the orchestrator skill issues all Task calls in a single response block, not one per turn
- [ ] **Document conversion pipeline set up:** Often appears working but vision conversion is silently skipped -- verify that `ANTHROPIC_API_KEY` is set in the shell environment if the opportunity folder contains scanned PDFs or image files
- [ ] **Agent output validated:** Agent may have written a file that exists but is nearly empty (< 500 bytes) or missing required template sections -- verify with the Phase 5 content validation checks in the due-diligence skill
- [ ] **Plugin tested after installation:** Local `--plugin-dir` testing does not catch path resolution bugs -- verify by actually installing from the marketplace and running the skill from a different directory
- [ ] **New converter added correctly:** Often added to one registry dict but not the other -- verify that both `_get_converter()` in `pipeline.py` and `_TYPE_TO_CONVERTER` in `scanner.py` include the new format
- [ ] **Skill description triggers correctly:** A vague description means Claude never auto-invokes the skill -- verify that the description includes the exact natural-language phrases users will type, as shown in the due-diligence skill's description field

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Committing `_converted/` output directories | Absolute paths in `manifest.json` expose the user's local filesystem layout; sensitive document content in the repo | Add `_converted/` to `.gitignore` (already done) and document this in setup instructions |
| Agents reading user documents without a prompt injection guard | A malicious document could embed "ignore previous instructions" to change agent behavior or extract system prompt | All dc-due-diligence agents already include a Document Safety Protocol block; all future agents processing untrusted documents should include the same |
| Setting `permissionMode: bypassPermissions` in agent frontmatter without justification | Agent can execute any operation without user approval, including destructive shell commands | Only use `bypassPermissions` when explicitly required and document why; prefer `acceptEdits` or `dontAsk` for specific scenarios |
| Hook scripts not made executable (`chmod +x`) | Hook silently does nothing; attacker who can replace the script file gets execution when the hook finally runs | Make hook scripts executable as part of plugin setup; check executability in plugin validation |
| Storing API keys in `.env` files committed to the repo | Key exposure leads to unauthorized API usage and billing | The `.gitignore` already excludes `.env`; document in setup instructions that keys go in the shell environment, not in the repo |
| Cross-plugin path traversal via symlinks | A plugin that symlinks outside its directory could access sensitive files in the user's home directory | Symlinks are honored by the plugin cache copy process -- only use them intentionally; never create symlinks in plugins that point to user home directory files |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Sequential API calls for scanned PDF pages | A 100-page scanned PDF takes 100 sequential Anthropic API calls; appears hung for 5-10+ minutes | Batch pages where possible; show a progress indicator; document the expected wait time | Any scanned PDF with more than ~20 pages |
| All agents serialize because orchestrator issues one Task call per turn | Parallel pipeline takes N times longer than expected; first agent must complete before second starts | Issue all parallel Task calls in a single response block as documented in the due-diligence skill | Any multi-agent pipeline where the orchestrator prompt says "spawn agents in order" |
| Skill description too long -- exceeds context budget | Claude stops auto-invoking skills; warns about excluded skills in `/context` | Keep individual skill descriptions concise; the total budget is ~2% of the context window (~16,000 characters fallback) | When total character count of all skill descriptions exceeds the budget |
| Image file handle not closed in vision converter | Memory leak grows with each page processed in a long batch run | Use `with Image.open(path) as img:` context manager instead of manual open (known issue in vision.py line 277) | Large batch processing runs with many scanned PDFs |
| Uncached re-conversion of already-processed documents | Each `/due-diligence` invocation on the same folder reprocesses all documents even if nothing changed | The skill already checks for existing `_converted/manifest.json` and skips conversion if it exists -- preserve this check in all future orchestrator edits | Any time the manifest existence check is accidentally removed |

## Sources

- Official Claude Code plugin documentation: https://code.claude.com/docs/en/plugins (HIGH confidence -- verified)
- Official Claude Code plugins reference: https://code.claude.com/docs/en/plugins-reference (HIGH confidence -- verified)
- Official Claude Code skills documentation: https://code.claude.com/docs/en/skills (HIGH confidence -- verified)
- Official Claude Code hooks reference: https://code.claude.com/docs/en/hooks (HIGH confidence -- verified)
- Official Claude Code plugin marketplaces guide: https://code.claude.com/docs/en/plugin-marketplaces (HIGH confidence -- verified)
- Official Claude Code subagents documentation: https://code.claude.com/docs/en/sub-agents (HIGH confidence -- verified)
- Codebase inspection: `dc-due-diligence/converters/`, `dc-due-diligence/skills/`, `create-image/skills/`, `dc-due-diligence/agents/`, `.claude-plugin/marketplace.json` (HIGH confidence -- direct code inspection)
- Existing analysis: `.director/codebase/CONCERNS.md` (HIGH confidence -- prior codebase mapping)

## Quality Gate

Before considering this file complete, verify:
- [x] At least 3 critical pitfalls documented with prevention strategies
- [x] Warning signs included for each critical pitfall
- [x] "Things That Look Done But Aren't" has at least 3 items
- [x] Prevention strategies are specific and actionable
- [x] No section left empty -- use "Not detected" if nothing found
