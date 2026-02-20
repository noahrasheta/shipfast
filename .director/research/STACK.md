# Stack Research

**Analysis Date:** 2026-02-20
**Confidence:** HIGH

## Recommended Stack

This project has three distinct technical areas, each requiring its own stack recommendation: (1) the existing Claude Code plugin factory, (2) a landing page / plugin showcase site at shipfast.cc, and (3) cross-platform plugin distribution infrastructure.

---

### Area 1: Claude Code Plugin Development (Existing)

The current plugin factory is built on the Claude Code plugin system. This is not a choice -- it is the target platform. The relevant tooling is:

#### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Claude Code Plugin System | 1.0.33+ | Plugin packaging, distribution, marketplace | The platform itself; all plugins must conform to its spec |
| Markdown + YAML frontmatter | N/A | Agent definitions, skill orchestrators | Required format for agents and SKILL.md files |
| Python | 3.11+ | Document processing pipelines, API integrations | Existing investment; strong for file I/O and scripting |
| JSON | N/A | Plugin manifests (`plugin.json`, `marketplace.json`) | Required format per official spec |

#### Plugin Manifest Schema (Current Official Spec)

The official schema as of 2026-02-20 supports these fields in `.claude-plugin/plugin.json`:

```json
{
  "name": "plugin-name",
  "version": "1.2.0",
  "description": "Brief plugin description",
  "author": { "name": "...", "email": "...", "url": "..." },
  "homepage": "https://...",
  "repository": "https://github.com/...",
  "license": "MIT",
  "keywords": ["keyword1", "keyword2"],
  "commands": ["./custom/commands/special.md"],
  "agents": "./custom/agents/",
  "skills": "./custom/skills/",
  "hooks": "./config/hooks.json",
  "mcpServers": "./mcp-config.json",
  "outputStyles": "./styles/",
  "lspServers": "./.lsp.json"
}
```

Key findings from official docs:
- `name` is the only required field if a manifest is included; the manifest itself is optional
- Skills live in `skills/<skill-name>/SKILL.md` -- the directory name becomes the skill name
- Components (commands/, agents/, skills/, hooks/) must be at plugin root, NOT inside `.claude-plugin/`
- `${CLAUDE_PLUGIN_ROOT}` is the only safe way to reference plugin-internal paths in hooks and MCP config
- Plugins are copied to `~/.claude/plugins/cache` on install -- external file references break
- `claude plugin validate .` is the CLI command for validating plugin structure

#### Marketplace Distribution Schema

The official `marketplace.json` supports plugin sources of type: relative path, `github`, `url` (git), `npm`, `pip`. The recommended approach for this repo is the GitHub source type since the marketplace is already GitHub-hosted:

```json
{
  "source": {
    "source": "github",
    "repo": "owner/plugin-repo",
    "ref": "v2.0.0",
    "sha": "full-40-char-sha"
  }
}
```

#### Hook System (Available Events)

The Claude Code hook system supports: `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, `UserPromptSubmit`, `Notification`, `Stop`, `SubagentStart`, `SubagentStop`, `SessionStart`, `SessionEnd`, `TeammateIdle`, `TaskCompleted`, `PreCompact`. Hook types: `command`, `prompt`, `agent`.

#### Supporting Libraries for Plugin Python Code

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| anthropic | >=0.40.0 | Vision API (scanned PDF OCR) | When processing image-based documents |
| google-genai | latest | Gemini image generation | create-image plugin |
| pdfplumber | latest | Native PDF text extraction | When PDFs have selectable text |
| openpyxl | latest | Excel file reading | When processing .xlsx files |
| python-docx | latest | Word document parsing | When processing .docx files |
| python-pptx | latest | PowerPoint parsing | When processing .pptx files |
| pytest | >=8.0.0 | Testing converter modules | All Python converter tests |

---

### Area 2: Landing Page / Plugin Showcase (shipfast.cc)

This is a greenfield addition. The site needs to: showcase plugins, explain what each does, provide installation instructions, and potentially serve as a library catalog.

#### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Astro | 5.x | Static site framework | Best-in-class for content/showcase sites; zero JS by default; content collections for plugin catalog management; 5x faster builds than v4 for Markdown-heavy sites |
| Tailwind CSS | 4.x | Styling | Zero-runtime utility CSS; fastest path to polished design without custom CSS; works natively with Astro |
| Cloudflare Pages | N/A | Hosting | Free tier has unlimited bandwidth and static requests; 500 builds/month; auto-deploys from GitHub; edge network for fast global delivery |

**Why Astro over Next.js:** Next.js 16 is the right choice when you need server-side rendering, API routes, or complex interactivity. A plugin showcase/library site is content-driven and primarily static. Astro produces smaller bundles, ships zero JavaScript by default, and has first-class support for content collections -- exactly what a plugin catalog needs. Next.js would be overkill here.

**Why Cloudflare Pages over Vercel/Netlify:** Cloudflare's free tier has no bandwidth cap and no seat limits, making it ideal for a solo developer with potentially viral traffic. Vercel's free tier limits bandwidth to 100GB/month and adds function execution costs. Netlify's free tier limits builds to 300/month. Cloudflare Pages at 500 builds/month with unlimited bandwidth is the clear winner for this use case.

#### Supporting Libraries for the Site

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| @astrojs/mdx | latest | MDX support for rich plugin docs | When plugin pages need interactive components mixed into docs |
| @astrojs/sitemap | latest | Auto-generates sitemap.xml | For SEO on plugin pages |
| @astrojs/tailwind | latest | Astro-Tailwind integration | Required adapter for Tailwind v4 + Astro |
| shiki | latest | Syntax highlighting | For displaying plugin SKILL.md and manifest code examples |

#### Astro Content Collections for Plugin Catalog

Use Astro's Content Collections to manage plugin data in a type-safe way:

```
src/
├── content/
│   └── plugins/
│       ├── create-image.md
│       └── dc-due-diligence.md
└── pages/
    └── plugins/
        └── [slug].astro
```

This approach makes adding new plugins a matter of dropping a Markdown file -- no code changes needed.

---

### Area 3: Cross-Platform Plugin Distribution

This is future-state. The user wants plugins on Cursor and OpenCode eventually.

#### Platform Comparison

| Platform | Extension Format | Distribution | Compatibility with Claude Code Plugins |
|----------|-----------------|--------------|----------------------------------------|
| Claude Code | Markdown agents + SKILL.md + plugin.json | GitHub marketplace catalog | Source of truth |
| Cursor | `.cursor/rules/*.md` or `.mdc` files with YAML frontmatter | GitHub repo sharing or remote rules import | PARTIAL -- agent Markdown content is reusable; packaging format differs |
| OpenCode | JavaScript/TypeScript npm packages with hook functions | npm packages or local files in `.opencode/plugins/` | LOW -- fundamentally different architecture (JS hooks vs Markdown agents) |

**Key finding:** There is no universal plugin format. Claude Code and Cursor both use Markdown files with YAML frontmatter, making content reuse feasible. OpenCode uses JS/TS modules. A multi-platform strategy requires separate packaging for OpenCode.

**Recommended cross-platform approach:**
- Keep Claude Code plugin format as the canonical source
- For Cursor: extract agent content into `.cursor/rules/` format (thin adapter layer -- mostly copy/paste with frontmatter adjustment)
- For OpenCode: write thin JS wrapper plugins that call the same underlying logic or provide equivalent AGENTS.md instructions
- Do NOT try to unify all formats into one abstraction -- the overhead exceeds the benefit at this project's scale

---

### Area 4: CI/CD and Automation

#### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| `claude plugin validate .` | Validate plugin manifest structure | Built into Claude Code CLI; run before every release |
| GitHub Actions | CI/CD automation | Already configured in `.github/workflows/`; free for public repos |
| `claude --plugin-dir ./<plugin>` | Local development testing | Load plugin without marketplace install; supports multiple `--plugin-dir` flags |
| pytest | Python converter testing | Already configured; run with `cd dc-due-diligence && python -m pytest tests/` |

#### Existing GitHub Actions Workflows

Two workflows already exist:
- `claude-code-review.yml` -- Uses `anthropics/claude-code-action@v1` to run automated code review on PRs via Claude Code
- `claude.yml` -- Responds to `@claude` mentions in issues and PR comments using the same action

#### Recommended CI Additions for Plugin Validation

```yaml
# Suggested addition: .github/workflows/validate-plugins.yml
name: Validate Plugins
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Claude Code
        run: npm install -g @anthropic-ai/claude-code
      - name: Validate create-image plugin
        run: claude plugin validate ./create-image
      - name: Validate dc-due-diligence plugin
        run: claude plugin validate ./dc-due-diligence
      - name: Run Python tests
        run: cd dc-due-diligence && python -m pytest tests/ -v
```

## Installation

```bash
# Astro landing page setup
npm create astro@latest shipfast-site -- --template minimal
cd shipfast-site
npx astro add tailwind
npx astro add mdx
npx astro add sitemap

# Local plugin development testing
claude --plugin-dir ./create-image
claude --plugin-dir ./dc-due-diligence

# Plugin validation
claude plugin validate ./create-image
claude plugin validate ./dc-due-diligence

# Python test suite
cd dc-due-diligence && python -m pytest tests/ -v

# Cloudflare Pages: connect via GitHub integration in Cloudflare dashboard
# Build command: npm run build
# Output directory: dist/
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Astro | Next.js | If the site needs user accounts, dynamic search, or server-rendered plugin stats |
| Astro | Hugo | If the team prefers Go and wants even faster builds with zero Node.js dependency |
| Astro | Docusaurus | If the primary use case is documentation rather than showcasing |
| Cloudflare Pages | Vercel | If Next.js is chosen (Vercel has better Next.js-specific optimization) |
| Cloudflare Pages | Netlify | If form handling or serverless functions are needed immediately |
| Cloudflare Pages | GitHub Pages | GitHub Pages is free but has no CDN edge optimization and limited build flexibility |
| GitHub Marketplace | npm distribution | If Claude Code ever supports npm plugin sources more fully (it's listed but flagged as "not yet fully implemented") |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Hardcoded absolute paths in agent Markdown files | Plugins are copied to `~/.claude/plugins/cache` on install; absolute paths break | `${CLAUDE_PLUGIN_ROOT}` variable for all plugin-internal references |
| `../shared-utils` style paths in plugin files | Plugin cache copy does not follow parent directory references | Symlinks within plugin directory (honored during cache copy) |
| Next.js for the showcase site | Brings SSR complexity, heavier deployment, and framework lock-in for what is a content site | Astro with static generation |
| npm plugin source type in marketplace.json | Official docs flag this as "not yet fully implemented" | `github` or relative path sources |
| Raising exceptions in Python converter `convert()` methods | Breaks the pipeline; agents receive no graceful error signal | Return `ExtractionResult(success=False)` |
| Omitting version bumps when updating plugin code | Claude Code uses version to determine update eligibility; unchanged version means users never get updates | Bump `version` in `plugin.json` with every meaningful change |

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| anthropic>=0.40.0 | claude-sonnet-4-20250514 | Loose pin is a stability risk; consider pinning to specific minor version |
| google-genai (latest) | Gemini 3 Pro | No lockfile present; version drift risk |
| Claude Code 1.0.33+ | Plugin system skills/agents/hooks | Version 1.0.33 is the minimum for `/plugin` command support |
| Astro 5.x | Tailwind CSS 4.x | Use `@astrojs/tailwind` adapter; Tailwind v4 has different config format than v3 |
| Astro 5.x | Node.js 18+ | Astro 5 requires Node.js 18 or higher |
| Python 3.11+ | pdfplumber, openpyxl, python-docx, python-pptx | All tested against 3.11+; no known conflicts |

## Sources

- `https://code.claude.com/docs/en/plugins` -- Official Claude Code plugin creation docs (HIGH confidence, verified Feb 2026)
- `https://code.claude.com/docs/en/plugin-marketplaces` -- Official marketplace creation and distribution docs (HIGH confidence, verified Feb 2026)
- `https://code.claude.com/docs/en/plugins-reference` -- Complete plugin manifest schema and CLI reference (HIGH confidence, verified Feb 2026)
- `https://astro.build/blog/astro-5/` -- Astro 5.0 release blog, Dec 2024 (HIGH confidence)
- `https://nextjs.org/docs` -- Next.js 16 docs (HIGH confidence, verified Feb 2026)
- `https://pages.cloudflare.com/` -- Cloudflare Pages features and free tier (HIGH confidence, verified Feb 2026)
- `https://tailwindcss.com/docs/installation` -- Tailwind CSS v4.2 docs (HIGH confidence, verified Feb 2026)
- `https://opencode.ai/docs/plugins/` -- OpenCode plugin system (MEDIUM confidence, verified Feb 2026)
- `https://cursor.com/docs/context/rules` -- Cursor rules format (MEDIUM confidence, verified Feb 2026)
- `/Users/noahrasheta/Dev/GitHub/shipfast/.github/workflows/` -- Existing CI workflows (HIGH confidence, read directly)
- `/Users/noahrasheta/Dev/GitHub/shipfast/.director/codebase/SUMMARY.md` -- Codebase analysis (HIGH confidence)

## Quality Gate

Before considering this file complete, verify:
- [x] Every recommendation includes a rationale
- [x] Specific version numbers included for core technologies
- [x] Alternatives mentioned for major recommendations
- [x] "What NOT to Use" section populated with at least 2 entries
- [x] Sources include links or tool references for verification
- [x] Confidence level reflects actual source quality
