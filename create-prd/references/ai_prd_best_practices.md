# Writing PRDs for AI Coding Agents

This reference covers what makes a Product Requirements Document effective when the primary consumer is an AI coding agent (Claude Code, Cursor, Windsurf, Lovable, GSD, Director, or any LLM-based builder).

## Core Principles

### 1. Explicit Over Implicit

AI agents cannot read between the lines. State everything directly:
- If a feature should NOT be built, say so explicitly in Out of Scope
- If a technology should be used, name it with the version
- If a behavior is expected, describe the exact input/output

**Bad:** "The app should handle authentication"
**Good:** "Use Clerk for authentication. Support Google and Apple social login. No email/password auth at MVP. Account creation is optional and happens AFTER the user completes the primary action."

### 2. Machine-Verifiable Acceptance Criteria

Every user story needs acceptance criteria that can be tested — by a human or by an automated test. Avoid subjective language.

**Bad:** "The page should feel responsive"
**Good:** "Page load completes in under 2 seconds on a 4G mobile connection as measured by Lighthouse"

**Bad:** "The search should return relevant results"
**Good:** "Search by product name returns matching results within 500ms. Empty query shows all items. No results displays 'No items found' message with suggestion to broaden search."

### 3. Non-Goals Are Critical

AI agents will add features their training data suggests are standard (authentication, error handling, caching, analytics, admin panels) unless explicitly told not to. The Out of Scope section prevents this.

Strong non-goals are specific and positive:
- "No mobile app — web only, mobile-responsive"
- "No admin dashboard at MVP — use database directly"
- "No subscription billing — one-time purchases only"
- "No internationalization — English only"

### 4. Phased Implementation

Break the build into sequential phases where each phase leaves the product in a runnable, verifiable state. This matches how AI agents work best — incremental building with checkpoints.

**Bad:** One monolithic spec that describes the entire product
**Good:** Phase 1 (auth + core data model) -> Phase 2 (primary feature) -> Phase 3 (payments) -> Phase 4 (polish + secondary features)

Each phase should specify what can be manually verified when complete.

### 5. Concrete Over Abstract

Show, don't just tell. Include examples wherever possible:
- Example API requests and responses
- Example user flows with specific data
- Example UI states (empty, loading, populated, error)
- Example database records

### 6. Structured for Scanning

AI agents process structured content better than prose. Use:
- Tables for comparisons, feature lists, tech stack choices
- Bullet lists for requirements and criteria
- Code blocks for schemas, configs, and env variables
- Consistent heading hierarchy for navigation
- Table of contents with anchor links

## Sections That Matter Most to AI Agents

**High value** (AI agents reference these constantly):
1. Tech Stack & Architecture — what to build with
2. User Flows — what to build
3. Data Models / Schema — how data is structured
4. Out of Scope — what NOT to build
5. Acceptance Criteria — how to verify correctness
6. Implementation Phases — build order
7. Environment Variables — what needs to be configured

**Medium value** (provides context for decisions):
8. UI/UX Requirements — how it should look and feel
9. API Integrations — external service connections
10. Non-Functional Requirements — performance and security constraints
11. Open Questions — where to make reasonable choices

**Low value for building** (but valuable for the founder to think through):
12. Revenue Model & Pricing
13. Go-to-Market Strategy
14. Market Size / Competitive Analysis
15. Financial Projections

## Common PRD Mistakes That Confuse AI Agents

### Vague scope boundaries
"We might add social features later" — the agent may start building social infrastructure. Say: "No social features. No user profiles visible to other users. No sharing between users."

### Prose-heavy descriptions
Long paragraphs with multiple requirements blended together. The agent may miss or blend details. Use bullets, one requirement per line.

### Human-judgment criteria
"The onboarding should feel intuitive" is untestable. "User completes onboarding in 3 steps or fewer without reading help text" is testable.

### Missing executable commands
Not including the actual commands to build, test, and run the project. Agents reference these constantly and will guess (often wrong) if not provided. Include: package manager, dev server command, test command, build command.

### Overambitious single specification
Dumping the entire product into one monolithic spec leads to drift and incomplete implementation. Break into phases.

### Dead-end phases
Each phase must leave the codebase runnable. Half-implemented features, commented-out code, or placeholder functions create ambiguity.

## Format Compatibility

The PRD output is designed to work with any downstream tool:

- **Claude Code / Cursor / Windsurf** — Drop the PRD.md file into the project and reference it: "Build this product following PRD.md"
- **GSD** — Use `/gsd:new-project --auto @PRD.md` to bootstrap a full project from the PRD
- **Director** — The PRD contains all the information Director's `/director:onboard` interview would extract
- **Conductor** — The PRD's tech stack, product vision, and feature specs map directly to Conductor's `product.md` and `tech-stack.md`
- **Lovable / Bolt / v0** — Paste the relevant sections (features, user flows, UI requirements) as the initial prompt

## The Dual-Document Pattern

For maximum effectiveness, pair the PRD with a `CLAUDE.md` (or equivalent agent config) file:

- **PRD** describes WHAT to build — product requirements, features, scope
- **CLAUDE.md** describes HOW to build — coding conventions, file structure, commit style, testing approach

The PRD is tool-agnostic. The CLAUDE.md is specific to the coding environment. Together, they give AI agents complete context.
