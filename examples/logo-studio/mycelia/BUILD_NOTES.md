# Mycelia — Build Notes

## Font substitutions

The brand brief calls for a contemporary transitional serif "in the lineage of
Caslon or Mrs Eaves, but with sharper terminals and a touch of the modernist",
a humanist body sans (Söhne / GT America), and a monospaced serif (Pitch).
All three are paid typefaces, so they have been substituted with SIL Open Font
License (OFL) Google Fonts equivalents cleared for commercial logo use:

| Brief intent | Substitute (OFL) | Rationale |
|---|---|---|
| Caslon / Mrs Eaves display serif | **Fraunces** (144pt opsz, Regular) | Variable transitional serif with modernist terminals; matches the brief's "sharper terminals and touch of modernist" almost exactly. |
| Söhne / GT America humanist sans | **Work Sans** | Warm, slightly irregular humanist rhythm; available at all required weights. |
| Pitch monospaced serif | **IBM Plex Mono** | Corporate-warm monospace with serif tendencies; used only for specimen-label metadata (small caps, dose, origin, batch). |

The working wordmark uses live `<text>` with these Google Fonts plus a system
fallback cascade. The outlined deliverable (`logo-mycelia-outlined.svg`) was
generated from the Fraunces 144pt Regular TTF via opentype.js and optimized
with svgo.

## Selected finalist

**A1 — The Understory** (Direction A, canonical spec from the brief).

This is the combination mark the brief explicitly specifies: the monoline
circular mycelial diagram (hub + twelve radiating filaments at a single
hairline weight, with graded spore-node terminals) paired with "mycelia" in
Fraunces, lowercase, loose tracking, a single hairline rule underneath.

A3 (symbol only, larger viewBox) is the source for the app-asset icon master.

## Deliverable inventory

```
mycelia/
├── logo-studio-mycelia.html            — Phase 5 gallery (9 concepts × 5 variants)
├── logo-mycelia.svg                    — Final combination mark (Loam on Parchment)
├── logo-mycelia-mono.svg               — Monochrome on light
├── logo-mycelia-reversed.svg           — Reversed (Parchment on Loam)
├── logo-mycelia-icon.svg               — Symbol only (200×200)
├── logo-mycelia-outlined.svg           — Text-to-path delivery asset (font-independent)
├── icon-master.svg                     — 1024×1024 square icon master (Loam bg)
├── build-assets.mjs                    — Phase 7 pipeline (adapted for Mycelia)
├── outline-wordmark.mjs                — Generates the outlined combination mark
├── post-build.mjs                      — Adds favicon.svg, safari-pinned-tab.svg, maskable icons
├── fix-social.mjs                      — Corrects social-image canvas dimensions
├── fraunces.ttf                        — Fraunces 144pt Regular (OFL) for outlining
└── dist/assets/
    ├── logo.svg, icon-master.svg       — Optimized working SVGs
    ├── AppIcon.appiconset/              — iOS 18 (light/dark/tinted 1024 + Contents.json)
    ├── AppIcon.icns                    — Real macOS .icns (10-size iconset compiled by iconutil)
    ├── AppIcon.iconset/                — Intermediate iconset source
    ├── android/                        — android-chrome PNGs 36–512
    ├── windows/                        — MS tile PNGs (70/144/150/310×150/310)
    ├── web/
    │   ├── favicon.ico (multi-res)
    │   ├── favicon.svg                 — Added by post-build
    │   ├── favicon-16/32/48.png
    │   ├── apple-touch-icon*.png       — 57 / 60 / 72 / 76 / 114 / 120 / 144 / 152 / 167 / 180 / 1024
    │   ├── maskable-192.png, maskable-512.png   — Added by post-build (70% safe zone)
    │   ├── safari-pinned-tab.svg       — Added by post-build (16×16 monochrome silhouette)
    │   ├── manifest.webmanifest, site.webmanifest
    │   └── browserconfig.xml
    ├── social/                         — og / twitter / linkedin / profile (correct dimensions)
    └── favicon.ico                     — Top-level convenience copy
```

## Gaps and deviations

1. **Wordmark-only outlined variant.** The skill's delivery list names
   `logo-{name}-outlined.svg` — singular. This ships as the outlined
   combination mark (mycelial mark + outlined "mycelia"). If a wordmark-only
   outlined asset is required later, rerun `node outline-wordmark.mjs` with the
   combination block removed.

2. **PNG optimization step.** The build pipeline's final `pngquant`/`oxipng`
   optimization is a no-op on this machine because neither binary is installed
   (`brew install pngquant oxipng` if smaller files are needed). The output
   PNGs are still valid, just not losslessly crunched.

3. **Social-image pipeline fix.** The shipped `build-assets.mjs` produces
   oversized social canvases because of its resize + extend + cover chain.
   `fix-social.mjs` regenerates them at exact target dimensions
   (1200×630, 1200×628, 1200×627, 400×400, 512×512). The `social/*.png` on
   disk are the corrected versions.

4. **svgo plugin warnings.** `build-assets.mjs` prints a preset-default
   warning about `removeViewBox` / `removeDimensions`. It is cosmetic — svgo
   still optimizes and preserves the viewBox. Upstream fix: move those two
   plugin names out of `overrides` and into the plugin list as separate
   entries.

5. **Safari pinned-tab mark.** Simplified to a legible silhouette at 16×16
   (ring, hub, six cardinal filaments, twelve spore nodes). The full A3 mark
   has too many hairlines to render cleanly at favicon scale; this is the
   "small-band" simplification the skill's multi-master design section
   recommends.
