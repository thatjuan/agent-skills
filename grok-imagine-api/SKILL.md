---
name: grok-imagine-api
description: xAI Grok Imagine API expertise for generating, editing, and refining images through xAI REST, xai_sdk, OpenAI-compatible SDKs, and Vercel AI SDK. Use when code calls `api.x.ai/v1/images/generations` or `api.x.ai/v1/images/edits`, imports `xai_sdk` or `@ai-sdk/xai`, points an OpenAI SDK at `https://api.x.ai/v1`, or mentions Grok Imagine, `grok-imagine-image`, `grok-imagine-image-quality`, `aspect_ratio`, image editing, image variations, base64 image output, or `sample_batch()`.
---

# Grok Imagine API

Grok Imagine is xAI's image generation and editing API. It supports text-to-image, JSON-based image edits, multi-image edits, multi-turn refinement, batch variations, aspect-ratio control, 1k/2k resolution, URL output, and base64 output.

Use official xAI docs for exact current model availability and pricing when that matters. Do not recommend the deprecated `grok-imagine-image-pro`; migrate existing uses to `grok-imagine-image-quality` or the current documented Grok Imagine image model.

## Quick start

Raw REST:

```bash
curl -X POST https://api.x.ai/v1/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-imagine-image",
    "prompt": "A collage of London landmarks in a stenciled street-art style"
  }'
```

Python xAI SDK:

```python
import xai_sdk

client = xai_sdk.Client()
response = client.image.sample(
    model="grok-imagine-image",
    prompt="A collage of London landmarks in a stenciled street-art style",
)
print(response.url)
```

OpenAI-compatible generation:

```python
from openai import OpenAI

client = OpenAI(base_url="https://api.x.ai/v1", api_key="YOUR_API_KEY")
response = client.images.generate(
    model="grok-imagine-image",
    prompt="A collage of London landmarks in a stenciled street-art style",
)
print(response.data[0].url)
```

## Integration choices

| Path | Best for | Notes |
|---|---|---|
| `xai_sdk` | Python, first-party features | Use `client.image.sample()` and `sample_batch()`. |
| REST | Any language, full control | Send JSON to `/images/generations` or `/images/edits`. |
| OpenAI SDK | Drop-in image generation | Point `base_url` / `baseURL` at `https://api.x.ai/v1`. |
| Vercel AI SDK | TypeScript apps already using AI SDK | Use `xai.image("grok-imagine-image")` with `generateImage()`. |

The OpenAI SDK's `images.edit()` is not supported for Grok Imagine edits because it sends `multipart/form-data`; xAI image edits require `application/json`.

## Core workflow

1. Choose generation vs editing:
   - New image: `POST /v1/images/generations`, `client.image.sample()`, or `images.generate()`.
   - Edit image: `POST /v1/images/edits`, xAI SDK `sample(image_url=...)`, or Vercel AI SDK provider options.
2. Set `model`, `prompt`, and optional `n`, `aspect_ratio`, `resolution`, or output format.
3. For image edits, pass a public image URL or a base64 data URI. Up to 5 input images are supported.
4. Treat generated URLs as temporary. Download them promptly or request base64 output when embedding/saving directly.
5. Check moderation metadata when using `xai_sdk`; do not assume every request produces a usable image.

## Common patterns

- Same prompt, multiple variants: use `sample_batch(..., n=...)` or `images.generate(..., n=...)`.
- Different prompts in parallel: use `xai_sdk.AsyncClient()` with `asyncio.gather()`.
- Single-image edit: output aspect ratio follows the input image.
- Multi-image edit: output aspect ratio follows the first input unless `aspect_ratio` is set.
- Base64 output: xAI SDK uses `image_format="base64"`; OpenAI-compatible SDKs use `response_format="b64_json"`.
- Resolution values: `1k` or `2k`.
- Maximum images per request: 10.

## Reference

See [references/image-api.md](references/image-api.md) for endpoint shapes, parameter names by SDK, editing payloads, aspect ratios, response handling, and troubleshooting.
