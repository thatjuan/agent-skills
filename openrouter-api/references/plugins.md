# Plugins

Plugins extend model behavior. Enable via `plugins: [...]` array in the request body.

```typescript
type Plugin = {
  id: 'web' | 'file-parser' | 'response-healing' | 'context-compression' | 'auto-router';
  enabled?: boolean;
  [key: string]: unknown;  // plugin-specific options
};
```

## `file-parser` — PDF / file processing

```json
{
  "plugins": [{
    "id": "file-parser",
    "pdf": { "engine": "mistral-ocr" }
  }]
}
```

Engines: `mistral-ocr` (scanned/image-heavy, paid per 1000 pages), `cloudflare-ai` (free, default fallback), `native` (model-supported, charged as input tokens). Deprecated: `pdf-text` → auto-redirects to `cloudflare-ai`. See [multimodal.md](multimodal.md).

## `response-healing` — JSON repair

```json
{
  "plugins": [{ "id": "response-healing" }],
  "response_format": { "type": "json_schema", "json_schema": { ... } }
}
```

Repairs imperfect JSON returned by the model before responding. Non-streaming requests with `response_format` only.

## `context-compression` — middle-out truncation

```json
{ "plugins": [{ "id": "context-compression" }] }
```

For prompts that exceed model context. Removes/truncates messages from the **middle** of the prompt (LLMs attend less to middle content). Also handles message-count limits (Claude has a max-messages cap; plugin keeps half from start, half from end).

When enabled, OpenRouter prefers models whose context length is ≥ half the required tokens (input + completion). If none qualify, falls back to the highest-context model.

**Default-on** for all OpenRouter endpoints with ≤ 8192 token context. Disable with:

```json
{ "plugins": [{ "id": "context-compression", "enabled": false }] }
```

Without compression, exceeding context fails with a suggestion to enable it.

## `web` — web search (deprecated, prefer `openrouter:web_search` server tool)

```json
{ "plugins": [{ "id": "web" }] }
```

Or shortcut: `model: "openai/gpt-5.2:online"`. Always searches once per request. See [web-search.md](web-search.md).

## `auto-router` — restrict Auto Router model pool

Only meaningful when `model: "openrouter/auto"`.

```json
{
  "model": "openrouter/auto",
  "plugins": [{
    "id": "auto-router",
    "allowed_models": ["anthropic/*", "openai/gpt-5.1", "*/claude-*"]
  }]
}
```

Wildcard patterns: `provider/*`, `provider/model-prefix*`, `*/substring-*`, exact match. Defaults configurable via Settings → Plugins UI.

## Disabling a plugin

Pass `enabled: false`:

```json
{ "plugins": [{ "id": "context-compression", "enabled": false }] }
```

Useful for opting out of an OpenRouter default (e.g., context compression on small-context models).
