// Post-build: supplement favicons package output with assets it doesn't generate
// by default — favicon.svg, safari-pinned-tab.svg, and maskable icons.
import sharp from 'sharp';
import { readFile, writeFile, copyFile } from 'node:fs/promises';
import { join } from 'node:path';

const outRoot = 'dist/assets';
const webDir = join(outRoot, 'web');
const iconMasterPath = 'icon-master.svg';

// 1. favicon.svg — same as icon-master (small square with brand background)
await copyFile(iconMasterPath, join(webDir, 'favicon.svg'));
console.log('wrote web/favicon.svg');

// 2. safari-pinned-tab.svg — single-colour monochrome silhouette, viewBox 0 0 16 16
// Approximates the mycelial network as a minimal monochrome silhouette.
const safariPinned = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">
  <g transform="translate(8 8)" fill="black">
    <path d="M 0 -6.5 A 6.5 6.5 0 1 1 0 6.5 A 6.5 6.5 0 1 1 0 -6.5 Z M 0 -5.5 A 5.5 5.5 0 1 0 0 5.5 A 5.5 5.5 0 1 0 0 -5.5 Z"/>
    <circle r="0.7"/>
    <rect x="-0.1" y="-6" width="0.2" height="12"/>
    <rect x="-6" y="-0.1" width="12" height="0.2"/>
    <rect x="-0.1" y="-6" width="0.2" height="12" transform="rotate(30)"/>
    <rect x="-0.1" y="-6" width="0.2" height="12" transform="rotate(60)"/>
    <rect x="-0.1" y="-6" width="0.2" height="12" transform="rotate(120)"/>
    <rect x="-0.1" y="-6" width="0.2" height="12" transform="rotate(150)"/>
    <circle cx="6" cy="0" r="0.45"/><circle cx="-6" cy="0" r="0.45"/>
    <circle cx="0" cy="6" r="0.4"/><circle cx="0" cy="-6" r="0.4"/>
    <circle cx="5.2" cy="3" r="0.35"/><circle cx="-5.2" cy="3" r="0.35"/>
    <circle cx="5.2" cy="-3" r="0.35"/><circle cx="-5.2" cy="-3" r="0.35"/>
    <circle cx="3" cy="5.2" r="0.4"/><circle cx="-3" cy="5.2" r="0.4"/>
    <circle cx="3" cy="-5.2" r="0.4"/><circle cx="-3" cy="-5.2" r="0.4"/>
  </g>
</svg>
`;
await writeFile(join(webDir, 'safari-pinned-tab.svg'), safariPinned);
console.log('wrote web/safari-pinned-tab.svg');

// 3. Maskable icons — 192 and 512 with 15% safe-zone padding (content inside central 80%)
//    We render the 1024 icon-master onto a padded canvas of the brand colour.
const brandBg = { r: 0x2B, g: 0x24, b: 0x1C };

async function makeMaskable(size, outPath) {
  const contentSize = Math.round(size * 0.7); // conservative 70% safe
  const margin = Math.round((size - contentSize) / 2);
  const contentBuffer = await sharp(iconMasterPath, { density: 512 })
    .resize(contentSize, contentSize, {
      fit: 'contain',
      background: { r: 0, g: 0, b: 0, alpha: 0 },
    })
    .png()
    .toBuffer();
  await sharp({
    create: { width: size, height: size, channels: 4, background: brandBg },
  })
    .composite([{ input: contentBuffer, top: margin, left: margin }])
    .png()
    .toFile(outPath);
  console.log('wrote', outPath);
}

await makeMaskable(192, join(webDir, 'maskable-192.png'));
await makeMaskable(512, join(webDir, 'maskable-512.png'));

// 4. Patch manifest.webmanifest — add maskable icons and extend descriptor with
//    the standard 192/512 "any" sizes pointing at the android-chrome PNGs.
const manifestPath = join(webDir, 'manifest.webmanifest');
const manifest = JSON.parse(await readFile(manifestPath, 'utf8'));
manifest.icons.push(
  {
    src: '/assets/maskable-192.png',
    sizes: '192x192',
    type: 'image/png',
    purpose: 'maskable',
  },
  {
    src: '/assets/maskable-512.png',
    sizes: '512x512',
    type: 'image/png',
    purpose: 'maskable',
  },
);
await writeFile(manifestPath, JSON.stringify(manifest, null, 2));
console.log('patched manifest.webmanifest with maskable icons');

// 5. Also copy manifest to the canonical site.webmanifest filename used in
//    html head references.
await copyFile(manifestPath, join(webDir, 'site.webmanifest'));
console.log('wrote web/site.webmanifest');

// 6. Also place the favicon.ico at the top of dist/assets/ for convenience
await copyFile(join(webDir, 'favicon.ico'), join(outRoot, 'favicon.ico')).catch(() => {});
console.log('\n✓ Post-build supplements complete.');
