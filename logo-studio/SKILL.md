---
name: logo-studio
description: Professional logo design studio that produces 9+ SVG logo concepts through brand discovery, archetype mapping, and iterative refinement. Use when the user asks for a logo, brand mark, icon, wordmark, or visual identity for a business, product, or project. Presents concepts in an interactive HTML gallery for review and iteration.
---

# Logo Design Studio

A professional logo design studio combining three industry-standard methodologies — Rand's Reductive Rationalism, Pentagram's Strategy-to-Craft, and Neumeier's Brand Gap — to produce distinctive, memorable brand marks as clean, hand-coded SVG.

## Capabilities

- Extracts brand essence through structured discovery interviews
- Maps brands to Jungian archetypes for psychology-informed visual direction
- Generates 9+ distinct SVG logo concepts across 3 strategic directions
- Produces clean, compatible SVG markup using geometric construction (no font dependencies)
- Presents all concepts in a self-contained HTML gallery with light/dark backgrounds, zoom, and variant strips
- Supports iterative refinement cycles based on user selection and feedback

## Workflow

| Phase | Name | Reference |
|-------|------|-----------|
| 1 | Brand Discovery | [methodologies.md](references/methodologies.md) |
| 2 | Strategic Positioning | [brand-psychology.md](references/brand-psychology.md) |
| 3 | Concept Generation | [methodologies.md](references/methodologies.md) |
| 4 | SVG Construction | [svg-techniques.md](references/svg-techniques.md) |
| 5 | Studio Presentation | [gallery-template.html](assets/gallery-template.html) |
| 6 | Iteration & Evaluation | [evaluation-criteria.md](references/evaluation-criteria.md) |

## Phase 1: Brand Discovery

The discovery phase extracts the information needed for strategic logo design.

### Discovery Interview

| Item | Purpose |
|------|---------|
| Brand/company name | The wordmark foundation |
| Industry/category | Category conventions and differentiation opportunities |
| Target audience | Demographics, psychographics, aspirations |
| Brand values (top 3) | Core personality traits to express visually |
| Competitors (3-5) | Visual landscape for competitive differentiation |
| The "Only Statement" | "Our brand is the ONLY [category] that [differentiator]" |
| Tone/personality | Where the brand falls on personality spectrums |
| Existing assets | Colors, fonts, or visual elements already in use |
| Use contexts | Where the logo appears (app icon, signage, print, web) |

### Personality Spectrums

Position the brand on these axes (1-10):

```
Traditional ←————→ Modern
Playful     ←————→ Serious
Luxurious   ←————→ Accessible
Bold        ←————→ Subtle
Organic     ←————→ Geometric
```

See [methodologies.md](references/methodologies.md) for how each methodology approaches the discovery process.

## Phase 2: Strategic Positioning

### Archetype Mapping

Each brand maps to one of 12 Jungian archetypes. The archetype determines the visual vocabulary — shapes, colors, typography, and composition style.

See [brand-psychology.md](references/brand-psychology.md) for the complete archetype-to-visual mapping, color psychology, shape psychology, and typography psychology.

### Competitive Landscape

Competitor logos are mapped on two axes to identify visual white space:

```
Axis 1: Traditional ←→ Modern
Axis 2: Playful ←→ Serious
```

Logo concepts target the empty quadrants — visual territory not yet claimed.

### Three Strategic Directions

| Direction | Characteristics |
|-----------|----------------|
| Direction A | Aligns with the primary archetype. Market-conventional, safe. |
| Direction B | Blends primary + adjacent archetype. Distinctive while familiar. |
| Direction C | Contrasts category conventions. Highest differentiation, highest risk. |

## Phase 3: Concept Generation

### Concept Matrix

Each direction produces 3 logo types, yielding a minimum of 9 concepts:

| | Direction A | Direction B | Direction C |
|---|---|---|---|
| **Combination mark** | A1 | B1 | C1 |
| **Wordmark** | A2 | B2 | C2 |
| **Symbol / Icon** | A3 | B3 | C3 |

Expandable with additional types: lettermark, abstract mark, emblem.

### Concept Development

Each concept follows the Reductive Rationalism process:

1. Start with the core idea from the Only Statement
2. Generate visual metaphors — forced connections between brand noun + unexpected associations
3. Thumbnail: quantity over quality
4. Reduce: strip to essential elements
5. Test mentally: is it drawable from memory?

See [methodologies.md](references/methodologies.md) for the full process from each methodology.

## Phase 4: SVG Construction

### Technical Standards

| Standard | Value |
|----------|-------|
| Scaling | `viewBox`-based (no fixed width/height) |
| Namespace | `xmlns="http://www.w3.org/2000/svg"` on every `<svg>` |
| Shapes | Geometric primitives: `circle`, `rect`, `polygon`, `path` |
| Typography | `<path>` elements — no `<text>` or font dependencies |
| Reusables | Gradients, clipPaths, masks inside `<defs>` |
| Negative space | `fill-rule="evenodd"` for counter shapes |
| File size | Under 5KB per logo |
| ViewBox | 200×200 for symbols, 400×120 for combination/wordmarks |

### SVG Skeleton

```svg
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Gradients, clipPaths, reusable elements -->
  </defs>
  <!-- Logo construction from geometric primitives -->
</svg>
```

### Color Variants

Each logo is produced in three variants:

| Variant | Description |
|---------|-------------|
| Full color | Brand colors informed by archetype and psychology |
| Monochrome | Single dark color (#1d1d1f) on light background |
| Reversed | White (#ffffff) on dark background |

See [svg-techniques.md](references/svg-techniques.md) for geometric construction methods, bezier curves, symmetry, golden ratio, and compatibility rules.

## Phase 5: Studio Presentation

### Gallery Output

All concepts are presented in a self-contained HTML file based on the [gallery template](assets/gallery-template.html).

**Output path:** `./logo-studio-{brandname}.html` in the working directory.

After writing the file, it is opened with `open` (macOS), `xdg-open` (Linux), or `start` (Windows).

### Gallery Card Structure

```
┌─────────────────────────────┐
│  [Light BG]  │  [Dark BG]   │  ← Side-by-side display
├─────────┬─────────┬─────────┤
│ Color   │  Mono   │ Reversed│  ← Variant strip
├─────────┴─────────┴─────────┤
│ [ID] Concept Name           │
│ Description + rationale     │
│ #tag #tag #tag              │
└─────────────────────────────┘
```

### Gallery Sections

Cards are grouped by strategic direction:

- **Section: Direction A** — "Conservative / Archetype-aligned"
- **Section: Direction B** — "Distinctive / Hybrid"
- **Section: Direction C** — "Disruptive / Category-breaking"

## Phase 6: Iteration

### Feedback Protocol

Users reference concepts by ID (e.g., "A1", "C2").

| Iteration Type | Trigger | Action |
|----------------|---------|--------|
| Refine | "I like A1 but..." | 3-5 variations of the selected concept |
| Combine | "Mix A1 icon with B2 type" | Synthesize elements from multiple concepts |
| Redirect | "None of these feel right" | Return to Phase 1 for deeper discovery |
| Expand | "More like C-row" | Additional concepts in that direction |

### Quality Gates

Each finalist is evaluated against six tests:

| Test | Criterion |
|------|-----------|
| Napkin test | Drawable from memory after 5-second viewing |
| Thumbnail test | Recognizable at 16×16 pixels (favicon size) |
| Silhouette test | Identifiable as outline only |
| B&W test | Functional without color |
| Swap test | Looks wrong on a competitor's product |
| Context test | Holds presence next to competitor logos at real scale |

See [evaluation-criteria.md](references/evaluation-criteria.md) for detailed evaluation frameworks.

### Iteration Gallery

Each iteration produces an updated HTML file: `logo-studio-{brandname}-r{N}.html`

The updated gallery contains the refined/new concepts with a header noting the round number.

### Final Deliverables

The final selected logo is exported as:

| File | Contents |
|------|----------|
| `logo-{name}.svg` | Full-color SVG |
| `logo-{name}-mono.svg` | Monochrome SVG |
| `logo-{name}-reversed.svg` | Reversed/knockout SVG |
| `logo-{name}-icon.svg` | Symbol-only variant (if combination mark) |
