# Task: Initialize Astro 5 + Tailwind CSS 4 project and deploy to Cloudflare Pages

## What To Do

Scaffold an Astro 5 project in the `landing-page/` directory using `npm create astro@latest`. Add Tailwind CSS 4 using the `@tailwindcss/vite` plugin (not the deprecated `@astrojs/tailwind` adapter). Configure Cloudflare Pages deployment from GitHub with the root directory set to `landing-page/` and `NODE_VERSION=20` in environment variables. Deploy a minimal "coming soon" page to verify the build and deploy pipeline works end to end.

## Why It Matters

Getting the foundation deployed early means every subsequent change to the site can be previewed immediately. Starting with a working deploy pipeline prevents "it works locally but not in production" surprises later.

## Size

**Estimate:** medium

Project scaffolding is quick, but Tailwind 4 integration has changed significantly from v3 (use @tailwindcss/vite, not @astrojs/tailwind). Cloudflare Pages monorepo setup requires configuring the root directory correctly. Need to verify the full build-deploy cycle works.

## Done When

- [ ] Astro 5 project initialized in landing-page/ directory
- [ ] Tailwind CSS 4 integrated via @tailwindcss/vite plugin
- [ ] Site builds successfully with `npm run build`
- [ ] Cloudflare Pages configured with root directory = landing-page/ and NODE_VERSION=20
- [ ] Minimal page deployed and accessible at shipfast.cc (or preview URL)

## Needs First

Needs plugin READMEs from Goal 3, since the site will render README content.
