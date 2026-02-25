#!/bin/bash
# dc-due-diligence plugin setup
# Run this script from the plugin directory after extracting the zip.
#
# This installs Docling (offline document conversion) and GLiNER (offline PII
# redaction).  Both include ML models that are downloaded on first use.  The
# pre-download step at the end fetches them so the first pipeline run doesn't
# stall.
#
# NOTE: The full install is ~3-5 GB (PyTorch, Docling models, GLiNER model).

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "Setting up dc-due-diligence plugin in: $SCRIPT_DIR"

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv "$SCRIPT_DIR/.venv"

# Install dependencies
echo "Installing dependencies (this may take several minutes)..."
"$SCRIPT_DIR/.venv/bin/pip" install --upgrade pip
"$SCRIPT_DIR/.venv/bin/pip" install -e "$SCRIPT_DIR"

# Pre-download Docling models (layout analysis + TableFormer)
echo ""
echo "Pre-downloading Docling models..."
"$SCRIPT_DIR/.venv/bin/python3" -c "
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableStructureOptions, TableFormerMode
from docling.document_converter import PdfFormatOption

# Build the converter to trigger model download
opts = PdfPipelineOptions()
opts.do_ocr = True
opts.do_table_structure = True
opts.enable_remote_services = False
opts.table_structure_options = TableStructureOptions(
    do_cell_matching=True,
    mode=TableFormerMode.ACCURATE,
)

converter = DocumentConverter(
    allowed_formats=[InputFormat.PDF],
    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)},
)
print('Docling models downloaded successfully.')
"

# Pre-download GLiNER PII model
echo ""
echo "Pre-downloading GLiNER PII model..."
"$SCRIPT_DIR/.venv/bin/python3" -c "
from gliner import GLiNER
model = GLiNER.from_pretrained('urchade/gliner_multi_pii-v1')
print('GLiNER PII model downloaded successfully.')
"

echo ""
echo "Setup complete!"
echo ""
echo "All document conversion and PII redaction runs fully offline."
echo "No API keys are needed for the conversion pipeline."
echo ""
echo "If you installed via the marketplace (/plugin install dc-due-diligence@shipfast),"
echo "you're all set. The plugin is already registered with Claude Code."
echo ""
echo "If you're running this from a local clone, register the plugin with:"
echo "  claude --plugin-dir \"$SCRIPT_DIR\""
