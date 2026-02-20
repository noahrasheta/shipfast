# Step 2: Plugin catalog

## What This Delivers

The homepage shows a grid of all available plugins pulled from marketplace.json at build time. Each plugin has its own detail page rendered from its README, with a prominent install command and copy button. Adding a new plugin to the marketplace automatically adds it to the site on the next build.

## Tasks

- [ ] Task 1: Build homepage with plugin grid from marketplace.json
- [ ] Task 2: Build individual plugin pages from READMEs with install commands

## Needs First

Needs the Astro site deployed from Step 1.

## Decisions

### Locked
- Plugin data comes from marketplace.json at build time via direct JSON import
- Individual plugin pages render README content as HTML
- Install commands displayed prominently with copy-to-clipboard functionality
- Static generation only -- no client-side data fetching

### Flexible
- Data loading approach -- research recommends direct Vite JSON import over content collections since the current marketplace.json lacks the `id` field content collections require; use `marked` for README-to-HTML conversion with `@tailwindcss/typography` for styling

### Deferred
- Search and filtering UI
- Plugin ratings or reviews
- Plugin submission form for external contributors
