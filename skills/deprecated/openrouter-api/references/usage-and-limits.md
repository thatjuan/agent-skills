# Usage accounting, costs, rate limits

## Contents

- [Always-on usage object](#always-on-usage-object)
- [Async lookup — `/generation`](#async-lookup--generation)
- [Activity dashboard](#activity-dashboard)
- [Key info & credits](#key-info--credits)
- [Rate limits](#rate-limits)
- [Cost optimization patterns](#cost-optimization-patterns)
- [Querying upstream cost vs OpenRouter cost](#querying-upstream-cost-vs-openrouter-cost)

## Always-on usage object

Every response includes:

```json
{
  "usage": {
    "prompt_tokens": 194,
    "completion_tokens": 2,
    "total_tokens": 196,
    "prompt_tokens_details": {
      "cached_tokens": 0,
      "cache_write_tokens": 100,
      "audio_tokens": 0
    },
    "completion_tokens_details": {
      "reasoning_tokens": 0
    },
    "cost": 0.95,
    "is_byok": false,
    "cost_details": {
      "upstream_inference_cost": 19            // BYOK only
    },
    "server_tool_use": { "web_search_requests": 0 }
  }
}
```

Streaming: usage arrives once in the **final chunk** (with empty `choices`) before `data: [DONE]`.

The legacy `usage: {include: true}` and `stream_options: {include_usage: true}` parameters are deprecated — usage is always returned now.

### Field meanings

| Field | Meaning |
|-------|---------|
| `prompt_tokens` | Input tokens (incl. images, input audio, tool definitions) |
| `completion_tokens` | Output tokens |
| `total_tokens` | sum |
| `prompt_tokens_details.cached_tokens` | Tokens read from cache |
| `prompt_tokens_details.cache_write_tokens` | Tokens written to cache (provider with explicit caching) |
| `prompt_tokens_details.audio_tokens` | Input audio tokens |
| `prompt_tokens_details.video_tokens` | Input video tokens |
| `completion_tokens_details.reasoning_tokens` | Reasoning tokens (counted toward completion) |
| `completion_tokens_details.audio_tokens` | Output audio tokens |
| `completion_tokens_details.image_tokens` | Output image tokens |
| `cost` | OpenRouter credits charged |
| `is_byok` | True if served via your provider key |
| `cost_details.upstream_inference_cost` | Upstream cost (BYOK only) |
| `server_tool_use.web_search_requests` | Searches made by `openrouter:web_search` |

Token counts use the model's **native tokenizer** — costs vary across models even for identical input/output.

## Async lookup — `/generation`

```bash
curl "https://openrouter.ai/api/v1/generation?id=$GEN_ID" \
  -H "Authorization: Bearer $KEY"
```

Generation ID is in the response body `id` and the `X-Generation-Id` response header. Use for audit, async cost reporting, or batched accounting.

## Activity dashboard

<https://openrouter.ai/activity> — per-generation expansion shows full cost, cache savings (`cache_discount`), provider used, fallbacks attempted.

## Key info & credits

```bash
curl https://openrouter.ai/api/v1/key -H "Authorization: Bearer $KEY"
```

```typescript
type Key = {
  data: {
    label: string;
    limit: number | null;            // credit limit, null = unlimited
    limit_reset: string | null;      // null = never resets
    limit_remaining: number | null;
    include_byok_in_limit: boolean;

    usage: number;                   // all-time credits
    usage_daily: number;             // current UTC day
    usage_weekly: number;            // current UTC week (Mon-start)
    usage_monthly: number;           // current UTC month

    byok_usage: number;              // BYOK equivalents
    byok_usage_daily: number;
    byok_usage_weekly: number;
    byok_usage_monthly: number;

    is_free_tier: boolean;           // true if no credits ever purchased
  };
};
```

```typescript
const keyInfo = await openRouter.apiKeys.getCurrent();
```

## Rate limits

OpenRouter governs capacity **globally per account** — extra accounts/keys do not multiply quota. Different models have different limits; spread load across models if hitting one.

### Free models (`:free` suffix)

- 20 requests / minute.
- Daily request cap depends on account credit history:
  - **Never purchased credits** → low daily cap.
  - **Purchased ≥ threshold credits** → higher daily cap.
- Negative balance → 402 errors **even on free models** until balance is non-negative.

### DDoS protection

Cloudflare blocks requests that dramatically exceed reasonable usage.

### `/credits` endpoint

```bash
curl https://openrouter.ai/api/v1/credits -H "Authorization: Bearer $KEY"
```

Returns purchased / used credit totals at the account level (separate from per-key limits).

## Cost optimization patterns

- **Suffix shortcuts**: `:floor` for cheapest provider, `:nitro` for fastest.
- **Provider sorting**: `provider.sort = "price"` to disable load balancing in favor of price.
- **Prompt caching**: monitor `cached_tokens`; place stable content first.
- **`max_price`**: hard cap; request fails (503) if no provider qualifies.
- **`models[]` fallbacks**: Pricing follows the model that ultimately served (not the first in the list).
- **`require_parameters`**: prevents over-paying for premium providers when cheaper ones support all needed params.
- **BYOK**: sends requests through your own provider account at provider rates + 5% OpenRouter fee (waived for first ~1000 requests/month).

## Querying upstream cost vs OpenRouter cost

`cost` = what you're charged in OpenRouter credits.
`cost_details.upstream_inference_cost` = what the upstream provider charged (BYOK requests only).
`cost_details.upstream_inference_prompt_cost` and `upstream_inference_completions_cost` = upstream split.
