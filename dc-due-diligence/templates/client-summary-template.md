# Client Summary Template

This template defines the structure for the client-facing summary document. The client summary is a standalone deliverable designed for the deal presenter -- the person who brought the opportunity to Data Canopy. It draws from the executive summary and research reports but is reframed for an external audience.

**Key difference from the executive summary:** The executive summary is an internal evaluation document with detailed scoring, confidence percentages, traffic light indicators, and cross-report conflict analysis. The client summary is an external communication that presents findings professionally without exposing Data Canopy's internal scoring methodology. It focuses on what was found, what looks strong, what needs attention, and what questions need answering.

## When This Template Is Used

The client summary agent reads the completed `EXECUTIVE_SUMMARY.md` and the 10 research reports, then produces a `CLIENT_SUMMARY.md` in the opportunity folder. This runs as the final step in the pipeline, after the executive summary is complete.

## Template Structure

The client summary must follow this exact structure:

```markdown
# Due Diligence Summary: [Opportunity Name]

**Date:** [Current date in YYYY-MM-DD format]
**Prepared for:** [Deal presenter name or organization, if known from broker documents; otherwise omit this line]
**Prepared by:** Data Canopy

---

## Overview

[2-3 paragraphs providing context on what was analyzed and how. Cover:
- What the opportunity is (location, site type, stated capacity, primary use case if known)
- What Data Canopy reviewed (number of source documents, types of documents -- agreements, permits, financial materials, site plans, etc.)
- The scope of the analysis (which domains were evaluated -- power, connectivity, land and zoning, environmental, commercial terms, ownership, water and cooling, natural gas, market conditions, and cross-domain risk assessment)

Do not mention tier classifications, scoring rubrics, confidence percentages, or internal methodology. Present the analysis as a professional review of the opportunity's merits and risks.]

---

## Recommendation

**[Pursue / Proceed with Caution / Pass]**

[2-4 sentences summarizing the recommendation in plain business language. Always lead with genuine appreciation for what the opportunity offers before raising any conditions or concerns. Frame the recommendation around the opportunity's strengths first:
- For Pursue: Express enthusiasm for the opportunity's strengths and note any minor items remaining to finalize.
- For Proceed with Caution: Appreciate what is promising about the opportunity and express interest in resolving specific items so Data Canopy can move forward with confidence.
- For Pass: Acknowledge the opportunity's merits and thank the presenter for bringing it forward. Explain what would need to change for Data Canopy to revisit -- frame as openness to future engagement, not a closed door.

Do not reference tier numbers, score labels (High/Medium/Low), or internal scoring logic. Translate the verdict into business reasoning: "Data Canopy appreciates the opportunity to review this site and sees a clear path to adequate power and legal permissibility for data center use" rather than "All Tier 1 domains scored High."]

---

## Key Findings

[Organized presentation of the most important findings from the analysis. This section replaces the internal executive summary's scored breakdown with a narrative organized by importance -- infrastructure fundamentals first, then deal-specific factors, then supporting context.]

### Infrastructure Fundamentals

[Findings related to power, connectivity, and land/zoning -- the factors that determine whether the site can physically and legally operate as a data center. Present 3-6 bullet points covering the most important verified facts and any concerns in these areas.

For each finding:
- **[Finding title]** -- [1-2 sentences describing the finding and its significance. Reference specific data points -- capacity figures, agreement status, timeline dates -- where available. If a claim could not be independently verified, say so.]

Example:
- **Power capacity** -- The utility has reserved 20 MW for this site under a signed interconnection agreement, with an energization timeline of Q3 2026. Grid upgrades required to deliver this capacity are included in the utility's current capital plan.
- **Zoning status** -- The site is zoned for industrial use, which permits data center operations by right. No variance or special use permit is required.]

### Deal Factors

[Findings related to environmental conditions, commercial terms, and ownership -- the factors that determine whether the deal is attractive and executable. Present 3-6 bullet points covering the most important findings.

For each finding:
- **[Finding title]** -- [1-2 sentences describing the finding and its significance.]

Example:
- **Lease terms** -- A letter of intent outlines a 20-year NNN lease with two 5-year renewal options. Rent escalation is tied to CPI with a 3% annual cap.
- **Ownership verification** -- The property owner matches the counterparty in the LOI, with no liens or encumbrances on the title.]

### Supporting Context

[Findings related to water/cooling, natural gas, and market conditions -- background that informs the risk profile and negotiation strategy. Present 2-4 bullet points. These findings provide useful context but are not the primary drivers of the recommendation.

For each finding:
- **[Finding title]** -- [1-2 sentences describing the finding and its relevance.]

Example:
- **Market conditions** -- Three comparable data center transactions have closed in this market within the past 18 months, with pricing consistent with the terms proposed here.
- **Water availability** -- The region has adequate municipal water supply with no drought restrictions currently in effect.]

---

## Items Requiring Attention

[Items where Data Canopy would appreciate additional context or documentation to move forward with confidence. These are organized by urgency, not by internal tier classification. Frame each item with curiosity and partnership -- Data Canopy is raising these because it is interested and wants to find a way to make the deal work.

For each item:
- **[Item title]** -- [2-3 sentences framed with curiosity. Use language like "Data Canopy would appreciate additional context on..." or "It would be helpful to understand..." Be specific: "Data Canopy would appreciate additional context on how the $4.2M grid upgrade cost is allocated between the parties, as this would help complete the financial assessment" rather than "There are some cost concerns."]

Present the most urgent items first -- items that would help Data Canopy feel confident about whether the site can function as a data center, followed by items related to deal terms and execution, followed by background items.

3-8 items total. If the analysis found no significant concerns, state: "Data Canopy did not identify any items requiring immediate attention. The questions below would help strengthen confidence in the opportunity."]

---

## Questions

[Questions where additional information from the deal presenter would help Data Canopy provide a more complete assessment. These questions are drawn from all domain analyses and represent areas where the deal presenter or property owner may be able to provide helpful context.

Present questions in order of importance, without tier labels or domain attribution. Each question should be self-explanatory to someone unfamiliar with Data Canopy's analysis process. Frame the explanation for each question in terms of how the answer helps Data Canopy build a stronger picture -- not as a prerequisite or blocker.

For each question:
1. **[Question text]** -- [1 sentence explaining how the answer would help Data Canopy's assessment.]

5-12 questions total. If the opportunity is well-documented and few questions remain, fewer is acceptable.

Example:
1. **Has the utility issued a binding interconnection agreement, or is the current capacity reservation non-binding?** -- Having clarity on this would help Data Canopy assess the security of the 20 MW allocation.
2. **Can you help us understand how the $4.2M grid upgrade cost is allocated between landlord and tenant?** -- This would allow Data Canopy to complete its assessment of the capital required to bring the site online.
3. **Is the Q3 2026 energization timeline contingent on any approvals beyond the substation upgrade?** -- Understanding the full timeline would help Data Canopy plan around the project schedule.]

---

## Next Steps

[3-5 concrete next steps framed as collaborative invitations -- things the deal presenter can help with to move the evaluation forward together. Use warm, inviting language rather than bare imperatives.

For each step:
- [Collaborative request in 1-2 sentences. Use framing like "It would be helpful to share..." or "When available, providing X would help Data Canopy..." rather than directive verbs like "Provide..." or "Confirm..."]

Example:
- It would be helpful to share the cost allocation agreement for the grid upgrade, or to confirm how the upgrade cost is expected to be handled between the parties.
- When convenient, scheduling a call to discuss the backup power strategy and timeline for natural gas delivery would help Data Canopy refine its assessment.
- If available, sharing any updated utility correspondence regarding the Q3 2026 energization timeline would be appreciated.]

---

*This summary is based on Data Canopy's independent analysis of [count] source documents provided for this opportunity. Detailed findings for each domain are available upon request.*
```

---

## Writing Style

The client summary is an external communication. Every word reflects on Data Canopy's professionalism and analytical rigor.

### Tone

- **Professional and approachable.** Write as a consulting firm that is genuinely excited about the opportunity and eager to find a way to make it work. The tone should be warm, clear, and confident -- not casual, not academic, not sales-oriented. The document should read as if Data Canopy wants to partner with the deal presenter and is enthusiastic about what the site offers.
- **Curiosity-driven, not demanding.** The deal presenter is a potential partner Data Canopy wants to work with. Frame concerns and information gaps with curiosity: "Data Canopy would appreciate additional context on..." or "It would be helpful to understand..." rather than declarative statements like "The analysis identified several items that would benefit from additional documentation." The reader should feel that Data Canopy is asking because it is interested, not because it is testing them.
- **Measured confidence.** State what the analysis found, what it could verify, and what remains uncertain. Do not overstate conclusions or hedge excessively.
- **Partnership-first principle.** The entire document should read as if Data Canopy is genuinely excited about the opportunity and wants to find a way to make it work, while being transparent about what it needs to get comfortable. Lead with what is strong before raising what needs attention.

### What to Exclude

The following elements are internal to Data Canopy's evaluation process and must NOT appear in the client summary:

- **Scoring labels** (High / Medium / Low)
- **Tier classifications** (Tier 1, Tier 2, Tier 3, Critical, Important, Context)
- **Confidence percentages** (65%, 40%, etc.)
- **Traffic light indicators** (GREEN / YELLOW / RED)
- **Internal methodology references** (scoring rubric, agent reports, validation rules)
- **Agent names or pipeline details** (Power agent, Risk Assessment agent, Wave 1/2/3)
- **Cross-report conflict analysis** (present the resolved finding, not the internal debate)
- **Document safety protocol references**
- **Deal-breaker language from the internal framework** (use plain business language instead)

### What to Include

- **Specific data points** -- MW capacity, dollar amounts, dates, document names, entity names
- **Verification status in plain language** -- "independently confirmed" or "stated in broker documents but not independently verified"
- **Actionable next steps** -- what the deal presenter can do to move things forward
- **Balanced findings** -- strengths and concerns presented with equal weight
- **Clear recommendation** -- the verdict translated into business language

### Formatting

- Use horizontal rules (`---`) between major sections for clean visual separation
- Bold key terms and finding titles for scanability
- Numbered list for questions (implies priority order)
- Bulleted list for findings and next steps
- No emoji
- Keep the total document length to roughly 2-4 pages when rendered (significantly shorter than the executive summary)

---

## Output File

The client summary is written to:

```
[opportunity-folder]/CLIENT_SUMMARY.md
```

This file sits alongside the `EXECUTIVE_SUMMARY.md` in the opportunity folder root. The executive summary is the internal document; the client summary is the external deliverable.

---

## Source Document Count

To report the number of source documents analyzed, check the manifest file:
```
${OPPORTUNITY_FOLDER}/_converted/manifest.json
```
Count the total files in the manifest. If the manifest does not exist, state "the provided documents" instead of a specific count.

---

## Relationship to Executive Summary

The client summary draws from the executive summary but is not a shortened copy of it. The transformation requires:

1. **Removing internal scoring framework** -- Replace scored categories with narrative findings organized by importance
2. **Translating tier language** -- "Tier 1 Critical domains" becomes "infrastructure fundamentals"; "Tier 2 Important domains" becomes "deal factors"; "Tier 3 Context domains" becomes "supporting context"
3. **Reframing concerns as curiosity-based collaborative items** -- Internal "Critical Concerns" become "Items Requiring Attention" framed with curiosity and partnership language
4. **Condensing detail** -- The executive summary's 10-section detailed findings become a focused set of key findings organized by importance
5. **Aggregating questions** -- The tiered Key Questions from the executive summary become a single numbered list without tier labels, ordered by importance
6. **Adding next steps** -- Concrete collaborative actions the deal presenter can take, which do not appear in the internal executive summary
