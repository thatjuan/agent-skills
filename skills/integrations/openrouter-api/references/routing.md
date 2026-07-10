# Routing — providers, models, fallbacks, presets

## Contents

- [Provider preferences object](#provider-preferences-object)
- [Default load balancing](#default-load-balancing)
- [Provider sorting](#provider-sorting)
- [Suffix shortcuts (`:nitro`, `:floor`, `:online`)](#suffix-shortcuts)
- [Performance thresholds](#performance-thresholds)
- [`max_price`](#max_price)
- [Allow / ignore / order specific providers](#allow--ignore--order-specific-providers)
- [Quantization filter](#quantization-filter)
- [Disabling fallbacks](#disabling-fallbacks)
- [`require_parameters`](#require_parameters)
- [Data collection / ZDR](#data-collection--zdr)
- [Model fallbacks (`models[]`)](#model-fallbacks-models)
- [Auto Router (`openrouter/auto`)](#auto-router-openrouterauto)
- [Body Builder (`openrouter/bodybuilder`)](#body-builder-openrouterbodybuilder)
- [Presets](#presets)

## Provider preferences object

```typescript
type ProviderPreferences = {
  order?: string[];                      // ['anthropic', 'openai'] — try in order
  allow_fallbacks?: boolean;             // default true
  require_parameters?: boolean;          // default false — only providers supporting all req params
  data_collection?: 'allow' | 'deny';    // default 'allow'
  zdr?: boolean;                         // restrict to ZDR endpoints
  enforce_distillable_text?: boolean;    // restrict to providers allowing text distillation
  only?: string[];                       // whitelist provider slugs
  ignore?: string[];                     // blacklist provider slugs
  quantizations?: string[];              // ['int4', 'int8', 'fp8', 'fp16', 'bf16', 'fp32', ...]
  sort?: 'price' | 'throughput' | 'latency'
       | { by: 'price' | 'throughput' | 'latency'; partition?: 'model' | 'none' };
  preferred_min_throughput?: number | { p50?: number; p75?: number; p90?: number; p99?: number }; // tokens/sec
  preferred_max_latency?: number | { p50?: number; p75?: number; p90?: number; p99?: number };    // seconds
  max_price?: { prompt?: number; completion?: number; image?: number; request?: number };          // USD per 1M tokens / per image / per request
};
```

EU in-region routing is available for Enterprise customers via privacy settings.

## Default load balancing

For a single model, OpenRouter default behavior:

1. Filter out providers with significant outages in the last 30s.
2. Among stable providers, weight selection by **inverse square of price**.
3. Use the rest as fallbacks.

If `sort` or `order` is set, load balancing is disabled.

> Example: providers cost $1, $2, $3 / 1M tokens. Provider A is `1/1²=1`, B is `1/2²=0.25`, C is `1/3²≈0.11` → A picked 9× more than C.

When `tools` / `tool_choice` / `max_tokens` are set, OpenRouter only routes to providers that support those.

## Provider sorting

```json
{ "provider": { "sort": "throughput" } }   // disables load balancing
{ "provider": { "sort": "price" } }
{ "provider": { "sort": "latency" } }
```

## Suffix shortcuts

| Slug | Equivalent |
|------|------------|
| `<model>:nitro` | `provider.sort = "throughput"` |
| `<model>:floor` | `provider.sort = "price"` |
| `<model>:online` | `model: "openrouter/auto"` + `plugins: [{id: "web"}]` (deprecated; use `openrouter:web_search`) |
| `<model>:free` | free-tier variant — daily caps + 20 RPM |

Combinable with `:free`: `openai/gpt-oss-20b:free:online`.

## Performance thresholds

Soft preferences — never block a request, only sort candidates:

```json
{
  "provider": {
    "preferred_min_throughput": 100,
    "preferred_max_latency": { "p90": 2.5 }
  }
}
```

vs `max_price` which **does** prevent execution if no provider qualifies.

## `max_price`

Hard ceiling. Pricing is per 1M tokens (or per image / per request). Request fails (503) if no provider beats it.

```json
{
  "provider": {
    "max_price": { "prompt": 0.50, "completion": 1.50 }
  }
}
```

## Allow / ignore / order specific providers

```json
// only these providers, in this order
{ "provider": { "order": ["anthropic", "google-vertex"], "allow_fallbacks": false } }

// whitelist
{ "provider": { "only": ["fireworks", "deepinfra"] } }

// blacklist
{ "provider": { "ignore": ["azure"] } }
```

Provider slugs visible at <https://openrouter.ai/models?modality=...>.

## Quantization filter

```json
{ "provider": { "quantizations": ["fp8", "bf16"] } }
```

## Disabling fallbacks

```json
{ "provider": { "allow_fallbacks": false } }
```

If the primary provider fails: error returned, no retry.

## `require_parameters`

Only route to providers that fully honor every request parameter (e.g., `logit_bias`, `structured_outputs`). Use when correctness depends on the param.

```json
{ "provider": { "require_parameters": true } }
```

## Data collection / ZDR

```json
{ "provider": { "data_collection": "deny" } }   // exclude providers that may store data
{ "provider": { "zdr": true } }                  // only ZDR-policy endpoints
```

`zdr: true` ORs with the account-wide ZDR setting. ZDR endpoint list: `GET /api/v1/endpoints/zdr` or <https://openrouter.ai/docs/features/zdr>. In-memory provider caching is **not** considered "retention".

## Model fallbacks (`models[]`)

Try multiple models in priority order. Triggered by any error: context length, moderation, rate limit, downtime.

```json
{
  "models": ["anthropic/claude-sonnet-4.6", "gryphe/mythomax-l2-13b"],
  "messages": [{ "role": "user", "content": "..." }]
}
```

Pricing: charged at the model that **ultimately served** the request (returned in `model` field of response).

OpenAI SDK (no native `models` field): pass via `extra_body`:

```python
completion = openai_client.chat.completions.create(
    model="openai/gpt-4o",
    extra_body={ "models": ["anthropic/claude-sonnet-4.6", "gryphe/mythomax-l2-13b"] },
    messages=[...]
)
```

### Sort partitioning across model fallbacks

`sort` as an object controls how endpoints across multiple `models[]` are ranked:

| `partition` | Effect |
|-------------|--------|
| `"model"` (default) | Group by model first, then sort within. Primary model's endpoints always tried first. |
| `"none"` | Global ranking across all models — pick whichever endpoint best matches `sort` regardless of model. |

```json
{
  "models": ["anthropic/claude-sonnet-4.5", "openai/gpt-5-mini", "google/gemini-3-flash-preview"],
  "provider": { "sort": { "by": "throughput", "partition": "none" } }
}
```

Use `partition: "none"` when speed matters more than which exact model serves.

## Auto Router (`openrouter/auto`)

Powered by NotDiamond. Picks the best model per prompt from a curated pool (Claude Sonnet/Opus, GPT-5.x, Gemini 3.x Pro, DeepSeek 3.x, etc.). The actually-selected model is in the response's `model` field. Standard model pricing applies; no router fee.

```json
{ "model": "openrouter/auto", "messages": [...] }
```

Restrict the candidate pool with the `auto-router` plugin:

```json
{
  "model": "openrouter/auto",
  "plugins": [{ "id": "auto-router", "allowed_models": ["anthropic/*", "openai/gpt-5.1"] }]
}
```

Patterns: `anthropic/*`, `openai/gpt-5*`, `*/claude-*`, exact `openai/gpt-5.1`. Defaults can also be set via Settings → Plugins UI.

Limitation: requires `messages` (not `prompt`). Streaming and all standard features work with the selected model.

## Body Builder (`openrouter/bodybuilder`)

Free model that converts a natural-language description into one-or-more OpenRouter request bodies for parallel multi-model fan-out.

```json
{
  "model": "openrouter/bodybuilder",
  "messages": [{ "role": "user", "content": "Count to 10 using Claude Sonnet and GPT-5" }]
}
```

Returns:

```json
{
  "requests": [
    { "model": "anthropic/claude-sonnet-4.5", "messages": [{ "role": "user", "content": "Count to 10" }] },
    { "model": "openai/gpt-5.1",              "messages": [{ "role": "user", "content": "Count to 10" }] }
  ]
}
```

Then `Promise.all` (TS) or `asyncio.gather` (Python) over the requests. Ideal for benchmarking, redundancy, A/B prompt testing.

## Presets

Saved configs (system prompt + params + provider rules) at <https://openrouter.ai/settings/presets>. Three invocation forms:

```json
// 1) as the model
{ "model": "@preset/email-copywriter", "messages": [...] }

// 2) preset field + model
{ "model": "openai/gpt-4", "preset": "email-copywriter", "messages": [...] }

// 3) combined
{ "model": "openai/gpt-4@preset/email-copywriter", "messages": [...] }
```

- Per-request params shallow-merge over preset.
- Always uses the latest preset version (history kept for rollback).
- Org accounts: presets shared across members.

## Uptime

OpenRouter monitors response time, error rate, and availability per provider in real-time, used in default load balancing. Charts at <https://openrouter.ai/models/<slug>>.
