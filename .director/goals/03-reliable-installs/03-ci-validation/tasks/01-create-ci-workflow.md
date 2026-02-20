# Task: Create GitHub Actions validation workflow

## What To Do

Create a `.github/workflows/validate-plugins.yml` workflow that runs on every push and pull request. The workflow should: run `claude plugin validate` for each plugin directory, execute the Python test suite with pytest, and verify that all plugin dependencies install correctly from their lockfiles.

## Why It Matters

CI catches broken manifests, failing tests, and dependency issues before they reach users. Without it, the only validation is manual testing, which is easy to skip.

## Size

**Estimate:** medium

GitHub Actions YAML with multiple jobs (validation, testing, dependency check). Needs to handle the Python venv setup for the dc-due-diligence tests.

## Done When

- [ ] Workflow file exists at .github/workflows/validate-plugins.yml
- [ ] Runs on push and pull request events
- [ ] Validates each plugin with claude plugin validate
- [ ] Runs Python tests with pytest
- [ ] Workflow passes on the current state of the repo

## Needs First

Needs READMEs and lockfile from Steps 1 and 2, so CI validates the complete plugin state.
