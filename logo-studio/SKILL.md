---
name: logo-studio
description: Professional logo design studio that produces 9+ SVG logo concepts through brand discovery, archetype mapping, and iterative refinement, then generates a complete app asset package (iOS, Android, macOS, Windows, favicons, PWA, social) from the final selection. Use when the user asks for a logo, brand mark, icon, wordmark, app icon, or visual identity for a business, product, or project.
---

# Logo Design Studio

A professional logo design studio combining three industry-standard methodologies — Rand's Reductive Rationalism, Pentagram's Strategy-to-Craft, and Neumeier's Brand Gap — to produce distinctive, memorable brand marks as clean, hand-coded SVG.

## Capabilities

- Extracts brand essence through structured discovery interviews
- Maps brands to Jungian archetypes for psychology-informed visual direction
- Generates 9+ distinct SVG logo concepts across 3 strategic directions
- Produces clean, compatible SVG markup with real typography (Google Fonts) or geometric construction
- Presents all concepts in a self-contained HTML gallery with light/dark backgrounds, zoom, and variant strips
- Supports iterative refinement cycles based on user selection and feedback
- Produces a complete app asset package (iOS, Android, macOS, Windows, favicons, PWA, social) from the final logo

## Workflow

| Phase | Name | Reference |
|-------|------|-----------|
| 1 | Brand Discovery | [methodologies.md](references/methodologies.md) |
| 2 | Strategic Positioning | [brand-psychology.md](references/brand-psychology.md) |
| 3 | Concept Generation | [methodologies.md](references/methodologies.md) |
| 4 | SVG Construction | [svg-techniques.md](references/svg-techniques.md) + [typography.md](references/typography.md) |
| 5 | Studio Presentation | [gallery-template.html](assets/gallery-template.html) |
| 6 | Iteration & Evaluation | [evaluation-criteria.md](references/evaluation-criteria.md) |
| 7 | App Asset Production | [app-assets.md](references/app-assets.md) + [build-assets.mjs](assets/build-assets.mjs) |

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
| Typography | `<text>` with real fonts by default; paths for custom lettering |
| Reusables | Gradients, clipPaths, masks inside `<defs>` |
| Negative space | `fill-rule="evenodd"` for counter shapes |
| File size | Under 5KB per logo |
| ViewBox | 200×200 for symbols, 400×120 for combination/wordmarks |

### Typography Strategy

Logo wordmarks use **real typography** by default. The HTML gallery loads Google Fonts so `<text>` elements render with the intended typeface during preview and iteration.

| Approach | When |
|----------|------|
| **`<text>` + font-family** | Set-type wordmarks (most modern tech brands). Default for iteration. |
| **Embedded `@font-face`** | Portable SVG delivery (email, PDFs, third-party viewers). Font subset to used glyphs. |
| **Outlined `<path>`** | Custom lettering (Coca-Cola, Disney style), modified glyphs, or final print/merch delivery. |

**Every `font-family` cascades to a system fallback** — e.g. `'Inter', -apple-system, sans-serif` — so the logo never renders in Times New Roman.

See [typography.md](references/typography.md) for the curated font catalog (Inter, Work Sans, Fraunces, Playfair Display, Space Grotesk, Manrope, Archivo, and more), classic pairings, licensing, and the text-vs-path decision tree.

### SVG Skeletons

**Symbol / Icon:**

```svg
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Gradients, clipPaths, reusable elements -->
  </defs>
  <!-- Logo construction from geometric primitives -->
</svg>
```

**Wordmark with real typography:**

```svg
<svg viewBox="0 0 400 100" xmlns="http://www.w3.org/2000/svg">
  <text x="200" y="65" text-anchor="middle"
        font-family="Inter, -apple-system, system-ui, sans-serif"
        font-size="48" font-weight="800" letter-spacing="-1"
        fill="#0A0A0A">Acme</text>
</svg>
```

**Combination mark (symbol + typographic wordmark):**

```svg
<svg viewBox="0 0 400 120" xmlns="http://www.w3.org/2000/svg">
  <g transform="translate(20, 30)">
    <!-- Symbol from primitives -->
    <circle cx="30" cy="30" r="28" fill="#0071e3"/>
  </g>
  <text x="90" y="72"
        font-family="Inter, system-ui, sans-serif"
        font-size="42" font-weight="700"
        fill="#0A0A0A">Acme</text>
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

### Final Logo Deliverables

The final selected logo is exported as:

| File | Contents |
|------|----------|
| `logo-{name}.svg` | Full-color SVG (working file with `<text>` elements) |
| `logo-{name}-mono.svg` | Monochrome SVG |
| `logo-{name}-reversed.svg` | Reversed/knockout SVG |
| `logo-{name}-icon.svg` | Symbol-only variant (if combination mark) |
| `logo-{name}-outlined.svg` | Delivery version with text converted to paths (font-independent) |

The working file (`logo-{name}.svg`) remains editable. The outlined version is the delivery asset for print, merch, and environments where the font may not load.

## Phase 7: App Asset Production

After the final logo is selected, Phase 7 generates a complete app asset package for every major platform from a canonical icon master.

### Icon Master

The icon master is a square-format SVG derived from (but distinct from) the final logo:

| Property | Value |
|----------|-------|
| Canvas | 1024×1024, square |
| Background | Deliberate brand color (not transparent, not white) |
| Content | Usually the symbol only; monograms for wordmark-only brands |
| Typography | Text outlined to paths (font rendering is unreliable in headless rasterizers) |
| Corner radius | None — platforms apply their own masks |
| Safe zone | Central ~61% (matches Android's most restrictive 66/108) |

The icon master is the input to the build pipeline. It is a separate artifact from the logo because icons and logos have different jobs — see [app-assets.md](references/app-assets.md) for the full design rationale.

### Platform Outputs

| Platform | Assets |
|----------|--------|
| **iOS** | `AppIcon.appiconset/` with light/dark/tinted 1024 PNGs + Contents.json (iOS 18 format) |
| **Android** | Adaptive icon (`ic_launcher.xml` + foreground/background/monochrome layers) + legacy densities (mdpi-xxxhdpi) + Play Store 512 |
| **macOS** | `AppIcon.icns` built via `iconutil` from a 10-size `.iconset` (16 through 1024@2x) |
| **Windows** | Multi-resolution `.ico` (16/32/48/256) + UWP tile PNGs (44, 71, 150, 310, wide) |
| **Web / Favicon** | `favicon.ico`, `favicon.svg`, `apple-touch-icon.png` (180), PWA manifest icons (192, 512, maskable), `safari-pinned-tab.svg` (monochrome) |
| **PWA** | `site.webmanifest`, splash screens, maskable icons with safe-zone padding |
| **Social** | Open Graph (1200×630), Twitter card (1200×628), LinkedIn, profile pictures (400, 512) |

### Tool Stack

| Purpose | Tool | Install |
|---------|------|---------|
| Programmatic rasterization | sharp (Node, libvips) | `npm i sharp` |
| Favicon + iOS + Android + Windows package | favicons (npm) | `npm i favicons` |
| PWA splash + maskable icons | pwa-asset-generator (npm) | `npm i pwa-asset-generator` |
| CLI rasterization fallback | resvg or rsvg-convert | `brew install resvg librsvg` |
| macOS .icns builder | iconutil | Built into macOS |
| SVG optimization | svgo | `npm i svgo` |
| PNG optimization | pngquant + oxipng | `brew install pngquant oxipng` |

See [app-assets.md](references/app-assets.md) for the full tool comparison, platform specifications, and gotchas (especially font handling in headless SVG rasterization).

### Build Pipeline

The complete pipeline is scripted in [build-assets.mjs](assets/build-assets.mjs):

```bash
# Install prerequisites (one time)
npm i -D sharp favicons pwa-asset-generator svgo png-to-ico

# Run the build
node build-assets.mjs
```

Pipeline stages:

1. Optimize source SVGs with svgo
2. Generate favicon/iOS/Android/Windows package with `favicons`
3. Build macOS `.iconset` with sharp, then `iconutil` → `.icns`
4. Build iOS AppIcon.appiconset (light + dark + tinted 1024 PNGs)
5. Generate social/Open Graph images
6. Optimize all PNGs with pngquant + oxipng

### Output Structure

```
dist/assets/
├── logo.svg                         # Optimized source logo
├── icon-master.svg                  # 1024×1024 square icon master
├── AppIcon.appiconset/              # iOS asset catalog
├── AppIcon.icns                     # macOS compiled icon
├── android/                         # Adaptive + legacy densities
├── windows/                         # .ico + UWP tiles
├── web/                             # favicons, PWA manifest, safari-pinned-tab
└── social/                          # OG, Twitter, profile images
```

### Critical Typography Note

SVG rasterizers (sharp, librsvg, resvg) render `<text>` elements using system-installed fonts. In CI or on machines missing the brand font, the output silently substitutes a fallback font. The icon master sidesteps this by using outlined paths — the working SVG keeps live text, the icon master ships outlined.

See [typography.md](references/typography.md) for the dual-output workflow.
