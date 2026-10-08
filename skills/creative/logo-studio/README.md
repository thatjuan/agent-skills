# logo-studio

> Designs an iconic logo with full creative freedom, then turns the final mark into a complete app asset package and, on request, a multi-page brand guidelines document.

## What it does

`logo-studio` hands the design to the model with one brief: full creative freedom, any tool, and a mandate to produce its most polished, memorable, iconic work. It prescribes no design method. The skill only frames the work around the design:

1. **Learns the brand** from the repo, the product site, and the user, asking only for what it cannot find
2. **Designs** with whatever tools fit (hand-built SVG, computed geometry, image generation for exploration), rendering and viewing its own candidates at real sizes
3. **Presents** the work on a page designed as carefully as the logo, then iterates on feedback
4. **Exports** the final as full-color, mono, reversed, icon, and outlined SVGs
5. Builds a **complete app asset package** (iOS, Android, macOS, Windows, favicons, PWA, social)
6. Offers a **brand guidelines document** in Essentials / Standard / Full depth

## When to use it

Invoke this skill when you hear requests like:

- *"Design a logo for my SaaS startup called Veridian."*
- *"I need a brand mark for a specialty coffee roaster — something warm but modern."*
- *"Create an app icon for my iOS game studio."*
- *"Explore some visual identity directions for a fintech product targeting Gen Z."*
- *"I have a final logo, now generate the full favicon and PWA package."*
- *"Produce a brand guidelines PDF for this identity — full depth with motion and voice."*

If the user is asking for a **concept only** (no SVG, mood boards and visual language), route to [`creative-director`](../creative-director/) instead. Use `logo-studio` when the deliverable includes actual logo files.

## Example walkthrough

**Prompt**

> Design a logo for GittPub.

**What the skill does**

1. **Learns the brand** from the repo's README and site: what GittPub is and who uses it.
2. **Designs** freely, rendering each candidate to PNG and looking at it on light and dark grounds, from 16px to full size, until the mark is its best work.
3. **Presents** the mark and the idea behind it on a showcase page and opens it. The user asks for changes; the skill iterates.
4. **Exports** `logo-gittpub.svg` with mono, reversed, icon, and outlined variants.
5. **App assets**: builds a 1024×1024 icon master and runs `build-assets.mjs` to produce `dist/assets/`.
6. **Brand guidelines**: offers the document and, if accepted, writes `brand-guidelines-gittpub.html`, ready to print to PDF.

## Installation

```bash
npx skills add thatjuan/agent-skills --skill logo-studio
```

Then simply ask your agent to design a logo — the skill activates automatically on matching prompts.

## Bundled resources

| File | Purpose |
|------|---------|
| `SKILL.md` | The brief and the steps around it |
| `references/app-assets.md` | Platform specs (iOS 18, Android adaptive, .icns, Windows tiles, PWA) |
| `references/brand-guidelines.md` | Guidelines document structure, section spec, extension interview, render workflow |
| `assets/build-assets.mjs` | Node.js pipeline: icon master SVG → full app asset package |
| `assets/brand-guidelines-template.html` | Print-ready guidelines template with CSS variables and `{{TOKEN}}` slots |

## Tips

- **The icon master is not the logo.** The app asset step produces a square-format icon optimized for platform masks — not a scaled-down logo. Treat them as sibling artifacts.
- **Fonts and headless rasterization.** When building assets in CI, outline text to paths first — sharp/librsvg substitute system fonts silently if the brand font is missing. The pipeline handles this automatically.
- **Guidelines mode defaults to Standard.** Pick *Essentials* for a 4–6 page identity-only deliverable, *Full* when motion and approvals matter. Every extension-interview item has a sensible default — accept with one confirmation, override only what you care about.

## Related skills

- [`creative-director`](../creative-director/) — for brand/visual identity **concepts** (no SVG output, no files)
