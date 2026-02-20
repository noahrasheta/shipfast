# Task: Verify full install on a clean machine

## What To Do

Test the complete installation flow from scratch: create a fresh Python virtual environment, run the setup script, verify all dependencies install correctly from the lockfile, and confirm the due diligence plugin runs successfully on a test opportunity. Document any issues found and fix them.

## Why It Matters

No amount of code review substitutes for actually running the install from scratch. If first-run setup fails, the plugin is dead to new users. This is the single most important acceptance test for distribution reliability.

## Size

**Estimate:** medium

Requires creating a clean environment and running through the full install + execution flow. May surface issues that need fixing, which adds scope.

## Done When

- [ ] Fresh venv created and setup script runs without errors
- [ ] All dependencies install from the lockfile
- [ ] Due diligence plugin executes successfully on a test folder
- [ ] Any issues discovered during testing are fixed
- [ ] Setup script works on macOS (primary development platform)

## Needs First

Needs the setup script updated to use the lockfile from the previous task.
