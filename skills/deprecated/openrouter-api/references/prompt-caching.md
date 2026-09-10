# Prompt caching

## Contents

- [Provider sticky routing](#provider-sticky-routing)
- [Inspecting cache usage](#inspecting-cache-usage)
- [OpenAI](#openai)
- [Grok / Moonshot AI / Groq](#grok--moonshot-ai--groq)
- [DeepSeek](#deepseek)
- [Google Gemini — implicit caching](#google-gemini--implicit-caching)
- [Google Gemini — explicit caching via `cache_control`](#google-gemini--explicit-caching-via-cache_control)
- [Anthropic Claude](#anthropic-claude)
- [Patterns](#patterns)
- [Detecting cache discount](#detecting-cache-discount)

Most providers cache automatically; some (Anthropic, Gemini via OpenRouter) require `cache_control` breakpoints. Cache savings appear in `usage.prompt_tokens_details.cached_tokens` and `cache_write_tokens`.

## Provider sticky routing

Once a request uses caching, OpenRouter remembers the provider and routes subsequent same-conversation requests to it to keep cache warm. Conversations are identified by hashing the first system/developer message and the first non-system message. Sticky routing only activates when the provider's cache-read price is cheaper than its regular prompt price. Disabled when `provider.order` is set explicitly.

## Inspecting cache usage

```json
{
  "usage": {
    "prompt_tokens": 10339,
    "completion_tokens": 60,
    "total_tokens": 10399,
    "prompt_tokens_details": {
      "cached_tokens": 10318,        // tokens read from cache
      "cache_write_tokens": 0        // tokens written to cache (first-write only)
    }
  }
}
```

Activity dashboard: <https://openrouter.ai/activity>. Per-generation lookup: `GET /api/v1/generation?id=<gen-id>`.

## OpenAI

- Automatic; no config needed.
- Min cacheable prompt: 1024 tokens.
- Cache writes free; cache reads at 0.25× or 0.50× input price (model-dependent).

## Grok / Moonshot AI / Groq

- Automatic.
- Cache writes free; cache reads multiplied (model-dependent).
- Groq currently caching only Kimi K2 models.

## DeepSeek

- Automatic.
- Cache writes at full input price; cache reads at fractional rate.

## Google Gemini — implicit caching

Gemini 2.5 Pro / 2.5 Flash cache automatically. No setup. TTL averages 3-5 min, varies. Minimum tokens for cache eligibility differ per model. To maximize hit rate, keep the start of `messages` consistent and put dynamic content (user questions) at the end.

## Google Gemini — explicit caching via `cache_control`

OpenRouter accepts Anthropic-style `cache_control` breakpoints for Gemini and abstracts cache lifecycle (no manual cache create/update/delete). Recommended for large stable content (CSVs, character cards, RAG, books).

```json
{
  "messages": [
    {
      "role": "system",
      "content": [
        { "type": "text", "text": "You are a historian studying the fall of the Roman Empire. Below is reference material:" },
        { "type": "text", "text": "HUGE TEXT BODY", "cache_control": { "type": "ephemeral" } }
      ]
    },
    { "role": "user", "content": [{ "type": "text", "text": "What triggered the collapse?" }] }
  ]
}
```

Multiple breakpoints are accepted but only the **last** is used for Gemini. Gemini's `systemInstruction` is immutable once cached — for dynamic content, place it in a later `user` message instead of trailing the cached system block.

## Anthropic Claude

Two modes:

### Automatic caching (recommended for multi-turn)

Single top-level `cache_control`. The breakpoint auto-advances as conversation grows.

```json
{
  "model": "anthropic/claude-sonnet-4.6",
  "cache_control": { "type": "ephemeral" },
  "messages": [
    { "role": "system", "content": "You are a historian... HUGE TEXT BODY" },
    { "role": "user",   "content": "What triggered the collapse?" }
  ]
}
```

Top-level `cache_control` **only routes to the Anthropic provider directly** — Bedrock and Vertex AI are excluded. Per-block `cache_control` works on all three.

### Explicit per-block breakpoints

Up to **4** breakpoints per request. Best on large stable text bodies.

```json
{
  "messages": [{
    "role": "system",
    "content": [
      { "type": "text", "text": "You are a historian studying the fall of the Roman Empire. You know the following book very well:" },
      { "type": "text", "text": "HUGE TEXT BODY", "cache_control": { "type": "ephemeral" } }
    ]
  }, {
    "role": "user",
    "content": [{ "type": "text", "text": "What triggered the collapse?" }]
  }]
}
```

### TTL options

| TTL | Syntax | Cache write multiplier |
|-----|--------|-----------------------|
| 5 minutes (default) | `{"type": "ephemeral"}` | provider-specific (often 1.25×) |
| 1 hour | `{"type": "ephemeral", "ttl": "1h"}` | 2× |

Cache reads are at a fractional multiplier of input price (provider-specific). 1-hour TTL pays off for long sessions where the same content is queried many times — avoid repeated 5-min re-writes.

### Supported Claude models & minimums

| Model | Min cacheable tokens |
|-------|---------------------|
| Claude Opus 4.7 / 4.6 / 4.5 | 4096 |
| Claude Haiku 4.5 | 4096 |
| Claude Sonnet 4.6 | 2048 |
| Claude Haiku 3.5 | 2048 |
| Claude Sonnet 4.5 / Opus 4.1 / Opus 4 / Sonnet 4 / Sonnet 3.7 | 1024 |

Below the minimum: not cached.

## Patterns

- **Multi-turn chat with large system prompt** (Anthropic, recommended): top-level `cache_control: { type: "ephemeral" }`. Breakpoint advances automatically per turn.
- **One-shot RAG over a doc** (Anthropic / Gemini): place the doc in a user message with explicit `cache_control` block, ask the question after the cached block.
- **Long sessions (>5 min between turns)** (Anthropic): use `ttl: "1h"` to skip repeated cache writes.

## Detecting cache discount

Activity page or `cache_discount` field in the generation response. Some providers (Anthropic) show a negative discount on cache writes and positive on reads — net effect is total cost savings.
