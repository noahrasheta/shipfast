# PRD: Due Diligence Plugin v0.3 — Compliance Redesign

**Document Type:** Product Requirements Document
**Version:** 0.3.0
**Author:** Noah Rasheta
**Date:** 2026-02-24
**Status:** Draft — Ready for implementation

---

## 1. Context & Motivation

The dc-due-diligence plugin (v0.2.1) works well functionally — it analyzes 30-84 deal documents across 9 domains, independently verifies claims via web research, and produces scored executive summaries. However, a compliance audit revealed that the current pipeline sends **all** converted document content to Anthropic's cloud API, including:

- Banking information (routing numbers, account numbers, tax IDs)
- Documents explicitly marked "CONFIDENTIAL AND PROPRIETARY" with nondisclosure clauses
- Personal contact information (home addresses, personal emails, cell phones)
- Proprietary pricing and contract terms from executed agreements

This redesign adds a **local pre-processing layer** that classifies documents, redacts sensitive content, and extracts investigation targets — all using a local Ollama model that never transmits data externally. The cloud-based analysis pipeline then receives only safe, pre-processed data.

### What Must NOT Change

- The plugin's functional output (domain reports, risk assessment, executive summary, client summary, PDFs)
- The quality and depth of analysis
- The ability to discover critical findings through web research (e.g., the securities enforcement discovery via email address inference)
- The agent architecture (9 domain agents + risk + exec summary + client summary)
- The document conversion pipeline (Python converters for PDF/Excel/Word/PPT)
- Web research capabilities (WebSearch, WebFetch, MCP-enhanced search)

### What Must Change

- Sensitive document content must never reach Anthropic's cloud API
- Images/scanned PDFs must be processed locally (not via Anthropic Vision API)
- Investigation targets (names, entities) must still flow to the research phase
- A classification and redaction step must run between conversion and analysis
- The manifest must track sensitivity classification per document
- The SKILL.md orchestrator must coordinate the new pre-processing phase

---

## 2. Architecture Overview

### Current Pipeline (v0.2.1)

```
[Broker Docs] → [Python Converters (local)] → [_converted/*.md]
                                                       |
                                              [ALL docs sent to Claude API]
                                                       |
                                              [9 Domain Agents (cloud)]
                                                       |
                                              [Risk Assessment (cloud)]
                                                       |
                                              [Executive Summary (cloud)]
                                                       |
                                              [Client Summary (cloud)]
                                                       |
                                              [PDF Generation (local)]
```

### New Pipeline (v0.3.0)

```
[Broker Docs] → [Python Converters (local)] → [_converted/*.md]
                                                       |
                                              [Classifier (local Ollama)]
                                                       |
                              ┌─────────────────────────┼─────────────────────────┐
                              |                         |                         |
                     CAT 1: SENSITIVE          CAT 2: INVESTIGATION       CAT 3: STANDARD
                     (redact locally)          TARGETS (extract)          (pass through)
                              |                         |                         |
                     [Local Ollama Model]               |                         |
                     Produces redacted                  |                         |
                     summary + extracts                 |                         |
                     investigation targets              |                         |
                              |                         |                         |
                              └────────────┬────────────┘                         |
                                           |                                      |
                              [_preprocessed/manifest.json]                       |
                              [_preprocessed/summaries/*.md]                      |
                              [_preprocessed/targets.json]                        |
                                           |                                      |
                                           └──────────────┬───────────────────────┘
                                                          |
                                                 [9 Domain Agents (cloud)]
                                                 Read: redacted summaries (Cat 1)
                                                 Read: investigation targets (Cat 2)
                                                 Read: full docs (Cat 3)
                                                 Do: web research as before
                                                          |
                                                 [Risk Assessment (cloud)]
                                                          |
                                                 [Executive Summary (cloud)]
                                                          |
                                                 [Client Summary (cloud)]
                                                          |
                                                 [PDF Generation (local)]
```

---

## 3. Three-Category Classification System

Every converted document gets classified into one of three categories. The classifier determines the category; the extractor processes Category 1 documents.

### Category 1: SENSITIVE (Redact — process locally, never send externally)

**Content that triggers Category 1 classification:**
- Banking information: account numbers, routing numbers (ABA), SWIFT codes
- Tax identification: SSNs, EINs, Federal Tax IDs
- Financial account details: credit card numbers, loan account numbers
- Documents with explicit "CONFIDENTIAL", "PROPRIETARY", or "PRIVILEGED" markings
- Executed contracts and agreements (identifiable by signature blocks, DocuSign IDs, "EXECUTED" headers)
- NDA content or documents referencing nondisclosure obligations
- Personal home addresses (not property/site addresses being evaluated)
- Personal phone numbers and personal email addresses (e.g., @hotmail.com, @gmail.com)
- Proprietary pricing schedules, rate cards, fee structures within confidential agreements
- Internal communications (forwarded emails, memos) containing any of the above

**What happens to Category 1 documents:**
1. The local Ollama model reads the full document
2. It produces a **redacted summary** — business facts only, no sensitive data
3. It extracts **investigation targets** (names, entities, roles) → these become Category 2 items
4. The redacted summary is written to `_preprocessed/summaries/<filename>.md`
5. The original converted document is **not** passed to cloud agents

**Redacted summary format:**
```markdown
# Redacted Summary: <original-filename>

## Document Type
<contract/agreement/correspondence/financial/etc.>

## Key Business Facts
- <fact 1>
- <fact 2>
- ...

## Parties Involved
- <entity name> (role: <role>)
- <individual name> (role: <role>, associated entity: <entity>)

## Redacted Content Notice
The following categories of information were present but redacted:
- [x] Financial account information
- [x] Confidential pricing terms
- [ ] Personal contact information
- [ ] NDA/confidentiality clauses
- ...

## Source
Original document: <filename>
Classification: SENSITIVE
Reason: <why this was classified as sensitive>
```

### Category 2: INVESTIGATION TARGETS (Extract — pass to online research)

**Information classified as Category 2:**
- Names of counterparties, principals, officers, signatories
- Company and entity names (LLCs, Corps, partnerships)
- Email addresses and email domains (used for identity resolution, not sent as PII but as search hints)
- Roles and relationships between parties (e.g., "managing member of X LLC")
- Property addresses being evaluated (the deal site, not personal addresses)

**What happens to Category 2 items:**
1. They are collected from ALL documents (both directly from Category 3 docs and extracted from Category 1 docs during redaction)
2. They are written to `_preprocessed/targets.json` as a structured list
3. They are passed to cloud agents as investigation directives
4. Agents use them to form targeted web searches against public records

**targets.json format:**
```json
{
  "investigation_targets": {
    "entities": [
      {
        "name": "Crypto LLC",
        "type": "LLC",
        "source_documents": ["Construction--DAELIMG25178-Crypto_LLC.md"],
        "associated_individuals": ["Andrey (ataranov)"],
        "domains": ["cryptollc.org"]
      }
    ],
    "individuals": [
      {
        "name": "Andrey",
        "inferred_full_name": "Andrey Taranov",
        "inference_source": "email prefix ataranov@cryptollc.org",
        "email": "ataranov@cryptollc.org",
        "roles": ["equipment purchaser", "project contact"],
        "associated_entities": ["Crypto LLC"],
        "source_documents": ["Construction--DAELIMG25178-Crypto_LLC.md", "Construction--Phase_1-4_schedule.md"]
      }
    ],
    "properties": [
      {
        "address": "1125 Arkansas Ln, Arlington, TX",
        "type": "site_under_evaluation",
        "source_documents": ["Property--1125_Arkansas_Ln_Fully_Executed_Lease_08.18.2025.md"]
      }
    ]
  }
}
```

### Category 3: STANDARD (Pass through — process normally)

**Content classified as Category 3:**
- Marketing materials and pitch decks (unless they contain confidential markings)
- Public filings, permits, zoning documents
- Technical specifications, equipment specs, site plans
- Environmental reports and studies (public record)
- General site descriptions and infrastructure overviews
- Construction photos and site images (non-document images)
- Publicly available utility information

**What happens to Category 3 documents:**
- They pass through to the cloud agents exactly as they do today
- Full text is available for analysis
- No redaction needed

---

## 4. New Components to Build

### 4.1 Document Classifier (`converters/classifier.py`)

**Purpose:** Read each converted markdown file and classify it into Category 1, 2, or 3.

**Implementation approach:** Python script that calls the local Ollama model via the `ollama` Python library.

**Input:** Path to `_converted/` folder + `manifest.json`

**Output:** Updated manifest with classification data, written to `_preprocessed/classifications.json`

**Classification prompt for the local model:**

```
You are a document classification assistant for a data center due diligence workflow.

Read the following document and classify it into exactly ONE category:

SENSITIVE — The document contains ANY of the following:
- Banking information (account numbers, routing numbers, tax IDs)
- Documents marked "CONFIDENTIAL", "PROPRIETARY", or "PRIVILEGED"
- Executed contracts or agreements (has signature blocks, DocuSign IDs, or "EXECUTED" in header)
- NDA content or nondisclosure references
- Personal home addresses, personal phone numbers, personal email addresses (@gmail, @hotmail, @yahoo, etc.)
- Proprietary pricing, rate cards, or fee structures
- Internal email communications containing any of the above

STANDARD — The document contains NONE of the sensitive markers above. Examples:
- Marketing materials, pitch decks, site descriptions
- Public filings, permits, zoning documents
- Technical specifications, equipment specs
- Environmental studies, construction photos
- General infrastructure information

Respond with ONLY a JSON object:
{
  "classification": "SENSITIVE" or "STANDARD",
  "reason": "<one sentence explaining why>",
  "sensitive_markers_found": ["<list of specific markers detected, empty if STANDARD>"],
  "investigation_targets_present": true/false
}
```

**Technical notes:**
- Use `ollama` Python library (already installable via pip)
- Model: `qwen2.5:14b` or `llama3.1:8b` (configurable in settings)
- Each document is classified independently
- Classification runs sequentially (local model is the bottleneck)
- Estimated time: 5-15 seconds per document depending on length and model

### 4.2 Sensitive Document Extractor (`converters/extractor.py`)

**Purpose:** For each Category 1 document, produce a redacted summary and extract investigation targets.

**Implementation approach:** Python script that calls the local Ollama model.

**Input:** List of Category 1 document paths from classifier output

**Output:**
- `_preprocessed/summaries/<filename>.md` — one redacted summary per sensitive document
- Appends investigation targets to the shared targets collection

**Extraction prompt for the local model:**

```
You are a document extraction assistant for a data center due diligence workflow.

Read the following document carefully. Your job is to:

1. EXTRACT all business-relevant facts (what the document is about, key terms, dates, locations, capacities, specifications)
2. EXTRACT all people, companies, and entities mentioned (names, roles, relationships, email addresses)
3. REDACT all sensitive information:
   - Replace banking info with [REDACTED - FINANCIAL]
   - Replace specific pricing with [REDACTED - CONFIDENTIAL PRICING]
   - Replace personal addresses with [REDACTED - PERSONAL ADDRESS]
   - Replace personal phone numbers with [REDACTED - PHONE]
   - Replace tax IDs/SSNs with [REDACTED - TAX ID]
   - Do NOT redact company names, entity names, or individual names — these are investigation targets
   - Do NOT redact property addresses being evaluated — these are needed for analysis
   - Do NOT redact email addresses — these are needed for identity resolution

Respond with a JSON object:
{
  "summary": "<markdown formatted summary of the document with business facts, redacted where needed>",
  "document_type": "<contract/agreement/correspondence/financial/technical/other>",
  "investigation_targets": {
    "entities": [{"name": "...", "type": "LLC/Corp/etc", "role": "..."}],
    "individuals": [{"name": "...", "email": "...", "role": "...", "associated_entity": "..."}],
    "properties": [{"address": "...", "type": "site_under_evaluation/other"}]
  },
  "redacted_categories": ["financial_accounts", "confidential_pricing", "personal_addresses", "nda_content", ...]
}
```

**Technical notes:**
- Same local Ollama model as classifier
- Larger context window needed — some documents are 10K+ tokens
- For very large documents (>32K tokens), chunk and process in segments
- The redacted summary should be 500-2000 words (enough for agents to work with, short enough to exclude sensitive details)

### 4.3 Vision Converter — Local Alternative (`converters/vision_local.py`)

**Purpose:** Replace the Anthropic Vision API with a local vision model for image/scanned PDF OCR.

**Implementation approach:** Use a local multimodal model via Ollama (e.g., `llava:13b`, `bakllava`, or `moondream`) for OCR extraction.

**Changes to existing code:**
- `converters/vision.py` currently calls `anthropic.Anthropic().messages.create()` with image data
- New `vision_local.py` uses `ollama.chat()` with image data instead
- `converters/pipeline.py` gets a configuration flag: `use_local_vision: bool = True`
- When `use_local_vision=True`, the pipeline uses `VisionLocalConverter` instead of `VisionConverter`
- Fallback: if local vision model is not available, warn the user and skip image files (don't silently fall back to cloud)

**Technical notes:**
- Ollama supports multimodal models that accept images
- Quality may be lower than Claude Vision — document this tradeoff
- For critical scanned documents, the user can manually convert and review
- The local vision output still goes through the classifier (it might contain sensitive content)

### 4.4 Pre-Processing Pipeline (`converters/preprocess.py`)

**Purpose:** Orchestrate the full pre-processing flow: classify all documents, extract/redact sensitive ones, collect investigation targets.

**Input:** Path to `_converted/` folder (output of existing conversion pipeline)

**Output:**
- `_preprocessed/classifications.json` — classification for every document
- `_preprocessed/summaries/*.md` — redacted summaries for Category 1 documents
- `_preprocessed/targets.json` — all investigation targets from all documents
- `_preprocessed/manifest.json` — master manifest mapping each original doc to its preprocessed output

**Preprocessed manifest format:**
```json
{
  "opportunity_folder": "/path/to/deal",
  "preprocessed_dir": "/path/to/deal/_preprocessed",
  "model_used": "qwen2.5:14b",
  "processing_timestamp": "2026-02-25T10:30:00Z",
  "statistics": {
    "total_documents": 27,
    "sensitive": 8,
    "standard": 19,
    "processing_time_seconds": 142
  },
  "documents": [
    {
      "original_file": "Construction--DAELIMG25178-Crypto_LLC.md",
      "classification": "SENSITIVE",
      "classification_reason": "Contains proprietary pricing from equipment quotation",
      "sensitive_markers": ["confidential_pricing"],
      "preprocessed_file": "_preprocessed/summaries/Construction--DAELIMG25178-Crypto_LLC.md",
      "investigation_targets_extracted": true
    },
    {
      "original_file": "Property--zoning_map.md",
      "classification": "STANDARD",
      "classification_reason": "Public zoning document with no sensitive markers",
      "sensitive_markers": [],
      "preprocessed_file": null,
      "investigation_targets_extracted": false
    }
  ]
}
```

**Execution flow:**
```python
def preprocess_folder(converted_dir: Path, model: str = "qwen2.5:14b") -> PreprocessResult:
    # 1. Read the conversion manifest
    # 2. Classify each document (sequential, local model)
    # 3. For each SENSITIVE document, run extractor (sequential, local model)
    # 4. Collect all investigation targets into targets.json
    # 5. Write preprocessed manifest
    # 6. Print status report
```

### 4.5 Updated SKILL.md Orchestrator

**Changes to the skill workflow:**

The current SKILL.md has these phases:
1. Input Validation and Setup
2. Document Processing (conversion)
3. Research Subfolder Setup
4. Parallel Agent Orchestration (Wave 1: 9 agents, Wave 2: risk assessment)
5. Output Validation
6. Executive Summary Generation
6b. Client Summary Generation
6c. PDF Generation
7. Results Reporting
8. Graceful Degradation

**New phase to insert between Phase 2 and Phase 3:**

#### Phase 2b: Sensitive Data Pre-Processing (NEW)

1. **Check for existing pre-processed data:**
   ```bash
   test -f "<folder>/_preprocessed/manifest.json" && echo "manifest exists" || echo "no manifest"
   ```
   If pre-processed manifest exists and is newer than the conversion manifest, skip pre-processing.

2. **Check Ollama availability:**
   ```bash
   ollama list 2>/dev/null | head -5
   ```
   If Ollama is not installed or no models are available, stop and instruct:
   ```
   Local AI model required for compliance pre-processing.
   Install Ollama: https://ollama.com
   Then pull a model: ollama pull qwen2.5:14b
   ```

3. **Run the pre-processing pipeline:**
   ```bash
   "$PLUGIN_DIR/.venv/bin/python3" -m converters.preprocess "<absolute-folder-path>"
   ```

4. **Report to user:**
   ```
   Document classification complete.

   Total documents: <N>
   Sensitive (processing locally): <N> documents
   Standard (ready for cloud analysis): <N> documents
   Investigation targets extracted: <N> entities, <N> individuals

   Sensitive documents have been redacted. Only redacted summaries and
   investigation targets will be sent to the cloud AI for analysis.
   ```

**Changes to Phase 4 (Agent Orchestration):**

Currently, agents are told: "Read ALL converted markdown files in `${OPPORTUNITY_FOLDER}/_converted/`"

New instruction for agents:
```
Document Access Instructions:

1. Read the preprocessed manifest at ${OPPORTUNITY_FOLDER}/_preprocessed/manifest.json
2. For documents classified as STANDARD: read the full file from ${OPPORTUNITY_FOLDER}/_converted/
3. For documents classified as SENSITIVE: read the redacted summary from ${OPPORTUNITY_FOLDER}/_preprocessed/summaries/
4. Read investigation targets from ${OPPORTUNITY_FOLDER}/_preprocessed/targets.json
5. Use investigation targets for your web research (names, entities, email domains)

IMPORTANT: Do NOT read files from _converted/ that are classified as SENSITIVE in the preprocessed manifest.
Only read their redacted summaries from _preprocessed/summaries/.
```

### 4.6 Updated Agent Definitions

**Every domain agent** needs the following changes to their "Phase 1: Claim Extraction" section:

**Current:**
```
1. Read the manifest at ${OPPORTUNITY_FOLDER}/_converted/manifest.json
2. Read ALL converted markdown files in ${OPPORTUNITY_FOLDER}/_converted/
```

**New:**
```
1. Read the preprocessed manifest at ${OPPORTUNITY_FOLDER}/_preprocessed/manifest.json
2. For each document in the manifest:
   a. If classification is "STANDARD": read from ${OPPORTUNITY_FOLDER}/_converted/<filename>
   b. If classification is "SENSITIVE": read from ${OPPORTUNITY_FOLDER}/_preprocessed/summaries/<filename>
3. Read investigation targets from ${OPPORTUNITY_FOLDER}/_preprocessed/targets.json
4. Include investigation targets in your Phase 2 web research queries
```

**The ownership agent specifically** needs an additional instruction:
```
## Investigation Target Research

In addition to claims extracted from documents, you MUST investigate all individuals
and entities listed in the investigation targets file (targets.json). For each:

- Verify the individual's identity using their name + associated entity + email domain
- Search for litigation, regulatory actions, enforcement proceedings
- Search for SEC/state securities enforcement actions
- Cross-reference entity names with state business registries

These targets were extracted from sensitive documents that you cannot read directly.
The redacted summaries provide business context; the targets file provides the names
and entities you must investigate.
```

### 4.7 Backward Compatibility

**The pre-processing step must be optional for now.** If `_preprocessed/` doesn't exist (e.g., old runs or Ollama not installed), agents fall back to reading from `_converted/` directly, exactly as they do today.

Agent instruction for fallback:
```
If ${OPPORTUNITY_FOLDER}/_preprocessed/manifest.json does not exist:
  Fall back to reading ALL files from ${OPPORTUNITY_FOLDER}/_converted/ directly.
  This means pre-processing was not run. Proceed with the standard workflow.
```

This ensures existing deal folders and the current workflow aren't broken during the transition.

---

## 5. Configuration

### Plugin Settings (New)

Add a configuration section to the plugin or a `config.json` at the plugin root:

```json
{
  "compliance": {
    "require_preprocessing": true,
    "local_model": "qwen2.5:14b",
    "local_vision_model": "llava:13b",
    "use_local_vision": true,
    "classification_confidence_threshold": 0.8,
    "skip_preprocessing_if_no_ollama": false
  }
}
```

**Setting descriptions:**
- `require_preprocessing`: If true, the workflow will not run cloud agents without pre-processing. If false, pre-processing is attempted but agents fall back to direct access if it fails.
- `local_model`: Which Ollama model to use for classification and extraction.
- `local_vision_model`: Which Ollama model to use for local image/OCR processing.
- `use_local_vision`: If true, use local vision model instead of Anthropic Vision API.
- `skip_preprocessing_if_no_ollama`: If true, silently skip pre-processing when Ollama is not available (not recommended for compliance).

---

## 6. Dependencies

### New Python Dependencies

Add to `pyproject.toml`:
```toml
[project]
dependencies = [
    # ... existing deps ...
    "ollama>=0.4.0",        # Ollama Python client
]
```

### System Requirements

- **Ollama** must be installed on the machine: https://ollama.com
- At least one text model must be pulled: `ollama pull qwen2.5:14b`
- For local vision: a multimodal model must be pulled: `ollama pull llava:13b`
- **RAM:** Local models need 8-16GB RAM depending on model size. The 14B parameter model needs ~10GB.

### Setup Script Update

`setup.sh` should:
1. Check if Ollama is installed (warn if not, don't fail — it's needed at runtime, not build time)
2. Suggest which models to pull
3. Install the `ollama` Python package in the venv

---

## 7. File Changes Summary

### New Files to Create

| File | Purpose |
|------|---------|
| `converters/classifier.py` | Document classification using local Ollama model |
| `converters/extractor.py` | Sensitive document redaction and target extraction using local Ollama model |
| `converters/preprocess.py` | Pre-processing pipeline orchestrator (calls classifier + extractor) |
| `converters/vision_local.py` | Local vision model OCR (replacement for Anthropic Vision API) |
| `config.json` | Plugin configuration including compliance settings |

### Files to Modify

| File | Changes |
|------|---------|
| `skills/due-diligence/SKILL.md` | Add Phase 2b (pre-processing), update Phase 4 agent instructions, update agent document access patterns |
| `agents/power-agent.md` | Update document reading instructions to use preprocessed manifest |
| `agents/connectivity-agent.md` | Same |
| `agents/water-cooling-agent.md` | Same |
| `agents/land-zoning-agent.md` | Same |
| `agents/ownership-agent.md` | Same + add investigation target research section |
| `agents/environmental-agent.md` | Same |
| `agents/commercials-agent.md` | Same |
| `agents/natural-gas-agent.md` | Same |
| `agents/market-comparables-agent.md` | Same |
| `agents/risk-assessment-agent.md` | Update to note which reports used redacted vs. full documents |
| `agents/executive-summary-agent.md` | Same |
| `agents/client-summary-agent.md` | Same |
| `converters/pipeline.py` | Add `use_local_vision` flag, integrate `VisionLocalConverter` option |
| `converters/vision.py` | No changes (kept as fallback, but not used when compliance mode is on) |
| `pyproject.toml` | Add `ollama` dependency |
| `setup.sh` | Add Ollama check and model pull suggestions |
| `.claude-plugin/plugin.json` | Bump version to 0.3.0 |

### Files Unchanged

| File | Reason |
|------|--------|
| `converters/pdf.py` | Text-based PDF conversion is local, no changes needed |
| `converters/excel.py` | Local conversion, no changes needed |
| `converters/word.py` | Local conversion, no changes needed |
| `converters/powerpoint.py` | Local conversion, no changes needed |
| `converters/scanner.py` | File scanning is local, no changes needed |
| `converters/base.py` | Base classes unchanged |
| `converters/generate_pdf.py` | PDF output generation is local, no changes needed |
| `templates/` | Scoring rubric and report template unchanged |

---

## 8. Implementation Order

Build in this sequence. Each step is independently testable.

### Step 1: Document Classifier
- Build `converters/classifier.py`
- Test: classify a handful of known-sensitive and known-standard documents
- Verify: banking docs → SENSITIVE, marketing materials → STANDARD, executed contracts → SENSITIVE

### Step 2: Sensitive Document Extractor
- Build `converters/extractor.py`
- Test: feed it a known sensitive document (e.g., the Shell Energy contract from MattSanders)
- Verify: redacted summary has business facts but no account numbers, pricing, or personal addresses
- Verify: investigation targets include entity names and individual names

### Step 3: Pre-Processing Pipeline
- Build `converters/preprocess.py`
- Test: run on the MattSanders `_converted/` folder
- Verify: `_preprocessed/` folder created with correct structure
- Verify: classifications match expectations
- Verify: `targets.json` contains all entities and individuals

### Step 4: Local Vision Converter
- Build `converters/vision_local.py`
- Test: feed it a scanned PDF and a standalone image
- Verify: text extraction quality is acceptable (compare to Anthropic Vision output)
- Update `converters/pipeline.py` to support `use_local_vision` flag

### Step 5: Update SKILL.md Orchestrator
- Add Phase 2b to the orchestrator
- Update agent spawning instructions in Phase 4
- Add Ollama availability check
- Test: run full workflow on a test folder

### Step 6: Update All Agent Definitions
- Update document reading instructions in all 13 agents
- Add investigation target research to ownership agent
- Add backward compatibility fallback to all agents
- Test: run individual agents against pre-processed data

### Step 7: Integration Testing
- Run full workflow on MattSanders folder with pre-processing enabled
- Compare output quality to v0.2.1 output (should be equivalent or better)
- Verify: no sensitive data appears in any cloud API call
- Verify: the securities enforcement finding (Taranov/Kechik) is still discovered via investigation targets

### Step 8: Configuration and Polish
- Add `config.json` with compliance settings
- Update `setup.sh` with Ollama guidance
- Bump version to 0.3.0 in all locations
- Update CLAUDE.md with version locations for new files

---

## 9. Testing Checklist

### Classification Accuracy
- [ ] Banking documents (Oncor SOC with JP Morgan details) → classified SENSITIVE
- [ ] Executed contracts (Shell Energy MESA) → classified SENSITIVE
- [ ] Documents with "CONFIDENTIAL" marking → classified SENSITIVE
- [ ] Email threads with personal addresses → classified SENSITIVE
- [ ] Marketing materials → classified STANDARD
- [ ] Zoning maps and permits → classified STANDARD
- [ ] Technical equipment specs → classified STANDARD
- [ ] Construction estimates (may be borderline — check for confidential pricing)

### Extraction Quality
- [ ] Redacted summary of banking document: no account/routing numbers, but states "utility deposit agreement" with relevant terms
- [ ] Redacted summary of executed contract: no specific pricing, but states contract type, parties, duration, capacity
- [ ] Investigation targets extracted from all sensitive documents include all named individuals and entities
- [ ] Email addresses preserved in targets (needed for identity resolution)
- [ ] Entity names preserved in targets (needed for public record searches)

### Critical Discovery Preservation
- [ ] Run on MattSanders folder: ownership agent still discovers Taranov/Kechik securities enforcement
- [ ] Verify discovery chain: email addresses from targets.json → agent infers full names → web search finds DFI enforcement
- [ ] Run on DigipowerX folder: all domain findings preserved despite sensitive contract redaction

### End-to-End Compliance
- [ ] No Category 1 document content appears in cloud API calls (check by reviewing agent task prompts)
- [ ] Images/scanned PDFs processed by local vision model (no Anthropic Vision API calls)
- [ ] Investigation targets (names, entities) DO appear in web search queries (this is expected and correct)
- [ ] Redacted summaries contain business context but no banking info, confidential pricing, or personal addresses
- [ ] Executive summary quality is equivalent to v0.2.1 output

### Backward Compatibility
- [ ] Plugin works without Ollama installed when `require_preprocessing: false`
- [ ] Existing `_converted/` folders without `_preprocessed/` still work (agents fall back)
- [ ] Pre-processing can be re-run without destroying existing analysis output

---

## 10. Workflow — What the User Experiences

### With Pre-Processing (v0.3.0 default)

```
$ claude
> /due-diligence ./opportunities/NewDeal

Processing documents in NewDeal...
Converting 35 documents... done (32 converted, 3 skipped)

Running compliance pre-processing...
Classifying documents using local model (qwen2.5:14b)...
  - 35 documents classified in 47 seconds
  - 9 sensitive documents identified
  - 26 standard documents ready for cloud analysis

Processing sensitive documents locally...
  - 9 redacted summaries generated
  - 14 investigation targets extracted (6 entities, 8 individuals)

Sensitive document content will NOT leave this machine.
Investigation targets will be researched via public records.

Launching 9 domain research agents in parallel...
[... normal workflow continues ...]

Due diligence complete.
Executive Summary: ./opportunities/NewDeal/EXECUTIVE_SUMMARY.pdf
Client Summary: ./opportunities/NewDeal/CLIENT_SUMMARY.pdf
Verdict: Proceed with Caution
```

### Without Ollama (fallback)

```
$ claude
> /due-diligence ./opportunities/NewDeal

Processing documents in NewDeal...
Converting 35 documents... done (32 converted, 3 skipped)

WARNING: Ollama not installed. Compliance pre-processing cannot run.
All document content will be sent to the cloud AI for analysis.
To enable compliance mode: install Ollama and pull qwen2.5:14b
Proceeding with standard workflow...

[... v0.2.1 behavior ...]
```

---

## 11. Out of Scope (Future Considerations)

These are NOT part of v0.3.0 but may be addressed later:

- **Automated data room integration** — pulling documents directly from virtual data rooms
- **Audit logging** — formal log of what data was sent to which API, timestamped
- **Andrew's standalone version** — a simplified interface that non-technical users can run (requires the compliance controls to be fully baked in first)
- **Model quality benchmarking** — systematic comparison of local vs. cloud model quality for classification/extraction
- **Real-time classification** — classifying documents as they're converted rather than as a separate pass
- **Encryption at rest** — encrypting `_converted/` and `_preprocessed/` folders
- **Data retention policy** — automatic deletion of converted/preprocessed data after N days
