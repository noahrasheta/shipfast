# Feature Research

**Analysis Date:** 2026-02-20
**Confidence:** HIGH

## Feature Landscape

This project has three distinct product surfaces, each with its own feature expectations:
1. **The plugin marketplace/catalog** -- the GitHub repo with `marketplace.json` that users install from
2. **Individual plugins** -- the actual Claude Code plugins (create-image, dc-due-diligence, and future ones)
3. **The landing page** -- shipfast.cc as a public showcase and library

---

### Must-Haves

_Features users expect. Missing these means the product feels incomplete._

#### Plugin Marketplace (the GitHub repo catalog)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Single-command install | Users expect `npm install`-level simplicity for any package/extension ecosystem | LOW | Already works: `/plugin install dc-due-diligence@shipfast` |
| Semantic versioning on all plugins | Users need to know what changed and whether to update. Every mature package ecosystem requires it. | LOW | Currently inconsistent -- both plugins should pin versions in `plugin.json` |
| README per plugin | VS Code, npm, and Raycast all show the README as the primary discovery artifact | LOW | Both plugins need a proper `README.md` inside the plugin directory, not just repo-level docs |
| Changelog or release notes | Users need to know what changed between versions before updating. npm, VS Code, and Raycast all surface this. | LOW | Not currently present for either plugin |
| Working installation on a clean machine | If setup fails for a new user, the plugin is dead to them | MEDIUM | The Python venv auto-setup helps; needs to be verified on a fresh machine |
| Clear prerequisites listed | Users need to know: what API keys, what system tools, what versions are required | LOW | Currently documented in CLAUDE.md but not in each plugin's own README |
| Validated JSON in marketplace.json | A syntax error in the catalog breaks all installs | LOW | Use `claude plugin validate .` in CI |

#### Individual Plugins (Claude Code quality)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| YAML frontmatter with `name` and `description` on all agents | Required by the plugin system; Claude uses description to decide when to invoke | LOW | Already done in both plugins |
| `${CLAUDE_PLUGIN_ROOT}` used for all paths | Plugins fail if hardcoded paths are used after being copied to cache | LOW | Convention documented; enforce it |
| Skill description that triggers correctly | Claude uses the description field to decide when to invoke a skill automatically. Poor descriptions mean the skill never fires. | MEDIUM | Descriptions should include trigger phrases ("Use when...", "Use for...") |
| `argument-hint` on user-invocable skills | Claude Code shows this hint during autocomplete; users expect argument guidance | LOW | Not currently set on either plugin's SKILL.md |
| Error messages users can act on | When a plugin fails, the error should tell users what to do -- not just that something went wrong | MEDIUM | The dc-due-diligence plugin is silent when the venv setup fails |
| Agent Skills spec compliance | Skills follow the `agentskills.io` open standard for cross-platform compatibility | LOW | The standard requires `name` and `description` frontmatter; description max 1024 chars |

#### Landing Page (shipfast.cc)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Plugin catalog with one-line install commands | Users expect to copy a command and be done. Raycast and VS Code both show install buttons prominently. | LOW | Show `/plugin marketplace add noahrasheta/shipfast` and then the per-plugin install command |
| What each plugin does in plain language | Technical jargon loses users. Raycast uses one-sentence descriptions with clear outcomes. | LOW | Lead with the user's outcome ("Analyze data center deals in minutes") not the mechanism |
| Installation prerequisites | Users need to know what API keys and system tools they need before installing | LOW | Show this clearly for each plugin so users aren't surprised mid-install |
| Contact / feedback link | Users of open-source tools expect a way to report issues or ask questions | LOW | GitHub issues link is sufficient |

---

### Nice-to-Haves

_Features that provide competitive advantage. Not required, but valuable._

| Feature | Value | Complexity | Notes |
|---------|-------|------------|-------|
| Screenshots or demo output | Raycast and VS Code show screenshots of extensions in action. Users evaluate visually before installing. | LOW | A sample executive summary output or sample generated image would dramatically increase install confidence |
| `compatibility` field in SKILL.md | The Agent Skills spec supports this; tells users which platforms and tools are required | LOW | Example: `compatibility: Requires Claude Code, ANTHROPIC_API_KEY for PDF processing` |
| Category tags on plugins in marketplace.json | Claude Code plugin marketplace schema supports `category` and `tags` fields | LOW | Helps when Noah has 10+ plugins -- users can filter by type |
| Plugin health badge in README | Shows last-tested version, CI status. Builds trust. npm and VS Code extensions both surface this. | MEDIUM | A GitHub Actions workflow that runs `claude plugin validate .` on each push would power this |
| Per-plugin CHANGELOG.md | Transparent history of what changed. Expected by anyone who depends on the plugin for real work. | LOW | Even a two-line changelog is better than nothing |
| `homepage` and `repository` fields in plugin.json | The manifest schema supports these; VS Code marketplace displays them prominently under Resources | LOW | Already documented in the schema; just not set in either plugin's `plugin.json` |
| Cross-platform skill compatibility | Agent Skills standard is supported by Cursor, OpenCode, Gemini CLI, VS Code, GitHub Copilot, OpenAI Codex, and 20+ others. Writing to the open standard unlocks this automatically. | MEDIUM | Already partially done -- SKILL.md format is compliant. The gap is Claude Code-specific frontmatter extensions (`disable-model-invocation`, `context: fork`) that other platforms may ignore but do not break. |
| Platform compatibility matrix per plugin | Tells users which platforms each plugin works on | LOW | A simple table in each plugin's README: Claude Code (full), Cursor (skill only), etc. |
| Blog posts or write-ups per plugin | Raycast's most popular extension authors write about their extensions on community forums and personal blogs. This drives organic discovery. | MEDIUM | A brief "how it works" for each plugin on shipfast.cc would be valuable |
| Automated marketplace validation in CI | Prevents catalog from going stale or broken | MEDIUM | GitHub Actions running `claude plugin validate .` catches JSON errors, missing files, and broken references |

---

### Avoid Building

_Features that seem good but create problems._

| Feature | Why Tempting | Why Problematic | Better Approach |
|---------|--------------|-----------------|-----------------|
| A custom web-based marketplace UI with search and filtering | Looks impressive; VS Code and Raycast have this | Requires a web server, database, ongoing hosting costs, and maintenance. The user base for Claude Code plugins is small enough that GitHub + a clean landing page is sufficient. | Use GitHub as the authoritative catalog and ship a clean static landing page at shipfast.cc that lists plugins with install commands |
| Automated update notifications pushed to users | Feels like great UX | The Claude Code marketplace already handles updates via `/plugin marketplace update` and auto-update on startup. Building a separate notification layer duplicates this and creates a separate channel to maintain. | Rely on the built-in auto-update system; document it in the README |
| Plugin ratings and user reviews | Mimics app store credibility signals | Requires a backend, user accounts, moderation. With a small user base, a ratings system will show "0 reviews" for months, which looks worse than nothing. | Use GitHub stars and issue counts as social proof instead |
| A plugin submission form from external contributors | Looks like a community platform | Adds PR review burden without community scale to justify it. Noah's goal is his own curated collection, not a open marketplace. | Accept contributions via GitHub pull requests, which is already the convention for Raycast extensions |
| Versioned plugin docs per release | Seems professional | Extremely high maintenance cost for a one-person operation. | Keep a single current README and a CHANGELOG.md that notes breaking changes |
| Real-time plugin health monitoring | Seems valuable | Requires external infrastructure (cron jobs, uptime monitoring, alerting). The plugins run locally on users' machines -- there is nothing to monitor from the server side. | Document known issues in CHANGELOG.md; use GitHub issues for bug tracking |

---

## Feature Priorities

_How should features be ordered based on user value and build cost?_

| Feature | User Value | Build Cost | Priority |
|---------|------------|------------|----------|
| README per plugin (with prerequisites and install command) | HIGH | LOW | P1 |
| Clear one-command install flow on landing page | HIGH | LOW | P1 |
| `argument-hint` on skills | MEDIUM | LOW | P1 |
| `homepage` and `repository` in plugin.json manifests | MEDIUM | LOW | P1 |
| Semantic versioning enforcement across plugins | HIGH | LOW | P1 |
| Demo output / screenshots per plugin | HIGH | LOW | P1 |
| CHANGELOG.md per plugin | MEDIUM | LOW | P2 |
| Category and tags in marketplace.json | MEDIUM | LOW | P2 |
| Agent Skills spec `compatibility` field | MEDIUM | LOW | P2 |
| Platform compatibility matrix per plugin | MEDIUM | LOW | P2 |
| CI validation of marketplace.json | HIGH | MEDIUM | P2 |
| Cross-platform skill compliance audit | MEDIUM | MEDIUM | P2 |
| Blog posts or write-ups per plugin | MEDIUM | HIGH | P3 |
| Plugin health badge in README | LOW | MEDIUM | P3 |

_Priority key: P1 = must have for launch, P2 = should have when possible, P3 = future consideration._

---

## What Competitors Do

_How do similar products handle these features?_

| Feature | How Others Do It | Our Approach |
|---------|------------------|--------------|
| Plugin installation | VS Code: one-click install in editor UI. npm: `npm install`. Raycast: visual store with install button. | Claude Code: `/plugin install name@marketplace` -- single command, no browser needed. Already good; just needs to be prominent on the landing page. |
| Plugin discovery | VS Code Marketplace: search, categories, download counts, ratings, screenshots. Raycast store: categories, download counts, sorting. npm: search by keywords. | GitHub repo + static landing page. Fine for this scale. The key gap is each plugin needs a standalone README that shows up in Claude Code's `/plugin` UI. |
| Plugin quality signals | VS Code: verified publisher badges, download counts, ratings, last updated date. npm: weekly downloads, GitHub stars, open issues. Raycast: download count prominently shown. | Currently: none. Add: version numbers, last updated date in marketplace.json, demo screenshots. |
| Cross-platform standards | VS Code extensions: VS Code only. npm: platform-agnostic. Raycast: macOS/Windows explicit flags. | The Agent Skills standard (`agentskills.io`) is the emerging cross-platform standard. It is already supported by Claude Code, Cursor, OpenCode, Gemini CLI, VS Code, GitHub Copilot, and OpenAI Codex. Writing SKILL.md to this standard with minimal Claude Code-specific extensions maximizes portability. |
| Author presence | Raycast top authors have personal profiles with extension collections. npm authors have profile pages showing all packages. | shipfast.cc as a personal plugin library site is the right move. One page listing all plugins with install commands and brief descriptions. |
| Update mechanism | VS Code: built-in auto-update with changelog shown. npm: `npm update`. Raycast: auto-update from store. | Claude Code: `/plugin marketplace update` and startup auto-update. Already handled by the platform. Document it in each plugin's README. |
| Documentation standard | VS Code: README shown in marketplace; requires good first impression. npm: README.md is the primary artifact. Raycast: description shown in store card. | Each plugin needs its own README.md. The repo-level README is for contributors; the plugin-level README is for users. |

---

## Sources

- Claude Code official plugin documentation: `code.claude.com/docs/en/plugins`, `code.claude.com/docs/en/skills`, `code.claude.com/docs/en/plugin-marketplaces`, `code.claude.com/docs/en/discover-plugins` (verified February 2026)
- Agent Skills open standard: `agentskills.io` and `agentskills.io/specification` (verified February 2026)
- Cursor Marketplace: `cursor.com/marketplace` (verified February 2026, shows Cursor has adopted the SKILL.md plugin system with plugins from Stripe, Figma, Linear, etc.)
- Raycast Store: `raycast.com/store` (verified February 2026)
- VS Code Extension Marketplace: `marketplace.visualstudio.com/vscode` and `code.visualstudio.com/api/references/extension-manifest` (verified February 2026)
- npm package publishing best practices: npm documentation (verified February 2026)
- Current codebase: `.director/codebase/SUMMARY.md`

## Quality Gate

- [x] Must-haves represent genuine user expectations, not aspirational features
- [x] Avoid Building section has at least 2 entries with alternatives
- [x] Priorities reflect user value, not technical interest
- [x] No section left empty
- [x] Plain language throughout
