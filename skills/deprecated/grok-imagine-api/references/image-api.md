# Grok Imagine Image API Reference

This reference is based on the user-supplied xAI Grok Imagine API notes. If exact model names, prices, or limits are important, verify against official xAI docs before making final claims.

## Authentication and base URL

Use bearer auth with an xAI API key:

```http
Authorization: Bearer $XAI_API_KEY
Content-Type: application/json
```

Base URL:

```text
https://api.x.ai/v1
```

Primary endpoints:

```text
POST /images/generations
POST /images/edits
```

## Models

Use the currently documented Grok Imagine image model for new work. The supplied notes use `grok-imagine-image` throughout examples and state that `grok-imagine-image-pro` is deprecated; do not introduce new `-pro` usage. When migrating `-pro`, prefer `grok-imagine-image-quality` or the current official replacement.

## Image generation

Raw HTTP:

```bash
curl -X POST https://api.x.ai/v1/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-imagine-image",
    "prompt": "A futuristic city skyline at night"
  }'
```

Python xAI SDK:

```python
import xai_sdk

client = xai_sdk.Client()
response = client.image.sample(
    model="grok-imagine-image",
    prompt="A futuristic city skyline at night",
)
print(response.url)
```

Python OpenAI-compatible SDK:

```python
from openai import OpenAI

client = OpenAI(base_url="https://api.x.ai/v1", api_key="YOUR_API_KEY")
response = client.images.generate(
    model="grok-imagine-image",
    prompt="A futuristic city skyline at night",
)
print(response.data[0].url)
```

JavaScript OpenAI-compatible SDK:

```javascript
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.XAI_API_KEY,
  baseURL: "https://api.x.ai/v1",
});

const response = await client.images.generate({
  model: "grok-imagine-image",
  prompt: "A futuristic city skyline at night",
});

console.log(response.data[0].url);
```

Vercel AI SDK:

```javascript
import { xai } from "@ai-sdk/xai";
import { generateImage } from "ai";

const { image } = await generateImage({
  model: xai.image("grok-imagine-image"),
  prompt: "A futuristic city skyline at night",
});

console.log(image.base64);
```

## Image editing

The xAI edit endpoint expects JSON. Do not use OpenAI SDK `images.edit()` for this API because that method uses `multipart/form-data`.

Supported input image forms:

- Public image URL.
- Base64 data URI such as `data:image/png;base64,...` or `data:image/jpeg;base64,...`.

Raw HTTP edit with a public URL:

```bash
curl -X POST https://api.x.ai/v1/images/edits \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-imagine-image",
    "prompt": "Render this as a pencil sketch with detailed shading",
    "image": {
      "url": "https://example.com/photo.png",
      "type": "image_url"
    }
  }'
```

Python xAI SDK edit from a local file:

```python
import base64
import xai_sdk

client = xai_sdk.Client()

with open("photo.png", "rb") as f:
    image_data = base64.b64encode(f.read()).decode("utf-8")

response = client.image.sample(
    model="grok-imagine-image",
    prompt="Render this as a pencil sketch with detailed shading",
    image_url=f"data:image/png;base64,{image_data}",
)

print(response.url)
```

Vercel AI SDK edit:

```javascript
import { xai } from "@ai-sdk/xai";
import { generateImage } from "ai";
import fs from "fs";

const imageBuffer = fs.readFileSync("photo.png");
const base64Image = imageBuffer.toString("base64");

const { image } = await generateImage({
  model: xai.image("grok-imagine-image"),
  prompt: "Render this as a pencil sketch with detailed shading",
  providerOptions: {
    xai: {
      image: `data:image/png;base64,${base64Image}`,
    },
  },
});

console.log(image.base64);
```

Multi-image edits support up to 5 images. Preserve the order deliberately; the first image controls output aspect ratio unless `aspect_ratio` is explicitly set.

## Multi-turn editing

For iterative refinement, feed each generated output into the next edit request. Since generated URLs are temporary, either download each intermediate image or request base64 output and store the bytes locally before chaining the next step.

## Multiple images

Use one request for multiple variants of the same prompt:

```python
import xai_sdk

client = xai_sdk.Client()
responses = client.image.sample_batch(
    model="grok-imagine-image",
    prompt="A futuristic city skyline at night",
    n=4,
)

for i, image in enumerate(responses):
    print(f"Variation {i + 1}: {image.url}")
```

OpenAI-compatible SDKs use `n` on `images.generate()`:

```javascript
const response = await client.images.generate({
  model: "grok-imagine-image",
  prompt: "A futuristic city skyline at night",
  n: 4,
});
```

Maximum images per request: 10.

## Concurrent requests

Use concurrency for different prompts or independent edits:

```python
import asyncio
import xai_sdk

async def generate_concurrently():
    client = xai_sdk.AsyncClient()
    source_image = "https://example.com/photo.png"
    prompts = [
        "Render this image as an oil painting in the style of impressionism",
        "Render this image as a pencil sketch with detailed shading",
        "Render this image as pop art with bold colors and halftone dots",
        "Render this image as a watercolor painting with soft edges",
    ]

    tasks = [
        client.image.sample(
            model="grok-imagine-image",
            prompt=prompt,
            image_url=source_image,
        )
        for prompt in prompts
    ]

    results = await asyncio.gather(*tasks)
    for prompt, result in zip(prompts, results):
        print(f"{prompt}: {result.url}")

asyncio.run(generate_concurrently())
```

## Aspect ratio

`aspect_ratio` works for image generation and for multi-image editing. For single-image editing, output follows the input image aspect ratio.

Supported ratios from the supplied notes:

| Ratio | Use case |
|---|---|
| `1:1` | Social media, thumbnails |
| `16:9` / `9:16` | Widescreen, mobile, stories |
| `4:3` / `3:4` | Presentations, portraits |
| `3:2` / `2:3` | Photography |
| `2:1` / `1:2` | Banners, headers |
| `19.5:9` / `9:19.5` | Modern smartphone displays |
| `20:9` / `9:20` | Ultra-wide displays |
| `auto` | Model chooses for the prompt |

Parameter names:

```python
client.image.sample(
    model="grok-imagine-image",
    prompt="Mountain landscape at sunrise",
    aspect_ratio="16:9",
)
```

```python
client.images.generate(
    model="grok-imagine-image",
    prompt="Mountain landscape at sunrise",
    extra_body={"aspect_ratio": "16:9"},
)
```

```javascript
await client.images.generate({
  model: "grok-imagine-image",
  prompt: "Mountain landscape at sunrise",
  aspect_ratio: "16:9",
});
```

```javascript
await generateImage({
  model: xai.image("grok-imagine-image"),
  prompt: "Mountain landscape at sunrise",
  aspectRatio: "16:9",
});
```

## Resolution

Supported values from the supplied notes:

- `1k`
- `2k`

Parameter names:

```python
client.image.sample(
    model="grok-imagine-image",
    prompt="An astronaut performing EVA in LEO.",
    resolution="2k",
)
```

```python
client.images.generate(
    model="grok-imagine-image",
    prompt="An astronaut performing EVA in LEO.",
    extra_body={"resolution": "2k"},
)
```

```javascript
await client.images.generate({
  model: "grok-imagine-image",
  prompt: "An astronaut performing EVA in LEO.",
  resolution: "2k",
});
```

## Base64 output

xAI SDK:

```python
response = client.image.sample(
    model="grok-imagine-image",
    prompt="A serene Japanese garden",
    image_format="base64",
)

with open("garden.jpg", "wb") as f:
    f.write(response.image)
```

OpenAI-compatible SDKs:

```python
import base64

response = client.images.generate(
    model="grok-imagine-image",
    prompt="A serene Japanese garden",
    response_format="b64_json",
)

image_bytes = base64.b64decode(response.data[0].b64_json)
with open("garden.jpg", "wb") as f:
    f.write(image_bytes)
```

```javascript
import fs from "fs";

const response = await client.images.generate({
  model: "grok-imagine-image",
  prompt: "A serene Japanese garden",
  response_format: "b64_json",
});

const imageBuffer = Buffer.from(response.data[0].b64_json, "base64");
fs.writeFileSync("garden.jpg", imageBuffer);
```

Vercel AI SDK returns base64 by default:

```javascript
const { image } = await generateImage({
  model: xai.image("grok-imagine-image"),
  prompt: "A serene Japanese garden",
});

fs.writeFileSync("garden.jpg", Buffer.from(image.base64, "base64"));
```

## Response handling

xAI SDK response fields in the supplied notes:

```python
if response.respect_moderation:
    print(response.url)
else:
    print("Image filtered by moderation")

print(f"Model: {response.model}")
```

For URL output, persist the file promptly because URLs expire. For base64 output, decode and store the bytes directly.

## Pricing and limits

Pricing is flat per generated image rather than token-based. For image editing, the supplied notes state that both the input image and generated output image are charged. Verify official pricing before giving cost estimates.

Limits from the supplied notes:

- Maximum images per request: 10.
- Generated URLs are temporary.
- Images are subject to content moderation.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `images.edit()` fails through OpenAI SDK | It sends `multipart/form-data` | Use xAI SDK, Vercel AI SDK, or raw JSON `/images/edits`. |
| Generated URL no longer works | URL expired | Download promptly or request base64 output. |
| Aspect ratio ignored on single-image edit | Single-image edits follow input aspect ratio | Resize/crop input first or use multi-image/edit generation flow where supported. |
| TypeScript rejects `aspect_ratio` or `resolution` | xAI-specific params are not in OpenAI SDK types | Use `// @ts-expect-error` narrowly, or an SDK path with provider-specific options. |
| Multiple outputs needed from one prompt | Issuing serial calls is slower and less efficient | Use `n` / `sample_batch()`. |
| Multiple different prompts needed | Batch variations do not apply | Use async/concurrent requests. |
