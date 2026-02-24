---
name: create-prd
description: This skill should be used when the user wants to create a PRD, write a product spec, plan a new product, define an MVP, scope out an idea, document product requirements, prepare specifications for AI coding agents, or says things like "I have an idea for an app," "help me plan my product," "write me a spec," or "turn my idea into a plan." It guides non-technical founders and technical builders through an adaptive brainstorming conversation that produces a comprehensive, AI-agent-optimized PRD in markdown compatible with any AI building tool.
---

# Create PRD

Generate a comprehensive Product Requirements Document through adaptive conversation. The PRD produced is optimized for AI coding agents to build from — structured with clear sections, testable acceptance criteria, explicit scope boundaries, and implementation-ready technical detail.

## Who This Is For

Solo founders, entrepreneurs, and vibe coders who have a product idea and want to turn it into a document that any AI building tool can execute from. Users range from non-technical ("I've never heard of a database") to technical ("I want Next.js + Convex + Clerk"). Adapt to their level.

## Conversation Flow

When triggered, run through these phases. Ask ONE question at a time. Offer suggested answers where helpful. Move faster with technical users, slower with non-technical ones.

If the user provides extensive notes, a document, or multi-topic answers, skip questions already answered. Consolidate remaining gaps into fewer questions. The goal is a complete PRD, not completing every phase sequentially.

### Phase 1: Vision & Context

Start with an open-ended question to understand what they want to build.

- "What are you building? Describe it like you'd explain it to a friend."
- If the user provides a document, notes, or prior research, read and incorporate it.
- Listen for clues about their technical level. If they mention frameworks, databases, or APIs, they're technical. If they say "an app" or "a website," they may be non-technical.

Follow up with:
- "What problem does this solve? Why does it need to exist?"
- "Who is this for? Describe your ideal user."
- "What makes your approach different or better than what already exists?"

### Phase 2: Technical Assessment

Adapt based on detected technical level.

**Non-technical users** — Ask in plain language:
- "Will this be a website, a phone app, or both?"
- "Do users need to create an account or log in?"
- "Will people pay for this? If so, how — subscription, one-time purchase, free with upgrades?"
- "Does it need to connect to any outside services?" (give examples relevant to their idea: payments, email, maps, AI, etc.)
- If they say "I don't know" to stack questions, make a recommendation based on what they described and explain why in one sentence. Use popular, well-supported stacks that AI agents work with well (Next.js, React, Supabase, Vercel, Clerk, Stripe, etc.).

**Technical users** — Ask directly:
- "What stack are you thinking? Frontend, backend, database, hosting?"
- "Any specific integrations or APIs?"
- "Any constraints I should know about — performance requirements, compliance, budget?"
- Move quickly through what they already know. Don't re-explain their own choices.

### Phase 3: Features & Scope

Extract the core features for MVP. Probe for completeness without overwhelming.

- "What are the 3-5 core things this product must do on day one?"
- For each feature: "How would a user interact with this? What does success look like?"
- "What should this product explicitly NOT do in version 1?" (This is critical — probe for scope boundaries the user hasn't considered. AI agents cannot infer boundaries from omission.)
- "Is there anything you're unsure about — decisions that still need to be made?"

### Phase 4: User Experience

Extract enough detail for an AI agent to build the UI.

- "Walk me through the main flow — what happens from the moment someone opens the app to when they accomplish their goal?"
- "Are there other important flows? (onboarding, payments, sharing, admin, etc.)"
- "Any design preferences — minimal, playful, professional? Any apps you admire the look of?"

### Phase 5: Business Context (Optional)

Offer this section. Include if the user engages, skip if they decline.

- "Have you thought about how this makes money? (subscription, freemium, one-time purchase, marketplace fees, ads, etc.)"
- "Do you have a sense of pricing?"
- "How will people find out about this product?"
- "What metrics would tell you this is working?"

If the user says "I'll figure that out later," respect it. Note it in Open Questions.

### Phase 6: Generate the PRD

Once enough information is gathered, generate the complete PRD document. Follow the structure defined below. For expected output format and depth, see the sample PRD at `${CLAUDE_PLUGIN_ROOT}/examples/sample_prd.md`. Fill in reasonable defaults for any gaps — but clearly mark assumptions with "(Recommended)" or "(Default — verify)" so the user and the builder know what was inferred vs. stated.

**Before delivering the PRD, run a quality check:**

1. Does every MVP feature have at least one user story with testable acceptance criteria?
2. Is Out of Scope explicitly stated with concrete items?
3. Is the tech stack specified (even if recommended by the skill)?
4. Are user flows written out step by step?
5. Are data models or schema defined (even if high-level for non-technical users)?
6. Is there at least one open question flagged?
7. Would an AI coding agent reading only this document know what to build, what NOT to build, what tools to use, and in what order to build it?

If any check fails, go back and fill the gap — either by asking the user or by providing a reasonable default marked as such.

**Save the PRD** to the user's project directory as `PRD.md` (or a name they prefer). Confirm the file path.

### Phase 7: Refine

After presenting the PRD, ask: "Anything you'd like to change, add, or remove?" Iterate until the user is satisfied.

## PRD Output Structure

Use this section ordering. Include all Core sections. Include Optional sections only if the conversation surfaced relevant information.

### Core Sections (Always Include)

**1. Executive Summary**
Product name, one-line pitch, 2-3 sentence description of what it does and for whom.

**2. Problem Statement**
What specific problem exists, how people solve it today, why current solutions fall short.

**3. Solution & Value Proposition**
Core solution description, unique differentiators, value to the customer.

**4. Target Users & Personas**
Primary user description with goals, pain points, and motivations. Include a concrete persona with a name and a "moment" showing how they'd use the product. Keep it behavioral, not demographic essays.

**5. User Stories**
Organized by epic/feature area. Each story follows: "As a [user], I want to [action] so that [benefit]." Each story includes testable acceptance criteria — specific, measurable conditions (not vague prose like "works well"). Use bullet checklists for acceptance criteria.

**6. MVP Feature Scope**
Table or list of must-have features for launch vs. features deferred to later phases. Be explicit about priority (P0 = launch day, P1 = soon after).

**7. User Flows**
Plain-text flow diagrams showing step-by-step user journeys. Use indented arrow notation:
```
Landing Page
  -> "Get Started" CTA
  -> Upload Screen
    -> Upload file
    -> Preview + confirm
  -> Processing (loading state)
  -> Results Screen
    -> Download / Share / Purchase
```
Cover the primary flow and any important secondary flows (onboarding, checkout, sharing, admin).

**8. Tech Stack & Architecture**
Technology choices in a table with rationale. Include: framework, language, styling, auth, database, hosting, key integrations. For technical users, include architecture diagrams in plain text and actual schema code if the conversation went deep enough. For non-technical users, include recommended choices with brief justifications.

**9. Data Models**
Database schema or data structure. For technical users who specified a database, write actual schema code (SQL, Convex, Prisma, etc.). For non-technical users, describe the key data entities and their relationships in plain language or a simple table.

**10. UI/UX Requirements**
Screen-by-screen requirements covering key screens. Include design principles, mobile/responsive requirements, and any specific UI patterns. Not wireframes — written descriptions that an AI agent can implement from.

**11. Non-Functional Requirements**
Performance targets (load times, response times), security requirements, scalability expectations, accessibility standards, SEO requirements. Keep concise — bullets, not paragraphs.

**12. Out of Scope**
Explicit list of things NOT being built in this version. This is the most important section for AI agents. State boundaries clearly: "No mobile app," "No subscription model," "No international shipping." AI agents will add features their training suggests are standard unless explicitly told not to.

**13. Open Questions**
Decisions that haven't been made yet. Flag each clearly so the builder knows to make a reasonable choice or ask. These often include: specific design choices, pricing details, policy decisions, edge cases.

**14. Risks & Mitigations**
Table with columns: Risk, Likelihood, Impact, Mitigation. Cover technical risks, business risks, and dependency risks.

**15. Implementation Phases**
Recommended build order with 2-week phases. Each phase should leave the product in a runnable state. Include what gets built in each phase and what can be verified at the end. This is critical for AI agents that build incrementally.

**16. Environment Variables & Setup Checklist**
List all API keys, service accounts, and environment variables needed. Include a checklist of third-party accounts to create before development begins. This ensures the builder doesn't get blocked mid-implementation.

### Optional Sections (Include If Discussed)

**Revenue Model & Pricing** — How the product makes money, pricing tiers, margin estimates.

**Go-to-Market Strategy** — How users will discover the product, launch plan, growth channels.

**Success Metrics / KPIs** — North star metric, core metrics with targets, business health indicators.

**Hypotheses & Assumptions** — Key bets being made, how to validate them, what would trigger a pivot.

**Competitive Reference** — Brief comparison table of alternatives (not a full competitive analysis).

**API Integrations** — For each third-party service: what it does, key endpoints or features used, authentication method, and the integration flow. Include only when the product has external integrations beyond the core stack.

## Formatting Rules

- Use markdown throughout. Headers, tables, bullet lists, code blocks.
- Keep language concise. Bullets over paragraphs. Every sentence should earn its place.
- Use tables for structured comparisons (features, tech stack, risks, pricing).
- User flows use indented arrow notation, not Mermaid or ASCII diagrams.
- Code blocks for schemas, environment variables, and configuration.
- Mark all assumptions and recommendations explicitly so the user can verify.
- Include a table of contents at the top with anchor links.
- End with: *"This PRD is a living document. Update it as you build, learn, and iterate."*

## Reference Material

For guidance on what makes a PRD effective for AI coding agents, see `${CLAUDE_PLUGIN_ROOT}/references/ai_prd_best_practices.md`.

For a complete example PRD showing the expected output format and depth, see `${CLAUDE_PLUGIN_ROOT}/examples/sample_prd.md`.
