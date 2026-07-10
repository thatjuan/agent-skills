// Generate outlined (text-to-path) versions of the Mycelia wordmark.
// Uses opentype.js with Fraunces Regular (144pt optical).
import opentype from 'opentype.js';
import { readFile, writeFile } from 'node:fs/promises';

const font = opentype.parse((await readFile('./fraunces.ttf')).buffer);

function wordmarkPath(x, y, fontSize, letterSpacing = 2) {
  // Render "mycelia" as a series of glyph paths with letter-spacing.
  const text = 'mycelia';
  const glyphs = font.stringToGlyphs(text);
  const scale = fontSize / font.unitsPerEm;
  let cursor = x;
  const pathData = [];
  for (const glyph of glyphs) {
    const p = glyph.getPath(cursor, y, fontSize);
    pathData.push(p.toPathData(1));
    cursor += glyph.advanceWidth * scale + letterSpacing;
  }
  return pathData.join(' ');
}

// Compute total advance width for centering
function advanceWidth(text, fontSize, letterSpacing = 2) {
  const glyphs = font.stringToGlyphs(text);
  const scale = fontSize / font.unitsPerEm;
  let w = 0;
  for (const glyph of glyphs) w += glyph.advanceWidth * scale + letterSpacing;
  return w - letterSpacing;
}

// ---- Outlined A2 wordmark (viewBox 400×120) ----
{
  const fontSize = 58;
  const letterSpacing = 3;
  const w = advanceWidth('mycelia', fontSize, letterSpacing);
  const xStart = (400 - w) / 2;
  const y = 70;
  const d = wordmarkPath(xStart, y, fontSize, letterSpacing);
  const svg = `<svg viewBox="0 0 400 120" xmlns="http://www.w3.org/2000/svg">
  <title>Mycelia — outlined wordmark</title>
  <path d="${d}" fill="#2B241C"/>
  <line x1="60" y1="90" x2="340" y2="90" stroke="#2B241C" stroke-width="0.7"/>
</svg>
`;
  await writeFile('./logo-mycelia-wordmark-outlined.svg', svg);
  console.log('wrote logo-mycelia-wordmark-outlined.svg');
}

// ---- Outlined A1 combination (viewBox 460×140) ----
{
  const fontSize = 46;
  const letterSpacing = 2;
  const xStart = 150;
  const y = 83;
  const textPath = wordmarkPath(xStart, y, fontSize, letterSpacing);

  const mark = `
  <g transform="translate(72 70)" fill="none" stroke="#2B241C" stroke-width="1.1" stroke-linecap="round">
    <circle r="44"/>
    <g stroke-width="0.8">
      <line x1="0" y1="0" x2="44" y2="0"/>
      <line x1="0" y1="0" x2="38.1" y2="22"/>
      <line x1="0" y1="0" x2="22" y2="38.1"/>
      <line x1="0" y1="0" x2="0" y2="44"/>
      <line x1="0" y1="0" x2="-22" y2="38.1"/>
      <line x1="0" y1="0" x2="-38.1" y2="22"/>
      <line x1="0" y1="0" x2="-44" y2="0"/>
      <line x1="0" y1="0" x2="-38.1" y2="-22"/>
      <line x1="0" y1="0" x2="-22" y2="-38.1"/>
      <line x1="0" y1="0" x2="0" y2="-44"/>
      <line x1="0" y1="0" x2="22" y2="-38.1"/>
      <line x1="0" y1="0" x2="38.1" y2="-22"/>
    </g>
    <circle r="2.8" fill="#2B241C" stroke="none"/>
    <g fill="#2B241C" stroke="none">
      <circle cx="44" cy="0" r="1.8"/><circle cx="38.1" cy="22" r="1.4"/>
      <circle cx="22" cy="38.1" r="1.6"/><circle cx="0" cy="44" r="1.4"/>
      <circle cx="-22" cy="38.1" r="1.6"/><circle cx="-38.1" cy="22" r="1.3"/>
      <circle cx="-44" cy="0" r="1.8"/><circle cx="-38.1" cy="-22" r="1.3"/>
      <circle cx="-22" cy="-38.1" r="1.6"/><circle cx="0" cy="-44" r="1.4"/>
      <circle cx="22" cy="-38.1" r="1.6"/><circle cx="38.1" cy="-22" r="1.4"/>
    </g>
  </g>`;

  const svg = `<svg viewBox="0 0 460 140" xmlns="http://www.w3.org/2000/svg">
  <title>Mycelia — outlined combination mark</title>${mark}
  <path d="${textPath}" fill="#2B241C"/>
  <line x1="150" y1="100" x2="420" y2="100" stroke="#2B241C" stroke-width="0.7"/>
</svg>
`;
  await writeFile('./logo-mycelia-outlined.svg', svg);
  console.log('wrote logo-mycelia-outlined.svg');
}
