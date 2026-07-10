// Regenerate social images at correct dimensions.
// Previous pipeline produced oversized canvases due to chained resize + extend.
import sharp from 'sharp';
import { join } from 'node:path';

const iconPath = 'icon-master.svg';
const outDir = 'dist/assets/social';
const brandBg = '#2B241C';

const sizes = [
  { name: 'og-image-1200x630.png', w: 1200, h: 630 },
  { name: 'twitter-card-1200x628.png', w: 1200, h: 628 },
  { name: 'linkedin-1200x627.png', w: 1200, h: 627 },
  { name: 'profile-400x400.png', w: 400, h: 400 },
  { name: 'profile-square-512.png', w: 512, h: 512 },
];

for (const { name, w, h } of sizes) {
  // For square formats, render the icon to fit with a small inset.
  // For wide formats (og/twitter/linkedin), centre the icon within the canvas.
  const short = Math.min(w, h);
  const iconSize = Math.round(short * 0.65); // 65% of the shorter edge
  const iconBuf = await sharp(iconPath, { density: 512 })
    .resize(iconSize, iconSize, {
      fit: 'contain',
      background: { r: 0, g: 0, b: 0, alpha: 0 },
    })
    .png()
    .toBuffer();
  await sharp({
    create: {
      width: w,
      height: h,
      channels: 4,
      background: { r: 0x2B, g: 0x24, b: 0x1C, alpha: 1 },
    },
  })
    .composite([
      {
        input: iconBuf,
        top: Math.round((h - iconSize) / 2),
        left: Math.round((w - iconSize) / 2),
      },
    ])
    .png()
    .toFile(join(outDir, name));
  console.log('wrote', name, `${w}x${h}`);
}
console.log('\n✓ Social images regenerated at correct dimensions.');
