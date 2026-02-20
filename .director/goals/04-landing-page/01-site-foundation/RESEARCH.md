# Step Research: Site Foundation

**Researched:** 2026-02-20
**Step:** Site foundation
**Domain:** Astro 5 + Tailwind CSS 4 + Cloudflare Pages static site
**Confidence:** HIGH

## Reuse Metadata

_This section is used by the smart reuse check to determine if re-research is warranted. Populate all fields._

- **Step scope:** Initialize an Astro 5 project with Tailwind CSS 4 in `landing-page/` subdirectory, connect to Cloudflare Pages for auto-deploy from GitHub, fully static
- **Locked decisions:** Astro 5 (latest stable), Tailwind CSS 4, Cloudflare Pages (free tier, GitHub auto-deploy), project lives in `landing-page/` subdirectory, zero backend fully static
- **Flexible decisions:** None -- all technology choices are locked
- **Onboarding research used:** Yes -- referenced the note about `@astrojs/tailwind` adapter being deprecated and the need to verify adapter setup, and the Cloudflare Pages static deployment note
- **Inputs checksum:** astro5+tailwind4+cloudflare-pages+monorepo-subdirectory+fully-static

## User Decisions

### Locked (researched deeply)

- **Astro 5 (v5.17.3 latest stable):** Created with `npm create astro@latest`. Project structure: `src/pages/` (file-based routing), `public/` (static assets), `astro.config.mjs`, `tsconfig.json`. Astro 5 ships Vite 6 under the hood. Default output is static (all routes prerendered at build time). Content Layer (new in v5) enables type-safe content collections with loaders -- useful when the plugin catalog page is built in a future step. For a fully static site, no adapter is needed. Build command: `npm run build`, output goes to `dist/`.

- **Tailwind CSS 4:** The `@astrojs/tailwind` integration package is **deprecated** as of Astro 5.2+. The correct approach uses the native `@tailwindcss/vite` Vite plugin. As of Astro 5.2+, running `astro add tailwind` handles setup automatically (installs `tailwindcss` + `@tailwindcss/vite`, wires up the plugin). For Astro 5.2+, the setup steps are: (1) `npm install -D tailwindcss @tailwindcss/vite`, (2) add the Vite plugin to `astro.config.mjs`, (3) create `src/styles/global.css` with `@import "tailwindcss"`, (4) import that CSS file in the layout. No `tailwind.config.js` needed for basic setups -- configuration moves to CSS via `@theme` directive. Breaking changes vs v3: utility renames (e.g., `shadow-sm` -> `shadow-xs`), `!` modifier moves to end of class, ring width default changed to `1px`, border color default changed to `currentColor`.

- **Cloudflare Pages (free tier, GitHub auto-deploy):** Connect GitHub repo in Cloudflare dashboard under Workers & Pages > Create > Pages > Import Git repository. Build settings: build command `npm run build`, build directory `dist`, production branch `main`. Since the project is in a `landing-page/` subdirectory, set the **root directory** to `landing-page` in Cloudflare Pages settings -- Cloudflare Pages supports monorepo subdirectory builds via this setting. No adapter needed for a fully static Astro site. Auto-deploys on every push to `main`. Preview deployments created for every PR. Note: Cloudflare now recommends Workers for new projects, but Pages remains fully supported and is simpler for purely static sites with no serverless functions needed.

- **Monorepo subdirectory (`landing-page/`):** The Astro project lives at `shipfast/landing-page/`. In Cloudflare Pages dashboard, set the root directory to `landing-page` so Cloudflare runs `npm install` and `npm run build` from that subdirectory. No special monorepo tooling (workspaces, turborepo) needed -- the landing page is independent from the rest of the repo.

### Flexible (comparative recommendations)

None -- all technology choices are locked.

### Deferred (not researched)

- **Custom search/filtering UI:** Out of scope per user decision -- static catalog is sufficient at this scale.
- **Backend or database:** Out of scope per user decision -- fully static.

## Recommended Approach

Initialize the Astro 5 project inside `landing-page/` using `npm create astro@latest` (or manually scaffold it). Choose the minimal starter template (empty or minimal) rather than a blog template since the site will be built to spec. Configure TypeScript with the `strict` tsconfig preset.

For Tailwind CSS 4, do NOT install `@astrojs/tailwind` (it is deprecated). Instead install `tailwindcss` and `@tailwindcss/vite` as dev dependencies, then wire the Vite plugin into `astro.config.mjs` and create `src/styles/global.css` with `@import "tailwindcss"`. Import that file in the base layout. This approach eliminates the PostCSS layer and is the officially supported path for Astro 5.2+.

For Cloudflare Pages, push the repo to GitHub (already done), then create a new Pages project in the Cloudflare dashboard. The key non-obvious configuration is setting the **root directory** to `landing-page` so Cloudflare knows to build from the subdirectory rather than the repo root. Build command is `npm run build`, output directory is `dist`. No wrangler CLI setup is required for a purely static site deployed via the dashboard -- the dashboard CI/CD path is simpler than the Wrangler path.

## Stack for This Step

| Library/Tool | Version | Purpose | Why |
|--------------|---------|---------|-----|
| `astro` | ^5.17.3 (latest) | Static site framework | Locked decision; v5 has Content Layer and Vite 6 |
| `tailwindcss` | ^4.x | Utility CSS framework | Locked decision; v4 is CSS-first, no config file needed |
| `@tailwindcss/vite` | ^4.x | Vite plugin for Tailwind 4 | Required peer for Tailwind 4 in Vite/Astro; replaces deprecated @astrojs/tailwind |
| `typescript` | bundled with Astro | Type safety | Astro projects use TypeScript by default |
| Cloudflare Pages | free tier | Hosting + CI/CD | Locked decision; auto-deploys from GitHub |

## Architecture Patterns

### Astro Vite Plugin Integration

**What:** Tailwind 4 integrates via a Vite plugin added directly to `astro.config.mjs`, not as an Astro integration.
**When:** Required for any Astro 5.2+ project using Tailwind 4.
**Example:**
```typescript
// astro.config.mjs
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  vite: {
    plugins: [
      tailwindcss(),
    ],
  },
});
```

### CSS-First Tailwind Configuration

**What:** Tailwind 4 eliminates `tailwind.config.js` for most use cases. Customization happens in CSS via `@theme`.
**When:** Needed when customizing colors, fonts, breakpoints, or other design tokens.
**Example:**
```css
/* src/styles/global.css */
@import "tailwindcss";

@theme {
  --font-sans: "Inter", sans-serif;
  --color-brand: oklch(60% 0.15 250);
  --breakpoint-3xl: 120rem;
}
```

### Astro Base Layout

**What:** A single `Layout.astro` component provides the HTML shell, imports global CSS, and accepts a `title` prop.
**When:** Used by every page to ensure consistent head metadata and global styles.
**Example:**
```astro
---
// src/layouts/Layout.astro
import '../styles/global.css';

interface Props {
  title: string;
}
const { title } = Astro.props;
---
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width" />
    <title>{title}</title>
  </head>
  <body>
    <slot />
  </body>
</html>
```

### Cloudflare Pages Monorepo Root Directory

**What:** Cloudflare Pages allows specifying a root directory so it runs npm commands from a subdirectory of the repo.
**When:** Required when the Astro project is nested inside a monorepo (e.g., `landing-page/`).
**Example:**
```
Cloudflare Pages build settings:
  Root directory:          landing-page
  Build command:           npm run build
  Build output directory:  dist
  Production branch:       main
```

## Don't Hand-Roll

| Problem | Existing Solution | Why Not Build It |
|---------|-------------------|------------------|
| Tailwind CSS integration for Vite | `@tailwindcss/vite` plugin | PostCSS config, class scanning, tree-shaking, source map integration -- all handled; hand-rolling misses these |
| Cloudflare CDN edge caching | Cloudflare Pages built-in | Cache invalidation, global edge distribution, immutable asset hashing -- all automatic |
| Static asset hashing | Astro build pipeline | Astro generates content-hashed filenames for cache busting automatically |

## Pitfalls

### Using the Deprecated @astrojs/tailwind Integration

**What goes wrong:** Installing `@astrojs/tailwind` via `astro add tailwind` in an older workflow or finding tutorials that reference it. The package is deprecated for Tailwind 4. It still works for Tailwind 3 but will not work correctly with Tailwind 4 and will log deprecation warnings.
**How to avoid:** Install `tailwindcss` and `@tailwindcss/vite` directly. Add the Vite plugin to `astro.config.mjs` under `vite.plugins`. Do not add it to the `integrations` array. Verify by checking `package.json` -- you should see `tailwindcss` and `@tailwindcss/vite`, NOT `@astrojs/tailwind`.

### Missing Root Directory Setting in Cloudflare Pages

**What goes wrong:** Cloudflare Pages runs `npm run build` from the repo root (`shipfast/`) where there is no `package.json` with an Astro build script, causing the build to fail.
**How to avoid:** In the Cloudflare Pages project settings, explicitly set the **root directory** to `landing-page`. This is in the "Build configuration" section of the Pages project settings. After changing this setting, trigger a manual redeploy to verify.

### Tailwind v4 Class Name Renames Breaking UI

**What goes wrong:** Using v3 class names that were renamed in v4 (e.g., `shadow-sm` now means a larger shadow than intended; the old `shadow-sm` is now `shadow-xs`). The CSS compiles without errors but renders differently.
**How to avoid:** Reference the v4 rename table during development. Key renames: `shadow-sm` -> `shadow-xs`, `shadow` -> `shadow-sm`, `blur-sm` -> `blur-xs`, `rounded-sm` -> `rounded-xs`, `outline-none` -> `outline-hidden`, `ring` -> `ring-3`. Since this is a new project (not a migration), be aware of these as the current v4 names.

### Forgetting to Import Global CSS in the Layout

**What goes wrong:** Tailwind styles compile but never appear in the browser because the `global.css` file with `@import "tailwindcss"` is not imported anywhere in the component tree.
**How to avoid:** Import `../styles/global.css` (or the path relative to your layout) in `Layout.astro`'s frontmatter. Verify Tailwind is active by adding a test class like `text-red-500` during development.

### Node.js Version Mismatch on Cloudflare Pages

**What goes wrong:** Cloudflare Pages defaults to an older Node.js version that may not meet Astro 5's requirement (Node.js v18.20.8+ required; v20+ recommended). Build fails with Node version errors.
**How to avoid:** Set the `NODE_VERSION` environment variable in Cloudflare Pages project settings to `20` or `22`. This can be done under Settings > Environment variables > Production.

## Code Examples

### Full astro.config.mjs for This Step

```typescript
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  vite: {
    plugins: [
      tailwindcss(),
    ],
  },
});
```

### Minimal package.json for Landing Page Subdirectory

```json
{
  "name": "shipfast-landing",
  "type": "module",
  "scripts": {
    "dev": "astro dev",
    "build": "astro build",
    "preview": "astro preview"
  },
  "dependencies": {
    "astro": "^5.17.3"
  },
  "devDependencies": {
    "@tailwindcss/vite": "^4.0.0",
    "tailwindcss": "^4.0.0"
  }
}
```

### Verification Test After Setup

```bash
# From landing-page/ directory -- confirms Tailwind 4 is wired correctly
npm run build
# Should output: dist/ with CSS containing Tailwind utility classes
# Should NOT output: @tailwind deprecation warnings
```

## Conflicts with User Decisions

| Decision | Conflict | Severity | Recommendation |
|----------|----------|----------|---------------|
| Cloudflare Pages for hosting | Cloudflare now recommends Workers over Pages for new projects | LOW | Pages remains fully supported and is simpler for purely static sites. Workers adds complexity (worker script required) that provides no benefit here. Stay with Pages. |

## Quality Gate

Before considering this file complete, verify:
- [x] Every locked decision has deep investigation findings
- [x] Every flexible area has 2-3 ranked options with tradeoffs (N/A -- no flexible areas)
- [x] Deferred items are listed but NOT researched
- [x] Don't Hand-Roll section present (populated)
- [x] Conflicts section present (populated)
- [x] Reuse Metadata section has all fields populated
- [x] Confidence level reflects actual source quality
