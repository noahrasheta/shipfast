# Task: Update setup script to install from lockfile

## What To Do

Update the setup script to install Python dependencies from the requirements.txt lockfile (generated in Goal 1) instead of the loose `>=` pins in pyproject.toml. Keep pyproject.toml for development flexibility but use the lockfile for reproducible user installs.

## Why It Matters

Without this change, the lockfile exists but isn't used -- new users still get unpredictable dependency versions. The setup script is the entry point for every new install, so it must use the pinned versions.

## Size

**Estimate:** small

Change one install command in the setup script to reference requirements.txt.

## Done When

- [ ] Setup script uses `pip install -r requirements.txt` (or equivalent)
- [ ] pyproject.toml retained for development use
- [ ] Setup script still creates the venv if needed

## Needs First

Needs the dependency lockfile generated in Goal 1 Step 1.
