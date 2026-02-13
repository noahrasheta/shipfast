# PaperBanana: Key Insights for Image Generation

Distilled from the PaperBanana research paper (Zhu et al., 2026) — an agentic framework for automated generation of publication-ready academic illustrations by Google Cloud AI Research and Peking University.

## The Core Idea

Treat image generation like a design agency with a team of specialists, not a single prompt-to-image call. The multi-agent approach consistently outperforms single-shot generation across all quality dimensions.

## The 5-Agent Architecture

The paper defines 5 specialized agents in a pipeline:

1. **Retriever**: Finds relevant reference images to guide style and structure
2. **Planner**: Translates requirements into a comprehensive textual description
3. **Stylist**: Applies aesthetic guidelines to refine the description
4. **Visualizer**: Generates images from the refined description (with iterative refinement)
5. **Critic**: Evaluates output and provides feedback for refinement loops

Our Banana Squad maps these to: Research Agent (Retriever), Prompt Architect (Planner + Stylist), Generator Agent (Visualizer), and Critic Agent, with a Lead orchestrator.

## Key Findings

### Critique is the Secret Weapon

The paper's most important finding: adding iterative critique rounds dramatically improves quality.

- Without critique: ~45.1% accuracy
- With 1 round of critique: improved across all dimensions
- With 3 rounds of critique: ~55% accuracy (+10% improvement)
- Diminishing returns after 3 rounds

### Reference Images Teach Better Than Fine-Tuning

Showing the model good examples (retrieval) teaches it structure better than fine-tuning. Providing reference images for style, composition, and layout is more effective than describing attributes purely in text.

### Narrative Descriptions Beat Keyword Lists

The #1 prompting rule: describe the scene narratively. A descriptive paragraph always produces better images than disconnected keywords. This applies to all image generation with Nano Banana.

### 5 Variants Account for Stochasticity

Image generation is stochastic — one prompt, one shot = rolling the dice once. Generating 5 variants with different approaches (faithful, enhanced, alt composition, style variation, bold/creative) ensures you get options to choose from. This mirrors how design agencies work: present options, client picks, then refine.

## The 4 Evaluation Dimensions

Quality is measured on 4 dimensions with a priority hierarchy:

### Primary Dimensions (decisive)

1. **Faithfulness**: Does it match the original request? Correct elements, accurate data, correct relationships.
2. **Readability**: Is the layout clear, text legible, composition clean?

### Secondary Dimensions (tiebreakers)

3. **Conciseness**: Does it focus on core information without visual clutter?
4. **Aesthetics**: Does it look professional and visually appealing?

**Hierarchy rule**: Primary dimensions take precedence. An accurate, readable image ranks above a beautiful but inaccurate one. When primary dimensions tie, secondary dimensions break the tie.

## Performance Results

PaperBanana with Nano Banana Pro outperformed all baselines:

- Faithfulness: +2.8% over vanilla
- Conciseness: +37.2% over vanilla
- Readability: +12.9% over vanilla
- Aesthetics: +6.6% over vanilla
- Overall: +17.0% over vanilla

The agentic framework even outperformed human-created illustrations in conciseness and aesthetics.

## Practical Application Notes

### For the Research Agent

- Prioritize visual structure similarity over topic similarity when selecting references
- Analyze: colors, composition, typography, data visualization approach, mood, unique elements
- A single deeply-analyzed reference is better than many shallow ones

### For the Prompt Architect

- Always write narrative paragraphs, never keyword lists
- Include: subject, environment, lighting, camera angle, mood, textures, colors, composition
- For photorealistic: use photography terms (lens type, depth of field, bokeh)
- For text in images: specify exact text, font style, placement
- Apply aesthetic refinement: cohesive palette, deliberate composition, specific lighting

### For the Generator Agent

- Use Nano Banana Pro (`gemini-3-pro-image-preview`) for professional quality
- Default to 2K resolution for crisp output
- Retry with rephrased prompts on safety filter triggers (up to 2 retries)
- Reference images significantly improve style consistency

### For the Critic Agent

- Score each dimension 1-10
- Apply the hierarchy: Faithfulness and Readability are primary
- The tension between beauty (Stylist) and accuracy (Critic) is productive — the loop finds the balance
- Provide specific, actionable feedback for refinement
