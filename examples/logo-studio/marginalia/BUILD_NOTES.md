# Marginalia — Build Notes

## Font Substitutions

The brand brief specifies paid/custom typefaces. All were substituted with free,
OFL-licensed Google Fonts cleared for commercial logo use.

| Brief calls for | Substitution | Rationale |
|---|---|---|
| "A contemporary re-cut of a classical serif — Didone-meets-transitional" (display) | **Fraunces** (`700`, variable) | Variable transitional serif with high contrast, sharp terminals, and a slight warmth. The closest free cousin to Didone-meets-transitional. Playfair Display is the fallback. |
| "Lyon, Quarto, or Source Serif" (body) | **Spectral** (used only in gallery prose) | Book-grade reading serif; optically tuned, generous figures. |
| "Söhne, or a custom cut" (editorial sans) | **Work Sans** (`500/700`) | Humanist, slightly literary grotesque; tight family, confident at caption sizes. |
| "A specific human's handwriting" (C2 signature) | **Caveat** (`700`) | Natural upright script, reads as signed rather than scripted. |

All fonts are loaded in the gallery via Google Fonts. The final deliverable SVGs
reference the font stack with `Fraunces` first and sensible fallbacks (`Playfair
Display`, `Libre Caslon Display`, `Georgia`).

## Finalist

**A2 — Margin-Rule Wordmark**. Default per the skill spec: the canonical
concept specified in the brief.

The wordmark is constructed as two `<text>` fragments ("Marg" and "nalia") with
a hand-placed rectangle (`<rect x="220" y="38" width="6" height="58">`) sitting
in the position of the first lowercase i. This gives a slim, dotless "margin
rule" stem at full x-height. The second i renders naturally.

This arrangement assumes Fraunces 700 at size 90 with letter-spacing -1. In
browsers without Fraunces, Playfair Display / Georgia fall back — the rule
alignment is robust to roughly ±4px of advance-width variation. The rule
placement was visually calibrated in Safari/Chrome with Fraunces loaded.

## Outlined Delivery Variant

`logo-marginalia-outlined.svg` embeds an `@import` for Fraunces via Google
Fonts (self-contained for web delivery). True vector outlines (for print or
environments without internet) require running the file through
`Path → Object to Path` in Inkscape, or using `fonttools`/`opentype.js` to
convert the `<text>` elements to paths. Automating that conversion was out of
scope for this pass — production finishing should do it before merch/print.

## Icon Master

The icon master at `dist/assets/icon-master.svg` is **not** a rasterization of
the wordmark. It is an M monogram hand-constructed from outlined shapes
(`<rect>`, `<polygon>`, `<path>`) — deliberately **not** `<text>` — so every
rasterizer (sharp, librsvg, resvg, CI without fonts) produces the same glyph.
The high-contrast serif M with tapered-bracket serifs and the stamp-red baseline
rule reads as a literary press mark at 1024px and remains legible as a silhouette
at 32px.

A wordmark-only brand still needs a square icon: the M is the handshake
between the wordmark (which owns `marginalia.com`) and the home-screen icon
(which owns the 60×60 square next to other apps).

## Pipeline

`build-assets.mjs` was copied from `logo-studio/assets/build-assets.mjs` and
adapted by editing only the `CONFIG` block. The pipeline generated:

- ✅ iOS AppIcon.appiconset (light / dark / tinted 1024 PNGs + Contents.json)
- ✅ macOS AppIcon.icns (real Mac OS X icon resource, 86 KB, built via `iconutil`)
- ✅ Android adaptive icon (background / foreground / monochrome + `ic_launcher.xml`)
- ✅ Android legacy mipmap densities (mdpi through xxxhdpi)
- ✅ Android Play Store 512 PNG
- ✅ Windows multi-resolution `.ico` (16/24/32-bit) + MSIX tiles (70/144/150/310²)
- ✅ Web: `favicon.ico`, `favicon.svg`, `favicon-16/32/48`, `apple-touch-icon` suite
- ✅ PWA: `site.webmanifest`, `manifest.webmanifest`, `icon-192/512`, `maskable-192/512`, `safari-pinned-tab.svg`
- ✅ Social: OG 1200×630, Twitter 1200×628, LinkedIn 1200×627, profile 400 + 512

## Minor Gaps

- **PNG optimization** (pngquant + oxipng) was skipped by the pipeline because
  those CLI tools aren't installed in the environment. Output PNGs are
  unoptimized but correct. Run `brew install pngquant oxipng` and re-execute
  the build to close this gap.
- **pwa-asset-generator splash screens** were not generated (not installed).
  The maskable PWA icons were built directly with sharp instead, covering the
  core PWA icon contract. Splash screens for each iOS device size are a larger
  asset set that can be generated with `npx pwa-asset-generator icon-master.svg
  out/ --type png --background "#F4EBDD"` if needed.
- **Outlined wordmark** is currently `<text>` with `@font-face` import, not true
  vector paths — see "Outlined Delivery Variant" above.
