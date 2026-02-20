# Research Summary

**Project:** shipfast -- Claude Code Plugin Marketplace (noahrasheta/shipfast)
**Analysis Date:** 2026-02-20
**Confidence:** HIGH

## Executive Summary

Shipfast is a personal Claude Code plugin marketplace: a GitHub monorepo that doubles as both an author workspace and a plugin distribution catalog. Each plugin is a self-contained directory with its own manifest, skill orchestrator, specialized agents, and optional Python support code. The marketplace registry at `.claude-plugin/marketplace.json` makes all plugins installable with a single Claude Code command. The two existing plugins (create-image and dc-due-diligence) already follow the correct foundational architecture -- the work ahead is about maturing them (versioning, per-plugin READMEs, dependency lockfiles) and extending the platform with a public landing page at shipfast.cc.

Experts build Claude Code plugin marketplaces using a small set of well-established patterns: a skill orchestrator that coordinates but never does work itself, stateless domain agents spawned via the Task tool, and the filesystem as the state bus between pipeline waves. The PaperBanana-style multi-agent approach (parallel wave execution followed by sequential synthesis) is proven to outperform single-shot generation by +17% and is already in use in dc-due-diligence. The landing page should be a static site built with Astro 5.x and deployed to Cloudflare Pages -- zero backend, zero ongoing infrastructure cost, reading directly from the existing marketplace JSON at build time.

The key risks fall into two categories. First, distribution reliability: loose Python dependency pins, missing per-plugin READMEs, no CHANGELOG entries, and inconsistent version management mean users can install a plugin and have it fail or never receive updates. Second, developer process: three files must stay in sync for every plugin addition (marketplace.json, CLAUDE.md, README.md) with no automated enforcement. Both risk categories are solvable with low-effort hygiene steps -- none require architectural changes.

## Key Findings

### Recommended Stack

The stack has four distinct areas. For the existing plugin system, the platform is fixed: Claude Code Plugin System 1.0.33+, Markdown with YAML frontmatter for agents and skills, Python 3.11+ for document processing pipelines, and JSON for manifests. For the landing page (shipfast.cc), Astro 5.x with Tailwind CSS 4.x deployed to Cloudflare Pages is the clear choice: content-driven, zero-JS by default, and Cloudflare's free tier has no bandwidth cap. Cross-platform expansion to Cursor is achievable via thin adapters (Markdown content is reusable; only frontmatter format differs); OpenCode requires separate JS/TS wrappers and should be deferred until its spec stabilizes.

**Core technologies:**
- Claude Code Plugin System (1.0.33+): The target platform -- all plugin packaging and distribution must conform to its spec
- Markdown + YAML frontmatter: Required format for all agents and SKILL.md orchestrators
- Python (3.11+): Document processing pipelines and API integrations -- already invested; strong for file I/O
- Astro (5.x): Landing page framework -- best-in-class for content/showcase sites; zero JS by default; content collections for plugin catalog
- Tailwind CSS (4.x): Landing page styling -- zero-runtime utility CSS; requires `@astrojs/tailwind` adapter for Astro compatibility
- Cloudflare Pages: Landing page hosting -- free tier, unlimited bandwidth, auto-deploys from GitHub, global CDN
- pytest (>=8.0.0): Python converter testing -- already configured in dc-due-diligence

### Expected Features

The product has three surfaces with distinct feature expectations: the GitHub repo as a plugin catalog, the individual plugins themselves, and the landing page at shipfast.cc. The most impactful gaps today are per-plugin READMEs (missing from both plugins), `argument-hint` fields on skills (missing from both), semantic versioning enforcement (inconsistent), and dependency lockfiles (absent entirely). The landing page does not yet exist. None of these are complex -- they are hygiene items that make the difference between a plugin users trust and one they abandon mid-install.

**Must-haves:**
- Per-plugin README.md with prerequisites and install command -- users need this before the plugin shows up correctly in Claude Code's `/plugin` UI
- Single-command install with clear documentation on shipfast.cc -- users expect `npm install`-level simplicity
- Semantic versioning on all plugins -- required for update eligibility; currently inconsistent
- Working installation on a clean machine (verified) -- if first-run setup fails, the plugin is dead to new users
- `argument-hint` on all user-invocable skills -- Claude Code shows this during autocomplete; currently absent
- Validated marketplace.json in CI -- a syntax error in the catalog breaks all installs
- `${CLAUDE_PLUGIN_ROOT}` used for all internal path references -- plugins fail after marketplace installation without this

**Nice-to-haves:**
- Demo output / screenshots per plugin -- dramatically increases install confidence (Raycast and VS Code both show this prominently)
- CHANGELOG.md per plugin -- expected by users who depend on plugins for real work
- Category tags and `homepage`/`repository` fields in plugin manifests -- low effort, improves discoverability
- Automated CI validation workflow (`validate-plugins.yml`) -- prevents broken catalog from reaching users
- Agent Skills spec `compatibility` field -- enables cross-platform portability signaling

**Defer for later:**
- Custom web-based marketplace UI with search and filtering -- requires a backend, database, and ongoing maintenance; GitHub + a clean landing page is sufficient at this scale
- Plugin ratings and user reviews -- requires backend and moderation; "0 reviews" looks worse than nothing at low volume
- Plugin submission form for external contributors -- adds PR review burden without community scale to justify it
- Real-time plugin health monitoring -- plugins run locally; there is nothing server-side to monitor
- Cross-platform OpenCode packaging -- OpenCode's plugin spec is not yet stable as of February 2026

### Architecture Approach

The correct architecture is already in place: a plugin-per-directory monorepo where each plugin is fully self-contained, the repo root hosts the marketplace registry, and no shared code crosses plugin boundaries. The three core patterns to preserve are (1) orchestrator-agent separation -- the SKILL.md coordinates but never executes work, (2) multi-wave parallel execution -- non-dependent agents spawn in a single Task tool response block, and (3) filesystem as state bus -- agents write to predictable paths and subsequent waves read from those paths rather than through the orchestrator's context. The planned landing page belongs in a `landing-page/` subdirectory reading from existing marketplace JSON at build time.

**Major components:**
1. Marketplace registry (`.claude-plugin/marketplace.json`) -- unified plugin catalog; single source of truth for discovery and installation
2. Plugin manifest (`<plugin>/.claude-plugin/plugin.json`) -- per-plugin identity, version, and component declarations
3. Skill orchestrator (`<plugin>/skills/<name>/SKILL.md`) -- receives user command, coordinates agent pipeline, manages phase transitions; never does substantive work itself
4. Domain agents (`<plugin>/agents/<name>.md`) -- stateless, specialized task executors spawned via Task tool; each receives full context via prompt injection
5. Support layer (`<plugin>/converters/`, `scripts/`, `templates/`, `references/`) -- Python code, templates, and reference docs that agents invoke or read
6. Landing page (`landing-page/`) -- future static site; reads from marketplace.json and plugin READMEs at Astro build time; no backend

### Critical Pitfalls

1. **Hardcoded absolute paths in agent/hook files** -- Use `${CLAUDE_PLUGIN_ROOT}` for every internal file reference. Plugins work locally with `--plugin-dir` but break silently after marketplace installation because the cache path differs per machine. Any occurrence of `/Users/` or `~/` in agent Markdown is a bug.

2. **Version not bumped after changes** -- Users never receive updates if the version field does not change. For this project's relative-path plugin structure, set version only in `marketplace.json` and omit `version` from `plugin.json` to avoid the silent conflict where `plugin.json` wins and the marketplace version is ignored.

3. **Parallel agents spawned sequentially** -- Write all parallel Task calls in a single response block in the SKILL.md. If the orchestrator issues one Task call per turn, agents run in series and a 5-minute parallel job becomes a 45-minute sequential one. Always explicitly instruct: "Make all N Task calls in a single response block."

4. **Agent context starvation** -- Every agent invocation must include: the absolute path to input data, the absolute path for the output file, and a reference to the output template. Agents are stateless and cannot infer any of these from prior context. The dc-due-diligence skill's `OPPORTUNITY_FOLDER` + `PLUGIN_DIR` pattern is the correct template.

5. **Loose Python dependency pins with no lockfile** -- The current `pyproject.toml` uses `>=` lower-bound pins only and has no lockfile. Fresh installs may resolve newer incompatible versions (especially `anthropic` and `google-genai`, both of which have breaking change histories). Generate `requirements.txt` with `pip freeze` from the known-good development environment and use that file in `setup.sh`.

## Implications for Gameplan

Based on the combined research, the following goal/step structure is recommended. The ordering prioritizes distribution reliability first (nothing else matters if users can't install and run the plugins), then feature quality for existing plugins, then the new surface (landing page), and finally cross-platform expansion.

### Suggested Structure

**Goal 1: Distribution Reliability -- Make Existing Plugins Installable and Updatable**
- **Rationale:** Two plugins exist but have known gaps that prevent reliable distribution: no per-plugin READMEs, inconsistent versioning, no dependency lockfiles, no CI validation. These gaps mean users can install a plugin and have it fail silently or never receive updates. This must come first because every other goal assumes working plugins.
- **Delivers:** Both plugins with proper READMEs (prerequisites, install command, usage), pinned dependencies, version management (one source of truth), and CI validation running on every push
- **Addresses:** Per-plugin README (P1), semantic versioning enforcement (P1), `argument-hint` on skills (P1), `homepage`/`repository` in plugin manifests (P1), validated marketplace.json in CI (P2)
- **Avoids:** Version-not-bumped pitfall, loose dependency pins pitfall, three-files-out-of-sync pitfall
- **Research flag:** The "verified clean machine install" step needs hands-on testing -- no amount of code review replaces actually running the setup script from scratch on a machine that has never had the plugin

**Goal 2: Plugin Quality Polish -- Tighten What Users See**
- **Rationale:** With distribution working, the next gap is what users experience: no demo outputs, no changelogs, skill descriptions that may not trigger correctly, missing manifest fields. These are all low-effort, high-impact items. They should be batched together because they involve the same files (SKILL.md, plugin.json, README, marketplace.json).
- **Delivers:** Demo output samples for both plugins, CHANGELOG.md files, category/tag fields in marketplace.json, `compatibility` field in skills, platform compatibility matrix
- **Addresses:** Demo screenshots (P1), CHANGELOG.md (P2), category tags (P2), Agent Skills spec compliance (P2)
- **Avoids:** Skill description triggering incorrectly (vague descriptions mean skills never auto-invoke)
- **Research flag:** The Agent Skills `agentskills.io` specification should be reviewed directly to confirm which SKILL.md frontmatter fields are Claude Code extensions vs. portable standard fields before auditing for cross-platform compliance

**Goal 3: CI/CD Automation -- Remove Manual Process From the Release Loop**
- **Rationale:** The three-files-must-sync requirement for every new plugin is currently enforced only by a checklist in CLAUDE.md. A single GitHub Actions workflow catches broken manifests, missing entries, and failing Python tests before they reach users. This belongs before the landing page because the landing page reads from marketplace.json -- a broken catalog breaks the site too.
- **Delivers:** `validate-plugins.yml` workflow running `claude plugin validate` for each plugin, Python tests in CI, and optionally a script that checks marketplace.json entry count against plugin directory count
- **Addresses:** CI validation of marketplace.json (P2), plugin health badge in README (P3)
- **Avoids:** Three-files-out-of-sync pitfall, loose dependency pins surfacing in CI before users see them
- **Research flag:** Standard approach; GitHub Actions YAML pattern for this is well-documented in STACK.md -- minimal additional research needed

**Goal 4: Landing Page -- shipfast.cc**
- **Rationale:** The landing page is a new greenfield surface that reads from the now-reliable marketplace catalog. Building it after Goals 1-3 means the data source (marketplace.json, plugin READMEs) is complete and accurate. Astro + Cloudflare Pages is a well-understood stack with no ambiguity.
- **Delivers:** Static site at shipfast.cc with plugin grid on the home page, individual plugin pages rendering each plugin's README, one-command install instructions prominently shown, contact/feedback link
- **Addresses:** Plugin catalog with install commands (P1), plain-language plugin descriptions (P1), installation prerequisites (P1), contact link (P1)
- **Avoids:** Over-engineering (no backend, no ratings system, no submission form -- all deferred); keeps it static and zero-maintenance
- **Research flag:** Astro 5.x + Tailwind 4.x integration requires `@astrojs/tailwind` adapter with different config format than Tailwind v3 -- verify adapter setup during implementation. Cloudflare Pages deployment from GitHub is straightforward; no additional research needed.

**Goal 5: New Plugin -- (When Ready)**
- **Rationale:** By this point, the plugin scaffolding, CI validation, documentation template, and landing page pipeline are all in place. Adding a new plugin should be mechanical: follow the pattern, update three files, CI confirms it's valid, landing page picks it up automatically on next build.
- **Delivers:** Third plugin following the established pattern, with README, CHANGELOG, version set in marketplace.json, demo output
- **Addresses:** All P1 and P2 feature requirements should already be met by the scaffolding established in Goals 1-3
- **Avoids:** All pitfalls -- the established pattern prevents them by construction
- **Research flag:** Domain-specific -- depends entirely on what the plugin does. No general research needed; plugin-specific research should happen as part of planning this goal.

### Ordering Rationale

- Goals 1-3 address the existing codebase before adding new surfaces. Distribution reliability and CI must come before a landing page because the site reads from the same source the validator checks.
- The landing page (Goal 4) is blocked on having complete, reliable plugin data -- READMEs without proper content produce poor plugin pages.
- Cross-platform expansion (Cursor, OpenCode) is intentionally absent from this gameplan. The architecture research gives a clear approach for Cursor (thin adapter) and a clear deferral for OpenCode (spec not stable). These should become separate goals when the time comes.
- Goal 5 (new plugin) is deliberately last and intentionally vague -- it belongs after the foundation is solid but before shipfast.cc goes stale from having only two plugins.

### Research Flags

Areas needing deeper investigation during step planning:
- **Clean machine install verification:** Needs actual hands-on testing with `setup.sh` on a fresh environment. Cannot be confirmed from code review alone.
- **Agent Skills spec portability audit:** The `agentskills.io` specification should be read directly during Goal 2 planning to confirm which SKILL.md extensions are Claude Code-only and which are portable.
- **Astro content collection schema design:** The shape of the plugin data model in Astro's content collections should be designed carefully during Goal 4 planning -- it determines how easy it is to add new plugins to the site later.

Areas with standard patterns (minimal additional research needed):
- **GitHub Actions CI workflow:** Well-documented; the STACK.md already provides the complete YAML template.
- **Cloudflare Pages deployment:** Straightforward GitHub integration via dashboard; no custom configuration needed for a static Astro site.
- **Plugin manifest hygiene (version, homepage, repository fields):** All field names are confirmed in the official schema; implementation is mechanical.
- **Python dependency lockfile:** `pip freeze > requirements.txt` from the current development environment; update `setup.sh` to use it.

## Don't Hand-Roll

Problems with existing library solutions. Building these from scratch wastes time and introduces bugs.

| Problem | Existing Solution | Why Not Build It |
|---------|-------------------|------------------|
| PDF text extraction | `pdfplumber` (native selectable text) + Anthropic vision API (scanned PDFs) | Rolling a PDF parser from scratch requires handling font encoding, layout reconstruction, and multi-column text. Both solutions are already in use in dc-due-diligence. |
| Excel/Word/PowerPoint file parsing | `openpyxl`, `python-docx`, `python-pptx` | Office formats are binary or complex XML formats with years of edge case handling in these libraries. DIY parsers miss merged cells, embedded objects, and format variations. |
| Static site generation for the landing page | Astro 5.x | Building a custom SSG to render Markdown plugin pages with content collections, syntax highlighting, and sitemap generation would take weeks. Astro does all of this in hours. |
| Plugin validation | `claude plugin validate .` (built into Claude Code CLI) | The official validator knows the full schema, checks file references, and validates frontmatter. Reimplementing this risks missing schema fields or validation edge cases. |
| Syntax highlighting for code examples on the landing page | Shiki (bundled with Astro) | Shiki supports 100+ languages with accurate tokenization. Building accurate syntax highlighting from regex is a well-known rabbit hole. |
| Dependency version management | `pip freeze > requirements.txt` or `poetry.lock` | Manually tracking compatible version combinations across `anthropic`, `google-genai`, `pdfplumber`, and friends is infeasible. Lockfiles capture a known-good state that can be reproduced exactly. |
| CI plugin validation automation | GitHub Actions with `anthropics/claude-code-action` or `claude plugin validate` | The workflows and action are already available; the suggested YAML is in STACK.md. Writing a custom validation runner from scratch would miss CLI edge cases and plugin spec updates. |
| Web search in agents | Claude Code built-in WebSearch/WebFetch + optional Tavily/Exa/Firecrawl MCP | Implementing web search from scratch inside an agent requires handling rate limits, robots.txt, HTML parsing, and CAPTCHA. The built-in tools and MCP servers handle all of this. |

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All core recommendations verified against official docs (Claude Code, Astro, Cloudflare Pages, Tailwind). Alternatives clearly documented. Version compatibility matrix included. |
| Features | HIGH | Feature expectations verified against comparable ecosystems (VS Code Marketplace, Raycast Store, npm). Priorities reflect user value. Current codebase gaps confirmed by direct inspection. |
| Architecture | HIGH | Based on official Claude Code documentation plus direct codebase inspection. Patterns described are already proven in the existing plugins. Cross-platform abstraction is flagged as MEDIUM confidence separately. |
| Pitfalls | HIGH | All pitfalls verified against official Claude Code docs and direct codebase inspection. Several (loose pins, hardcoded model names) confirmed as present in the current codebase. |

**Overall confidence:** HIGH

## Gaps to Address

- **Cross-platform OpenCode packaging:** OpenCode's plugin spec is not yet stable or fully documented as of February 2026. This gap cannot be resolved until the spec matures. Revisit when planning a dedicated cross-platform goal.
- **Clean machine install verification:** Research cannot substitute for actually running `setup.sh` on a fresh machine. This should be the first acceptance criterion for Goal 1.
- **shipfast.cc domain and Cloudflare Pages account:** The research assumes the domain exists and Cloudflare Pages can be configured. If either is not set up, there may be domain transfer or DNS setup steps not covered here.
- **Astro content collection vs. direct JSON data loading:** Both approaches work for reading marketplace.json at build time. The choice affects how type-safe the plugin data model is. This decision should be made during Goal 4 planning.
- **`npm` source type in marketplace.json:** STACK.md notes this is "not yet fully implemented" in the official Claude Code docs. If this becomes a distribution channel, it needs re-evaluation at that time.

## Sources

### Primary (HIGH confidence)
- Official Claude Code plugin documentation: `code.claude.com/docs/en/plugins` -- plugin structure, component placement, `${CLAUDE_PLUGIN_ROOT}`, validation
- Official Claude Code plugins reference: `code.claude.com/docs/en/plugins-reference` -- complete manifest schema, CLI commands
- Official Claude Code marketplace guide: `code.claude.com/docs/en/plugin-marketplaces` -- marketplace.json format, source types, installation flow
- Official Claude Code skills documentation: `code.claude.com/docs/en/skills` and subagents: `code.claude.com/docs/en/sub-agents` -- SKILL.md format, Task tool, agent spawning
- Codebase inspection: `create-image/`, `dc-due-diligence/`, `.claude-plugin/marketplace.json`, `.github/workflows/` -- confirmed current state of all plugins and CI
- Astro 5.0 release blog and docs: `astro.build/blog/astro-5/` -- Astro 5 capabilities and content collections
- Cloudflare Pages documentation: `pages.cloudflare.com/` -- free tier confirmed, build limits confirmed

### Secondary (MEDIUM confidence)
- Agent Skills open standard: `agentskills.io/specification` -- cross-platform SKILL.md compatibility; standard is new and adoption is still growing
- OpenCode plugin system: `opencode.ai/docs/plugins/` -- JS/TS module format confirmed; spec flagged as not yet stable
- Cursor rules format: `cursor.com/docs/context/rules` -- `.mdc` file format; MEDIUM because Cursor's marketplace is evolving rapidly

### Tertiary (LOW confidence)
- PaperBanana multi-agent framework: Referenced in create-image plugin description as basis for +17% quality improvement claim; primary research paper not directly read; confidence in the claim relies on the plugin author's documentation

## Quality Gate

Before considering this file complete, verify:
- [x] Executive summary can stand alone -- someone reading only this section understands the conclusions
- [x] Key findings summarize, not duplicate, individual research files
- [x] Gameplan implications include specific goal/step suggestions
- [x] Don't Hand-Roll section has at least 3 entries (has 8)
- [x] Confidence assessment is honest about uncertainties
- [x] All sections populated -- no placeholders remaining from researcher output
