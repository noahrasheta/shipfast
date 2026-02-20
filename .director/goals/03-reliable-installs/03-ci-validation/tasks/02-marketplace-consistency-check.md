# Task: Add marketplace.json consistency check

## What To Do

Add a step to the CI workflow (or a standalone script it calls) that verifies marketplace.json stays in sync with the actual plugin directories. It should check that every plugin directory has an entry in marketplace.json, and every marketplace.json entry points to a real plugin directory.

## Why It Matters

The three-files-must-sync problem (marketplace.json, CLAUDE.md, README.md) is currently enforced only by a checklist. Automated checking for at least the most critical file (marketplace.json) prevents broken installs from reaching users.

## Size

**Estimate:** small

A shell script or Python script that compares directory names against marketplace.json entries. Straightforward logic.

## Done When

- [ ] Script checks that every plugin directory has a marketplace.json entry
- [ ] Script checks that every marketplace.json entry has a matching directory
- [ ] CI workflow runs the consistency check
- [ ] Check fails with a clear error message if entries are out of sync

## Needs First

Needs the CI workflow set up from the previous task.
