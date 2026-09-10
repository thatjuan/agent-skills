# API reference — request/response, parameters, errors

## Contents

- [Endpoint](#endpoint)
- [Message types](#message-types)
- [Sampling parameters](#sampling-parameters)
- [Response schema (full)](#response-schema-full)
- [Errors — codes, metadata, mid-stream](#errors--codes-metadata-mid-stream)
- [Debug option](#debug-option)
- [Assistant prefill](#assistant-prefill)
- [Generation lookup](#generation-lookup)

## Endpoint

```
POST https://openrouter.ai/api/v1/chat/completions
GET  https://openrouter.ai/api/v1/models[?supported_parameters=tools&output_modalities=text|image|audio|embeddings|all&category=programming|...]
GET  https://openrouter.ai/api/v1/generation?id=<gen-id>
GET  https://openrouter.ai/api/v1/key
GET  https://openrouter.ai/api/v1/credits
GET  https://openrouter.ai/api/v1/endpoints/zdr
```

OpenAPI spec: `https://openrouter.ai/openapi.yaml` (or `.json`).

## Message types

```typescript
type TextContent = { type: 'text'; text: string };
type ImageContentPart = { type: 'image_url'; image_url: { url: string; detail?: string } };
type FileContentPart = { type: 'file'; file: { filename: string; fileData: string } }; // PDF/file
type ContentPart = TextContent | ImageContentPart | FileContentPart;

type Message =
  | { role: 'user' | 'assistant' | 'system'; content: string | ContentPart[]; name?: string }
  | { role: 'tool'; content: string; tool_call_id: string; name?: string };

type Tool = { type: 'function'; function: { name: string; description?: string; parameters: object /*JSON Schema*/ } };
type ToolChoice = 'none' | 'auto' | 'required' | { type: 'function'; function: { name: string } };

type ResponseFormat =
  | { type: 'json_object' }
  | { type: 'json_schema'; json_schema: { name: string; strict?: boolean; schema: object } };

type Plugin = { id: 'web' | 'file-parser' | 'response-healing' | 'context-compression' | 'auto-router'; enabled?: boolean; [k: string]: unknown };
```

`ContentPart[]` is only valid on the `user` role for non-OpenAI models. `name` on a non-tool message is prepended as `"{name}: {content}"` for non-OpenAI models.

## Sampling parameters

| Key | Type | Range / values | Default | Notes |
|-----|------|---------------|---------|-------|
| `temperature` | float | 0.0 – 2.0 | 1.0 | 0 → deterministic |
| `top_p` | float | 0.0 – 1.0 | 1.0 | nucleus sampling |
| `top_k` | int | ≥ 0 | 0 (disabled) | not on OpenAI models |
| `min_p` | float | 0.0 – 1.0 | 0.0 | min relative probability |
| `top_a` | float | 0.0 – 1.0 | 0.0 | dynamic top-p variant |
| `frequency_penalty` | float | -2 – 2 | 0.0 | scales with count |
| `presence_penalty` | float | -2 – 2 | 0.0 | flat penalty |
| `repetition_penalty` | float | 0.0 – 2.0 | 1.0 | scales by token prob |
| `seed` | int | — | — | best-effort determinism |
| `max_tokens` | int | ≥ 1 | model default | capped at `context_length - prompt_length` |
| `max_completion_tokens` | int | ≥ 1 | — | alias of `max_tokens` for OpenAI parity |
| `logit_bias` | map<int,int> | -100 – 100 | — | token-id → bias |
| `logprobs` | bool | — | false | return per-token logprobs |
| `top_logprobs` | int | 0 – 20 | — | requires `logprobs: true` |
| `stop` | string \| string[] | — | — | hard stop sequences |
| `response_format` | object | `json_object` \| `json_schema` | — | structured outputs |
| `structured_outputs` | bool | — | — | filter on supported models |
| `tools` | Tool[] | — | — | function calling |
| `tool_choice` | string \| object | `none`/`auto`/`required`/`{...}` | `auto` | force/disable a tool |
| `parallel_tool_calls` | bool | — | true | allow multiple tools per turn |
| `verbosity` | enum | `low`/`medium`/`high`/`xhigh`/`max` | `medium` | OpenAI Responses-API param; maps to `output_config.effort` on Anthropic (`xhigh` ≥ Claude 4.7 Opus, `max` ≥ Claude 4.6 Opus) |
| `prediction` | `{type:'content',content:string}` | — | — | latency optimization via predicted output |
| `user` | string | — | — | end-user identifier for abuse detection |

Provider-specific extras (e.g., `safe_prompt` for Mistral, `raw_mode` for Hyperbolic) forward as-is.

## Response schema (full)

```typescript
type Response = {
  id: string;
  choices: (NonStreamingChoice | StreamingChoice | NonChatChoice)[];
  created: number;
  model: string;
  object: 'chat.completion' | 'chat.completion.chunk';
  system_fingerprint?: string;
  usage?: ResponseUsage;
};

type NonStreamingChoice = {
  finish_reason: string | null;       // normalized: tool_calls | stop | length | content_filter | error
  native_finish_reason: string | null;
  message: { content: string | null; role: string; tool_calls?: ToolCall[]; reasoning?: string; reasoning_details?: unknown; annotations?: Annotation[] };
  error?: ErrorResponse;
};

type StreamingChoice = {
  finish_reason: string | null;
  native_finish_reason: string | null;
  delta: { content: string | null; role?: string; tool_calls?: ToolCall[]; reasoning?: string };
  error?: ErrorResponse;
};

type NonChatChoice = { finish_reason: string | null; text: string; error?: ErrorResponse };

type ToolCall = { id: string; type: 'function'; function: { name: string; arguments: string /*JSON-encoded*/ } };

type Annotation = { type: 'url_citation'; url_citation: { url: string; title: string; content?: string; start_index: number; end_index: number } };

type ResponseUsage = {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  prompt_tokens_details?: { cached_tokens: number; cache_write_tokens?: number; audio_tokens?: number; video_tokens?: number };
  completion_tokens_details?: { reasoning_tokens?: number; audio_tokens?: number; image_tokens?: number };
  cost?: number;
  is_byok?: boolean;
  cost_details?: { upstream_inference_cost?: number; upstream_inference_prompt_cost: number; upstream_inference_completions_cost: number };
  server_tool_use?: { web_search_requests?: number };
};
```

Token counts use the model's native tokenizer; cost is in OpenRouter credits.

## Errors — codes, metadata, mid-stream

```typescript
type ErrorResponse = { error: { code: number; message: string; metadata?: Record<string, unknown> } };
```

HTTP status equals `error.code` when no tokens were sent. Once any token has streamed, status stays 200 and the error appears as a final SSE chunk.

| Code | Meaning |
|------|---------|
| 400 | Bad Request (invalid params, CORS) |
| 401 | Invalid credentials |
| 402 | Insufficient credits |
| 403 | Moderation flagged input |
| 408 | Timeout |
| 429 | Rate limited |
| 502 | Provider down / invalid response |
| 503 | No provider meets routing requirements |

### Moderation metadata

```typescript
type ModerationErrorMetadata = {
  reasons: string[];
  flagged_input: string;            // truncated mid-string with "..." if >100 chars
  provider_name: string;
  model_slug: string;
};
```

### Provider error metadata

```typescript
type ProviderErrorMetadata = { provider_name: string; raw: unknown };
```

### Mid-stream error chunk

```text
data: {"id":"cmpl-abc123","object":"chat.completion.chunk","created":1234567890,"model":"openai/gpt-4o","provider":"openai","error":{"code":"server_error","message":"Provider disconnected"},"choices":[{"index":0,"delta":{"content":""},"finish_reason":"error"}]}
```

The error sits at the **top level** of the chunk and `choices[].finish_reason` is `"error"`. Stream terminates after this event.

### Responses-API event types (`/api/alpha/responses`)

`response.failed` (final failure), `response.error` (mid-generation), `error` (plain). Some error codes (`context_length_exceeded`, `max_tokens_exceeded`, `token_limit_exceeded`, `string_too_long`) are transformed into successful responses with `finish_reason: "length"`.

### When no content is generated

Cold-start or scaling. May still be charged upstream. Retry or use a different provider/model.

## Debug option

Streaming-only. Returns the transformed upstream request body as the first chunk. Dev-only — may leak internals.

```json
{
  "stream": true,
  "debug": { "echo_upstream_body": true }
}
```

First chunk:

```json
{
  "id": "gen-xxxxx",
  "provider": "Anthropic",
  "model": "anthropic/claude-haiku-4.5",
  "object": "chat.completion.chunk",
  "created": 1234567890,
  "choices": [],
  "debug": {
    "echo_upstream_body": {
      "system": [{ "type": "text", "text": "You are a helpful assistant." }],
      "messages": [{ "role": "user", "content": "Hello!" }],
      "model": "claude-haiku-4-5-20251001",
      "stream": true,
      "max_tokens": 64000,
      "temperature": 1
    }
  }
}
```

Useful for: inspecting parameter transformations, system-message normalization, defaults applied, per-provider attempts during fallback (one debug chunk per attempt). OpenRouter best-effort redacts sensitive data.

## Assistant prefill

Append a final `{role: 'assistant', content: '...'}` to bias the start of the response.

```json
{
  "model": "openai/gpt-5.2",
  "messages": [
    { "role": "user", "content": "What is the meaning of life?" },
    { "role": "assistant", "content": "I'm not sure, but my best guess is" }
  ]
}
```

## Generation lookup

```bash
curl https://openrouter.ai/api/v1/generation?id=$GEN_ID -H "Authorization: Bearer $KEY"
```

Returns the same usage/cost data asynchronously. Useful for audit/historical lookup. Generation ID is also exposed as response header `X-Generation-Id` on every endpoint.
