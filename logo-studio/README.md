# logo-studio

> A professional logo design studio that produces 9+ SVG logo concepts from a brand brief, then generates a complete app asset package for every major platform from the final selection.

## What it does

`logo-studio` synthesizes three industry-standard logo design methodologies — **Paul Rand's Reductive Rationalism**, **Pentagram's Strategy-to-Craft**, and **Marty Neumeier's Brand Gap** — into a single, opinionated workflow.

Given a brand brief, it:

1. Runs a structured **brand discovery interview** (audience, values, competitors, "only statement")
2. Maps the brand to one of **12 Jungian archetypes** for psychology-informed visual direction
3. Generates **9+ distinct logo concepts** across 3 strategic directions (safe, hybrid, disruptive)
4. Produces clean, hand-coded **SVG** with real typography (Google Fonts) — not traced paths
5. Presents everything in a **self-contained HTML gallery** with light/dark backgrounds, color variants, and zoom
6. Supports **iteration** — refine, combine, redirect, or expand any concept
7. Builds a **complete app asset package** from the final selection (iOS, Android, macOS, Windows, favicons, PWA, social)

## When to use it

Invoke this skill when you hear requests like:

- *"Design a logo for my SaaS startup called Veridian."*
- *"I need a brand mark for a specialty coffee roaster — something warm but modern."*
- *"Create an app icon for my iOS game studio."*
- *"Explore some visual identity directions for a fintech product targeting Gen Z."*
- *"I have a final logo, now generate the full favicon and PWA package."*

If the user is asking for a **concept only** (no SVG, mood boards and visual language), route to [`creative-director`](../creative-director/) instead. Use `logo-studio` when the deliverable includes actual logo files.

## Example walkthrough

**Prompt**

> Design a logo for "Northbound" — a guided expedition company for first-time mountaineers. Audience is professionals 30-50 who want adventure without risk. Values: courage, preparation, clarity. Competitors feel either too hardcore (REI Co-op) or too corporate (Marriott Bonvoy).

**What the skill does**

1. **Discovery** — confirms the "only statement": *"The only mountaineering brand that makes first summits feel inevitable."*
2. **Archetype** — primary: *Explorer*; adjacent: *Sage*. Avoids *Hero* (oversaturated in competitor set).
3. **Competitive map** — white space identified in the "modern + serious" quadrant.
4. **Generates 9 concepts**:
   - Direction A (Explorer-aligned): compass rose mark, Inter wordmark, climber silhouette
   - Direction B (Explorer + Sage): polaris star monogram, Fraunces wordmark, topographic ring
   - Direction C (category-breaking): negative-space "N" as mountain + arrow, geometric wordmark, minimal bearing mark
5. **Gallery** — writes `./logo-studio-northbound.html` and opens it in the browser. Each card shows light/dark background, color/mono/reversed variants, rationale, and tags.
6. **Iteration** — user says *"Love C1 but the arrow is too subtle."* Skill generates C1-a, C1-b, C1-c as refinements.
7. **App assets** — on final selection, runs `build-assets.mjs` to produce `dist/assets/` with AppIcon.appiconset, .icns, adaptive Android icons, favicons, PWA manifest, and Open Graph images.

## Installation

```bash
npx skills add thatjuan/agent-skills --skill logo-studio
```

Then simply ask your agent to design a logo — the skill activates automatically on matching prompts.

## Bundled resources

| File | Purpose |
|------|---------|
| `SKILL.md` | The 7-phase workflow the agent follows |
| `references/methodologies.md` | Rand, Pentagram, and Neumeier methodologies synthesized |
| `references/brand-psychology.md` | 12 Jungian archetypes → visual vocabulary (shape, color, type) |
| `references/svg-techniques.md` | SVG construction, golden ratio, bezier curves, compatibility rules |
| `references/typography.md` | 20+ free commercial-safe fonts, pairings, text-vs-path decision tree |
| `references/evaluation-criteria.md` | Six quality gates (napkin, thumbnail, silhouette, B&W, swap, context) |
| `references/app-assets.md` | Platform specs (iOS 18, Android adaptive, .icns, Windows tiles, PWA) |
| `assets/gallery-template.html` | Self-contained gallery HTML with preloaded Google Fonts |
| `assets/build-assets.mjs` | Node.js pipeline: SVG → full app asset package |

## Tips

- **Rich brief = better concepts.** Feed the skill your audience, competitors, and a "this, not that" — generic briefs produce generic logos.
- **Reference concepts by ID.** Say *"A1"*, *"C2"*, or *"mix A1 icon with B2 type"* for fast iteration.
- **The icon master is not the logo.** Phase 7 produces a square-format icon optimized for platform masks — not a scaled-down logo. Treat them as sibling artifacts.
- **Fonts and headless rasterization.** When building assets in CI, outline text to paths first — sharp/librsvg substitute system fonts silently if the brand font is missing. The pipeline handles this automatically.

## Related skills

- [`creative-director`](../creative-director/) — for brand/visual identity **concepts** (no SVG output, no files)
