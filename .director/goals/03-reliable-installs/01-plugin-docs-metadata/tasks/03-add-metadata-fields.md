# Task: Add argument-hint and metadata fields to skills and manifests

## What To Do

Add `argument-hint` fields to all user-invocable skill frontmatter (e.g., `argument-hint: "<folder-path>"` for due-diligence, `argument-hint: "<image description>"` for create-image). Add `homepage` and `repository` fields to both plugin manifests pointing to the GitHub repo and future shipfast.cc pages.

## Why It Matters

Argument hints show up in Claude Code's autocomplete when users type the skill command, dramatically improving discoverability. Homepage and repository fields help users find documentation and report issues.

## Size

**Estimate:** small

Adding a few YAML fields to existing files. Quick and mechanical.

## Done When

- [ ] All user-invocable skills have argument-hint in frontmatter
- [ ] Both plugin.json manifests include homepage and repository fields
- [ ] Fields use correct format per Claude Code plugin spec

## Needs First

Nothing -- this can start right away.
