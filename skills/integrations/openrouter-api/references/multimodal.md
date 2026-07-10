# Multimodal — images, PDFs, audio, video, image-gen, TTS

Filter models by modality: `?input_modalities=image|file|audio|video` and `?output_modalities=text|image|audio|speech|embeddings|all` on the Models API and `https://openrouter.ai/models` page.

## Contents

- [Image inputs](#image-inputs)
- [PDF / file inputs](#pdf--file-inputs)
- [Audio inputs](#audio-inputs)
- [Video inputs](#video-inputs)
- [Image generation outputs](#image-generation-outputs)
- [Text-to-speech (TTS)](#text-to-speech-tts)

## Image inputs

`image_url` content part. URL or data URL. Send text first, then images (parsing-order recommendation). If images must come first, put them in the system prompt.

Supported MIME types: `image/png`, `image/jpeg`, `image/webp`, `image/gif`.

### URL

```python
messages = [{
  "role": "user",
  "content": [
    {"type": "text", "text": "What's in this image?"},
    {"type": "image_url", "image_url": {"url": "https://example.com/cat.jpg"}}
  ]
}]
```

### Base64

```python
import base64
with open("path/to/image.jpg", "rb") as f:
    data = base64.b64encode(f.read()).decode("utf-8")
data_url = f"data:image/jpeg;base64,{data}"

messages = [{
  "role": "user",
  "content": [
    {"type": "text", "text": "What's in this image?"},
    {"type": "image_url", "image_url": {"url": data_url}}
  ]
}]
```

`image_url.detail` controls fidelity (provider-specific; `auto` default).

## PDF / file inputs

`file` content part. Works on **any** OpenRouter model — when the model lacks native file support, OpenRouter parses the PDF and feeds extracted text. URL or base64 data URL.

```typescript
content: [
  { type: 'text', text: 'What are the main points in this document?' },
  {
    type: 'file',
    file: {
      filename: 'document.pdf',
      fileData: 'https://bitcoin.org/bitcoin.pdf',  // or 'data:application/pdf;base64,...'
    },
  },
]
```

### PDF parser engines via `file-parser` plugin

```json
{
  "plugins": [{
    "id": "file-parser",
    "pdf": { "engine": "mistral-ocr" }   // or "cloudflare-ai" or "native"
  }]
}
```

| Engine | Best for | Cost |
|--------|---------|------|
| `mistral-ocr` | Scanned docs / image-heavy PDFs | per-1000-pages fee |
| `cloudflare-ai` | Markdown extraction (default fallback) | free |
| `native` | Models with built-in PDF support | charged as input tokens |

Default behavior: native if the model supports it; otherwise `cloudflare-ai`. The `pdf-text` engine is deprecated → auto-redirects to `cloudflare-ai`. PDFs and other file types coexist in one request.

## Audio inputs

`input_audio` content part. **Base64-only** — direct URLs not supported.

```python
import base64
with open("audio.wav", "rb") as f:
    data = base64.b64encode(f.read()).decode("utf-8")

messages = [{
  "role": "user",
  "content": [
    {"type": "text", "text": "Please transcribe this audio file."},
    {"type": "input_audio", "input_audio": {"data": data, "format": "wav"}}
  ]
}]
```

TS SDK uses camelCase: `{ type: "input_audio", inputAudio: { data, format: "wav" } }`. Filter audio-capable models: `?input_modalities=audio`.

## Video inputs

`video_url` content part. URL or base64 data URL. **Provider support varies**:

- Google Gemini on **AI Studio**: only YouTube links.
- Google Gemini on **Vertex AI**: does not support YouTube; use uploaded video.

OpenRouter only sends video URLs to providers that support them. Video uploads via the OpenRouter chatroom UI are **API-only** (not in the chatroom).

```typescript
content: [
  { type: 'text', text: "Describe what's happening in this video." },
  { type: 'video_url', video_url: { url: 'https://www.youtube.com/watch?v=...' } }
]
```

Filter: `?input_modalities=video`.

## Image generation outputs

Send `modalities` parameter on `/chat/completions`. Returned images appear at `choices[0].message.images[]`.

| Model class | `modalities` |
|-------------|--------------|
| Models outputting text + images (Gemini 2.5 Flash Image) | `["image", "text"]` |
| Image-only models (Sourceful, Flux) | `["image"]` |

```typescript
const result = await openRouter.chat.send({
  model: 'google/gemini-2.5-flash-image',
  messages: [{ role: 'user', content: 'Generate a beautiful sunset over mountains' }],
  modalities: ['image', 'text'],
});

for (const img of result.choices[0].message.images ?? []) {
  const url = img.imageUrl.url;  // base64 data URL
  // save / display
}
```

Filter image-gen models: `?output_modalities=image`. Also available via the Responses API.

## Text-to-speech (TTS)

Dedicated endpoint: `POST /api/v1/audio/speech`. OpenAI-Audio-Speech-compatible. Returns a raw audio byte stream (not JSON).

```typescript
const stream = await openRouter.tts.createSpeech({
  speechRequest: {
    model: 'openai/gpt-4o-mini-tts-2025-12-15',
    input: 'Hello! This is a text-to-speech test.',
    voice: 'alloy',
    responseFormat: 'mp3',
  },
});

const reader = stream.getReader();
const chunks: Uint8Array[] = [];
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  if (value) chunks.push(value);
}
fs.writeFileSync('out.mp3', Buffer.concat(chunks));
```

Filter TTS models: `?output_modalities=speech`. Common formats: `mp3`, `wav`, `flac`, `opus`. Voices vary by model.
