# Step 3: CI validation

## What This Delivers

A GitHub Actions workflow that runs on every push: validates plugin structure with `claude plugin validate`, runs Python tests, and checks that marketplace.json stays in sync with the actual plugin directories. Problems get caught before they reach users.

## Tasks

- [ ] Task 1: Create GitHub Actions validation workflow
- [ ] Task 2: Add marketplace.json consistency check

## Needs First

Needs READMEs and lockfile from Steps 1 and 2, since CI should validate the complete plugin state.
