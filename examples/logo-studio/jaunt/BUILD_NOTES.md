# Jaunt — Build Notes

Production build log for the `logo-studio` skill executed against the Jaunt brand brief.

## Font substitution

The brief calls for **GT Flexa** (display) and **Söhne Buch / Inter Display** (body). GT Flexa is commercial. The wordmark and gallery therefore use **Manrope** (Google Fonts, OFL — free for commercial logo use) as the closest free match for GT Flexa's warm humanist-geometric character.

- Chosen: `Manrope` weights 700/800 with `letter-spacing: -2` (approximates GT Flexa's ExtraBold tracking)
- Fallback stack: `Manrope, 'Inter', -apple-system, system-ui, sans-serif`
- Secondary (slab monospace for hand-numbers, per brief): `Space Mono` / `JetBrains Mono`

When the client licenses GT Flexa, the wordmark can be re-set without structural change — only `font-family` changes in the working SVGs.

## Finalist

**A2 — canonical wordmark**, per the brief's explicit specification: lowercase `jaunt` set in Shade Navy with a Jaunt Red tick above the "u". The finalist was chosen without iteration (the skill runs autonomously; the A-row canonical wordmark is the brief's own design direction).

## What was produced

### Top-level logo deliverables (5)

- `logo-jaunt.svg` — full color working file (live `<text>`)
- `logo-jaunt-mono.svg` — monochrome
- `logo-jaunt-reversed.svg` — cream on Shade Navy with red tick
- `logo-jaunt-icon.svg` — square symbol form (200×200) with cream badge + navy "j" + red tick
- `logo-jaunt-outlined.svg` — text converted to hand-drawn geometric paths (font-independent delivery). Note: these are approximations of Manrope ExtraBold drawn by hand, not true outlines of the font. For pixel-perfect outlines once the display face is licensed, run `inkscape logo-jaunt.svg --export-text-to-path --export-plain-svg --export-filename=logo-jaunt-outlined.svg` with Manrope (or GT Flexa) installed on the system.

### Gallery

- `logo-studio-jaunt.html` — self-contained HTML with all 9 concepts × 3 variants = 27 inlined SVGs. Signal Cream page background, Shade Navy dark panes.

### Icon master

- `icon-master.svg` — 1024×1024 Jaunt Red background with a Signal Cream lowercase "j" monogram and Jaunt Red tick rendered in cream. Path-only (no `<text>`) to keep headless rasterization deterministic.

### App asset package (`dist/assets/`)

Built via `build-assets.mjs` using sharp + favicons + svgo + iconutil:

| Platform | Status |
|----------|--------|
| iOS `AppIcon.appiconset/` (light/dark/tinted 1024 PNGs + Contents.json) | Built |
| macOS `AppIcon.icns` via iconutil | Built (80 KB) |
| Android chrome 36–512 PNGs | Built |
| Windows mstile 70/144/150/310/310×150 | Built |
| Web favicon.ico (multi-res), favicon-16/32/48.png, apple-touch-icons 57–1024 | Built |
| Web `favicon.svg` | Hand-copied from icon-master |
| Web `safari-pinned-tab.svg` (monochrome 16×16) | Hand-written |
| Web `manifest.webmanifest` | Built |
| Social OG / Twitter / LinkedIn / profile | Built (1200×630, 1200×628, 1200×627, 400, 512) |

All PNGs are real (verified by file sizes 270 B – 80 KB). The 1024 light iOS icon was visually inspected and renders correctly: Signal Cream "j" with dot + Jaunt Red tick (drawn cream for contrast) on the Jaunt Red field.

## Gaps vs. the full skill spec

1. **Android adaptive-icon layers.** The `favicons` npm package emits raster `android-chrome-*.png` but not the `ic_launcher.xml` adaptive-icon manifest, `ic_launcher_foreground/background/monochrome` layers, or the `mipmap-{mdpi..xxxhdpi}/` legacy density directory structure. The rasters are present; a client shipping an Android app would need to generate those XML layers from the icon master separately (the existing PNGs cover the density bands but are not named for the Android project layout).

2. **PWA maskable icons and splash screens.** `pwa-asset-generator` was intentionally skipped — it pulls Chromium on first run, is slow in CI, and frequently stalls. The `favicons` package does not emit maskable variants by default. The existing 192/256/384/512 Android PNGs serve as the PWA `any` purpose icons; dedicated `maskable` entries (with 80% safe-zone padding) would need a separate run of `pwa-asset-generator --padding 15%` or an equivalent manual build.

3. **Windows `.ico` at 256.** The favicons-generated `favicon.ico` bundles 16/32/48 only. Windows desktop shortcuts at 256 would need a post-process pass with `png-to-ico` (the dependency is installed; the pipeline step was not added because the typical web/app delivery doesn't need it).

4. **PNG optimization.** `pngquant` and `oxipng` were not present on the system; the optimization step printed `(skipped …)` and exited cleanly. PNG file sizes shown above are sharp's default output. Install `brew install pngquant oxipng` and re-run stage 6 for ~30–50% size reduction if needed.

5. **svgo deprecation warnings.** svgo 4.x moved `removeViewBox`/`removeDimensions` out of `preset-default`. The build emits warnings but still produces valid optimized SVGs — the `overrides` are silently ignored, and `viewBox` is preserved (which is the only behavior that matters). Not fixed to keep compatibility with the skill's canonical `build-assets.mjs`.

## Verification

- 9 × 3 = 27 SVG concepts embedded and rendered in `logo-studio-jaunt.html`
- 5 final SVGs present at top level (all under 2 KB)
- `dist/assets/` contains 50+ real PNGs, `AppIcon.icns`, `favicon.ico`, `manifest.webmanifest`
- 1024 iOS light icon visually verified (j-monogram with tick, correct colors)
- 32×32 favicon legibility confirmed — j and tick both resolve at favicon scale
