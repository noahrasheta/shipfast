# Task: Pin Python dependency versions

## What To Do

Generate a requirements.txt lockfile from the current working Python environment using `pip freeze`. This captures the exact package versions that are known to work together, replacing the loose `>=` lower-bound pins in pyproject.toml for installation purposes.

## Why It Matters

The current `pyproject.toml` uses `>=` pins only, which means fresh installs may resolve newer incompatible versions -- especially `anthropic` and `google-genai`, both of which have breaking change histories. A lockfile ensures reproducible installs.

## Size

**Estimate:** small

Run pip freeze and save the output. The setup script update to use this lockfile happens in Goal 3.

## Done When

- [ ] requirements.txt exists with pinned versions from the working environment
- [ ] All currently-used packages appear in the lockfile
- [ ] pyproject.toml retained for development flexibility

## Needs First

Nothing -- this can start right away.
