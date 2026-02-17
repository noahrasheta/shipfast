# Scoring Rubric

This rubric defines how to translate each agent's research report into a High / Medium / Low confidence rating and how to combine those ratings into an overall verdict (Pursue / Proceed with Caution / Pass). The executive summary generator applies this rubric to produce consistent, repeatable scores across all opportunities.

---

## How to Read an Agent Report for Scoring

Every agent report contains structured data points that map to the scoring criteria below:

- **Status indicator**: GREEN, YELLOW, or RED -- the agent's own assessment of the domain
- **Confidence score**: 0-100% -- the agent's confidence in its analysis
- **Finding verification statuses**: Verified, Partially Verified, Unverified, Not Found
- **Risk severity ratings**: Critical, High, Medium, Low
- **Due diligence gaps**: Missing documents or data the agent could not obtain

The rubric uses these data points along with the substantive content of each finding to assign a category score.

---

## Handling Missing or Incomplete Reports

If an agent report is missing entirely or failed validation:

- **Score the category as Low** with the rationale: "No research report was produced for this domain. The category cannot be assessed."
- **Note the gap prominently** in the executive summary so stakeholders know this area was not analyzed.
- A missing report for a critical domain (Power, Land/Zoning, Ownership) should weigh heavily in the overall verdict.

If an agent report exists but is incomplete (missing required sections or very short):

- **Score based on whatever data is present**, but default toward Low if key sections (Findings, Risks) are missing.
- **Note the incompleteness** in the rationale: "Report was incomplete; scoring is based on partial data."

---

## Category Scoring Criteria

### 1. Power

Evaluates secured electrical capacity, utility interconnection status, delivery timelines, and redundancy design.

| Score | Criteria |
|-------|----------|
| **High** | Secured capacity meets or exceeds the site's stated needs. Signed interconnection agreement exists. Utility provider and grid connection are verified. Delivery timeline is credible and within 24 months. Redundancy design (N+1 or better) is documented. Agent status is GREEN. No Critical or High severity risks. Confidence score is 65% or above. |
| **Medium** | Capacity is available but interconnection agreement is pending, conditional, or partially executed. Delivery timeline has uncertainties (grid upgrades required, cost allocation unresolved). Some claims could not be independently verified. Redundancy design is mentioned but not fully detailed. Agent status is YELLOW. No Critical risks but may have High severity risks. Confidence score is 40-64%. |
| **Low** | Capacity claims cannot be verified or are contradicted by external sources. No evidence of an interconnection agreement. Timeline appears unrealistic or is missing. Critical infrastructure gaps (no path to power, unallocated costs exceeding $5M without resolution). Agent status is RED, or confidence score is below 40%. Any Critical severity risk is present. |

### 2. Connectivity

Evaluates fiber carrier access, route diversity, carrier neutrality, and network infrastructure.

| Score | Criteria |
|-------|----------|
| **High** | Multiple fiber carriers confirmed with verified presence. Route diversity exists (2+ physically separate paths). Carrier-neutral access is verified or the site is within an established carrier hotel / meet-me room. Metro and long-haul connectivity are both available. Agent status is GREEN. Confidence score is 65% or above. |
| **Medium** | At least one carrier confirmed, but route diversity is limited or unverified. Carrier neutrality is claimed but not independently verified. Fiber construction may be required (lit building not confirmed). Agent status is YELLOW. Confidence score is 40-64%. |
| **Low** | No carrier presence verified. No evidence of fiber infrastructure at or near the site. Route diversity does not exist. Connectivity claims are contradicted or entirely unverifiable. Site appears to be in a connectivity desert. Agent status is RED, or confidence score is below 40%. Any Critical severity risk is present. |

### 3. Water & Cooling

Evaluates water rights and supply, cooling system design, water scarcity risk, and environmental impact of water use.

| Score | Criteria |
|-------|----------|
| **High** | Water supply is secured through agreements or municipal connection with adequate capacity. Cooling design is documented and appropriate for the climate (air-cooled in water-scarce regions, or water-cooled with secured supply). Water scarcity risk is low for the region. No Critical or High severity risks. Agent status is GREEN. Confidence score is 65% or above. |
| **Medium** | Water supply is available but agreements are pending or capacity is unconfirmed. Cooling design is described but not fully engineered. Water scarcity is moderate or the cooling approach may face regional constraints. Agent status is YELLOW. Confidence score is 40-64%. |
| **Low** | No water supply agreement exists and the region has documented scarcity issues. Cooling design is absent, inappropriate for the climate, or depends on an unsecured water source. Water rights are contested or unavailable. Agent status is RED, or confidence score is below 40%. Any Critical severity risk is present. |

### 4. Land, Zoning & Entitlements

Evaluates zoning compliance, permit status, building readiness, and entitlement progress.

| Score | Criteria |
|-------|----------|
| **High** | Current zoning permits data center use (by right, no variance needed). Key building permits are obtained or in progress with no significant opposition. The site is ready for development (existing structure or cleared land with utilities). Entitlement process is complete or nearly complete. Agent status is GREEN. Confidence score is 65% or above. |
| **Medium** | Zoning allows data center use with conditions (special use permit, conditional use approval needed). Permits are in early stages but the path is clear and precedent exists. Some entitlement steps remain. Agent status is YELLOW. Confidence score is 40-64%. |
| **Low** | Zoning does not permit data center use and a rezoning or variance is required with uncertain outcome. Permit applications face known opposition or regulatory barriers. Entitlement timeline is unknown or extends beyond 24 months. Zoning verification could not be completed. Agent status is RED, or confidence score is below 40%. Any Critical severity risk is present. |

### 5. Ownership & Control

Evaluates verified property ownership, owner background, chain of title, and middleman indicators.

| Score | Criteria |
|-------|----------|
| **High** | Property owner is verified through public records and matches the counterparty in the deal. No middleman indicators detected. Owner has a clean background (no material litigation, no financial distress signals). Chain of title is clear. Agent status is GREEN. Confidence score is 65% or above. |
| **Medium** | Owner identity is partially verified but some gaps remain (e.g., entity registered but no public records match, or owner verified but entity structure is complex). Minor litigation or background concerns that are not deal-breaking. Possible middleman indicators but the entity may have legitimate authority. Agent status is YELLOW. Confidence score is 40-64%. |
| **Low** | Owner cannot be verified through public records. Middleman indicators are strong (entity has no apparent connection to the property, recently formed shell company, no operating history). Active material litigation against the owner or property. Ownership disputes or liens that could block the transaction. Agent status is RED, or confidence score is below 40%. Any Critical severity risk is present. |

### 6. Environmental

Evaluates natural hazard risk, environmental compliance, contamination history, and climate resilience.

| Score | Criteria |
|-------|----------|
| **High** | Site is not in a FEMA flood zone (Zone X or equivalent) or has verified flood mitigation. Seismic, tornado, and wildfire risk are low for the region. No known contamination (Phase I ESA completed or equivalent). Environmental compliance requirements are manageable. Agent status is GREEN. Confidence score is 65% or above. |
| **Medium** | Site has moderate natural hazard exposure (FEMA Zone B/C, moderate seismic zone, or tornado-prone region with standard construction codes). Environmental compliance is achievable but requires specific permits or mitigation measures. Phase I ESA is needed but no known contamination indicators. Agent status is YELLOW. Confidence score is 40-64%. |
| **Low** | Site is in a high-risk flood zone (FEMA Zone A or V), active seismic zone, or has known contamination requiring remediation. Environmental regulations may prohibit or severely constrain data center operations. Phase II ESA indicates contamination, or brownfield status creates financial liability. Agent status is RED, or confidence score is below 40%. Any Critical severity risk is present. |

### 7. Commercials

Evaluates land cost, power cost, lease terms, and financial structure of the deal.

| Score | Criteria |
|-------|----------|
| **High** | Deal terms are clearly documented (LOI, MOU, or lease with specific terms). Land and power costs are within market ranges (as benchmarked by the agent). Lease structure is standard for data center use (NNN or similar). Financial terms include reasonable contingencies and milestones. No Critical or High severity financial risks. Agent status is GREEN. Confidence score is 65% or above. |
| **Medium** | Some deal terms are documented but key items remain to be negotiated (rent escalations, TI allowance, power cost pass-through). Pricing is within a reasonable range but above or below market benchmarks. Some financial terms are missing or vague. Agent status is YELLOW. Confidence score is 40-64%. |
| **Low** | No formal deal terms exist (no LOI, MOU, or draft lease). Pricing is significantly above market or below market in a way that suggests missing costs. Critical financial terms are absent (no defined rent, no power cost structure, no term length). Financial red flags are present (unrealistic projections, hidden costs, unfavorable cost allocation). Agent status is RED, or confidence score is below 40%. Any Critical severity risk is present. |

### 8. Natural Gas

Evaluates gas supply agreements, pipeline access, on-site generation feasibility, and gas pricing.

| Score | Criteria |
|-------|----------|
| **High** | Gas supply agreement is in place or the site has confirmed pipeline access at adequate capacity. On-site generation feasibility is supported by documented infrastructure (existing pipeline, confirmed pressure/capacity). Gas pricing is within market ranges. Air quality permits for gas generation are obtainable. Agent status is GREEN. Confidence score is 65% or above. |
| **Medium** | Gas supply is available in the area but no specific agreement exists for this site. Pipeline access requires a lateral extension or capacity upgrade. On-site generation is feasible but permitting or infrastructure details are incomplete. Agent status is YELLOW. Confidence score is 40-64%. |
| **Low** | No gas supply infrastructure exists near the site. Pipeline access would require major construction with uncertain feasibility or cost. On-site gas generation is not feasible due to supply, permitting, or infrastructure constraints. Gas claims in broker documents are contradicted or cannot be verified. Agent status is RED, or confidence score is below 40%. Any Critical severity risk is present. |

**Special note for Natural Gas:** If the opportunity does not rely on natural gas for power generation or backup, and no gas-related claims are made in the broker documents, score this category as **High** with the rationale: "Natural gas is not a factor in this opportunity's infrastructure plan. No gas-related risks identified." Do not penalize an opportunity for the absence of gas infrastructure when gas is not part of the design.

### 9. Market Comparables

Evaluates comparable transactions, market rates, competitive landscape, and market trends.

| Score | Criteria |
|-------|----------|
| **High** | Comparable transactions exist in the same market at similar scale. Market rates support the deal's pricing assumptions. The competitive landscape shows healthy demand that justifies new supply. Market trends are favorable (growing absorption, stable or rising rates). Agent status is GREEN. Confidence score is 65% or above. |
| **Medium** | Some comparable transactions exist but may differ in scale, timing, or specifics. Market rates are available but the deal's terms deviate from benchmarks in ways that need explanation. Competitive landscape shows moderate supply that could affect lease-up. Agent status is YELLOW. Confidence score is 40-64%. |
| **Low** | No comparable transactions found in the market. Market data is sparse or contradicts the deal's assumptions. The competitive landscape shows oversupply or declining demand. Market trends are unfavorable (falling rates, rising vacancy, excess capacity under construction). Agent status is RED, or confidence score is below 40%. Any Critical severity risk is present. |

### 10. Risk Assessment

Evaluates the cross-domain risk synthesis, deal-breaker identification, and overall risk profile.

| Score | Criteria |
|-------|----------|
| **High** | No deal-breakers identified. Cross-domain risks are few and manageable. Most domain reports show GREEN or YELLOW status. The risk profile is typical for a data center development at this stage. Agent status is GREEN. Confidence score is 65% or above. |
| **Medium** | No clear deal-breakers, but significant cross-domain risks exist that need resolution. Multiple domains have YELLOW status or unresolved dependencies. Timeline misalignments or unresolved cost allocations span multiple domains. Agent status is YELLOW. Confidence score is 40-64%. |
| **Low** | Deal-breakers identified, or multiple High-severity cross-domain risks compound to make the opportunity very risky. Critical infrastructure dependencies are unresolved (e.g., power depends on gas that is not secured). Multiple domains show RED status. Verification failures are systemic. Agent status is RED, or confidence score is below 40%. Any Critical severity risk flagged as a deal-breaker. |

---

## Overall Verdict Logic

The overall verdict is determined by evaluating the 10 category scores together, with extra weight given to categories that are foundational to whether a data center can operate at the site.

### Category Weights

Not all categories carry equal weight in the final verdict. Some categories are prerequisites -- if they fail, nothing else matters. Others are important but can often be resolved through negotiation or investment.

**Tier 1 -- Prerequisites (any Low score here strongly pushes toward Pass):**
- Power
- Land, Zoning & Entitlements
- Ownership & Control

**Tier 2 -- Core Infrastructure (Low scores here push toward Proceed with Caution or Pass):**
- Connectivity
- Water & Cooling
- Environmental

**Tier 3 -- Deal Quality (Low scores here are concerning but potentially resolvable):**
- Commercials
- Natural Gas
- Market Comparables
- Risk Assessment

### Verdict: Pursue

All of the following must be true:

- No Tier 1 category scores Low
- No more than one Tier 2 category scores Low
- No more than two total categories score Low across all tiers
- The Risk Assessment category does not score Low
- No deal-breakers were identified by the Risk Assessment agent

In practice, a "Pursue" verdict means the opportunity has solid fundamentals across all critical areas and the remaining concerns are manageable within normal due diligence.

### Verdict: Proceed with Caution

The opportunity does not meet the criteria for Pursue, and all of the following are true:

- No more than one Tier 1 category scores Low
- No more than three total categories score Low
- If the Risk Assessment scores Low, it must be due to compounding Medium-severity risks, not identified deal-breakers
- There is a plausible resolution path for each Low-scoring category (i.e., the Low score results from missing information or pending agreements, not from verified negative findings)

In practice, "Proceed with Caution" means the opportunity has potential but specific issues need to be resolved before commitment. The summary must list what needs to happen for each Low-scoring category.

### Verdict: Pass

Any of the following triggers a Pass verdict:

- Two or more Tier 1 categories score Low
- Four or more total categories score Low
- The Risk Assessment agent identified a deal-breaker
- A Tier 1 category scores Low due to verified negative findings (not just missing data) -- for example, zoning explicitly prohibits data center use, or the property owner is embroiled in litigation that blocks the transaction
- Multiple Low-scoring categories have no plausible resolution path

In practice, "Pass" means the opportunity has fundamental problems that cannot be reasonably resolved through further diligence or negotiation.

### Edge Cases and Judgment Calls

When the category scores fall between clear-cut thresholds, the summary generator should apply these tiebreaker principles:

1. **Missing data vs. verified negative findings:** A Low score due to missing information (agent could not verify claims because data was unavailable) is less severe than a Low score due to contradicted claims or confirmed problems. Favor "Proceed with Caution" when Low scores stem from information gaps that can be filled. Favor "Pass" when Low scores stem from confirmed problems.

2. **Cluster effect:** If multiple related categories score Low (e.g., Power, Natural Gas, and Connectivity are all Low), treat this as more severe than the same number of Low scores across unrelated categories. Related failures often indicate a systemic location problem rather than individual fixable issues.

3. **Risk Assessment as tiebreaker:** When the overall picture is ambiguous, defer to the Risk Assessment agent's recommendation. If the Risk Assessment agent's overall status is GREEN but other categories drag the score down, lean toward the more favorable verdict. If the Risk Assessment agent identifies compound risks that individual categories missed, lean toward the more cautious verdict.

4. **Recency and actionability:** If a Low-scoring category is Low because agreements are "pending" with a clear near-term resolution date, this is less concerning than a Low score with no path to resolution.

5. **Phased opportunities:** When an opportunity has distinct development phases with materially different risk profiles, the verdict should reflect the most executable phase while characterizing later phases as contingent upside. For example, if Phase I (12 MW) has secured power and a credible timeline but Phase II (100+ MW) depends on unverified gas supply and conceptual utility agreements, the verdict should note that Phase I may be executable even if expansion capacity is speculative. The summary should explicitly distinguish between "firm, contracted" elements and "planned, uncontracted" elements so stakeholders can underwrite the deal based on what is real today.

6. **Information gap vs. verified negative:** A Low score because key documents are missing (information gap) is fundamentally different from a Low score because available evidence reveals confirmed problems (verified negative). The verdict rationale must explicitly state which type of Low is present for each Low-scoring category. Information gaps that have a clear resolution path (e.g., "obtain the title report") are less severe than verified negatives (e.g., "the title report shows active liens"). When all Low scores stem from information gaps with clear resolution paths, lean toward "Proceed with Caution" rather than "Pass."

---

## Quick Reference Table

| Category | High | Medium | Low |
|----------|------|--------|-----|
| Power | Secured capacity, signed interconnection, verified utility, credible timeline, N+1+ redundancy | Capacity available but agreements pending, some verification gaps, timeline uncertainties | Unverified or contradicted capacity, no interconnection evidence, unrealistic timeline |
| Connectivity | Multiple verified carriers, route diversity, carrier-neutral, metro + long-haul | One carrier confirmed, limited diversity, fiber build may be needed | No verified carrier presence, no fiber infrastructure, connectivity desert |
| Water & Cooling | Secured supply, appropriate cooling design, low scarcity risk | Supply available but unconfirmed, cooling described but not engineered, moderate scarcity | No supply agreement in scarce region, absent or inappropriate cooling design |
| Land & Zoning | By-right zoning, permits obtained or progressing, site ready | Conditional use possible, permits in early stages, entitlements in progress | Rezoning required with uncertain outcome, opposition, or 24+ month timeline |
| Ownership | Verified owner, clean background, clear title, no middleman | Partially verified, complex entity, minor concerns | Unverifiable owner, strong middleman signals, active litigation, liens |
| Environmental | Low hazard zone, no contamination, manageable compliance | Moderate hazard exposure, permits needed, no known contamination | High-risk flood/seismic, known contamination, regulations may block operations |
| Commercials | Clear documented terms, market-rate pricing, standard structure | Some terms documented, deviations from benchmarks, key items TBD | No formal terms, pricing far from market, critical terms absent |
| Natural Gas | Supply agreement or confirmed access, feasible generation, market pricing | Supply available in area, lateral needed, generation feasible but incomplete | No supply infrastructure, major construction needed, not feasible |
| Market Comparables | Comparables exist, market supports pricing, favorable trends | Some comparables, deviations need explanation, moderate supply | No comparables, oversupply, unfavorable trends |
| Risk Assessment | No deal-breakers, few cross-domain risks, typical profile | No deal-breakers, significant cross-domain risks needing resolution | Deal-breakers identified, compounding risks, systemic failures |

---

## Verdict Quick Reference

| Condition | Verdict |
|-----------|---------|
| 0-1 Low scores, none in Tier 1, no deal-breakers | **Pursue** |
| 2-3 Low scores, at most 1 in Tier 1, resolvable issues, no deal-breakers | **Proceed with Caution** |
| 2+ Tier 1 categories Low, or 4+ total Low, or deal-breakers identified | **Pass** |
