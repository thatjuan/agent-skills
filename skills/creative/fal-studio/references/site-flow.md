# Site flow

A site whose art direction and imagery you generate, whose code you write, and whose bundle contains no fal call. Phases run in order; each feeds the next, and the film phase is worthless without the still it is anchored to.

**Animated or static** was settled at intake. Animated adds phase 5; everything else is shared.

## 1. Brief

Invoked inside an existing repo, fill the brief from the repo before asking anything: positioning docs, an existing design system, the route map, the package manager, whether Tailwind is already there. Ask only what the repo cannot tell you, in one batch, and state what you inferred so the user can correct it.

What the brief has to end with: what the site sells, to whom, the one thing a visitor should feel, the section stack, and whether any real photography exists (generate around it rather than replacing it).

## 2. Direction spec

Load the `frontend-design` skill — it owns aesthetics, this flow owns the pipeline. Write `DESIGN-SPEC.md` in the working directory, or extend the repo's existing design doc rather than starting a competing one:

- Section stack top to bottom, one line each, with the job each section does
- Grid, page max width, vertical rhythm
- Type: two families at most, the scale, and the one display treatment the hero gets
- Palette as tokens, including the single accent that carries the CTA
- Per-section asset list: slot, shot description, aspect ratio, generated or existing
- The **style formula** (`generation.md`) — the string every prompt in the kit will carry
- Motion notes: what animates, what stays still
- Animated builds: the film's one-line story and which still is its anchor

Show the spec and take one round of correction. Generating a kit against an unapproved direction is the expensive mistake in this workflow.

## 3. Kit

Read [`generation.md`](generation.md). Submit the whole asset list in one batch, hero through two models, everything else through the winner. On an animated build, generate the **anchor** still here even though it is not used until phase 5 — the film's end frame is constrained by it.

Land every accepted asset into `public/generated/`, write the manifest, then run the single coherence pass. Kill anything with lettering or hands before it reaches the page.

## 4. Build

Build against the spec in whatever the repo already uses. A fresh project with no stack defaults to React, Vite, TypeScript, Tailwind, pnpm.

Wire the landed assets as you go. Building with placeholder boxes and swapping images in later gets the layout wrong, because the layout decisions depend on the actual images — how much contrast the hero has under the headline, whether the card art can carry a caption.

Copy is part of the build: real headlines, real proof, real CTA text. Lorem ipsum on a finished page is an unfinished page.

## 5. Motion

**Animated:** read [`scroll-scrub.md`](scroll-scrub.md) and follow it end to end — film, ffmpeg re-encode, scroll wiring, reduced-motion path, mobile fallback.

**Static:** motion is CSS and the scroll timeline only — entrance transitions, a parallax band, a sticky section that changes state. Keep it to what the spec's motion notes named, respect `prefers-reduced-motion`, and let nothing block first paint.

## 6. Cover and metadata

[`cover-and-meta.md`](cover-and-meta.md). Not optional, not deferred, no exception for a small site.

## 7. Gate

Walk the spec section by section against the running page, then check the mechanical list. Every line is a build failure until it passes:

- The build command succeeds and the dev server renders every section.
- No fal CDN URL survives anywhere in `src/` — every asset is a local path.
- `FAL_KEY` appears nowhere in the repo or the bundle.
- `public/generated/manifest.json` covers every shipped asset.
- Meta fields are filled and the cover image exists.
- `prefers-reduced-motion` has a path, and the page holds up at 390px wide.
- No placeholder copy.

Close with the run command, the local URL, and one line on what was built.
