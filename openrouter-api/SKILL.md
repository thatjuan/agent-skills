---
name: openrouter-api
description: "OpenRouter unified-LLM-API expertise. Use when code POSTs to `openrouter.ai/api/v1`, imports `@openrouter/sdk`, `openrouter` (Python), or `@openrouter/agent`; when the OpenAI SDK is pointed at `https://openrouter.ai/api/v1`; when the user asks about routing across hundreds of LLMs (OpenAI, Anthropic, Google, DeepSeek, Meta, xAI, Mistral, etc.) through one endpoint; when working with provider routing, model fallbacks (`models` array), the Auto Router (`openrouter/auto`), `:nitro`/`:floor`/`:online` model suffixes, presets (`@preset/...`), prompt caching with `cache_control`, structured outputs, tool calling, the `openrouter:web_search` server tool, reasoning tokens, multimodal (image/PDF/audio/video) inputs, BYOK provider keys, OAuth PKCE, the `openrouter:` plugins (`web`, `file-parser`, `response-healing`, `context-compression`), or generation/usage accounting via `/api/v1/generation` and `/api/v1/key`."
---

# OpenRouter API

OpenRouter is a unified API in front of 300+ LLMs. Schema is OpenAI-compatible at `/api/v1/chat/completions` plus OpenRouter-only extensions (`models[]`, `provider`, `plugins`, `reasoning`, `cache_control`, presets, `:suffix` shortcuts). Auth is `Authorization: Bearer <OPENROUTER_API_KEY>`.

## Base URL & auth

```
POST https://openrouter.ai/api/v1/chat/completions
Authorization: Bearer $OPENROUTER_API_KEY
Content-Type: application/json
```

Optional attribution headers (enable leaderboard ranking):
- `HTTP-Referer: <YOUR_SITE_URL>`
- `X-OpenRouter-Title: <YOUR_SITE_NAME>` (`X-Title` also accepted)
- `X-OpenRouter-Categories: <comma,separated>`

API keys are created at <https://openrouter.ai/keys>. Each key supports a credit limit and works for OAuth flows. OpenRouter is a GitHub secret-scanning partner — leaked `sk-or-...` keys trigger email notification.

## Three integration paths

| Path | Package | Best for |
|------|---------|----------|
| Raw HTTP | none | Any language, no deps |
| Client SDK | `@openrouter/sdk` (npm) / `openrouter` (pip) | Type-safe thin wrapper over REST |
| Agent SDK | `@openrouter/agent` (npm only, TS) | Multi-turn loops, tool execution, state via `callModel` |
| OpenAI SDK | `openai` with `baseURL: https://openrouter.ai/api/v1` | Drop-in for existing OpenAI code |

Use OpenRouter SDKs by default. Reference the OpenAI SDK only when user explicitly asks.

### Quickstart (TS SDK)

```typescript
import OpenRouter from '@openrouter/sdk';

const client = new OpenRouter({ apiKey: process.env.OPENROUTER_API_KEY });

const completion = await client.chat.send({
  model: 'openai/gpt-5.2',
  messages: [{ role: 'user', content: 'What is the meaning of life?' }],
});
console.log(completion.choices[0].message.content);
```

### Quickstart (Python SDK)

```python
from openrouter import OpenRouter
import os

with OpenRouter(api_key=os.getenv("OPENROUTER_API_KEY")) as client:
    response = client.chat.send(
        model="openai/gpt-5.2",
        messages=[{"role": "user", "content": "What is the meaning of life?"}],
    )
    print(response.choices[0].message.content)
```

### Quickstart (raw HTTP)

```bash
curl https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"openai/gpt-5.2","messages":[{"role":"user","content":"hi"}]}'
```

## Model identifiers

Format: `<provider>/<model>` (e.g., `anthropic/claude-sonnet-4.6`, `openai/gpt-5.2`, `google/gemini-3-flash-preview`, `meta-llama/llama-3.3-70b-instruct`, `deepseek/deepseek-v3.2`). Browse all: <https://openrouter.ai/models>. List via API: `GET /api/v1/models?supported_parameters=tools&output_modalities=text`.

### Suffix shortcuts

| Suffix | Effect | Equivalent |
|--------|--------|------------|
| `:nitro` | Sort providers by throughput | `provider.sort = "throughput"` |
| `:floor` | Sort providers by lowest price | `provider.sort = "price"` |
| `:online` | Enable web plugin (deprecated — prefer `openrouter:web_search` server tool) | `plugins: [{id: "web"}]` with `openrouter/auto` |
| `:free` | Free-tier variants (rate-limited, daily caps) | — |

Combinable: `openai/gpt-oss-20b:free:online`.

### Special model slugs

- `openrouter/auto` — Auto Router (NotDiamond-powered prompt-aware model selection)
- `openrouter/bodybuilder` — natural-language → structured request bodies for parallel multi-model fan-out (free)
- `@preset/<slug>` — invoke a saved preset (system prompt + params + provider rules) by name. Configure at <https://openrouter.ai/settings/presets>. Also usable as `preset: "<slug>"` field or `model: "openai/gpt-4@preset/<slug>"` (combined). Per-request params shallow-merge over preset config.

## Request body — top-level shape

```typescript
type Request = {
  // Either messages or prompt
  messages?: Message[];
  prompt?: string;

  model?: string;           // omit = user default
  models?: string[];        // model fallbacks in order

  stream?: boolean;
  stop?: string | string[];
  response_format?: ResponseFormat;       // json_object | json_schema
  tools?: Tool[];
  tool_choice?: ToolChoice;
  parallel_tool_calls?: boolean;          // default true

  // OpenRouter-only
  provider?: ProviderPreferences;         // see references/routing.md
  plugins?: Plugin[];                     // web, file-parser, response-healing, context-compression, auto-router
  reasoning?: ReasoningConfig;            // see references/reasoning.md
  preset?: string;
  user?: string;                          // stable end-user ID for abuse detection
  debug?: { echo_upstream_body?: boolean }; // streaming only

  // Standard sampling — see references/api-reference.md
  max_tokens?: number;
  temperature?: number;
  top_p?: number; top_k?: number; min_p?: number; top_a?: number;
  frequency_penalty?: number; presence_penalty?: number; repetition_penalty?: number;
  seed?: number; logit_bias?: Record<number, number>;
  logprobs?: boolean; top_logprobs?: number;
  prediction?: { type: 'content'; content: string };
  verbosity?: 'low' | 'medium' | 'high' | 'xhigh' | 'max';
};
```

Unsupported parameters for the chosen model are silently ignored; the rest forward to the upstream. To require providers that support all parameters, set `provider.require_parameters: true`.

## Response shape

```json
{
  "id": "gen-xxxxxxxxxxxxxx",
  "model": "openai/gpt-4o",
  "object": "chat.completion",
  "choices": [{
    "finish_reason": "stop",
    "native_finish_reason": "stop",
    "message": { "role": "assistant", "content": "Hello there!" }
  }],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 4,
    "total_tokens": 14,
    "prompt_tokens_details": { "cached_tokens": 0, "cache_write_tokens": 0 },
    "completion_tokens_details": { "reasoning_tokens": 0 },
    "cost": 0.00014
  }
}
```

Streaming chunks have `delta` instead of `message` and `object: "chat.completion.chunk"`. The final chunk before `data: [DONE]` carries `usage` with empty `choices`.

`finish_reason` is normalized to one of: `tool_calls`, `stop`, `length`, `content_filter`, `error`. Raw provider value is in `native_finish_reason`. The generation ID is also returned in the `X-Generation-Id` response header.

## Errors

```json
{ "error": { "code": 400, "message": "...", "metadata": { ... } } }
```

| Code | Meaning |
|------|---------|
| 400 | Bad request / invalid params / CORS |
| 401 | Invalid API key / expired OAuth |
| 402 | Insufficient credits — add credits |
| 403 | Moderation flagged input |
| 408 | Request timeout |
| 429 | Rate limited |
| 502 | Upstream model down / invalid response |
| 503 | No provider meets routing requirements |

Mid-stream errors (HTTP 200 already sent) arrive as a final SSE chunk with top-level `error` and a choice with `finish_reason: "error"`. See [streaming.md](references/streaming.md).

## Feature map

| Feature | Trigger | Reference |
|---------|---------|-----------|
| Sampling params, full request/response schema, debug option | any chat call | [references/api-reference.md](references/api-reference.md) |
| SSE streaming, cancellation, mid-stream errors | `stream: true` | [references/streaming.md](references/streaming.md) |
| Function/tool calling, agentic loop, parallel tools, streaming tool calls, MCP-to-OpenAI conversion | `tools: [...]` | [references/tool-calling.md](references/tool-calling.md) |
| Structured outputs (`json_schema`, `json_object`) | `response_format` | [references/structured-outputs.md](references/structured-outputs.md) |
| Reasoning/thinking tokens (effort, max_tokens, exclude) | `reasoning: {...}` | [references/reasoning.md](references/reasoning.md) |
| Prompt caching (auto, `cache_control`, sticky routing) | `cache_control` or supported provider | [references/prompt-caching.md](references/prompt-caching.md) |
| Provider routing (sort, order, only, ignore, max_price, throughput, ZDR) | `provider: {...}` | [references/routing.md](references/routing.md) |
| Model fallbacks, Auto Router, Body Builder, presets | `models[]`, `openrouter/auto`, `@preset/...` | [references/routing.md](references/routing.md) |
| Multimodal — images, PDFs, audio, video, image-gen, TTS | `image_url`/`file`/`input_audio` content parts | [references/multimodal.md](references/multimodal.md) |
| Plugins — `web`, `file-parser`, `response-healing`, `context-compression`, `auto-router` | `plugins: [...]` | [references/plugins.md](references/plugins.md) |
| `openrouter:web_search` server tool, `:online` shortcut, citations annotations | `tools: [{type:'openrouter:web_search'}]` | [references/web-search.md](references/web-search.md) |
| Usage accounting, costs, `/generation`, key/credits, rate limits | `usage` field, `GET /api/v1/key` | [references/usage-and-limits.md](references/usage-and-limits.md) |
| BYOK provider keys, OAuth PKCE, app attribution | `cbat_`-style provider keys configured at `/settings/integrations` | [references/byok-and-oauth.md](references/byok-and-oauth.md) |

## Always-fresh docs

OpenRouter exposes Markdown of any docs page by appending `.md` to the URL, plus aggregated `llms-full.txt` files per section. When reference material here is insufficient for a specific edge case, fetch the latest from:

- Quickstart: <https://openrouter.ai/docs/quickstart/llms-full.txt>
- API reference: <https://openrouter.ai/docs/api/reference/llms-full.txt>
- Features: <https://openrouter.ai/docs/guides/features/llms-full.txt>
- Routing: <https://openrouter.ai/docs/guides/routing/llms-full.txt>
- Plugins: <https://openrouter.ai/docs/guides/features/plugins/llms-full.txt>
- Multimodal: <https://openrouter.ai/docs/guides/overview/multimodal/llms-full.txt>
- Best practices (caching, reasoning): <https://openrouter.ai/docs/guides/best-practices/llms-full.txt>
- Auth (BYOK, OAuth): <https://openrouter.ai/docs/guides/overview/auth/llms-full.txt>
- Administration (usage accounting): <https://openrouter.ai/docs/guides/administration/llms-full.txt>
- Server tools (web search): <https://openrouter.ai/docs/guides/features/server-tools/llms-full.txt>
- OpenAPI spec: `https://openrouter.ai/openapi.yaml` or `.json`

Append `.md` to any docs URL for clean Markdown of that single page.

## Common pitfalls

- **`prompt` and `messages` are mutually exclusive** — pick one.
- **The `tools` array must be repeated on every turn** of an agentic loop. The router validates the schema each call. Forgetting to append the assistant's tool-call message to history before the tool-result message breaks Anthropic models.
- **Anthropic automatic caching (top-level `cache_control`) only routes to the Anthropic provider** — Bedrock and Vertex AI are excluded. Per-block `cache_control` works on all three.
- **`max_tokens` cap is `context_length - prompt_length`**, not unbounded.
- **OpenAI o-series and some reasoning models do not return reasoning tokens** even when present internally. `reasoning.exclude: true` controls visibility, not internal use.
- **`debug.echo_upstream_body` only works with `stream: true`** and is dev-only — it can leak request internals.
- **`:online` shortcut is the deprecated `web` plugin** routed through `openrouter/auto`. New code uses the `openrouter:web_search` server tool so the model decides when to search.
- **Mid-stream errors keep HTTP 200** because headers were already sent. Detect via the top-level `error` field on a chunk plus `finish_reason: "error"`.
- **BYOK keys always try first** before OpenRouter shared capacity, regardless of `provider.order`.
- **Free-tier (`:free`) rate limits are global per account** — extra API keys do not multiply quota.
- **The `usage: { include: true }` and `stream_options: { include_usage: true }` parameters are deprecated** — usage is always included now.
