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
echo "If you installed via the marketplace (/plugin install dc-due-diligence@shipfast),"
echo "you're all set. The plugin is already registered with Claude Code."
echo ""
echo "If you're running this from a local clone, register the plugin with:"
echo "  claude --plugin-dir \"$SCRIPT_DIR\""
