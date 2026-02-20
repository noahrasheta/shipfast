# Step Research: Plugin Catalog

**Researched:** 2026-02-20
**Step:** Plugin catalog
**Domain:** Astro 5 static data loading, dynamic routing, Markdown rendering, copy-to-clipboard
**Confidence:** HIGH

## Reuse Metadata

_This section is used by the smart reuse check to determine if re-research is warranted. Populate all fields._

- **Step scope:** Homepage with plugin grid from marketplace.json, and individual plugin detail pages rendering each plugin's README with prominent install commands
- **Locked decisions:** Astro 5 framework, marketplace.json as data source at build time, plugin READMEs as content for detail pages, static generation only, install commands with copy functionality
- **Flexible decisions:** Astro content collections (file() loader) vs. direct JSON import / fs.readFileSync for loading marketplace.json
- **Onboarding research used:** Yes -- STACK.md (Astro 5 + Tailwind 4 + Cloudflare Pages section), ARCHITECTURE.md (Static Site Plugin Catalog pattern)
- **Inputs checksum:** step=plugin-catalog, locked=astro5+json+static, flexible=data-loading-approach

## User Decisions

### Locked (researched deeply)

- **Astro 5 + static generation:** Astro 5 produces fully static HTML by default (zero JS runtime). `getStaticPaths()` in `[slug].astro` files generates one HTML file per plugin at build time. No server adapter is needed for Cloudflare Pages deployment -- the `@astrojs/cloudflare` adapter is only required for SSR. Build command: `npm run build`, output dir: `dist/`. The Astro build process runs on the developer's machine / CI, so Node.js `fs` module (with `node:fs` prefix) is fully available at build time with no Cloudflare runtime restrictions.

- **marketplace.json as data source:** The existing file at `.claude-plugin/marketplace.json` contains a `plugins` array with `name`, `source`, and `description` per plugin. Each entry's `source` is a relative directory path (e.g., `./create-image`). The landing page site will live in a `landing-page/` subdirectory, making the marketplace path `../.claude-plugin/marketplace.json` relative to the site root. Both direct import and `fs.readFileSync` can reach this file at build time.

- **Plugin READMEs as page content:** Each plugin directory has a `README.md` (confirmed: `create-image/README.md` exists; `dc-due-diligence/README.md` is implied by conventions). The site must read these files at build time and render them as HTML. Astro's internal Markdown processor does not render arbitrary strings -- only files in `src/` via content collections or imported `.md` files. The correct approach for rendering external Markdown strings is `marked.parse()` (synchronous, returns HTML string) combined with Astro's `set:html` directive or `<Fragment set:html={html} />` to inject the rendered HTML safely.

- **Install commands with copy functionality:** The install command for each plugin is `/plugin install {name}@shipfast`. Copy-to-clipboard requires a small amount of JavaScript since it uses the browser's `navigator.clipboard.writeText()` API. Astro ships zero JS by default -- a single `<script>` tag in the component is the correct pattern (no framework needed). The script targets buttons by `data-copy` attributes to avoid coupling to CSS classes.

- **Tailwind CSS 4 + Astro 5:** The `@astrojs/tailwind` integration is deprecated. The current approach uses `@tailwindcss/vite` (the official Tailwind Vite plugin). Run `npx astro add tailwind` in Astro 5.2.0+ to set it up automatically -- this installs `@tailwindcss/vite` and adds `@import "tailwindcss"` to a global CSS file. For styling rendered Markdown (README content), add `@tailwindcss/typography` and apply the `prose` class to the wrapper element: `<div class="prose prose-slate max-w-none">`.

- **@tailwindcss/typography for README rendering:** For Tailwind v4, install with `npm install -D @tailwindcss/typography` and add `@plugin "@tailwindcss/typography"` to the global CSS file (after `@import "tailwindcss"`). Apply `prose` and modifier classes (`prose-slate`, `prose-invert` for dark mode) to the container wrapping rendered README HTML.

### Flexible (comparative recommendations)

- **Data loading approach for marketplace.json:** Recommend **direct JSON import via Vite** because it is the simplest path for this use case. The marketplace.json lives outside `src/`, but Vite supports importing arbitrary JSON using `import data from '../../.claude-plugin/marketplace.json'` -- Vite resolves relative paths from the importing file, not from `src/`. This is zero-configuration, type-checkable with TypeScript, and requires no schema definition. The data becomes available as a plain JS object at build time. For the README files (one per plugin, path derived from marketplace.json), use `node:fs` + `node:path` + `import.meta.url` to read them at build time inside `getStaticPaths()`.

  Alternative 1 -- **Astro content collections with `file()` loader:** The `file()` loader accepts a path relative to the project root. It would require copying or symlinking `marketplace.json` into the `src/content/` structure, or referencing it as `../../.claude-plugin/marketplace.json`. Each plugin entry must have a unique `id` field -- the current marketplace.json uses `name` not `id`, requiring either a schema transform or a file mutation. Benefit: type-safe schema validation via Zod, `getCollection()` API. Downside: extra configuration overhead (content.config.ts, Zod schema) for a two-entry catalog. Not worth it at this scale.

  Alternative 2 -- **`fs.readFileSync` in `getStaticPaths()`:** More explicit than Vite import; necessary for reading README.md files anyway. Could be used for marketplace.json too. Slight disadvantage: no build-time bundling optimization (Vite import is tree-shaken and cached; `fs` read is not). Acceptable, but prefer Vite import for the JSON and reserve `fs` for the dynamic README reads.

### Deferred (not researched)

- **Search and filtering UI:** out of scope per user decision
- **Plugin ratings or reviews:** out of scope per user decision
- **Plugin submission form:** out of scope per user decision

## Recommended Approach

Build the homepage as a simple Astro page (`src/pages/index.astro`) that imports `marketplace.json` directly via Vite's native JSON import. The plugin grid maps over the `plugins` array to render a card component for each plugin. Each card shows the plugin name, description, and a copy-to-clipboard install command button. Keep the card as a pure Astro component (`.astro`) with no client framework needed -- a single `<script>` tag in the layout handles the clipboard API.

For individual plugin pages, use `src/pages/plugins/[slug].astro` with a `getStaticPaths()` function. This function imports marketplace.json, then uses `node:fs` and `node:path` to read each plugin's `README.md` file from the monorepo root (one level up from the `landing-page/` directory). Parse the README string with `marked.parse()` to produce HTML. Pass both the plugin metadata and the rendered HTML as props to the page component. Render the HTML using `<div class="prose prose-slate max-w-none" set:html={readmeHtml} />`.

Build the install command copy button with a plain `data-copy` attribute pattern and a `<script>` tag that uses `navigator.clipboard.writeText()`. No React, no Vue, no Alpine -- one event listener on the document using event delegation. Style everything with Tailwind utility classes; apply `@tailwindcss/typography` for the README prose rendering. Deploy to Cloudflare Pages with no adapter: `npm run build` outputs to `dist/`, connect the repository in the Cloudflare dashboard.

## Stack for This Step

| Library/Tool | Version | Purpose | Why |
|--------------|---------|---------|-----|
| astro | 5.x | Static site framework and routing | Locked decision; handles `getStaticPaths()`, file-based routing, build pipeline |
| @tailwindcss/vite | 4.x | Tailwind CSS integration via Vite plugin | Replaces deprecated `@astrojs/tailwind`; `npx astro add tailwind` installs automatically |
| @tailwindcss/typography | latest | Prose styling for rendered README HTML | Adds `prose` class that makes vanilla Markdown HTML look correct without custom CSS |
| marked | 15.x | Markdown-to-HTML rendering of README files | Synchronous `marked.parse()` works in `getStaticPaths()` server context; no config needed |
| node:fs, node:path | built-in | Read README.md files from monorepo at build time | Needed to traverse `../plugin-name/README.md` paths; runs only at build time |

## Architecture Patterns

### Static Plugin Grid from JSON Import

**What:** The homepage imports `marketplace.json` at the top of the frontmatter using a Vite JSON import. The `plugins` array is iterated to render PluginCard components.
**When:** Any Astro page that needs static data from a JSON file at build time.
**Example:**
```astro
---
// src/pages/index.astro
import marketplace from '../../.claude-plugin/marketplace.json';

const plugins = marketplace.plugins;
---
<main>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
    {plugins.map(plugin => (
      <a href={`/plugins/${plugin.name}`} class="border rounded-lg p-6 hover:shadow-md transition">
        <h2 class="text-xl font-bold">{plugin.name}</h2>
        <p class="text-gray-600 mt-2">{plugin.description}</p>
        <div class="mt-4 font-mono text-sm bg-gray-100 rounded px-3 py-2">
          /plugin install {plugin.name}@shipfast
        </div>
      </a>
    ))}
  </div>
</main>
```

### Dynamic Plugin Pages with getStaticPaths

**What:** A single `[slug].astro` file generates one HTML page per plugin. `getStaticPaths()` reads marketplace.json, finds each plugin's README.md path, reads and parses it, then passes metadata and rendered HTML as props.
**When:** Any content derived from a data source that varies per route.
**Example:**
```astro
---
// src/pages/plugins/[slug].astro
import { marked } from 'marked';
import fs from 'node:fs';
import path from 'node:path';
import marketplace from '../../../.claude-plugin/marketplace.json';

export async function getStaticPaths() {
  // Resolve the monorepo root (two levels up from landing-page/src/pages/)
  const repoRoot = path.resolve(process.cwd(), '..');

  return marketplace.plugins.map((plugin) => {
    const readmePath = path.join(repoRoot, plugin.source.replace('./', ''), 'README.md');
    let readmeHtml = '<p>No README available.</p>';
    try {
      const raw = fs.readFileSync(readmePath, 'utf-8');
      readmeHtml = marked.parse(raw) as string;
    } catch {
      // README not found -- use fallback
    }

    return {
      params: { slug: plugin.name },
      props: { plugin, readmeHtml },
    };
  });
}

const { plugin, readmeHtml } = Astro.props;
const installCommand = `/plugin install ${plugin.name}@shipfast`;
---
<main class="max-w-4xl mx-auto px-4 py-12">
  <h1 class="text-3xl font-bold">{plugin.name}</h1>
  <p class="text-gray-600 mt-2">{plugin.description}</p>

  <!-- Install command with copy button -->
  <div class="flex items-center gap-3 mt-6 bg-gray-100 rounded-lg px-4 py-3">
    <code class="font-mono text-sm flex-1">{installCommand}</code>
    <button data-copy={installCommand} class="text-sm px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700">
      Copy
    </button>
  </div>

  <!-- README rendered as prose -->
  <div class="prose prose-slate max-w-none mt-10" set:html={readmeHtml} />
</main>

<script>
  // Copy-to-clipboard: event delegation, no framework needed
  document.addEventListener('click', (e) => {
    const btn = (e.target as HTMLElement).closest('[data-copy]');
    if (!btn) return;
    const text = btn.getAttribute('data-copy') ?? '';
    navigator.clipboard.writeText(text).then(() => {
      const orig = btn.textContent;
      btn.textContent = 'Copied!';
      setTimeout(() => { btn.textContent = orig; }, 1500);
    });
  });
</script>
```

### Tailwind Typography for Prose

**What:** The `@tailwindcss/typography` plugin adds a `prose` class that applies opinionated typographic defaults to HTML rendered from Markdown. This avoids writing custom CSS for headings, code blocks, lists, and links inside README content.
**When:** Any container wrapping arbitrary HTML generated from Markdown.
**Example:**
```css
/* src/styles/global.css */
@import "tailwindcss";
@plugin "@tailwindcss/typography";
```
```html
<!-- In a .astro component -->
<div class="prose prose-slate prose-lg max-w-none dark:prose-invert" set:html={readmeHtml} />
```

## Don't Hand-Roll

| Problem | Existing Solution | Why Not Build It |
|---------|-------------------|------------------|
| Markdown-to-HTML conversion | `marked` package | Handles GFM (GitHub-Flavored Markdown) -- tables, task lists, fenced code blocks, auto-linking. Rolling your own breaks on edge cases in existing READMEs. |
| Prose typography for rendered HTML | `@tailwindcss/typography` (`prose` class) | Heading hierarchy, code block styling, list indentation, and link colors are non-trivial to get right across all Markdown elements. The plugin handles all of them with one class. |
| Clipboard API fallback | None needed -- `navigator.clipboard` is baseline modern | Do not implement a `document.execCommand('copy')` fallback; it is deprecated. The `navigator.clipboard` API has 96%+ browser support and works in all browsers that matter for this audience. |
| Syntax highlighting in READMEs | Shiki (Astro built-in via remark-shiki) | README code blocks need readable highlighting. `marked` alone produces plain `<code>` blocks. If highlighting matters, use `marked-highlight` with Shiki instead of rolling a custom highlighter. |

## Pitfalls

### process.cwd() varies by how the build is invoked

**What goes wrong:** When Astro runs a build, `process.cwd()` resolves to the directory where the build command was executed -- typically the `landing-page/` directory if that is where `npm run build` runs. If CI or Cloudflare Pages runs the build from the repo root, `process.cwd()` will differ, breaking relative paths like `../../.claude-plugin/marketplace.json`.

**How to avoid:** In `getStaticPaths()`, use `import.meta.url` to get the current file's absolute path, then traverse to the repo root from there. This is stable regardless of where the build runs:
```js
const thisFile = new URL(import.meta.url).pathname;
// thisFile = .../landing-page/src/pages/plugins/[slug].astro
const repoRoot = path.resolve(path.dirname(thisFile), '../../../../');
```
Alternatively, define the repo root in `astro.config.mjs` using `import.meta.dirname` and pass it as a build constant.

### marked returns string | Promise<string> depending on async option

**What goes wrong:** In older marked versions (before v5), `marked.parse()` could return a Promise if the async option was set. In current marked (v15+), `marked.parse()` returns a string synchronously by default. TypeScript may still infer the return type as `string | Promise<string>`, causing a type error when passing to `set:html`.

**How to avoid:** Cast the return value explicitly: `const html = marked.parse(raw) as string;`. Or use `await marked.parse(raw)` inside an async `getStaticPaths()` function -- both work since `getStaticPaths` supports async.

### @tailwindcss/tailwind vs @tailwindcss/vite: wrong package

**What goes wrong:** Following outdated tutorials that say `npm install @astrojs/tailwind` leads to installing a deprecated package. Astro 5.x will warn that `@astrojs/tailwind` is deprecated, but the project may silently build with an older Tailwind v3 config format, causing Tailwind v4 utilities to be missing.

**How to avoid:** Run `npx astro add tailwind` in the `landing-page/` directory. This installs `@tailwindcss/vite` (the current method) automatically. Do NOT add `@astrojs/tailwind` manually.

### Content Collections file() loader requires id field

**What goes wrong:** If the team decides to use Astro Content Collections for marketplace.json instead of a direct import, the `file()` loader requires each entry to have a unique `id` property. The current `marketplace.json` uses `name`, not `id`. Attempting to load without an `id` field will throw a validation error during build.

**How to avoid:** Either stick with the recommended direct Vite JSON import (no `id` requirement), or add an `id` field to each plugin entry in `marketplace.json` before switching to content collections.

### Rendering README from wrong path when source has ./ prefix

**What goes wrong:** The marketplace.json `source` values are `"./create-image"` and `"./dc-due-diligence"`. Using `plugin.source` directly in a path join without stripping the `./` prefix can produce double-relative paths on some platforms (e.g., `path.join(repoRoot, './create-image', 'README.md')` -- this actually works in Node.js `path.join`, but the `./` creates confusion when debugging).

**How to avoid:** Strip the `./` prefix explicitly: `plugin.source.replace(/^\.\//, '')`, or use `path.resolve()` instead of `path.join()` for the full path construction. `path.resolve(repoRoot, plugin.source, 'README.md')` handles the `./` correctly.

### Navigator.clipboard requires HTTPS

**What goes wrong:** `navigator.clipboard.writeText()` only works in secure contexts (HTTPS or localhost). If someone previews the site over HTTP (rare with Cloudflare Pages but possible during local dev via plain HTTP), the copy button silently fails or throws a `TypeError`.

**How to avoid:** Guard the call: `if (navigator.clipboard) { navigator.clipboard.writeText(text)... }`. During local Astro dev (`npx astro dev`), the dev server runs on localhost which is treated as a secure context, so this is a non-issue in practice.

## Code Examples

### Astro.config.mjs with Tailwind v4

```js
// landing-page/astro.config.mjs
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  vite: {
    plugins: [tailwindcss()],
  },
});
```

### Global CSS with Typography Plugin

```css
/* landing-page/src/styles/global.css */
@import "tailwindcss";
@plugin "@tailwindcss/typography";
```

### Resolving Repo Root from a Page File (stable path pattern)

```js
// In getStaticPaths() inside landing-page/src/pages/plugins/[slug].astro
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
// __dirname = .../landing-page/src/pages/plugins
// Navigate up 4 levels: plugins/ -> pages/ -> src/ -> landing-page/ -> repo root
const repoRoot = path.resolve(__dirname, '../../../../');
```

## Conflicts with User Decisions

| Decision | Conflict | Severity | Recommendation |
|----------|----------|----------|---------------|
| Astro + Tailwind 4 via `@astrojs/tailwind` | `@astrojs/tailwind` is deprecated as of Astro 5.x; the package no longer works with Tailwind v4 | MEDIUM | Use `@tailwindcss/vite` instead. Run `npx astro add tailwind` to set it up correctly. The onboarding STACK.md mentions `@astrojs/tailwind` as a supporting library -- that recommendation is now outdated. |

## Quality Gate

Before considering this file complete, verify:
- [x] Every locked decision has deep investigation findings
- [x] Every flexible area has 2-3 ranked options with tradeoffs
- [x] Deferred items are listed but NOT researched
- [x] Don't Hand-Roll section present (populated)
- [x] Conflicts section present (populated -- @astrojs/tailwind deprecation)
- [x] Reuse Metadata section has all fields populated
- [x] Confidence level reflects actual source quality
