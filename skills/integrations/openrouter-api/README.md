# openrouter-api

> Expertise for OpenRouter — one OpenAI-compatible endpoint in front of 300+ LLMs, with provider routing, model fallbacks, caching, tool calling, and multimodal inputs.

## What it does

`openrouter-api` makes your agent fluent in OpenRouter, whose schema is OpenAI-compatible at `/api/v1/chat/completions` plus OpenRouter-only extensions. The skill covers:

- **Integration paths** — raw HTTP, the `@openrouter/sdk`/`openrouter` client SDKs, the `@openrouter/agent` agent SDK, and pointing the OpenAI SDK at OpenRouter's base URL.
- **Model selection** — `<provider>/<model>` identifiers, the `:nitro`/`:floor`/`:online`/`:free` suffix shortcuts, the `openrouter/auto` Auto Router, `openrouter/bodybuilder`, and `@preset/...` presets.
- **The request body** — `models[]` fallbacks, `provider` routing preferences, `plugins`, `reasoning`, `response_format`, `tools`, and the full sampling parameter set.
- **Response and error handling** — normalized `finish_reason`, usage/cost accounting, and the full error-code table including mid-stream errors that keep HTTP 200.
- **Feature depth** — SSE streaming, tool calling and agentic loops, structured outputs, reasoning tokens, prompt caching with `cache_control`, provider routing, multimodal (image/PDF/audio/video), the `openrouter:` plugins, the `openrouter:web_search` server tool, usage accounting, and BYOK/OAuth PKCE.

It triggers when code POSTs to `openrouter.ai/api/v1`, imports `@openrouter/sdk`/`openrouter`/`@openrouter/agent`, points the OpenAI SDK at OpenRouter, or asks about routing across models, fallbacks, caching, or any of the extension features.

## When to use it

Invoke this skill when you hear:

- *"Call three models with a fallback chain if the first is down."*
- *"Route every request to the cheapest provider that supports tools."*
- *"Set up prompt caching for an Anthropic model through OpenRouter."*
- *"Give the model a web-search tool and capture citations."*
- *"Pass a PDF and a JSON schema and get structured output back."*
- *"Why did my mid-stream request return an error but HTTP 200?"*

## Example walkthrough

Asked for a resilient chat call, the skill reaches for the OpenRouter SDK by default and wires a `models[]` fallback chain plus `provider` routing preferences, rather than hardcoding one model. For an agentic loop it reminds you the `tools` array must be repeated on every turn and that the assistant's tool-call message must be appended to history before the tool-result message — otherwise Anthropic models break. It detects mid-stream failures via the top-level `error` field on a chunk with `finish_reason: "error"`, since headers are already sent as HTTP 200.

## Installation

```bash
npx skills add thatjuan/agent-skills --skill openrouter-api
```

## Bundled resources

| File | Purpose |
|------|---------|
| `SKILL.md` | Base URL/auth, integration paths with quickstarts, model identifiers and suffixes, request/response shape, error table, feature map, pitfalls |
| `references/api-reference.md` | Full sampling params, request/response schema, debug option |
| `references/streaming.md` | SSE streaming, cancellation, mid-stream errors |
| `references/tool-calling.md` | Function/tool calling, agentic loop, parallel tools, streaming tool calls, MCP-to-OpenAI conversion |
| `references/structured-outputs.md` | `json_schema` and `json_object` response formats |
| `references/reasoning.md` | Reasoning/thinking tokens — effort, max_tokens, exclude |
| `references/prompt-caching.md` | Automatic and `cache_control` caching, sticky routing |
| `references/routing.md` | Provider routing (sort/order/only/ignore/max_price/ZDR), fallbacks, Auto Router, Body Builder, presets |
| `references/multimodal.md` | Image, PDF, audio, video inputs plus image-gen and TTS |
| `references/plugins.md` | `web`, `file-parser`, `response-healing`, `context-compression`, `auto-router` plugins |
| `references/web-search.md` | `openrouter:web_search` server tool, `:online` shortcut, citation annotations |
| `references/usage-and-limits.md` | Usage accounting, costs, `/generation`, key/credits, rate limits |
| `references/byok-and-oauth.md` | BYOK provider keys, OAuth PKCE, app attribution |

## Tips

- **`prompt` and `messages` are mutually exclusive** — pick one.
- **Repeat the `tools` array every turn** of an agentic loop; the router revalidates each call. Append the assistant tool-call message before the tool-result message or Anthropic models break.
- **Anthropic top-level `cache_control` only routes to the Anthropic provider** — Bedrock and Vertex are excluded. Per-block `cache_control` works on all three.
- **Prefer the `openrouter:web_search` server tool over `:online`** — the `:online` shortcut is the deprecated `web` plugin, and the server tool lets the model decide when to search.
- **Mid-stream errors keep HTTP 200.** Detect them via the top-level `error` field on a chunk plus `finish_reason: "error"`.
- **Unsupported params are silently ignored.** Set `provider.require_parameters: true` to force providers that honor everything you sent.

## Related skills

- [`grok-imagine-api`](../grok-imagine-api/) — direct xAI image generation/editing when not routing through OpenRouter
