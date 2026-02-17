#!/bin/bash
# dc-due-diligence plugin setup
# Run this script from the plugin directory after extracting the zip.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "Setting up dc-due-diligence plugin in: $SCRIPT_DIR"

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv "$SCRIPT_DIR/.venv"

# Install dependencies
echo "Installing dependencies..."
"$SCRIPT_DIR/.venv/bin/pip" install --upgrade pip
"$SCRIPT_DIR/.venv/bin/pip" install -e "$SCRIPT_DIR"

echo ""
echo "Setup complete!"
echo ""
echo "To register the plugin with Claude Code, create a symlink:"
echo "  ln -s \"$SCRIPT_DIR\" ~/.claude/plugins/dc-due-diligence"
echo ""
echo "Then restart Claude Code to pick up the new plugin."
