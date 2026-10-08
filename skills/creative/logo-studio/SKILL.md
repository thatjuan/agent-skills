---
name: logo-studio
description: "Design an iconic, memorable logo with full creative freedom, then turn the final mark into an app asset package (iOS, Android, macOS, Windows, favicons, PWA, social) and, on request, a brand guidelines document. Use when the user asks for a logo, brand mark, wordmark, app icon, visual identity, or brand guidelines."
---

# Logo Studio

## The brief

You have full artistic and creative freedom to design the best, most memorable logo for this brand. Nothing in this skill limits the design: use your own imagination and every tool you have, and arrive at the most remarkable concept you can. Go all out. Show how polished, memorable, and iconic a logo you can create. You are a master designer, and this is your best piece.

The rest of this skill covers what happens around the design, not how to design it.

## 1. Learn the brand

Read what already exists: the user's words, the repo, its README, the product's site. Ask the user only for what you cannot find. Done when you can say in one sentence what the brand is and who it is for.

## 2. Design

The brief above is the whole method. Any tool is fair game: hand-built SVG, scripts that compute geometry, image generation for exploration (`fal-studio`, the fal MCP, or `treg`), anything else on the machine.

Look at your own work. Rasterize each candidate (`rsvg-convert`, `resvg`, or sharp) and view the PNG, on light and dark grounds and at real sizes from favicon to billboard. Keep going until the mark is one you would sign.

The final mark ships as clean, hand-finished vector SVG. Generated raster images can inspire the mark, never stand in for it. Fonts must be licensed for commercial logo use (SIL OFL fonts such as those on Google Fonts qualify).

## 3. Present

Build a presentation page for the work, designed as carefully as the logo, and open it (`open`, `xdg-open`, or `start`). Explain the idea behind the mark briefly. Iterate on the user's feedback until they pick a final.

## 4. Final files

| File | Contents |
|------|----------|
| `logo-{name}.svg` | Full-color working file |
| `logo-{name}-mono.svg` | Single dark color |
| `logo-{name}-reversed.svg` | White on dark |
| `logo-{name}-icon.svg` | Symbol alone, when the logo has one |
| `logo-{name}-outlined.svg` | Text converted to paths, for delivery |

## 5. App assets

Once the final is chosen, offer the app asset package. It is built from an **icon master**: a 1024×1024 square SVG on a deliberate brand-color background, text outlined to paths, content inside the central ~61% safe zone, no corner radius. The icon is a sibling of the logo, designed for its square canvas rather than shrunk into it.

Read [app-assets.md](references/app-assets.md) for platform specs, the tool stack, and gotchas. Configure and run [build-assets.mjs](assets/build-assets.mjs) to write `dist/assets/`.

## 6. Brand guidelines

After the final is chosen, offer a brand guidelines document in Essentials, Standard, or Full depth. It is offered, never produced unasked. Read [brand-guidelines.md](references/brand-guidelines.md) for the depth modes, section spec, extension interview, and rendering, and fill [brand-guidelines-template.html](assets/brand-guidelines-template.html).
