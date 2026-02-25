"""
Offline PII redaction for converted markdown documents.

Uses GLiNER (``urchade/gliner_multi_pii-v1``) running locally to detect
sensitive information, then replaces it with ``[REDACTED: <type>]`` placeholders.
A regex fallback catches structured patterns (EINs, SSNs, etc.) that NER
models sometimes miss.

All processing is local -- the GLiNER model runs on CPU, no API calls.

Design decisions:
- **Redact**: bank accounts, routing numbers, EINs/TINs, SSNs, credit cards,
  CVVs, driver's licenses, passport numbers, IBANs.
- **Preserve**: email addresses, phone numbers, organization/company names,
  property addresses, dollar amounts, person names -- these are essential
  for due diligence research (ownership verification, background checks).
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# GLiNER entity labels to detect (only the ones we want to REDACT).
_REDACT_LABELS: list[str] = [
    "social security number",
    "tax identification number",
    "credit card number",
    "credit card expiration date",
    "cvv",
    "bank account number",
    "iban",
    "driver's license number",
    "passport number",
    "health insurance id number",
]

# GLiNER confidence threshold -- lower = more aggressive detection.
# 0.3 is recommended for PII where recall matters more than precision.
_THRESHOLD: float = 0.3

# Maximum characters per chunk for GLiNER (model limit ~384 tokens).
_CHUNK_MAX_CHARS: int = 1000
_CHUNK_OVERLAP: int = 200

# Placeholder format for redacted values.
_REDACT_FMT = "[REDACTED: {label}]"

# Friendly label mapping for the placeholder text.
_LABEL_MAP: dict[str, str] = {
    "social security number": "ssn",
    "tax identification number": "ein",
    "credit card number": "credit_card",
    "credit card expiration date": "card_expiry",
    "cvv": "cvv",
    "bank account number": "bank_account",
    "iban": "iban",
    "driver's license number": "drivers_license",
    "passport number": "passport",
    "health insurance id number": "health_insurance_id",
}

# ---------------------------------------------------------------------------
# Regex fallback patterns for structured PII
# ---------------------------------------------------------------------------

_REGEX_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    # SSN: 123-45-6789 or 123 45 6789
    ("ssn", re.compile(r"\b\d{3}[-\s]\d{2}[-\s]\d{4}\b")),
    # EIN: 12-3456789
    ("ein", re.compile(r"\b\d{2}-\d{7}\b")),
    # Credit card: 4 groups of 4 digits separated by spaces or dashes
    ("credit_card", re.compile(r"\b\d{4}[-\s]\d{4}[-\s]\d{4}[-\s]\d{4}\b")),
    # Credit card: 16 consecutive digits (Visa, MC, Discover)
    ("credit_card", re.compile(r"\b[3-6]\d{15}\b")),
    # IBAN: 2 letter country code + 2 check digits + up to 30 alphanumeric
    ("iban", re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{4,30}\b")),
    # US bank routing number: 9 digits (starts with 0-3)
    ("routing_number", re.compile(r"\b[0-3]\d{8}\b")),
]


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class RedactedEntity:
    """A single PII entity that was redacted."""

    start: int
    end: int
    original_length: int
    label: str
    score: float
    source: str  # "gliner" or "regex"


@dataclass
class RedactionResult:
    """Result of redacting a single document."""

    original_path: str
    redacted_text: str
    entities_found: int
    entities: list[RedactedEntity] = field(default_factory=list)

    @property
    def was_redacted(self) -> bool:
        return self.entities_found > 0


@dataclass
class RedactionReport:
    """Summary of redaction across all documents in a pipeline run."""

    files_scanned: int = 0
    files_redacted: int = 0
    total_entities: int = 0
    entities_by_type: dict[str, int] = field(default_factory=dict)
    file_details: list[dict[str, Any]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# GLiNER model management
# ---------------------------------------------------------------------------

_model: Any = None


def _get_model() -> Any:
    """Lazily load the GLiNER PII model."""
    global _model
    if _model is None:
        logger.info("Loading GLiNER PII model (first call, downloading if needed)...")
        from gliner import GLiNER

        _model = GLiNER.from_pretrained("urchade/gliner_multi_pii-v1")
        logger.info("GLiNER PII model ready.")
    return _model


# ---------------------------------------------------------------------------
# Text chunking (GLiNER has a ~384 token limit)
# ---------------------------------------------------------------------------

def _chunk_text(
    text: str,
    max_chars: int = _CHUNK_MAX_CHARS,
    overlap: int = _CHUNK_OVERLAP,
) -> list[dict[str, Any]]:
    """Split text into overlapping chunks with character offset tracking."""
    chunks: list[dict[str, Any]] = []
    start = 0

    while start < len(text):
        end = min(start + max_chars, len(text))

        # Try to break at a sentence boundary in the last 20% of the chunk.
        if end < len(text):
            search_start = start + int(max_chars * 0.8)
            match = None
            for m in re.finditer(r"[.!?]\s+", text[search_start:end]):
                match = m
            if match:
                end = search_start + match.end()

        chunks.append({"text": text[start:end], "offset": start})
        start = end - overlap if end < len(text) else end

    return chunks


# ---------------------------------------------------------------------------
# PII detection
# ---------------------------------------------------------------------------

def _detect_pii_gliner(text: str) -> list[dict[str, Any]]:
    """Run GLiNER PII detection on text of any length."""
    model = _get_model()

    if len(text) < _CHUNK_MAX_CHARS:
        return model.predict_entities(text, _REDACT_LABELS, threshold=_THRESHOLD)

    # Long text: chunk, detect, deduplicate.
    chunks = _chunk_text(text)
    all_entities: list[dict[str, Any]] = []
    seen: set[tuple[int, int, str]] = set()

    for chunk in chunks:
        entities = model.predict_entities(
            chunk["text"], _REDACT_LABELS, threshold=_THRESHOLD
        )
        for ent in entities:
            abs_start = ent["start"] + chunk["offset"]
            abs_end = ent["end"] + chunk["offset"]
            key = (abs_start, abs_end, ent["label"])
            if key not in seen:
                seen.add(key)
                all_entities.append({
                    "start": abs_start,
                    "end": abs_end,
                    "text": ent["text"],
                    "label": ent["label"],
                    "score": ent["score"],
                    "source": "gliner",
                })

    all_entities.sort(key=lambda e: e["start"])
    return all_entities


def _detect_pii_regex(text: str) -> list[dict[str, Any]]:
    """Run regex-based PII detection as a fallback for structured patterns."""
    entities: list[dict[str, Any]] = []

    for label, pattern in _REGEX_PATTERNS:
        for match in pattern.finditer(text):
            entities.append({
                "start": match.start(),
                "end": match.end(),
                "text": match.group(),
                "label": label,
                "score": 1.0,
                "source": "regex",
            })

    entities.sort(key=lambda e: e["start"])
    return entities


def _merge_detections(
    gliner_entities: list[dict[str, Any]],
    regex_entities: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Merge GLiNER and regex detections, preferring GLiNER when they overlap."""
    if not regex_entities:
        return gliner_entities
    if not gliner_entities:
        return regex_entities

    # Build a set of character ranges covered by GLiNER detections.
    covered: set[int] = set()
    for ent in gliner_entities:
        covered.update(range(ent["start"], ent["end"]))

    # Add regex detections only if they don't overlap with GLiNER detections.
    merged = list(gliner_entities)
    for ent in regex_entities:
        ent_range = set(range(ent["start"], ent["end"]))
        if not ent_range & covered:
            merged.append(ent)

    merged.sort(key=lambda e: e["start"])
    return merged


# ---------------------------------------------------------------------------
# Redaction
# ---------------------------------------------------------------------------

def redact_text(text: str) -> RedactionResult:
    """Detect and redact PII from a text string.

    Returns the redacted text and a record of what was removed.
    The original PII values are NOT stored -- only the type, position,
    and original length are recorded.
    """
    gliner_entities = _detect_pii_gliner(text)
    regex_entities = _detect_pii_regex(text)
    merged = _merge_detections(gliner_entities, regex_entities)

    if not merged:
        return RedactionResult(
            original_path="",
            redacted_text=text,
            entities_found=0,
        )

    # Build the redacted text by replacing entities in reverse order
    # (so character positions stay valid).
    redacted = text
    entities: list[RedactedEntity] = []

    for ent in sorted(merged, key=lambda e: e["start"], reverse=True):
        friendly_label = _LABEL_MAP.get(ent["label"], ent["label"])
        replacement = _REDACT_FMT.format(label=friendly_label)
        redacted = redacted[: ent["start"]] + replacement + redacted[ent["end"] :]

        entities.append(
            RedactedEntity(
                start=ent["start"],
                end=ent["end"],
                original_length=ent["end"] - ent["start"],
                label=friendly_label,
                score=ent["score"],
                source=ent["source"],
            )
        )

    # Reverse so entities are in document order.
    entities.reverse()

    return RedactionResult(
        original_path="",
        redacted_text=redacted,
        entities_found=len(entities),
        entities=entities,
    )


def redact_file(file_path: Path) -> RedactionResult:
    """Read a markdown file, redact PII, and overwrite with redacted version.

    Returns a RedactionResult with details of what was redacted.
    """
    file_path = Path(file_path)
    text = file_path.read_text(encoding="utf-8")

    result = redact_text(text)
    result.original_path = str(file_path)

    if result.was_redacted:
        file_path.write_text(result.redacted_text, encoding="utf-8")
        logger.info(
            "Redacted %d entities in %s", result.entities_found, file_path.name
        )
    else:
        logger.debug("No PII found in %s", file_path.name)

    return result


def redact_converted_folder(converted_dir: Path) -> RedactionReport:
    """Redact PII from all markdown files in a _converted/ folder.

    Overwrites each file in place with the redacted version.
    Writes a ``redaction-report.json`` to the folder summarizing what
    was redacted (without storing original PII values).

    Returns a RedactionReport for inclusion in the pipeline manifest.
    """
    converted_dir = Path(converted_dir)
    report = RedactionReport()

    md_files = sorted(converted_dir.glob("*.md"))
    report.files_scanned = len(md_files)

    for md_file in md_files:
        result = redact_file(md_file)
        report.total_entities += result.entities_found

        if result.was_redacted:
            report.files_redacted += 1

        # Count by type.
        for ent in result.entities:
            report.entities_by_type[ent.label] = (
                report.entities_by_type.get(ent.label, 0) + 1
            )

        # File-level summary (no original values stored).
        report.file_details.append({
            "file": md_file.name,
            "entities_found": result.entities_found,
            "entity_types": [ent.label for ent in result.entities],
        })

    # Write the redaction report.
    report_path = converted_dir / "redaction-report.json"
    report_data = {
        "files_scanned": report.files_scanned,
        "files_redacted": report.files_redacted,
        "total_entities_redacted": report.total_entities,
        "entities_by_type": report.entities_by_type,
        "files": report.file_details,
    }
    report_path.write_text(
        json.dumps(report_data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    logger.info(
        "Redaction complete: %d entities in %d/%d files. Report: %s",
        report.total_entities,
        report.files_redacted,
        report.files_scanned,
        report_path,
    )

    return report
