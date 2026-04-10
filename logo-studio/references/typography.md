# Logo Typography Reference

Typography strategy and font catalog for logo design.

## Table of Contents

- [The Text-vs-Path Decision](#the-text-vs-path-decision)
- [Three Implementation Tiers](#three-implementation-tiers)
- [Professional Free Typefaces](#professional-free-typefaces)
- [Classic Pairings for Logos](#classic-pairings-for-logos)
- [Implementation Patterns](#implementation-patterns)
- [Licensing](#licensing)
- [Common Pitfalls](#common-pitfalls)

---

## The Text-vs-Path Decision

A logo wordmark is either **set type** (real font) or **custom lettering** (drawn paths). These have very different workflows.

### Set Type (use `<text>` elements)

Most modern tech and product brands use set type — their wordmark is an existing typeface applied directly.

| Brand | Typeface |
|-------|----------|
| Spotify | Circular |
| Google | Product Sans |
| Airbnb | Cereal |
| Figma | Whyte Inktrap |
| Vercel | Inter (ish) |
| Stripe | Camphor Pro |

**Characteristics of set type logos:**
- Recognizable typeface underneath
- Consistent stroke weight and proportions
- Editable — can be regenerated at any size
- Can be searched, read by screen readers, and selected as text

### Custom Lettering (use `<path>` elements)

Drawn letterforms unique to the brand.

| Brand | Notes |
|-------|-------|
| Coca-Cola | Spencerian script, hand-drawn |
| Disney | Walt Disney's signature stylized |
| Instagram (wordmark) | Custom brush script |
| FedEx | Modified Univers with the arrow ligature |
| Visa | Custom geometric with the golden slash |

**Characteristics of custom lettering:**
- Unique letterforms not from any font
- Modified glyphs (stretched S, custom ligature, proprietary curve)
- Delivered as vector paths
- Not editable as text

### Decision Tree

```
Is the wordmark built from an existing typeface?
├── Yes → Use <text> element with font-family
│         (Tier 1 or Tier 2 below)
│
└── No → Use <path> elements
          Is it based on a typeface with modifications?
          ├── Yes → Start from <text>, export as paths, edit in vector tool
          └── No → Construct from geometric primitives directly
```

**Default for the logo studio:** Start with `<text>` and real fonts. Switch to paths only when the concept explicitly calls for custom lettering or when delivering a finalized brand asset.

---

## Three Implementation Tiers

### Tier 1 — Live Text with Font Stack (iteration default)

Fastest to generate and iterate. The HTML gallery preview loads Google Fonts so `<text>` renders with the real font.

```svg
<svg viewBox="0 0 400 100" xmlns="http://www.w3.org/2000/svg">
  <text x="200" y="65" text-anchor="middle"
        font-family="Inter, -apple-system, system-ui, sans-serif"
        font-size="48" font-weight="800" letter-spacing="-1"
        fill="#0A0A0A">Acme</text>
</svg>
```

**When:** Concept generation, gallery preview, iteration cycles.

### Tier 2 — Base64-Embedded Subset (portable delivery)

Self-contained SVG that renders identically in any viewer. The font is subset to the needed glyphs only (typically 1–3 KB).

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

**When:** Shipping a portable SVG (email, embedded in PDFs, third-party tools).

**Subsetting command:**
```bash
pyftsubset Inter-Bold.ttf --text="Acme" --flavor=woff2 \
  --layout-features=liga,kern --output-file=inter-acme.woff2
base64 -i inter-acme.woff2
```

### Tier 3 — Outlined Paths (final brand asset)

The text is converted to geometric paths. No font dependencies, identical rendering everywhere, not editable as text.

```svg
<svg viewBox="0 0 400 100" xmlns="http://www.w3.org/2000/svg">
  <path d="M45 70 L60 15 L75 70 L68 70 L65 55 L55 55 L52 70 Z
           M57 48 L63 48 L60 30 Z" fill="#0A0A0A" fill-rule="evenodd"/>
  <!-- ... rest of letter paths ... -->
</svg>
```

**When:**
- Final deliverable for print, merch, signage, packaging
- Custom lettering that was never a font
- Licensing uncertainty or restricted font
- Guaranteed identical rendering in any tool (Inkscape, Illustrator, PDF readers)

**Conversion command:**
```bash
inkscape logo.svg --export-text-to-path --export-plain-svg --export-filename=logo-outlined.svg
```

---

## Professional Free Typefaces

All listed fonts are SIL Open Font License (OFL) or similar — cleared for commercial logo use.

### Sans-Serif Workhorses

| Font | Character | Best For |
|------|-----------|----------|
| **Inter** | Modern, geometric-humanist, huge weight range | Tech, SaaS, fintech, startups |
| **Work Sans** | Friendly, optimized for display sizes | Consumer products, agencies |
| **Manrope** | Semi-geometric, distinctive personality | Modern brands wanting character |
| **DM Sans** | Clean, neutral, warm | Minimal brands, editorial |
| **Space Grotesk** | Tech-forward, slightly quirky | Developer tools, indie tech |
| **Plus Jakarta Sans** | Friendly geometric | Fintech, consumer apps |
| **Archivo** / **Archivo Black** | Strong, confident display weight | Bold statements, sports, media |
| **Outfit** | Modern, slightly rounded | Youth brands, design tools |

### Serif Workhorses

| Font | Character | Best For |
|------|-----------|----------|
| **Playfair Display** | High contrast, editorial | Fashion, luxury, publishing |
| **Fraunces** | Variable, characterful, contemporary | Modern editorial, bold brands |
| **Cormorant Garamond** | Elegant, refined, classical | Luxury, wellness, boutique |
| **Libre Caslon Display** | Classical authority | Law, finance, institutions |
| **Spectral** | Modern serif with personality | Editorial tech, thought leaders |
| **Source Serif** | Workhorse serif, legible | Documentation, long-form |

### Display & Distinctive

| Font | Character | Best For |
|------|-----------|----------|
| **Bricolage Grotesque** | Modern, quirky, variable | Creative agencies, indie |
| **Unbounded** | Geometric display, bold | Tech bold statements |
| **Bungee** | Vertical-friendly, signage | Entertainment, retail |
| **Rubik Mono One** | Bold monospaced | Tech, gaming |
| **Zilla Slab** | Friendly slab serif | Editorial tech, media |
| **Syne** | Unconventional display | Art, culture, music |

### Monospace

| Font | Character | Best For |
|------|-----------|----------|
| **JetBrains Mono** | Developer-optimized, readable | Dev tools, technical brands |
| **Space Mono** | Geometric, distinctive | Crypto, indie tech |
| **IBM Plex Mono** | Corporate but warm | Enterprise tech |

---

## Classic Pairings for Logos

Combination marks often use two typefaces (primary mark + tagline/supporting text).

| Primary | Secondary | Feel |
|---------|-----------|------|
| Playfair Display | Inter | Editorial tech |
| Fraunces | Work Sans | Modern sophisticated |
| Archivo Black | DM Sans | Bold statement |
| Space Grotesk | Space Mono | Dev-tool consistency |
| Cormorant Garamond | Outfit | Luxury minimal |
| Manrope | Manrope | Single-family contrast via weight |
| Bricolage Grotesque | Inter | Indie modern |
| Libre Caslon Display | Source Serif | Classical authoritative |

**Single-family principle:** When in doubt, use one family at contrasting weights (Inter 800 + Inter 400) rather than forcing a pairing.

---

## Implementation Patterns

### Pattern A — Gallery Preview (HTML context)

The HTML gallery loads Google Fonts in `<head>`, then SVG `<text>` inherits the font.

```html
<head>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&family=Fraunces:wght@400;700;900&display=swap" rel="stylesheet">
</head>
```

Then inside any SVG card:
```svg
<text font-family="Inter, sans-serif" font-weight="800" ...>Acme</text>
```

### Pattern B — Fallback Cascade

Every `font-family` declaration ends with a system fallback:

```
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
font-family: 'Playfair Display', Georgia, 'Times New Roman', serif;
font-family: 'JetBrains Mono', 'SF Mono', Menlo, monospace;
```

A logo never renders in Times New Roman accidentally.

### Pattern C — Letter Spacing & Optical Size

Logo-specific typography requires tighter tracking than body text:

```svg
<!-- Display sizes: tight tracking -->
<text font-size="72" letter-spacing="-2" font-weight="800">ACME</text>

<!-- Wider tracking for all-caps elegance -->
<text font-size="24" letter-spacing="4" font-weight="500">ACME</text>

<!-- Variable font optical size for display use -->
<text style="font-variation-settings: 'opsz' 144;" font-size="64">Acme</text>
```

### Pattern D — Dual Output Workflow

Maintain two versions of each wordmark concept:

| File | Contents | Use |
|------|----------|-----|
| `logo-{name}.svg` | `<text>` with font-family | Working file, iteration |
| `logo-{name}-outlined.svg` | `<path>` elements | Delivery, print, merch |

The outlined version is generated at finalization:

```bash
inkscape logo-acme.svg --export-text-to-path \
  --export-plain-svg --export-filename=logo-acme-outlined.svg
```

---

## Licensing

### Safe for Commercial Logo Use

| License | Embed? | Modify? | Notes |
|---------|--------|---------|-------|
| **OFL** (SIL Open Font License) | Yes | Yes | Most Google Fonts, Adobe open-source |
| **Apache 2.0** | Yes | Yes | Roboto, some Google fonts |
| **Ubuntu Font License** | Yes | Yes | Ubuntu fonts |

### Restricted

| License | Notes |
|---------|-------|
| **Adobe Fonts / Typekit** | Cannot embed in logos. Web serving only. |
| **Monotype / Linotype retail** | Requires separate logo license ($$$) |
| **MyFonts commercial** | Usually requires extended license for logos |
| **Custom foundry retail** | Check the EULA; usually requires logo license |

### Safe Sources

- **Google Fonts** — fonts.google.com (all OFL or Apache)
- **Font Squirrel** — 100% commercially cleared, filter by "100% free"
- **GitHub** — Inter, IBM Plex, JetBrains Mono, etc. (check repo license)
- **Open Foundry** — open-foundry.com (curated OFL collection)

### Unsafe Sources

- **DaFont** / **1001Fonts** / **FontSpace** — licensing is inconsistent, many fonts marked "free" are actually personal-use only
- Fonts downloaded from unknown torrents or "free font" blogs

---

## Common Pitfalls

### Licensing

- License verification is required before embedding a font in a logo used commercially
- OFL is the safest default for generated work
- Outlining the final asset (Tier 3) sidesteps licensing questions entirely

### Rendering

- Variable font axes (`font-variation-settings`) are ignored in older renderers — bake into a static weight for delivery
- `letter-spacing` behaves differently in Safari vs. Chrome at subpixel values
- Windows GDI and macOS CoreText hint differently at small sizes
- Variable fonts in `<img src>` contexts may not apply custom axes

### Font Loading

- `font-display: block` is preferred for logos — prevents flash of fallback
- `font-display: swap` is fine for gallery previews (shows fallback, swaps when loaded)
- Screenshots of logos taken before font loads show fallback — wait for `document.fonts.ready` before capture

### Missing Fallbacks

- A bare `font-family="Inter"` declaration has no fallback — the cascade to `sans-serif` or a system stack is the safe pattern
- In standalone SVGs opened in email previews or file managers, external `@import` fails silently — base64 embedding or outlining is the reliable path

### Subsetting Gotchas

- Subset only includes the glyphs you specify — if the brand name later needs different characters (numbers, accents), re-subset
- Ligatures require including the OpenType `liga` feature: `--layout-features=liga,kern`
- Special characters (™, ®, ©) need to be added to the subset explicitly
