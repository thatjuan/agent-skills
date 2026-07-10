# grok-imagine-api

> xAI Grok Imagine API expertise for generating, editing, and refining images via xAI REST, `xai_sdk`, OpenAI-compatible SDKs, and the Vercel AI SDK. Covers text-to-image, JSON-based image edits, multi-image edits, multi-turn refinement, batch variations, aspect-ratio control, 1k/2k resolution, and base64 vs URL output.

## What it does

`grok-imagine-api` is the reference for shipping image generation and editing on top of xAI's Grok Imagine. It picks the right integration path for the codebase, gets the request shape correct (especially for edits, where the OpenAI SDK's `images.edit()` cannot be used because xAI requires `application/json`, not `multipart/form-data`), and steers users away from deprecated models (`grok-imagine-image-pro` → `grok-imagine-image-quality` or the current Grok Imagine image model).

It knows the four supported integration paths and when each one is the right call:

- **`xai_sdk` (Python)** — first-party, exposes `client.image.sample()` and `sample_batch()`, surfaces moderation metadata
- **Raw REST** — `POST /v1/images/generations` and `/v1/images/edits` for any language, full control
- **OpenAI SDK** — drop-in `images.generate()` with `base_url`/`baseURL` pointed at `https://api.x.ai/v1` (generation only — edits unsupported)
- **Vercel AI SDK** — `xai.image("grok-imagine-image")` with `generateImage()` for TypeScript apps already on the AI SDK

## When to use it

Trigger this skill when:

- Code imports `xai_sdk` or `@ai-sdk/xai`
- Code POSTs to `api.x.ai/v1/images/generations` or `api.x.ai/v1/images/edits`
- An OpenAI SDK is pointed at `https://api.x.ai/v1` for image work
- The user mentions Grok Imagine, `grok-imagine-image`, `grok-imagine-image-quality`, `aspect_ratio`, image editing, image variations, base64 image output, or `sample_batch()`

**Not the right skill if** the user wants OpenAI DALL·E, Google Imagen, Stability, Black Forest Labs / Flux, or Midjourney. This skill is xAI-specific.

## Example prompts

- *"Generate four square variants of this product hero image using `sample_batch`."*
- *"Edit this image to swap the background to a softly-lit studio cyclorama, base64 out."*
- *"Wire `generateImage` from the Vercel AI SDK into our Next.js app for Grok Imagine."*
- *"My OpenAI SDK call to `images.edit` against `api.x.ai/v1` is failing — why?"*
- *"Migrate our `grok-imagine-image-pro` calls off the deprecated model."*
- *"Write a Python async fan-out that hits `/v1/images/generations` with five different prompts."*

## Installation

```bash
npx skills add thatjuan/agent-skills --skill grok-imagine-api
```

## Bundled resources

| File | Purpose |
|------|---------|
| `SKILL.md` | Quick-start snippets across all four integration paths, integration-choice table, and core workflow |
| `references/image-api.md` | Endpoint shapes, parameter names per SDK, editing payloads, aspect ratios, response handling, and troubleshooting |

## Tips

- **Edits require JSON.** Do not reach for OpenAI SDK `images.edit()` against xAI — it sends `multipart/form-data`. Use raw REST, `xai_sdk`, or the Vercel AI SDK instead.
- **Treat URLs as temporary.** Generated image URLs expire. Download them promptly or request base64 (`image_format="base64"` in `xai_sdk`, `response_format="b64_json"` in OpenAI-compatible clients).
- **Multi-image edits up to 5 inputs.** Output aspect ratio follows the first input unless `aspect_ratio` is set explicitly.
- **Resolution is `1k` or `2k`.** Do not pass arbitrary pixel dimensions.
- **Maximum 10 images per request.**
- **Check moderation metadata** on `xai_sdk` responses — not every request produces a usable image.

## Related skills

- [`openrouter-api`](../openrouter-api/) — for routing across many image and LLM providers via one endpoint
- [`browserbase-sdk`](../browserbase-sdk/) — when generated images need to be uploaded into a headless-browser flow
