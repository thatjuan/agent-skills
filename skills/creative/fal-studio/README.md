# fal-studio

> Build a site or a generative app on fal.ai — art-directed marketing sites whose stills and scroll-scrub film are generated at build time, and apps whose users generate media at runtime behind a server-proxied queue.

## What it does

fal.ai is a generation API and nothing else: no hosting, no end-user accounts, no CLI that owns your project. `fal-studio` is the pipeline around it. It resolves one question up front — **who triggers a generation?** — and runs the matching flow end to end.

**`site`** — only you do, before ship. The skill writes the art direction, generates the still kit under a single style formula, lands every asset into the repo, builds the page against the spec, and (on the animated branch) produces a single-take film wired to scroll position. The shipped bundle contains no fal call and no API key.

**`app`** — the visitor does, on the user's fal bill. The skill pins the model contract, stands up the server route that holds `FAL_KEY`, builds the queue UX (queued / running / failed / rejected / cancel / retry), and handles result persistence off fal's temporary URLs.

Both flows ship a generated launch cover and filled OG metadata as a build step, and both end at a working local build — deploy stays the user's call.

## When to use it

- *"Build a landing page for my agency — we have no photography."*
- *"I need a product launch page with a cinematic scroll section."*
- *"Rebuild this marketing site; the blocker is that we have no assets."*
- *"Build an app where users upload a photo and get headshots back."*
- *"Add a generate-thumbnail feature to this dashboard."*

For a one-off generation with no product around it, use `fal-ai-media` instead. For visual concepts with no code, use [`creative-director`](../creative-director/).

## How a site build goes

**Prompt**

> Build a launch page for Northbound, a guided expedition company for first-time mountaineers. No photography, no video.

**What the skill does**

1. **Intake** — one batch: animated or static (mandatory), plus the brief gaps the repo cannot answer.
2. **Direction spec** — writes `DESIGN-SPEC.md`: section stack, grid, type, palette tokens, per-section asset list, motion notes, and the **style formula** every prompt will carry. One round of correction before spending anything.
3. **Kit** — submits the whole asset list in one batch, hero through two models, everything else through the winner. Lands the results into `public/generated/`, writes `manifest.json`, runs one coherence pass that kills anything with lettering or hands.
4. **Build** — the page against the spec, wired to real assets, with real copy.
5. **Film** — one continuous ~12s take anchored to the summit still, re-encoded all-keyframe with ffmpeg, scrubbed by a sticky scroll track, with a reduced-motion path and a mobile frame-sequence fallback.
6. **Cover + metadata** — generated cover at 1200×630, meta written to `src/site-meta.json`.
7. **Gate** — build green, no fal URLs in `src/`, no key in the repo, manifest complete, meta filled.

## Installation

```bash
npx skills add thatjuan/agent-skills --skill fal-studio
```

Set `FAL_KEY` in your environment ([fal.ai/dashboard/keys](https://fal.ai/dashboard/keys)) and configure the `fal-ai` MCP server; without MCP the skill falls back to the REST API. `ffmpeg` is needed only for animated sites.

## Bundled resources

| File | Purpose |
|------|---------|
| `SKILL.md` | Type routing, intake, prerequisites, and the rules both flows share |
| `references/site-flow.md` | Brief → direction spec → kit → build → motion → cover → gate |
| `references/app-flow.md` | Model contract → server route → queue UX → shell → cover → gate |
| `references/generation.md` | Build-time fal: access paths, model roles, the style formula, landing and the manifest |
| `references/fal-runtime.md` | `@fal-ai/client`, the server proxy and why to own the route, queue and webhooks, cost control |
| `references/scroll-scrub.md` | The single-take film, ffmpeg re-encode, scroll wiring, the two fallbacks |
| `references/cover-and-meta.md` | Launch cover, OG fields, the done bar |

## Tips

- **Approve the spec before the kit.** Regenerating twelve assets against a corrected direction is the expensive mistake; correcting a markdown file is free.
- **Stills are cheap, video is not.** Two video generations for a section is normal. Six means the anchor still or the prompt structure is wrong.
- **Anchor the film.** Passing the finished-state still as the image input is what stops the last frame drifting away from the page it lands on.
- **One style formula, one seed.** It is the cheapest coherence available, and it is what makes separate generations read as one shoot.
- **`FAL_KEY` server-side, always.** The stock fal proxy forwards whatever model the browser names — fine for a prototype, a billing hole in production.

## Related skills

- `fal-ai-media` — one-off image, video, and audio generation with no build around it
- [`creative-director`](../creative-director/) — visual concepts and strategy, no code
- [`logo-studio`](../logo-studio/) — the identity a site build can be art-directed against
