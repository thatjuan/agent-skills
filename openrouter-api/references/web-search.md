# Web search

## Contents

- [Server tool (recommended)](#server-tool-recommended)
- [Citations](#citations)
- [Works with the Responses API](#works-with-the-responses-api)
- [Deprecated `web` plugin / `:online` suffix](#deprecated-web-plugin--online-suffix)

Two ways to ground responses with real-time web data:

- **`openrouter:web_search` server tool** (recommended) — model decides when/whether to search; can search 0–N times per request.
- **`web` plugin / `:online` suffix** (deprecated) — always searches once per request.

Both support multiple engines under the hood: `auto` (native if available, else Exa), `native`, `exa`, `firecrawl` (BYOK), `parallel`.

## Server tool (recommended)

```json
{
  "model": "openai/gpt-5.2",
  "messages": [{ "role": "user", "content": "What were the major AI announcements this week?" }],
  "tools": [{ "type": "openrouter:web_search" }]
}
```

The model emits search queries when needed; OpenRouter executes them; results (URLs, titles, snippets) flow back to the model; the model synthesizes a grounded, cited response. Multiple searches per request allowed.

### Parameters

```json
{
  "type": "openrouter:web_search",
  "parameters": {
    "engine": "exa",
    "max_results": 5,
    "max_total_results": 20,
    "search_context_size": "medium",
    "allowed_domains": ["example.com"],
    "excluded_domains": ["reddit.com"],
    "user_location": {
      "type": "approximate",
      "city": "San Francisco",
      "region": "California",
      "country": "US",
      "timezone": "America/Los_Angeles"
    }
  }
}
```

| Param | Default | Notes |
|-------|---------|-------|
| `engine` | `auto` | `auto`, `native`, `exa`, `firecrawl`, `parallel` |
| `max_results` | 5 | per-search-call (1-25); ignored on native engines |
| `max_total_results` | — | cap across all searches in one request — useful for cost control in agentic loops |
| `search_context_size` | `medium` | `low`/`medium`/`high`; Exa: chars per result; Parallel: total chars |
| `user_location` | — | only honored by native provider search |
| `allowed_domains` | — | Exa, Parallel, most native |
| `excluded_domains` | — | Exa, Parallel, some native |

### Engine capabilities

| Feature | Exa | Firecrawl | Parallel | Native |
|---------|-----|-----------|----------|--------|
| Domain filtering | Yes | No | Yes | Varies |
| Context size control | per-result | No | total chars | No |
| API key | server-side | BYOK | server-side | provider-handled |

### Domain filtering matrix

| Engine | `allowed` | `excluded` | Notes |
|--------|-----------|------------|-------|
| Exa | ✓ | ✓ | both simultaneously |
| Parallel | ✓ | ✓ | mutually exclusive |
| Firecrawl | ✗ | ✗ | error if set |
| Native (Anthropic) | ✓ | ✓ | mutually exclusive |
| Native (OpenAI) | ✓ | silently ignored | — |
| Native (xAI) | ✓ | ✓ | mutually exclusive |
| Native (Perplexity) | ✗ | ✗ | use `:online` plugin path |

### Firecrawl setup (BYOK)

1. Settings → Plugins → set Firecrawl as engine.
2. Accept Firecrawl ToS (creates linked account; 100k free credits).
3. Searches deduct from Firecrawl credits, not OpenRouter.

### Tracking usage

```json
"usage": {
  "input_tokens": 105,
  "output_tokens": 250,
  "server_tool_use": { "web_search_requests": 2 }
}
```

### Pricing

| Engine | Cost |
|--------|------|
| Exa | $4 / 1000 results in OpenRouter credits (default 5 results → max $0.02/search) |
| Parallel | $4 / 1000 results |
| Firecrawl | Firecrawl credits (no OpenRouter charge) |
| Native | provider pass-through (OpenAI, Anthropic, Perplexity, xAI rate cards) |

LLM token cost still applies on top.

## Citations

All engines normalize to OpenAI-Chat-style annotations on `message.annotations`:

```json
{
  "message": {
    "role": "assistant",
    "content": "Here's the latest news I found: ...",
    "annotations": [{
      "type": "url_citation",
      "url_citation": {
        "url": "https://www.example.com/article",
        "title": "Article title",
        "content": "Snippet content if available",
        "start_index": 100,
        "end_index": 200
      }
    }]
  }
}
```

## Works with the Responses API

`POST /api/v1/responses`:

```json
{
  "model": "openai/gpt-5.2",
  "input": "What is the current price of Bitcoin?",
  "tools": [{ "type": "openrouter:web_search", "parameters": { "max_results": 3 } }]
}
```

## Deprecated `web` plugin / `:online` suffix

```json
// :online suffix — always searches once
{ "model": "openai/gpt-5.2:online" }

// equivalent
{ "model": "openrouter/auto", "plugins": [{ "id": "web" }] }
```

`:online` works on `:free` variants too (`openai/gpt-oss-20b:free:online`). Web search costs apply even on free models.

### Migration

| Aspect | Plugin (deprecated) | Server tool |
|--------|---------------------|-------------|
| Enable | `plugins: [{id: "web"}]` | `tools: [{type: "openrouter:web_search"}]` |
| Who decides | always searches once | model decides 0–N |
| Engine options | Native, Exa, Firecrawl, Parallel | + `auto` |
| `allowed_domains` field name | `include_domains` | `allowed_domains` |
| Context size | `web_search_options` | `search_context_size` parameter |
| Total cap | none | `max_total_results` |
