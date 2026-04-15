#!/usr/bin/env node
// ============================================================================
// build-assets.mjs — Logo Studio app asset pipeline
// ============================================================================
// Converts a finalized icon master SVG into a complete app asset package for
// iOS, Android, macOS, Windows, web (favicons + PWA), and social platforms.
//
// Prerequisites:
//   npm i -D sharp favicons pwa-asset-generator svgo png-to-ico
//   brew install resvg librsvg pngquant oxipng   # optional optimizers
//   iconutil is built into macOS
//
// Usage:
//   node build-assets.mjs
//
// Configure the CONFIG block below for the target brand.
// ============================================================================

import sharp from 'sharp';
import { favicons } from 'favicons';
import { optimize } from 'svgo';
import { execSync } from 'node:child_process';
import { readFile, writeFile, mkdir, copyFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { dirname, join } from 'node:path';

// ============================================================================
// CONFIG — edit for the target brand
// ============================================================================
const CONFIG = {
  // Source: the 1024×1024 square icon master with text outlined to paths
  iconMaster: 'icon-master.svg',

  // Optional: the full logo (combination mark) for web and documentation
  logo: 'logo.svg',

  // Output directory
  out: 'dist/assets',

  // Brand metadata
  brand: {
    name: 'Acme',
    shortName: 'Acme',
    description: 'Acme brand',
    themeColor: '#0A0A0A',
    backgroundColor: '#FFFFFF',
    startUrl: '/',
  },
};

// ============================================================================
// Pipeline
// ============================================================================

async function main() {
  const out = CONFIG.out;
  await mkdir(join(out, 'web'), { recursive: true });
  await mkdir(join(out, 'android'), { recursive: true });
  await mkdir(join(out, 'windows'), { recursive: true });
  await mkdir(join(out, 'social'), { recursive: true });
  await mkdir(join(out, 'AppIcon.appiconset'), { recursive: true });
  await mkdir(join(out, 'AppIcon.iconset'), { recursive: true });

  // --------------------------------------------------------------------------
  // Stage 1: Optimize source SVGs
  // --------------------------------------------------------------------------
  console.log('[1/6] Optimizing source SVGs with svgo...');
  const iconSvg = await optimizeSvg(CONFIG.iconMaster);
  await writeFile(join(out, 'icon-master.svg'), iconSvg);

  if (existsSync(CONFIG.logo)) {
    const logoSvg = await optimizeSvg(CONFIG.logo);
    await writeFile(join(out, 'logo.svg'), logoSvg);
  }

  const iconPath = join(out, 'icon-master.svg');

  // --------------------------------------------------------------------------
  // Stage 2: favicons package (iOS + Android + Windows + favicon + manifest)
  // --------------------------------------------------------------------------
  console.log('[2/6] Generating favicons package...');
  const faviconResult = await favicons(iconPath, {
    path: '/assets',
    appName: CONFIG.brand.name,
    appShortName: CONFIG.brand.shortName,
    appDescription: CONFIG.brand.description,
    background: CONFIG.brand.backgroundColor,
    theme_color: CONFIG.brand.themeColor,
    start_url: CONFIG.brand.startUrl,
    display: 'standalone',
    orientation: 'any',
    icons: {
      favicons: true,
      android: true,
      appleIcon: true,
      appleStartup: false,
      windows: true,
      yandex: false,
    },
  });

  // Write favicons images
  for (const image of faviconResult.images) {
    const subdir = routeFaviconImage(image.name);
    await mkdir(join(out, subdir), { recursive: true });
    await writeFile(join(out, subdir, image.name), image.contents);
  }

  // Write favicons manifest files (site.webmanifest, browserconfig.xml, etc.)
  for (const file of faviconResult.files) {
    await writeFile(join(out, 'web', file.name), file.contents);
  }

  // --------------------------------------------------------------------------
  // Stage 3: macOS .icns via iconutil
  // --------------------------------------------------------------------------
  console.log('[3/6] Building macOS .icns...');
  const icnsSizes = [
    { name: 'icon_16x16.png', size: 16 },
    { name: 'icon_16x16@2x.png', size: 32 },
    { name: 'icon_32x32.png', size: 32 },
    { name: 'icon_32x32@2x.png', size: 64 },
    { name: 'icon_128x128.png', size: 128 },
    { name: 'icon_128x128@2x.png', size: 256 },
    { name: 'icon_256x256.png', size: 256 },
    { name: 'icon_256x256@2x.png', size: 512 },
    { name: 'icon_512x512.png', size: 512 },
    { name: 'icon_512x512@2x.png', size: 1024 },
  ];

  for (const { name, size } of icnsSizes) {
    await sharp(iconPath, { density: 384 })
      .resize(size, size, {
        fit: 'contain',
        background: { r: 0, g: 0, b: 0, alpha: 0 },
      })
      .png()
      .toFile(join(out, 'AppIcon.iconset', name));
  }

  if (process.platform === 'darwin') {
    execSync(
      `iconutil -c icns "${join(out, 'AppIcon.iconset')}" -o "${join(out, 'AppIcon.icns')}"`,
    );
  } else {
    console.log('  (skipping iconutil — not on macOS; use png2icns on Linux)');
  }

  // --------------------------------------------------------------------------
  // Stage 4: iOS AppIcon.appiconset (iOS 18 single 1024 format)
  // --------------------------------------------------------------------------
  console.log('[4/6] Building iOS AppIcon.appiconset...');

  // Light variant: brand color background, full color logo
  await sharp(iconPath, { density: 384 })
    .resize(1024, 1024, { fit: 'contain', background: CONFIG.brand.backgroundColor })
    .flatten({ background: CONFIG.brand.backgroundColor })
    .png()
    .toFile(join(out, 'AppIcon.appiconset', 'icon-light-1024.png'));

  // Dark variant: dark background, same logo
  await sharp(iconPath, { density: 384 })
    .resize(1024, 1024, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
    .png()
    .toFile(join(out, 'AppIcon.appiconset', 'icon-dark-1024.png'));

  // Tinted variant: grayscale, transparent background
  await sharp(iconPath, { density: 384 })
    .resize(1024, 1024, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
    .grayscale()
    .png()
    .toFile(join(out, 'AppIcon.appiconset', 'icon-tinted-1024.png'));

  // Contents.json
  const iosContents = {
    images: [
      {
        filename: 'icon-light-1024.png',
        idiom: 'universal',
        platform: 'ios',
        size: '1024x1024',
      },
      {
        filename: 'icon-dark-1024.png',
        idiom: 'universal',
        platform: 'ios',
        size: '1024x1024',
        appearances: [{ appearance: 'luminosity', value: 'dark' }],
      },
      {
        filename: 'icon-tinted-1024.png',
        idiom: 'universal',
        platform: 'ios',
        size: '1024x1024',
        appearances: [{ appearance: 'luminosity', value: 'tinted' }],
      },
    ],
    info: { version: 1, author: 'logo-studio' },
  };
  await writeFile(
    join(out, 'AppIcon.appiconset', 'Contents.json'),
    JSON.stringify(iosContents, null, 2),
  );

  // --------------------------------------------------------------------------
  // Stage 5: Social / Open Graph images
  // --------------------------------------------------------------------------
  console.log('[5/6] Generating social images...');
  const socialSizes = [
    { name: 'og-image-1200x630.png', w: 1200, h: 630 },
    { name: 'twitter-card-1200x628.png', w: 1200, h: 628 },
    { name: 'linkedin-1200x627.png', w: 1200, h: 627 },
    { name: 'profile-400x400.png', w: 400, h: 400 },
    { name: 'profile-square-512.png', w: 512, h: 512 },
  ];

  for (const { name, w, h } of socialSizes) {
    await sharp(iconPath, { density: 384 })
      .resize(Math.round(Math.min(w, h) * 0.5), Math.round(Math.min(w, h) * 0.5), {
        fit: 'contain',
        background: { r: 0, g: 0, b: 0, alpha: 0 },
      })
      .extend({
        top: Math.round((h - Math.min(w, h) * 0.5) / 2),
        bottom: Math.round((h - Math.min(w, h) * 0.5) / 2),
        left: Math.round((w - Math.min(w, h) * 0.5) / 2),
        right: Math.round((w - Math.min(w, h) * 0.5) / 2),
        background: CONFIG.brand.backgroundColor,
      })
      .resize(w, h, { fit: 'cover' })
      .png()
      .toFile(join(out, 'social', name));
  }

  // --------------------------------------------------------------------------
  // Stage 6: PNG optimization (optional — needs pngquant + oxipng)
  // --------------------------------------------------------------------------
  console.log('[6/6] Optimizing PNGs...');
  try {
    execSync(
      `find "${out}" -name "*.png" -print0 | xargs -0 -I{} sh -c 'pngquant --quality=80-95 --force --output "{}" "{}" 2>/dev/null || true'`,
      { stdio: 'inherit' },
    );
    execSync(`find "${out}" -name "*.png" -print0 | xargs -0 oxipng -o 4 --strip safe 2>/dev/null || true`, {
      stdio: 'inherit',
    });
  } catch {
    console.log('  (PNG optimization skipped — install pngquant + oxipng for best results)');
  }

  console.log(`\n✓ Asset package built at: ${out}`);
}

// ============================================================================
// Helpers
// ============================================================================

async function optimizeSvg(path) {
  const raw = await readFile(path, 'utf8');
  const result = optimize(raw, {
    multipass: true,
    plugins: [
      {
        name: 'preset-default',
        params: {
          overrides: {
            removeViewBox: false,
            removeDimensions: true,
          },
        },
      },
    ],
  });
  return result.data;
}

function routeFaviconImage(name) {
  if (name.includes('android') || name.includes('launcher')) return 'android';
  if (name.includes('mstile') || name.includes('tile')) return 'windows';
  if (name.includes('apple') || name.includes('favicon') || name.includes('manifest')) {
    return 'web';
  }
  return 'web';
}

// ============================================================================
// Entrypoint
// ============================================================================

main().catch((err) => {
  console.error('Asset build failed:', err);
  process.exit(1);
});
