# Reasoning tokens

Reasoning tokens (a.k.a. "thinking" tokens) appear on the response in `message.reasoning` and are billed as **output tokens**. OpenRouter normalizes per-provider reasoning controls under one `reasoning` parameter.

## Schema

```typescript
type ReasoningConfig = {
  // mutually exclusive — pick one:
  effort?: 'xhigh' | 'high' | 'medium' | 'low' | 'minimal' | 'none'; // OpenAI/Grok-style
  max_tokens?: number;                                                // Anthropic/Gemini-style

  exclude?: boolean;  // hide reasoning from response (still used internally). Default false.
  enabled?: boolean;  // turn on with default params (medium effort)
};
```

`effort` and `max_tokens` are translated to whichever the chosen model needs. For models that only accept `effort`, `max_tokens` is converted via approximate percentages. For models that only accept `max_tokens`, `effort` levels map to:

| Effort | Approx % of max_tokens |
|--------|------------------------|
| `xhigh` | ~95% |
| `high` | ~80% |
| `medium` | ~50% |
| `low` | ~20% |
| `minimal` | ~10% |
| `none` | reasoning disabled |

## Provider support

| Provider | Param accepted |
|----------|----------------|
| OpenAI o-series, GPT-5 series | `effort` |
| Grok | `effort` |
| Anthropic Claude reasoning models | `max_tokens` |
| Gemini thinking models | `max_tokens` |
| Alibaba Qwen thinking models | `max_tokens` (mapped to `thinking_budget`) — model-dependent |

OpenAI o-series do not return reasoning tokens in the response (used internally only).

## Example — control effort

```typescript
const response = await openRouter.chat.send({
  model: 'openai/o3-mini',
  messages: [{ role: 'user', content: "How would you build the world's tallest skyscraper?" }],
  reasoning: { effort: 'high' },
});

console.log('REASONING:', response.choices[0].message.reasoning);
console.log('CONTENT:',   response.choices[0].message.content);
```

## Example — Anthropic max_tokens

```json
{
  "model": "anthropic/claude-sonnet-4.6",
  "messages": [...],
  "reasoning": { "max_tokens": 8000 }
}
```

## Hide reasoning

```json
{ "reasoning": { "effort": "high", "exclude": true } }
```

Model still uses reasoning internally (and is billed for it via `usage.completion_tokens_details.reasoning_tokens`); just not returned.

## Default-on

```json
{ "reasoning": { "enabled": true } }
```

Maps to medium effort with no exclusions.

## Verifying via usage

```json
"usage": {
  "completion_tokens": 1245,
  "completion_tokens_details": { "reasoning_tokens": 1100 },
  "prompt_tokens": 80,
  "total_tokens": 1325,
  "cost": 0.013
}
```

Reasoning tokens count toward `completion_tokens` and cost.

## Latest details

For specific reasoning-model parameter quirks (Anthropic interleaved thinking, Qwen `thinking_budget` mapping per model, Gemini thinking budgets), fetch <https://openrouter.ai/docs/use-cases/reasoning-tokens.md>.
