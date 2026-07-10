# App Asset Production

Reference for generating platform-specific app assets from a finalized logo.

## Table of Contents

- [Icon vs Logo](#icon-vs-logo)
- [The Icon Master](#the-icon-master)
- [Platform Specifications](#platform-specifications)
  - [iOS](#ios)
  - [Android](#android)
  - [macOS](#macos)
  - [Windows](#windows)
  - [Favicons and Web](#favicons-and-web)
  - [Social and Open Graph](#social-and-open-graph)
- [Tool Stack](#tool-stack)
- [Build Pipeline](#build-pipeline)
- [Output Structure](#output-structure)
- [Gotchas and Troubleshooting](#gotchas-and-troubleshooting)

---

## Icon vs Logo

A logo and an app icon are related but distinct artifacts. A logo lives on a page with horizontal breathing room. An icon lives in a fixed square, competes with dozens of siblings on a home screen, and must be legible at 16px.

**Why logos fail as icons:**

- Combination marks (symbol + wordmark) become illegible when squeezed into a square
- Horizontal lockups waste vertical space
- Thin strokes vanish at small sizes
- Logo on white reads as absence of design next to filled neighbors

**The icon test:** Place the mark in a 1024×1024 square with a filled background. If it feels intentional, balanced, and recognizable at 48px, it is ready. If it looks like a shrunken logo, the icon design work has not started.

**Key principle:** The icon is a portrait of the brand, not a reproduction. It usually isolates the symbol, drops the wordmark, and sits on a deliberate background color — the icon owns its own canvas.

---

## The Icon Master

The icon master is the canonical source for all app assets — a single 1024×1024 SVG that is derived from (but distinct from) the final logo.

### Icon Master Construction Rules

| Property | Value |
|----------|-------|
| Canvas | 1024×1024, square |
| Background | Deliberate brand color — not transparent, not pure white |
| Content | Usually the symbol only; monograms for wordmark-only brands |
| Typography | Text outlined to paths before rasterization |
| Padding | Varies by platform (see below) |
| Corner radius | None — platforms apply their own masks |
| Format | SVG with flat fills or subtle gradients |

### Multi-Master Design

Large brands maintain distinct masters for different size bands:

| Size Band | Simplification |
|-----------|----------------|
| Large (512+) | Full detail, subtle texture, refined curves |
| Medium (64–256) | Drop hairlines, flatten gradients, nudge optical alignment |
| Small (16–32) | Reduce to single glyph or silhouette; manual pixel alignment |

For small brands, a single 1024 master with careful construction suffices.

### Platform Padding

Design content within these safe zones on the icon master:

| Platform | Content Zone |
|----------|-------------|
| iOS | ~80% centered (≈ 820px inside 1024) |
| Android adaptive | 66dp inside 108dp = ~61% centered |
| macOS | ~10% inset on all sides |
| Windows | ~16% inset on all sides |
| Favicon | Tight but with 1–2px breathing room |

The icon master targets the **most restrictive** safe zone (Android's 66/108) so it works across all platforms. Platform-specific variants can relax padding where more room is available.

### Monochrome Variant

A flat single-color silhouette variant of the icon is required for:

- Safari pinned tab (SVG)
- Android themed icons (Android 13+)
- iOS notification glyphs
- watchOS complications

This is designed together with the main icon, not derived afterward.

---

## Platform Specifications

### iOS

**Modern approach (Xcode 14+, iOS 18):** A single 1024×1024 PNG is sufficient — Xcode downscales all device sizes at build time.

**Format requirements:**

| Property | Value |
|----------|-------|
| Format | PNG, sRGB or Display P3 |
| Alpha | None — flattened, no transparency |
| Corner radius | None — iOS applies the squircle mask |
| Safe area | Central ~80% (820px inside 1024) |

**iOS 18 variants** (three 1024×1024 PNGs):

| Variant | Description |
|---------|-------------|
| Light (default) | Any background, full color |
| Dark | Transparent or dark background, bright glyph |
| Tinted | Grayscale only, no background, system applies tint |

**AppIcon.appiconset/Contents.json:**

```json
{
  "images": [
    {
      "filename": "icon-light-1024.png",
      "idiom": "universal",
      "platform": "ios",
      "size": "1024x1024"
    },
    {
      "filename": "icon-dark-1024.png",
      "idiom": "universal",
      "platform": "ios",
      "size": "1024x1024",
      "appearances": [{ "appearance": "luminosity", "value": "dark" }]
    },
    {
      "filename": "icon-tinted-1024.png",
      "idiom": "universal",
      "platform": "ios",
      "size": "1024x1024",
      "appearances": [{ "appearance": "luminosity", "value": "tinted" }]
    }
  ],
  "info": { "version": 1, "author": "xcode" }
}
```

### Android

**Adaptive icon geometry:** Each layer is 108×108 dp. The visible mask is a 72 dp circle/squircle. The safe content zone is the central 66×66 dp.

**Required layers:**

| Layer | Size | Content |
|-------|------|---------|
| `ic_launcher_background` | 108×108 dp | Full-bleed color or pattern |
| `ic_launcher_foreground` | 108×108 dp | Symbol, transparent outside safe zone |
| `ic_launcher_monochrome` | 108×108 dp | Single-channel alpha mask (Android 13+) |

**Legacy raster densities** (`res/mipmap-{density}/ic_launcher.png`):

| Density | Size |
|---------|------|
| mdpi | 48×48 |
| hdpi | 72×72 |
| xhdpi | 96×96 |
| xxhdpi | 144×144 |
| xxxhdpi | 192×192 |

**Play Store icon:** 512×512 PNG, 32-bit with alpha, under 1 MB.

**Notification icon:** White on transparent only, mdpi 24×24 through xxxhdpi 96×96. System applies tint.

**`res/mipmap-anydpi-v26/ic_launcher.xml`:**

```xml
<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@drawable/ic_launcher_background" />
    <foreground android:drawable="@drawable/ic_launcher_foreground" />
    <monochrome android:drawable="@drawable/ic_launcher_monochrome" />
</adaptive-icon>
```

### macOS

**Format:** `.icns` file built from a `.iconset` folder via `iconutil`.

**Exact filenames in `AppIcon.iconset/`:**

```
icon_16x16.png        (16)
icon_16x16@2x.png     (32)
icon_32x32.png        (32)
icon_32x32@2x.png     (64)
icon_128x128.png      (128)
icon_128x128@2x.png   (256)
icon_256x256.png      (256)
icon_256x256@2x.png   (512)
icon_512x512.png      (512)
icon_512x512@2x.png   (1024)
```

**Build command:**

```bash
iconutil -c icns AppIcon.iconset -o AppIcon.icns
```

**Shape:** macOS does not auto-mask. The icon's shape on disk is its shape on screen. Content fits the macOS squircle template with ~10% inset — the outer margin accommodates the system shadow.

### Windows

**.ico file:** Multi-resolution container. Includes 16, 20, 24, 32, 40, 48, 64, 256 in a single `.ico`. PNG compression for 256, BMP for smaller sizes.

**MSIX / UWP tile assets** (PNG in `Assets/` folder):

| Asset | Size (1x) |
|-------|-----------|
| Square44x44Logo (app list, taskbar) | 44×44 |
| Square71x71Logo (small tile) | 71×71 |
| Square150x150Logo (medium tile) | 150×150 |
| Wide310x150Logo (wide tile) | 310×150 |
| Square310x310Logo (large tile) | 310×310 |
| StoreLogo | 50×50 |
| SplashScreen | 620×300 |

Scale variants: `.scale-100.png`, `.scale-125`, `.scale-150`, `.scale-200`, `.scale-400`.

### Favicons and Web

**Classic:**

| File | Size |
|------|------|
| `favicon.ico` | Multi-res: 16, 32, 48 |
| `favicon-16x16.png` | 16 |
| `favicon-32x32.png` | 32 |
| `favicon.svg` | Scalable |

**Apple:**

| File | Size |
|------|------|
| `apple-touch-icon.png` | 180×180 (primary) |
| Optional | 152, 167, 120 |

**PWA Web App Manifest:**

```json
{
  "icons": [
    { "src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png" },
    { "src": "/icons/maskable-192.png", "sizes": "192x192", "type": "image/png", "purpose": "maskable" },
    { "src": "/icons/maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ]
}
```

Maskable icons need content within the central 80% safe circle (40% radius from center).

**Safari pinned tab:** `safari-pinned-tab.svg` — single-color monochrome SVG, `viewBox="0 0 16 16"`, no fills (Safari applies fill color).

**HTML head references:**

```html
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="mask-icon" href="/safari-pinned-tab.svg" color="#000000">
```

### Social and Open Graph

| Asset | Size (px) | Ratio | Notes |
|-------|-----------|-------|-------|
| Open Graph image | 1200×630 | 1.91:1 | `og:image`, under 5 MB |
| Twitter summary_large_image | 1200×628 | ~2:1 | Under 5 MB |
| LinkedIn share | 1200×627 | 1.91:1 | |
| Twitter/X profile | 400×400 | 1:1 | Circular crop; keep logo in central ~85% |
| LinkedIn company logo | 300×300 | 1:1 | Square |
| Discord server icon | 512×512 | 1:1 | Circular crop |

**Profile picture safe zone:** Critical content within a centered circle of ~85% diameter (all major platforms apply circular masks).

---

## Tool Stack

### Primary Tools (actively maintained, scriptable)

| Tool | Purpose | Install |
|------|---------|---------|
| **sharp** | Programmatic rasterization (Node, libvips) | `npm i sharp` |
| **resvg** | CLI rasterization, best SVG 1.1 compliance | `brew install resvg` |
| **rsvg-convert** | CLI rasterization (librsvg) | `brew install librsvg` |
| **favicons** | Complete favicon/iOS/Android/Windows package (npm) | `npm i favicons` |
| **pwa-asset-generator** | PWA icons, iOS splash, maskable icons | `npm i pwa-asset-generator` |
| **iconutil** | macOS .icns builder | Built into macOS |
| **svgo** | SVG optimization | `npm i svgo` |
| **pngquant** | Lossy PNG compression | `brew install pngquant` |
| **oxipng** | Lossless PNG optimization | `brew install oxipng` |

### Rasterizer Comparison

| Tool | Speed | SVG Coverage | Font Handling |
|------|-------|--------------|---------------|
| sharp (libvips) | Fastest in-process | Good: gradients, masks, clipPaths | Needs fontconfig + system fonts |
| resvg | Very fast, single binary | Best SVG 1.1 compliance | `--use-system-fonts` or `--font-file` |
| rsvg-convert | Fast | Very good, few filter gaps | Uses system fontconfig |
| Inkscape CLI | Slow (full app startup) | Highest fidelity (reference) | Full font support |
| ImageMagick | Slow for SVG | Weakest — delegates to rsvg/MSVG | Via delegate |

### Avoided Tools

These tools are abandoned or unreliable for 2026 builds:

- `svgexport` — last publish 2022, heavy Chromium dependency
- `app-icon` — abandoned
- `png2icons` — abandoned
- `electron-icon-builder` — abandoned
- `cli-real-favicon` — depends on hosted API, rate-limited
- ImageMagick as primary SVG rasterizer — silently falls back to MSVG and butchers gradients

### One-Time Install

```bash
# macOS
brew install resvg librsvg pngquant oxipng
npm i -D sharp favicons pwa-asset-generator svgo png-to-ico

# Linux (CI)
apt-get install -y librsvg2-bin pngquant fontconfig fonts-liberation
npm i -D sharp favicons pwa-asset-generator svgo png-to-ico
```

---

## Build Pipeline

The complete build pipeline runs as a Node.js script: [build-assets.mjs](../assets/build-assets.mjs).

**Pipeline stages:**

1. Optimize source SVG with svgo
2. Generate favicon/iOS/Android/Windows package with `favicons` npm
3. Build macOS `.iconset` with sharp, then `iconutil` to produce `.icns`
4. Generate PWA splash screens and maskable icons with `pwa-asset-generator`
5. Generate Open Graph and social images
6. Optimize all PNGs with pngquant + oxipng

**Pure-CLI fallback** (single size, no Node):

```bash
resvg --width 1024 --use-system-fonts icon-master.svg icon-1024.png
rsvg-convert -w 512 -h 512 -a icon-master.svg -o icon-512.png
```

---

## Output Structure

```
dist/assets/
├── logo.svg                         # Optimized source logo
├── icon-master.svg                  # 1024×1024 square icon master
├── AppIcon.appiconset/              # iOS asset catalog
│   ├── Contents.json
│   ├── icon-light-1024.png
│   ├── icon-dark-1024.png
│   └── icon-tinted-1024.png
├── AppIcon.icns                     # macOS compiled icon
├── android/
│   ├── ic_launcher.xml              # Adaptive icon manifest
│   ├── ic_launcher_foreground.png
│   ├── ic_launcher_background.png
│   ├── ic_launcher_monochrome.png
│   ├── mipmap-mdpi/
│   ├── mipmap-hdpi/
│   ├── mipmap-xhdpi/
│   ├── mipmap-xxhdpi/
│   ├── mipmap-xxxhdpi/
│   └── play-store-512.png
├── windows/
│   ├── favicon.ico                  # 16/32/48/256 multi-res
│   ├── Square44x44Logo.png
│   ├── Square150x150Logo.png
│   ├── Wide310x150Logo.png
│   └── ...
├── web/
│   ├── favicon.ico
│   ├── favicon.svg
│   ├── favicon-16x16.png
│   ├── favicon-32x32.png
│   ├── apple-touch-icon.png         # 180×180
│   ├── icon-192.png
│   ├── icon-512.png
│   ├── maskable-192.png
│   ├── maskable-512.png
│   ├── safari-pinned-tab.svg        # Monochrome
│   ├── site.webmanifest
│   └── browserconfig.xml
└── social/
    ├── og-image-1200x630.png
    ├── twitter-card-1200x628.png
    └── profile-400x400.png
```

---

## Gotchas and Troubleshooting

### Fonts in Headless SVG Rasterization

**This is the single biggest failure mode.** Sharp, librsvg, and resvg all need the font installed on the system when rasterizing an SVG that contains `<text>` elements. CI containers silently substitute, producing wrong-font output.

**Fix:** Convert `<text>` to paths in the icon master SVG before rasterization. The icon master uses outlined paths specifically to sidestep this issue. See [typography.md](typography.md) for the dual-output workflow — keep a working SVG with live text, ship an outlined version for rasterization.

Conversion commands:

```bash
# Via Inkscape CLI
inkscape logo.svg --export-text-to-path \
  --export-plain-svg --export-filename=icon-master.svg

# Via svgo with convertTextToPath plugin (where available)
```

### Sharp Density

SVG is rasterized at the density set on the input, not the output. The default 72 DPI produces blurry edges at large sizes.

```js
// ❌ Blurry at 1024
sharp('logo.svg').resize(1024, 1024);

// ✅ Crisp at 1024
sharp('logo.svg', { density: 384 }).resize(1024, 1024);
```

### Aspect Ratio Preservation

Non-square logos need explicit handling to avoid stretching:

```bash
# rsvg-convert needs -a flag
rsvg-convert -w 512 -a logo.svg -o out.png

# sharp needs fit: 'contain' with transparent background
sharp(src).resize(512, 512, {
  fit: 'contain',
  background: { r: 0, g: 0, b: 0, alpha: 0 }
})
```

### favicons Package .ico Limitation

The `favicons` npm package only embeds 16/32/48 in its `.ico` output. For Windows desktop shortcuts needing 256, post-process with `png-to-ico`.

### pwa-asset-generator Chromium

`pwa-asset-generator` downloads Chromium on first run. Pre-warm in CI or set `PUPPETEER_EXECUTABLE_PATH` to a system Chrome installation.

### Flag Differences Between Rasterizers

resvg and rsvg-convert use different flag conventions:

| Operation | resvg | rsvg-convert |
|-----------|-------|--------------|
| Width | `--width 512` | `-w 512` |
| Preserve aspect | Automatic | `-a` required |
| Font handling | `--use-system-fonts` | Uses fontconfig |

### iconutil Platform Limitation

`iconutil` is macOS-only. On Linux CI, use `png2icns` from libicns:

```bash
apt-get install icnsutils
png2icns AppIcon.icns icon_16.png icon_32.png ...
```

Avoid the abandoned `png2icons` npm package.

### Maskable Icon Safe Zone

Maskable icons need content within the central 80% circle (40% radius). `pwa-asset-generator` handles this with `--padding "15%"`. The `favicons` package does not generate maskables by default — enable via `icons.android` maskable option.
