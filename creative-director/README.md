# creative-director

> World-class creative director that produces detailed, richly-described design concepts for branding, websites, and UI experiences. Output is purely creative — visual language, mood, and rationale — not code.

## What it does

`creative-director` plays the role of a senior creative director in a top-tier agency. It doesn't draw, mock up, or implement — it **thinks and articulates**. Given a brand or product brief, it produces 3 genuinely distinct concept directions, each with a complete visual language system, mood, and strategic rationale.

The skill is grounded in the methodologies of Pentagram, IDEO, Sagmeister & Walsh, Collins, Wolff Olins, and R/GA, and informed by:

- A **catalog of 76 real-world design systems** (via `awesome-design-md`) that can be fetched as DESIGN.md specs for inspiration during concept development
- **Industry-specific conventions** across 11 verticals (tech, e-commerce, finance, healthcare, food, luxury, education, non-profit, entertainment, real estate, professional services)
- **Design psychology**: Gestalt principles, color psychology, scanning patterns, Don Norman's three levels of emotional design

## When to use it

Invoke this skill when the user wants **thinking**, not pixels:

- *"Give me creative direction for a premium EV charging network."*
- *"Explore three brand directions for a meditation app targeting engineers."*
- *"What's a fresh visual approach for a modern law firm that doesn't feel stuffy?"*
- *"Art-direct the hero experience for our new product landing page."*
- *"Help me pitch three visual territories to the client for their rebrand."*

**Not the right skill if** the user wants SVG files (→ [`logo-studio`](../logo-studio/)), coded UI (→ `stitch-design` or `heroui`), or implementation-ready mockups. This is the upstream thinking that those skills execute on.

## Example walkthrough

**Prompt**

> Creative direction for "Tide" — a sustainable ocean-friendly swimwear brand for women 30-45. Competitors feel either too surfy (Billabong) or too luxury (Eres). We want accessible premium.

**What the skill does**

1. **Discovery** — extracts the real brief: the gap is "premium that feels lived-in, not precious."
2. **Personality coordinates** — calm + restrained, contemporary, organic-leaning, mid-premium.
3. **Generates 3 concepts**:

   **Concept 1: "Saltwater"**
   > The feeling of reaching for your favorite piece after a long summer — softened, beloved, yours.
   - Palette: warm bone, faded denim, muted coral, deep tide green
   - Typography: Tiempos Text (editorial serif) + Söhne (neutral geometric sans)
   - Imagery: 35mm film, side-lit, skin tones intact, no retouching
   - Motion: languid easing, long transitions, 500ms+ durations

   **Concept 2: "Low Tide Line"**
   > Inspired by the visible memory of where the water was — confident, minimal, precise.
   - Palette: sand, fog, oxidized silver, single saturated accent (ultramarine)
   - Typography: GT Alpina for display only, Untitled Sans for everything else
   - Grid: aggressive negative space, type at the edge, product as protagonist

   **Concept 3: "Kelp Forest"**
   > Dense, textural, biophilic — swimwear that remembers the water has life in it.
   - Palette: layered greens, seaweed black, shell pink
   - Typography: Eksell Display paired with ABC Diatype
   - Imagery: underwater, sun-dappled, figure-in-environment

4. **Strategic rationale** for each, connecting every visual decision back to the "accessible premium" gap and the 30-45 audience.

## Installation

```bash
npx skills add thatjuan/agent-skills --skill creative-director
```

## Bundled resources

| File | Purpose |
|------|---------|
| `SKILL.md` | The 6-phase concept generation workflow and output format |
| `references/discovery-framework.md` | Brief extraction, discovery questions, competitive analysis, audience definition |
| `references/visual-design-system.md` | Color, typography, composition, spacing, motion, current trends, timeless principles |
| `references/industry-approaches.md` | Design conventions and differentiation opportunities across 11 industries |
| `references/design-psychology.md` | Gestalt, color psychology, scanning patterns, emotional design (Norman's three levels) |
| `references/concept-articulation.md` | Design vocabulary, presentation structure, rationale framework, sensory language |
| `references/design-inspirations.md` | Catalog of 76 real-world design systems fetchable as DESIGN.md specs for inspiration |

## Tips

- **Feed it a rich brief.** This skill scales with input quality. Generic prompts produce three variations of "modern and clean." Specific competitors, an audience, and a "this, not that" unlock genuinely distinct territories.
- **Concepts are meant to diverge.** If all three options feel similar, push back — the prompt isn't constraining enough.
- **Ask for the rationale.** The *why* behind each visual decision is often more useful than the visuals themselves, especially when presenting concepts to stakeholders.
- **Pair with `logo-studio`.** Once a concept is chosen, hand off the direction to `logo-studio` for actual logo production.

## Related skills

- [`logo-studio`](../logo-studio/) — the implementation counterpart for logo/brand mark deliverables
