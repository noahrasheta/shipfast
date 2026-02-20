# Task: Build individual plugin pages from READMEs with install commands

## What To Do

Create dynamic plugin detail pages using Astro's `getStaticPaths()`. Each page renders the plugin's README.md content as HTML using `marked.parse()` with `@tailwindcss/typography` (`prose` class) for styling. Include the install command prominently at the top with a copy-to-clipboard button (plain `<script>` with `navigator.clipboard.writeText()` -- no client framework needed).

## Why It Matters

Detail pages give users the full picture of what a plugin does before installing. Rendering from READMEs means the site stays in sync with the source of truth -- update the README, and the site updates on next build.

## Size

**Estimate:** medium

Dynamic routing with getStaticPaths, markdown parsing with marked, typography plugin setup, and copy-to-clipboard functionality. Multiple pieces that need to work together.

## Done When

- [ ] Each plugin has a detail page at a clean URL (e.g., /plugins/dc-due-diligence)
- [ ] README content renders as styled HTML with proper typography
- [ ] Install command is prominent at the top of each page
- [ ] Copy-to-clipboard button works for the install command
- [ ] Pages are statically generated at build time

## Needs First

Needs the homepage built from the previous task.
