# Scoring Rubric

This rubric defines how to translate each agent's research report into a High / Medium / Low confidence rating and how to combine those ratings into an overall verdict (Pursue / Proceed with Caution / Pass). The executive summary generator applies this rubric to produce consistent, repeatable scores across all opportunities.

The rubric uses **tiered qualitative reasoning** to reflect the reality that not all domains matter equally for a data center investment. Some domains are deal-critical -- a failure there means the site cannot function as a data center. Other domains provide important context but do not determine whether a site is viable. The tiers guide how category scores influence the overall verdict.

---

## Domain Tiers

### Tier 1 -- Critical (Can Sink a Deal Alone)

These domains are prerequisites for a viable data center site. A Low score in any Tier 1 domain is a serious red flag that pushes the verdict toward Pass, because without these fundamentals the site cannot operate as a data center regardless of how strong other domains look.

| Domain | Why It's Critical |
|--------|-------------------|
| **Power** | A data center without reliable, adequate power cannot operate. Power is the single most important domain in the entire evaluation. A site with weak power prospects has no path to viability, no matter how attractive the land, zoning, or pricing may be. When Power scores Low, treat it as the strongest possible signal toward Pass. |
| **Land, Zoning & Entitlements** | If the site cannot legally be used as a data center, nothing else matters. Zoning prohibitions, permit barriers, or entitlement failures block the entire project. Unlike power or connectivity problems that might be solved with investment, a zoning prohibition may have no resolution path at all. |
| **Connectivity** | A data center without fiber connectivity cannot serve customers. While fiber can sometimes be built to a site, the cost, timeline, and feasibility of that build determine whether the site is realistic. A site with no verified carrier presence and no credible path to connectivity is not a viable data center location. |

**Power holds a special position even within Tier 1.** When evaluating an opportunity where Power scores Low but other Tier 1 domains score well, the verdict should still lean strongly toward Pass. Power is the one domain where a Low score -- especially from verified negative findings rather than missing data -- is nearly always disqualifying. A site with excellent zoning and connectivity but no credible power path is not worth pursuing.

### Tier 2 -- Important (Matters, But Won't Independently Kill a Deal)

These domains materially affect the attractiveness and risk profile of a deal, but a Low score in one of these domains alone does not make the site unviable. Problems here can often be resolved through negotiation, investment, or further diligence. However, multiple Low scores across Tier 2 domains compound and can collectively push a verdict from Proceed with Caution to Pass.

| Domain | Why It Matters |
|--------|----------------|
| **Environmental** | Natural hazard exposure, contamination, and regulatory compliance affect long-term viability and insurance costs. A site in a flood zone or with contamination history is riskier but not necessarily unviable -- mitigation measures, proper engineering, and appropriate insurance can address many environmental concerns. |
| **Commercials** | Deal terms, pricing, and financial structure determine whether the investment makes economic sense. Poor commercial terms are a negotiation problem, not a site viability problem. Even unfavorable terms can be renegotiated if the site fundamentals are strong. |
| **Ownership & Control** | Verified ownership and clean title are important for deal execution, but ownership issues are often resolvable through legal channels. A complex entity structure or minor litigation history does not make a site unviable -- it makes the deal more complex and potentially slower to close. However, active ownership disputes or strong middleman indicators warrant serious caution. |

### Tier 3 -- Context (Provides Background, Doesn't Drive Pass/Fail)

These domains provide useful context for understanding the opportunity but do not determine whether the site is viable for data center use. Low scores here inform the risk profile and may highlight additional costs or limitations, but they should not be the reason a deal is rejected.

| Domain | What It Contributes |
|--------|---------------------|
| **Water & Cooling** | Water supply and cooling design affect operational costs and sustainability posture, but modern data centers have multiple cooling technology options. A site with limited water access can use air-cooled or hybrid systems. Water constraints add cost and design complexity -- they do not make a site unviable. |
| **Natural Gas** | Gas supply matters only when the opportunity relies on gas-fired generation for primary or backup power. When gas is not part of the plan, this domain is irrelevant. Even when gas is needed, alternative backup power strategies (diesel, battery) exist. A Low gas score adds risk to the power strategy but does not independently disqualify a site. |
| **Market Comparables** | Market data informs pricing expectations and demand validation, but the absence of comparable transactions does not mean a deal is bad -- it may mean the market is emerging. Market context shapes negotiation strategy and underwriting assumptions, not go/no-go decisions. |

### Risk Assessment -- Synthesis Layer (Not a Tier)

The Risk Assessment domain is not assigned to a tier because it is not an independent evaluation of the site. It is a cross-domain synthesis that identifies compound risks and deal-breakers by reading all other domain reports together. Its score reflects the quality and severity of cross-domain risk patterns, not the viability of any single infrastructure element.

The Risk Assessment score carries weight in the verdict through a different mechanism: if the Risk Assessment agent identifies deal-breakers, those deal-breakers directly trigger a Pass verdict regardless of all other scores. If the Risk Assessment shows compounding risks across multiple domains, that pattern informs the verdict reasoning even when individual domain scores might look acceptable in isolation.

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
- A missing report for a Tier 1 domain (Power, Land/Zoning, Connectivity) should be treated with the same gravity as a Low score in that domain -- the inability to assess a critical domain is itself a serious concern.

If an agent report exists but is incomplete (missing required sections or very short):

- **Score based on whatever data is present**, but default toward Low if key sections (Findings, Risks) are missing.
- **Note the incompleteness** in the rationale: "Report was incomplete; scoring is based on partial data."

---

## Category Scoring Criteria

### 1. Power (Tier 1 -- Critical)

Evaluates secured electrical capacity, utility interconnection status, delivery timelines, and redundancy design. **This is the single most important domain in the evaluation.**

| Score | Criteria |
|-------|----------|
| **High** | Secured capacity meets or exceeds the site's stated needs. Signed interconnection agreement exists. Utility provider and grid connection are verified. Delivery timeline is credible and within 24 months. Redundancy design (N+1 or better) is documented. Agent status is GREEN. No Critical or High severity risks. Confidence score is 65% or above. |
| **Medium** | Capacity is available but interconnection agreement is pending, conditional, or partially executed. Delivery timeline has uncertainties (grid upgrades required, cost allocation unresolved). Some claims could not be independently verified. Redundancy design is mentioned but not fully detailed. Agent status is YELLOW. No Critical risks but may have High severity risks. Confidence score is 40-64%. |
| **Low** | Capacity claims cannot be verified or are contradicted by external sources. No evidence of an interconnection agreement. Timeline appears unrealistic or is missing. Critical infrastructure gaps (no path to power, unallocated costs exceeding $5M without resolution). Agent status is RED, or confidence score is below 40%. Any Critical severity risk is present. |

### 2. Land, Zoning & Entitlements (Tier 1 -- Critical)

Evaluates zoning compliance, permit status, building readiness, and entitlement progress.

| Score | Criteria |
|-------|----------|
| **High** | Current zoning permits data center use (by right, no variance needed). Key building permits are obtained or in progress with no significant opposition. The site is ready for development (existing structure or cleared land with utilities). Entitlement process is complete or nearly complete. Agent status is GREEN. Confidence score is 65% or above. |
| **Medium** | Zoning allows data center use with conditions (special use permit, conditional use approval needed). Permits are in early stages but the path is clear and precedent exists. Some entitlement steps remain. Agent status is YELLOW. Confidence score is 40-64%. |
| **Low** | Zoning does not permit data center use and a rezoning or variance is required with uncertain outcome. Permit applications face known opposition or regulatory barriers. Entitlement timeline is unknown or extends beyond 24 months. Zoning verification could not be completed. Agent status is RED, or confidence score is below 40%. Any Critical severity risk is present. |

### 3. Connectivity (Tier 1 -- Critical)

Evaluates fiber carrier access, route diversity, carrier neutrality, and network infrastructure.

| Score | Criteria |
|-------|----------|
| **High** | Multiple fiber carriers confirmed with verified presence. Route diversity exists (2+ physically separate paths). Carrier-neutral access is verified or the site is within an established carrier hotel / meet-me room. Metro and long-haul connectivity are both available. Agent status is GREEN. Confidence score is 65% or above. |
| **Medium** | At least one carrier confirmed, but route diversity is limited or unverified. Carrier neutrality is claimed but not independently verified. Fiber construction may be required (lit building not confirmed). Agent status is YELLOW. Confidence score is 40-64%. |
| **Low** | No carrier presence verified. No evidence of fiber infrastructure at or near the site. Route diversity does not exist. Connectivity claims are contradicted or entirely unverifiable. Site appears to be in a connectivity desert. Agent status is RED, or confidence score is below 40%. Any Critical severity risk is present. |

### 4. Environmental (Tier 2 -- Important)

Evaluates natural hazard risk, environmental compliance, contamination history, and climate resilience.

| Score | Criteria |
|-------|----------|
| **High** | Site is not in a FEMA flood zone (Zone X or equivalent) or has verified flood mitigation. Seismic, tornado, and wildfire risk are low for the region. No known contamination (Phase I ESA completed or equivalent). Environmental compliance requirements are manageable. Agent status is GREEN. Confidence score is 65% or above. |
| **Medium** | Site has moderate natural hazard exposure (FEMA Zone B/C, moderate seismic zone, or tornado-prone region with standard construction codes). Environmental compliance is achievable but requires specific permits or mitigation measures. Phase I ESA is needed but no known contamination indicators. Agent status is YELLOW. Confidence score is 40-64%. |
| **Low** | Site is in a high-risk flood zone (FEMA Zone A or V), active seismic zone, or has known contamination requiring remediation. Environmental regulations may prohibit or severely constrain data center operations. Phase II ESA indicates contamination, or brownfield status creates financial liability. Agent status is RED, or confidence score is below 40%. Any Critical severity risk is present. |

### 5. Commercials (Tier 2 -- Important)

Evaluates land cost, power cost, lease terms, and financial structure of the deal.

| Score | Criteria |
|-------|----------|
| **High** | Deal terms are clearly documented (LOI, MOU, or lease with specific terms). Land and power costs are within market ranges (as benchmarked by the agent). Lease structure is standard for data center use (NNN or similar). Financial terms include reasonable contingencies and milestones. No Critical or High severity financial risks. Agent status is GREEN. Confidence score is 65% or above. |
| **Medium** | Some deal terms are documented but key items remain to be negotiated (rent escalations, TI allowance, power cost pass-through). Pricing is within a reasonable range but above or below market benchmarks. Some financial terms are missing or vague. Agent status is YELLOW. Confidence score is 40-64%. |
| **Low** | No formal deal terms exist (no LOI, MOU, or draft lease). Pricing is significantly above market or below market in a way that suggests missing costs. Critical financial terms are absent (no defined rent, no power cost structure, no term length). Financial red flags are present (unrealistic projections, hidden costs, unfavorable cost allocation). Agent status is RED, or confidence score is below 40%. Any Critical severity risk is present. |

### 6. Ownership & Control (Tier 2 -- Important)

Evaluates verified property ownership, owner background, chain of title, and middleman indicators.

| Score | Criteria |
|-------|----------|
| **High** | Property owner is verified through public records and matches the counterparty in the deal. No middleman indicators detected. Owner has a clean background (no material litigation, no financial distress signals). Chain of title is clear. Agent status is GREEN. Confidence score is 65% or above. |
| **Medium** | Owner identity is partially verified but some gaps remain (e.g., entity registered but no public records match, or owner verified but entity structure is complex). Minor litigation or background concerns that are not deal-breaking. Possible middleman indicators but the entity may have legitimate authority. Agent status is YELLOW. Confidence score is 40-64%. |
| **Low** | Owner cannot be verified through public records. Middleman indicators are strong (entity has no apparent connection to the property, recently formed shell company, no operating history). Active material litigation against the owner or property. Ownership disputes or liens that could block the transaction. Agent status is RED, or confidence score is below 40%. Any Critical severity risk is present. |

### 7. Water & Cooling (Tier 3 -- Context)

Evaluates water rights and supply, cooling system design, water scarcity risk, and environmental impact of water use.

| Score | Criteria |
|-------|----------|
| **High** | Water supply is secured through agreements or municipal connection with adequate capacity. Cooling design is documented and appropriate for the climate (air-cooled in water-scarce regions, or water-cooled with secured supply). Water scarcity risk is low for the region. No Critical or High severity risks. Agent status is GREEN. Confidence score is 65% or above. |
| **Medium** | Water supply is available but agreements are pending or capacity is unconfirmed. Cooling design is described but not fully engineered. Water scarcity is moderate or the cooling approach may face regional constraints. Agent status is YELLOW. Confidence score is 40-64%. |
| **Low** | No water supply agreement exists and the region has documented scarcity issues. Cooling design is absent, inappropriate for the climate, or depends on an unsecured water source. Water rights are contested or unavailable. Agent status is RED, or confidence score is below 40%. Any Critical severity risk is present. |

### 8. Natural Gas (Tier 3 -- Context)

Evaluates gas supply agreements, pipeline access, on-site generation feasibility, and gas pricing.

| Score | Criteria |
|-------|----------|
| **High** | Gas supply agreement is in place or the site has confirmed pipeline access at adequate capacity. On-site generation feasibility is supported by documented infrastructure (existing pipeline, confirmed pressure/capacity). Gas pricing is within market ranges. Air quality permits for gas generation are obtainable. Agent status is GREEN. Confidence score is 65% or above. |
| **Medium** | Gas supply is available in the area but no specific agreement exists for this site. Pipeline access requires a lateral extension or capacity upgrade. On-site generation is feasible but permitting or infrastructure details are incomplete. Agent status is YELLOW. Confidence score is 40-64%. |
| **Low** | No gas supply infrastructure exists near the site. Pipeline access would require major construction with uncertain feasibility or cost. On-site gas generation is not feasible due to supply, permitting, or infrastructure constraints. Gas claims in broker documents are contradicted or cannot be verified. Agent status is RED, or confidence score is below 40%. Any Critical severity risk is present. |

**Special note for Natural Gas:** If the opportunity does not rely on natural gas for power generation or backup, and no gas-related claims are made in the broker documents, score this category as **High** with the rationale: "Natural gas is not a factor in this opportunity's infrastructure plan. No gas-related risks identified." Do not penalize an opportunity for the absence of gas infrastructure when gas is not part of the design.

### 9. Market Comparables (Tier 3 -- Context)

Evaluates comparable transactions, market rates, competitive landscape, and market trends.

| Score | Criteria |
|-------|----------|
| **High** | Comparable transactions exist in the same market at similar scale. Market rates support the deal's pricing assumptions. The competitive landscape shows healthy demand that justifies new supply. Market trends are favorable (growing absorption, stable or rising rates). Agent status is GREEN. Confidence score is 65% or above. |
| **Medium** | Some comparable transactions exist but may differ in scale, timing, or specifics. Market rates are available but the deal's terms deviate from benchmarks in ways that need explanation. Competitive landscape shows moderate supply that could affect lease-up. Agent status is YELLOW. Confidence score is 40-64%. |
| **Low** | No comparable transactions found in the market. Market data is sparse or contradicts the deal's assumptions. The competitive landscape shows oversupply or declining demand. Market trends are unfavorable (falling rates, rising vacancy, excess capacity under construction). Agent status is RED, or confidence score is below 40%. Any Critical severity risk is present. |

### 10. Risk Assessment (Synthesis Layer)

Evaluates the cross-domain risk synthesis, deal-breaker identification, and overall risk profile.

| Score | Criteria |
|-------|----------|
| **High** | No deal-breakers identified. Cross-domain risks are few and manageable. Most domain reports show GREEN or YELLOW status. The risk profile is typical for a data center development at this stage. Agent status is GREEN. Confidence score is 65% or above. |
| **Medium** | No clear deal-breakers, but significant cross-domain risks exist that need resolution. Multiple domains have YELLOW status or unresolved dependencies. Timeline misalignments or unresolved cost allocations span multiple domains. Agent status is YELLOW. Confidence score is 40-64%. |
| **Low** | Deal-breakers identified, or multiple High-severity cross-domain risks compound to make the opportunity very risky. Critical infrastructure dependencies are unresolved (e.g., power depends on gas that is not secured). Multiple domains show RED status. Verification failures are systemic. Agent status is RED, or confidence score is below 40%. Any Critical severity risk flagged as a deal-breaker. |

---

## Overall Verdict Logic

The overall verdict is determined by evaluating category scores through the lens of tiered domain importance. The fundamental principle: **Tier 1 domains determine whether a site can function as a data center. Tier 2 domains determine whether the deal is attractive. Tier 3 domains provide context that informs the risk profile but does not drive the go/no-go decision.**

### How Tiers Influence the Verdict

**Tier 1 reasoning:** When evaluating the verdict, ask first: "Can this site physically and legally operate as a data center?" If Power, Land/Zoning, or Connectivity has fundamental problems, the answer is no -- and no amount of favorable Tier 2 or Tier 3 scores changes that. A site with excellent commercial terms, clean environmental history, and strong market fundamentals is worthless if it cannot get power, cannot get zoning approval, or cannot get fiber connectivity.

**Power as the anchor:** Within Tier 1, Power holds a uniquely important position. A Low Power score from verified negative findings (contradicted capacity claims, no interconnection path, unrealistic timelines backed by evidence) is the single strongest signal toward a Pass verdict. When Power scores Low, evaluate whether there is any credible resolution path. If not, the verdict should be Pass regardless of all other scores. If there is a plausible resolution path (e.g., power is available but agreements are pending with a clear timeline), the verdict may be Proceed with Caution -- but only if all other Tier 1 domains are solid.

**Tier 2 reasoning:** After confirming Tier 1 viability, ask: "Is this deal worth doing?" Environmental risks, commercial terms, and ownership clarity determine whether the opportunity is attractive enough to pursue. A Low score in one Tier 2 domain is a concern that adds conditions to the deal -- "proceed, but resolve this first." Multiple Low scores across Tier 2 suggest the deal has enough problems to warrant serious caution even if the site itself is viable.

**Tier 3 reasoning:** Finally, ask: "What does the broader context tell us?" Water/cooling constraints, natural gas availability, and market conditions inform the risk profile and help calibrate expectations. These scores should color the narrative and inform negotiation strategy, but they should not be the reason a deal gets a Pass verdict. A site with excellent Tier 1 and Tier 2 scores should not receive a Pass verdict because market comparables are sparse or natural gas is unavailable.

**Risk Assessment reasoning:** The Risk Assessment score operates differently from domain scores. It does not push toward Pass based on its tier -- instead, it acts as a pattern detector. If the Risk Assessment agent identified deal-breakers through cross-domain analysis that individual domain scores did not capture, those deal-breakers carry decisive weight. If the Risk Assessment score is Low because of compounding medium-severity risks rather than identified deal-breakers, it reinforces caution but does not independently trigger Pass.

### Verdict: Pursue

The opportunity has solid fundamentals across all critical areas. Remaining concerns are manageable within normal due diligence.

All of the following must be true:

- No Tier 1 category scores Low
- No more than one Tier 2 category scores Low, and that Low score has a clear resolution path
- Tier 3 scores do not factor into this threshold (any combination of Tier 3 scores is acceptable for a Pursue verdict, though they should be noted in the summary narrative)
- No deal-breakers were identified by the Risk Assessment agent
- The Risk Assessment category does not score Low due to identified deal-breakers

### Verdict: Proceed with Caution

The opportunity has potential but specific issues need resolution before commitment. The summary must list what needs to happen for each concern area.

The opportunity does not meet the criteria for Pursue, and all of the following are true:

- No more than one Tier 1 category scores Low, and that Low score stems from an information gap with a plausible resolution path (not from verified negative findings)
- If Power is the Tier 1 category scoring Low, there must be a credible path to securing adequate power -- otherwise the verdict is Pass
- No more than two Tier 2 categories score Low
- Tier 3 scores do not independently push the verdict to Pass (they inform the narrative and conditions)
- If the Risk Assessment scores Low, it must be due to compounding medium-severity risks, not identified deal-breakers
- Each Low-scoring Tier 1 or Tier 2 category has a plausible resolution path

### Verdict: Pass

The opportunity has fundamental problems that cannot be reasonably resolved through further diligence or negotiation.

Any of the following triggers a Pass verdict:

- Two or more Tier 1 categories score Low
- Power scores Low due to verified negative findings (not just missing data) with no credible resolution path
- A Tier 1 category scores Low due to verified negative findings that have no resolution path (e.g., zoning explicitly prohibits data center use with no variance process, or no power infrastructure exists within feasible distance)
- The Risk Assessment agent identified a deal-breaker
- All three Tier 2 categories score Low (indicating the deal itself is unattractive even if the site is technically viable)
- A Tier 1 Low score is compounded by multiple Tier 2 Low scores (e.g., Land/Zoning is Low AND both Commercials and Ownership are Low -- suggesting both site and deal problems)

Note that Tier 3 scores alone never trigger a Pass verdict. A site with Low scores in Water/Cooling, Natural Gas, and Market Comparables but strong Tier 1 and Tier 2 scores should receive Pursue or Proceed with Caution, with the Tier 3 concerns noted in the narrative.

### Edge Cases and Judgment Calls

When the category scores do not clearly map to a single verdict, apply these tiebreaker principles:

1. **Missing data vs. verified negative findings:** A Low score due to missing information (agent could not verify claims because data was unavailable) is less severe than a Low score due to contradicted claims or confirmed problems. Favor "Proceed with Caution" when Low scores stem from information gaps that can be filled. Favor "Pass" when Low scores stem from confirmed problems. This distinction is especially important for Tier 1 domains: a Power score of Low because no interconnection agreement was provided (information gap) is qualitatively different from a Power score of Low because the utility confirmed insufficient grid capacity (verified negative).

2. **Cluster effect within tiers:** If multiple domains within the same tier score Low, the effect compounds. Two Tier 2 domains scoring Low is more concerning than one Tier 2 and one Tier 3 domain scoring Low. When Tier 1 and Tier 2 Low scores cluster around the same underlying issue (e.g., Power is Low and Commercials is Low because power costs are unresolved), that shared root cause makes both scores harder to resolve independently.

3. **Cross-tier compounding:** When a Tier 1 Low score is reinforced by related Tier 2 or Tier 3 findings, it strengthens the case for Pass. For example, if Power scores Low and Natural Gas (Tier 3) also scores Low because the backup power strategy depends on gas that is not secured, the power problem is worse than the Tier 1 score alone suggests. Let the Risk Assessment agent's cross-domain analysis guide this reasoning.

4. **Risk Assessment as pattern detector:** When the overall picture is ambiguous, look to the Risk Assessment agent for patterns that individual scores miss. If the Risk Assessment agent's cross-domain analysis reveals compounding risks that are not visible from individual scores, lean toward the more cautious verdict. If the Risk Assessment agent finds the cross-domain picture is cleaner than individual scores suggest, lean toward the more favorable verdict.

5. **Recency and actionability:** If a Low-scoring category is Low because agreements are "pending" with a clear near-term resolution date, this is less concerning than a Low score with no path to resolution. For Tier 1 domains, a pending agreement with a 3-month timeline is very different from a pending agreement with no timeline.

6. **Phased opportunities:** When an opportunity has distinct development phases with materially different risk profiles, the verdict should reflect the most executable phase while characterizing later phases as contingent upside. For example, if Phase I (12 MW) has secured power and a credible timeline but Phase II (100+ MW) depends on unverified gas supply and conceptual utility agreements, the verdict should note that Phase I may be executable even if expansion capacity is speculative. The summary should explicitly distinguish between "firm, contracted" elements and "planned, uncontracted" elements so stakeholders can underwrite the deal based on what is real today.

7. **Information gap vs. verified negative:** A Low score because key documents are missing (information gap) is fundamentally different from a Low score because available evidence reveals confirmed problems (verified negative). The verdict rationale must explicitly state which type of Low is present for each Low-scoring category. Information gaps that have a clear resolution path (e.g., "obtain the title report") are less severe than verified negatives (e.g., "the title report shows active liens"). When all Low scores stem from information gaps with clear resolution paths, lean toward "Proceed with Caution" rather than "Pass."

---

## Quick Reference Table

| Category | Tier | High | Medium | Low |
|----------|------|------|--------|-----|
| Power | 1 - Critical | Secured capacity, signed interconnection, verified utility, credible timeline, N+1+ redundancy | Capacity available but agreements pending, some verification gaps, timeline uncertainties | Unverified or contradicted capacity, no interconnection evidence, unrealistic timeline |
| Land & Zoning | 1 - Critical | By-right zoning, permits obtained or progressing, site ready | Conditional use possible, permits in early stages, entitlements in progress | Rezoning required with uncertain outcome, opposition, or 24+ month timeline |
| Connectivity | 1 - Critical | Multiple verified carriers, route diversity, carrier-neutral, metro + long-haul | One carrier confirmed, limited diversity, fiber build may be needed | No verified carrier presence, no fiber infrastructure, connectivity desert |
| Environmental | 2 - Important | Low hazard zone, no contamination, manageable compliance | Moderate hazard exposure, permits needed, no known contamination | High-risk flood/seismic, known contamination, regulations may block operations |
| Commercials | 2 - Important | Clear documented terms, market-rate pricing, standard structure | Some terms documented, deviations from benchmarks, key items TBD | No formal terms, pricing far from market, critical terms absent |
| Ownership | 2 - Important | Verified owner, clean background, clear title, no middleman | Partially verified, complex entity, minor concerns | Unverifiable owner, strong middleman signals, active litigation, liens |
| Water & Cooling | 3 - Context | Secured supply, appropriate cooling design, low scarcity risk | Supply available but unconfirmed, cooling described but not engineered, moderate scarcity | No supply agreement in scarce region, absent or inappropriate cooling design |
| Natural Gas | 3 - Context | Supply agreement or confirmed access, feasible generation, market pricing | Supply available in area, lateral needed, generation feasible but incomplete | No supply infrastructure, major construction needed, not feasible |
| Market Comparables | 3 - Context | Comparables exist, market supports pricing, favorable trends | Some comparables, deviations need explanation, moderate supply | No comparables, oversupply, unfavorable trends |
| Risk Assessment | Synthesis | No deal-breakers, few cross-domain risks, typical profile | No deal-breakers, significant cross-domain risks needing resolution | Deal-breakers identified, compounding risks, systemic failures |

---

## Verdict Quick Reference

| Condition | Verdict |
|-----------|---------|
| All Tier 1 solid, at most 1 Tier 2 Low with resolution path, no deal-breakers | **Pursue** |
| At most 1 Tier 1 Low (information gap, not verified negative), at most 2 Tier 2 Low, resolution paths exist | **Proceed with Caution** |
| 2+ Tier 1 Low, or Power Low from verified negatives with no resolution, or deal-breakers identified, or all Tier 2 Low | **Pass** |

**Remember:** Tier 3 scores (Water/Cooling, Natural Gas, Market Comparables) inform the narrative and risk profile but never independently trigger a Pass verdict. Power is the single most important domain -- a Low Power score from verified negative findings is the strongest possible signal toward Pass.
