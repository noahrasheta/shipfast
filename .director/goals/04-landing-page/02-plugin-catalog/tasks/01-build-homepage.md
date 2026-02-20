# Task: Build homepage with plugin grid from marketplace.json

## What To Do

Build the homepage for shipfast.cc showing a grid of all available plugins. Import marketplace.json directly using Vite's JSON import (e.g., `import marketplace from '../../.claude-plugin/marketplace.json'`). Each plugin card should display the plugin name, description, author, and a prominent install command. Use Tailwind CSS 4 for layout and styling.

## Why It Matters

The homepage is the first thing visitors see. A clean grid of plugins with clear install commands is the core value proposition of the site -- discover a plugin, install it immediately.

## Size

**Estimate:** medium

Involves Astro page layout, Vite JSON import for data, responsive grid with Tailwind, and plugin card component design. Straightforward but requires attention to visual presentation.

## Done When

- [ ] Homepage displays all plugins from marketplace.json
- [ ] Each plugin card shows name, description, and install command
- [ ] Grid is responsive and looks good on desktop and mobile
- [ ] Plugin cards link to individual detail pages

## Needs First

Needs the Astro site deployed from Step 1.
