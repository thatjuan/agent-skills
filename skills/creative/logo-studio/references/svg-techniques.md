# SVG Construction Techniques

Technical reference for building professional logo SVGs programmatically.

## Table of Contents

- [Fundamentals](#fundamentals)
- [Geometric Construction](#geometric-construction)
- [Logo Styles](#logo-styles)
- [Typography in SVG](#typography-in-svg)
- [Advanced Techniques](#advanced-techniques)
- [Compatibility Rules](#compatibility-rules)
- [Optimization](#optimization)

> For the full typography strategy — font catalog, pairings, licensing, and the text-vs-path decision — see [typography.md](typography.md).

---

## Fundamentals

### ViewBox and Scaling

```svg
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
```

- `viewBox` defines the internal coordinate space
- Omit `width`/`height` or set to `100%` for container-responsive scaling
- Symbol logos: `viewBox="0 0 200 200"` (square)
- Combination marks: `viewBox="0 0 400 120"` (wide)
- Wordmarks: `viewBox="0 0 300 80"` (wide and short)

### Core Elements

| Element | Use For | Key Attributes |
|---------|---------|----------------|
| `<path>` | Any shape (workhorse) | `d` (M, L, C, A, Z commands) |
| `<circle>` | Dots, orbs, rings | `cx`, `cy`, `r` |
| `<ellipse>` | Ovals | `cx`, `cy`, `rx`, `ry` |
| `<rect>` | Squares, rectangles, bars | `x`, `y`, `width`, `height`, `rx` |
| `<polygon>` | Triangles, stars, shields | `points` |
| `<line>` | Strokes, dividers | `x1`, `y1`, `x2`, `y2` |
| `<g>` | Grouping for transforms | `transform`, shared `fill`/`stroke` |

### Defs Block

Gradients, clipPaths, masks, and reusable elements go inside `<defs>`:

```svg
<defs>
  <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#6366f1"/>
    <stop offset="100%" stop-color="#8b5cf6"/>
  </linearGradient>
  <clipPath id="clip1">
    <circle cx="100" cy="100" r="90"/>
  </clipPath>
</defs>
<rect fill="url(#grad1)" clip-path="url(#clip1)" width="200" height="200"/>
```

Use `gradientUnits="userSpaceOnUse"` when transforms are applied to the target element.

### Fills and Strokes

```svg
<!-- Solid fill -->
<circle cx="100" cy="100" r="50" fill="#0071e3"/>

<!-- Stroke only -->
<circle cx="100" cy="100" r="50" fill="none" stroke="#0071e3" stroke-width="4"
        stroke-linejoin="round" stroke-linecap="round"/>

<!-- Gradient fill -->
<circle cx="100" cy="100" r="50" fill="url(#grad1)"/>
```

---

## Geometric Construction

### Grid-Based Design

Snap anchor points to a regular grid within the viewBox. For a 200×200 canvas, a 10-unit grid provides 20×20 snap points.

```
Grid intersections for a 200×200 viewBox at 10-unit intervals:
(0,0) (10,0) (20,0) ... (200,0)
(0,10) (10,10) ...
...
(0,200) ... (200,200)
```

### Golden Ratio Construction

The golden ratio (φ = 1.618) provides natural visual harmony:

```
Golden rectangle: width = height × 1.618
For h=100: w=161.8

Golden section: divide a line at 61.8% / 38.2%
For a 200-unit line: split at 123.6 and 76.4
```

Example: proportioned rectangles

```svg
<!-- Outer rectangle (golden proportions) -->
<rect x="19" y="40" width="162" height="100" rx="8" fill="#1e293b"/>
<!-- Inner accent at golden section point -->
<rect x="19" y="40" width="100" height="100" rx="8" fill="#2563eb"/>
```

### Circle-Based Construction

Many professional logos are built from overlapping circles:

1. Define circle positions and radii
2. Trace intersection paths
3. Fill selected regions

Intersection point formula for two circles:
```
d = sqrt((x2-x1)² + (y2-y1)²)
If d < r1+r2: circles intersect
```

Use arc commands (`A`) to trace the visible segments between intersection points.

### Symmetry via Transform

```svg
<!-- Define one half -->
<g id="halfShape">
  <path d="M100 20 L100 180 L40 100 Z" fill="#3b82f6"/>
</g>
<!-- Mirror for perfect symmetry -->
<use href="#halfShape" transform="scale(-1,1) translate(-200,0)"/>
```

---

## Logo Styles

### Combination Mark (symbol + wordmark)

```svg
<svg viewBox="0 0 400 120" xmlns="http://www.w3.org/2000/svg">
  <!-- Symbol on the left -->
  <g transform="translate(10, 10)">
    <circle cx="50" cy="50" r="45" fill="#2563eb"/>
    <!-- Icon paths inside circle -->
  </g>
  <!-- Wordmark on the right -->
  <g transform="translate(130, 30)">
    <!-- Letter paths -->
  </g>
</svg>
```

### Wordmark (text-based)

Constructed from geometric letter paths with consistent stroke weight and mathematical kerning:

```svg
<svg viewBox="0 0 300 80" xmlns="http://www.w3.org/2000/svg">
  <!-- Each letter as a path, positioned with calculated spacing -->
  <path d="M20 65 L35 15 L50 65 M27 45 L43 45" fill="none"
        stroke="#1d1d1f" stroke-width="6" stroke-linecap="round"/>
  <!-- Next letter offset by kern value -->
</svg>
```

### Symbol / Icon

```svg
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <!-- Geometric construction within square canvas -->
  <circle cx="100" cy="100" r="90" fill="#2563eb"/>
  <path d="..." fill="#ffffff"/>
</svg>
```

### Lettermark (monogram)

1-3 letters, often interlocked via overlapping paths with opacity or shared geometry:

```svg
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <!-- Letter 1 -->
  <path d="..." fill="#2563eb"/>
  <!-- Letter 2, offset and overlapping -->
  <path d="..." fill="#2563eb" opacity="0.7"/>
</svg>
```

### Abstract Mark

Non-representational forms using arcs, bezier curves, and geometric primitives:

```svg
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <path d="M100 10 C150 10 190 50 190 100 C190 150 150 190 100 190
           C50 190 10 150 10 100 C10 50 50 10 100 10 Z" fill="#8b5cf6"/>
  <path d="M60 100 Q100 40 140 100 Q100 160 60 100 Z" fill="#ffffff"/>
</svg>
```

### Emblem

Enclosed badge/crest with border and internal elements:

```svg
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <!-- Shield/badge outline -->
  <path d="M100 10 L180 50 L180 130 Q180 180 100 195 Q20 180 20 130 L20 50 Z"
        fill="#1e293b" stroke="#c9a84c" stroke-width="3"/>
  <!-- Internal elements -->
</svg>
```

---

## Typography in SVG

Logo wordmarks use real typography by default — real fonts via `<text>` elements. Paths are reserved for custom lettering, modified glyphs, or final brand asset delivery.

See [typography.md](typography.md) for the full font catalog, pairings, licensing, and the text-vs-path decision framework.

### Approach 1: `<text>` with Font Family (default)

Fast to generate, editable, accessible. The HTML gallery loads Google Fonts in `<head>` so `<text>` elements render with the real typeface during preview.

```svg
<svg viewBox="0 0 400 100" xmlns="http://www.w3.org/2000/svg">
  <text x="200" y="65" text-anchor="middle"
        font-family="Inter, -apple-system, system-ui, sans-serif"
        font-size="48" font-weight="800" letter-spacing="-1"
        fill="#0A0A0A">Acme</text>
</svg>
```

**Key attributes:**

| Attribute | Purpose |
|-----------|---------|
| `font-family` | Primary font + system fallback cascade (never bare font name) |
| `font-size` | Integer pixels, matched to viewBox coordinates |
| `font-weight` | 100-900 (logo weights typically 700-900 for bold, 300-400 for light) |
| `letter-spacing` | Negative values for tight display tracking, positive for all-caps elegance |
| `text-anchor` | `start`, `middle`, or `end` — positioning origin |
| `dominant-baseline` | `middle`, `central`, `hanging` — vertical alignment |

**Font family must cascade to a system fallback** so the logo never renders in Times New Roman:

```
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
font-family: 'Playfair Display', Georgia, 'Times New Roman', serif;
font-family: 'JetBrains Mono', 'SF Mono', Menlo, monospace;
```

### Approach 2: Embedded `@font-face` (portable delivery)

For a self-contained SVG that renders identically anywhere — email, PDFs, third-party viewers:

```svg
<svg viewBox="0 0 400 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style type="text/css">
      @font-face {
        font-family: 'BrandFont';
        font-weight: 800;
        src: url('data:font/woff2;base64,d09GMgABAAAA...') format('woff2');
      }
    </style>
  </defs>
  <text x="200" y="65" text-anchor="middle"
        font-family="'BrandFont', Inter, sans-serif"
        font-size="48" font-weight="800" fill="#0A0A0A">Acme</text>
</svg>
```

The font is subset to only the glyphs used (typically 1–3 KB for a wordmark):

```bash
pyftsubset Inter-Bold.ttf --text="Acme" --flavor=woff2 \
  --layout-features=liga,kern --output-file=inter-acme.woff2
base64 -i inter-acme.woff2
```

### Approach 3: Outlined Paths (custom lettering or final asset)

Letters constructed from `<path>` elements. Used when:

- The wordmark is custom lettering (Coca-Cola, Disney, Instagram) — not from any font
- Glyphs are modified (stretched S, custom ligature, proprietary curve)
- Delivering the final brand asset for print, merch, or packaging
- Licensing restricts font embedding
- Guaranteed identical rendering in Inkscape, Illustrator, and PDF readers

**Letter construction methods:**

Geometric letters — built from primitives:
- Straight letters (A, E, F, H, I, K, L, M, N, T, V, W, X, Y, Z): lines and angles
- Curved letters (B, C, D, G, J, O, P, Q, R, S, U): arcs and bezier curves

Stroke-based letters — using stroke properties:

```svg
<!-- Letter "A" from strokes -->
<path d="M30 80 L50 20 L70 80 M37 55 L63 55"
      fill="none" stroke="#1d1d1f" stroke-width="8"
      stroke-linecap="round" stroke-linejoin="round"/>
```

Fill-based letters — solid paths with `fill-rule="evenodd"` counters:

```svg
<!-- Letter "A" as filled shape with counter -->
<path d="M50 80 L75 10 L100 80 L88 80 L75 35 L62 80 Z M65 55 L85 55 L80 65 L70 65 Z"
      fill="#1d1d1f" fill-rule="evenodd"/>
```

**Dual-output workflow:** Iterate with `<text>` (editable, fast), then export to paths at finalization:

```bash
inkscape logo.svg --export-text-to-path \
  --export-plain-svg --export-filename=logo-outlined.svg
```

### Kerning

For `<text>` elements, kerning is handled by the font's built-in kern table. The `letter-spacing` attribute adds uniform tracking on top.

For path-based letters, calculate spacing mathematically:
- Base kern: character width × 0.15
- Pairs with visual gaps (AV, To, LT) need tighter kern
- Pairs that crowd (HH, NN) need standard or wider kern

### Variable Fonts

Variable fonts expose axes (weight, width, optical size) via `font-variation-settings`:

```svg
<text style="font-variation-settings: 'wght' 850, 'opsz' 144;"
      font-family="Fraunces, serif" font-size="64">Acme</text>
```

Recommended variable fonts for logos: Inter, Fraunces, Bricolage Grotesque, Recursive, Space Grotesk.

Older renderers ignore variation settings — for portable delivery, bake into a static weight.

---

## Advanced Techniques

### Negative Space

Create counter shapes (holes) using `fill-rule="evenodd"`:

```svg
<!-- Circle with inner cutout -->
<path d="M100 10 A90 90 0 1 1 100 190 A90 90 0 1 1 100 10 Z
         M100 40 A60 60 0 1 0 100 160 A60 60 0 1 0 100 40 Z"
      fill="#1d1d1f" fill-rule="evenodd"/>
```

### Bezier Curves

Cubic bezier (`C`) for smooth curves with two control points:

```
M startX,startY C cp1x,cp1y cp2x,cp2y endX,endY
```

Quadratic bezier (`Q`) for simpler curves with one control point:

```
M startX,startY Q cpx,cpy endX,endY
```

### Arc Commands

`A rx ry rotation large-arc-flag sweep-flag x y`

```svg
<!-- Semicircle -->
<path d="M50 100 A50 50 0 0 1 150 100" fill="none" stroke="#2563eb" stroke-width="4"/>

<!-- Full ring -->
<path d="M100 10 A90 90 0 1 1 99.99 10" fill="none" stroke="#2563eb" stroke-width="8"/>
```

### Optical Corrections

Visual perception requires size adjustments:

| Shape | Correction |
|-------|-----------|
| Circle | Extend 3-5% beyond square bounding box to appear same size |
| Triangle (pointed) | Extend 5-8% beyond bounding box |
| Rounded shapes | Slightly larger than geometric shapes at same nominal size |
| Horizontal strokes | Slightly thinner than vertical strokes for optical consistency |

---

## Compatibility Rules

| Rule | Reason |
|------|--------|
| Include `xmlns="http://www.w3.org/2000/svg"` | Required for `<img src>` rendering |
| Avoid `<foreignObject>` | No cross-browser support |
| Avoid CSS `var()` in SVG attributes | Not supported in all contexts |
| Prefer `fill`/`stroke` attributes over CSS classes | Inline styles survive all embedding methods |
| Use `stroke-linejoin="round"` / `stroke-linecap="round"` | Polished joins and caps |
| Avoid complex `<filter>` chains | Performance and compatibility issues |
| `<text>` always cascades to system fallback | Font not loading = renders in fallback, not Times New Roman |
| Final brand deliverables outline `<text>` to paths | Guarantees identical rendering in every tool |

### Embedding Methods

| Method | Styling | Scripting | Font Loading | Best For |
|--------|---------|-----------|--------------|----------|
| Inline SVG in HTML | Full CSS access | Full JS access | HTML `<head>` fonts available | Gallery preview |
| `<img src="logo.svg">` | No external CSS | No JS | Only embedded `@font-face` | Production use |
| CSS `background-image` | No styling | No JS | Only embedded `@font-face` | Decorative use |

**Implication:** Logos used via `<img src>` or CSS backgrounds need either embedded `@font-face` (Approach 2) or outlined paths (Approach 3). Only inline SVG in HTML can rely on external font loading.

---

## Optimization

### Size Targets

| Logo Type | Target Size |
|-----------|-------------|
| Symbol | < 3KB |
| Wordmark | < 4KB |
| Combination mark | < 5KB |

### Techniques

- Remove editor metadata, comments, default attributes (`fill-opacity="1"`)
- Reduce path decimal precision to 1-2 places
- Merge identical shapes
- Use `<use href="#id">` for repeated elements
- Combine adjacent paths with same fill
- Remove empty `<g>` wrappers
