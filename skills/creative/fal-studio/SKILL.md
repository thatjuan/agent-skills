---
name: fal-studio
description: "Build a site or a generative app on fal.ai: art-directed marketing sites whose stills and scroll-scrub film are generated at build time, and apps whose users generate media at runtime behind a server-proxied queue. Use for landing pages, portfolios, launch pages, brand sites with no photography, and any product with an AI image, video, or audio feature."
---

# fal.ai product builder — two types, two flows

fal.ai is a generation API and nothing else: no hosting, no end-user accounts, no CLI that owns your project. You generate media with fal and write the code on the local filesystem with git and the repo's package manager. Every build lands as a **working local build in the user's repo** — the user owns deploy.

## The two types

Resolve the type first. The test is one question: **who triggers a generation?**

- **`site`** — only you do, before ship. Stills, film, and cover are generated now, **landed** into `public/generated/`, and committed. The shipped bundle carries no fal call and no `FAL_KEY`; the site renders fine with fal offline. Every site gets an independent brand — palette, type, and chrome from its own design brief. Flow: [`references/site-flow.md`](references/site-flow.md).
- **`app`** — the visitor does, on the user's fal bill. Someone types a prompt or drops an image and gets media back, through the fal **queue** behind a server route that holds `FAL_KEY`. Flow: [`references/app-flow.md`](references/app-flow.md).

Quick tells: "landing page / portfolio / marketing site / rebuild with no photography" → site. "users generate headshots / thumbnails / voiceovers / clips", "a generate button" → app. A site that wants a generate button is an app; build it as one rather than putting a key in the browser.

An app also generates its own brand assets at build time (shell art, cover), so it reads [`references/generation.md`](references/generation.md) too. A site never reads the runtime reference.

## Intake — one batch, before any generation

Ask everything you still need in a single message, then build:

1. **Type**, when the request leaves it open.
2. **Site only, and mandatory: animated or static?** Animated is a scroll-driven journey through a generated film ([`references/scroll-scrub.md`](references/scroll-scrub.md)) and is the recommended default; static spends the whole budget on stills. Ask even when the request seems to imply an answer.
3. **App only:** which media users generate (image / video / audio), whether results must outlive fal's temporary CDN URLs, and whether generation sits behind login or a quota.

Video costs real money and a retry is not cheap. State the model and duration and get a yes before the first video run; stills need no permission.

## Prerequisites

- `FAL_KEY` in the environment. Keys come from [fal.ai/dashboard/keys](https://fal.ai/dashboard/keys).
- The `fal-ai` MCP server, which is how you generate at build time (`search`, `find`, `generate`, `status`, `result`, `upload`, `estimate_cost`). With no MCP server present, call the REST API directly — see [`references/generation.md`](references/generation.md).
- `command -v ffmpeg` on the animated branch. It re-encodes the film for scrubbing; a missing ffmpeg is worth saying at intake rather than at the end.

## Flows

| Type | Flow |
|------|------|
| `site` | [`references/site-flow.md`](references/site-flow.md) — intake → direction spec → kit → build-to-spec → motion → cover + metadata → gate |
| `app` | [`references/app-flow.md`](references/app-flow.md) — model contract → server route → queue client → result handling → shell + cover → gate |

Each flow is complete on its own and names the references it needs. `frontend-design` owns aesthetics for both; this skill owns the pipeline.

## Hard rules, both flows

**Land every output.** fal returns temporary CDN URLs. Download each accepted asset into the repo, reference it locally, and record file + model + prompt + seed + request id in `public/generated/manifest.json`. A src pointing at a fal URL is a broken build with a delay fuse.

**`FAL_KEY` is server-side.** It belongs in a server env var read by a server route — never in client code, never behind a `VITE_`/`NEXT_PUBLIC_` prefix, never committed.

**Cover + metadata are build steps.** Every build — a one-page toy included — ships the generated cover image and filled `og_title` / `og_description` / favicon per [`references/cover-and-meta.md`](references/cover-and-meta.md), written before the work is presented as done. An empty `og_title` or a blank card means the build is incomplete.

**Spend on stills, ration video.** Stills are cheap enough to iterate on and that is where taste gets made. Run `estimate_cost` before any video, and let an approved spec plus an existing anchor still justify the run. Two video generations for one section is normal; six means the prompt or the anchor is wrong, not the model.

## Turn economy

Agent runtimes cap turns, and a build that dies mid-flight leaves the user an unfinished product. Turns are the scarcest resource after credits:

- Compose each file in full, then write it once. No write-then-patch loops, and no re-reading a file you just wrote.
- Submit everything that can render concurrently in one batch (the whole still kit plus the cover), and write the page while it renders.
- Wait on a job once, at the point its output is the next input.
- Ask for variants with `num_images` in a single call rather than repeat calls.
- Inspect the landed kit in one batched pass, not generation by generation.

## Talking to the user

Most users are not technical. Speak in product terms: "Setting up your site…", "Saving your changes…", "Your site is running at localhost:5173". Keep repos, branches, commits, and package managers out of chat unless the user is clearly technical and asks about them — you still do all of it, you just do not narrate it. Reply in the user's language; code and CLI flags stay English. Report a live path and a one-line summary, never raw request ids or JSON dumps.

## Reference index

Both flows: [`generation.md`](references/generation.md) (build-time fal: models, prompt craft, the style formula, landing and the manifest), [`cover-and-meta.md`](references/cover-and-meta.md).

Site flow only: [`scroll-scrub.md`](references/scroll-scrub.md) (the animated branch — film, ffmpeg, scroll wiring, fallbacks).

App flow only: [`fal-runtime.md`](references/fal-runtime.md) (`@fal-ai/client`, the server proxy, queue and webhooks, uploads, result persistence, cost control).

For a one-off generation with no product around it, `fal-ai-media` is the lighter skill.
