# Step 1: Site foundation

## What This Delivers

A working Astro 5 site with Tailwind CSS 4 styling, deployed to Cloudflare Pages at shipfast.cc. The site builds and deploys automatically from GitHub on every push to the landing-page/ directory.

## Tasks

- [ ] Task 1: Initialize Astro 5 + Tailwind CSS 4 project and deploy to Cloudflare Pages

## Needs First

Needs plugin READMEs from Goal 3 -- the site renders README content, so the content needs to exist first.

## Decisions

### Locked
- Astro 5 for static site generation -- zero JS by default, content-focused
- Tailwind CSS 4 for styling -- use @tailwindcss/vite plugin directly (the @astrojs/tailwind adapter is deprecated)
- Cloudflare Pages for hosting -- free tier, auto-deploys from GitHub, global CDN
- Project lives in landing-page/ subdirectory of the monorepo
- Set NODE_VERSION=20 in Cloudflare Pages environment variables
- Fully static output -- no SSR adapter needed

### Deferred
- Custom search/filtering UI
- Backend or database
- Plugin ratings or reviews
