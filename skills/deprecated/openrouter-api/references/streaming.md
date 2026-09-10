# Streaming (SSE)

## Contents

- [Quick example (TS SDK)](#quick-example-ts-sdk)
- [Raw fetch (TS)](#raw-fetch-ts)
- [Python raw](#python-raw)
- [Recommended SSE clients](#recommended-sse-clients)
- [Cancellation](#cancellation)
- [Error handling](#error-handling)
- [Streaming with structured outputs](#streaming-with-structured-outputs)
- [Streaming with tool calls](#streaming-with-tool-calls)
- [Streaming with debug](#streaming-with-debug)

Set `stream: true`. Response is `text/event-stream`. Lines:

- `data: {json chunk}` — content delta
- `data: [DONE]` — end of stream
- `: OPENROUTER PROCESSING` — keep-alive comment, ignore per SSE spec

The final chunk before `[DONE]` carries `usage` with `choices: []`.

## Quick example (TS SDK)

```typescript
const stream = await openRouter.chat.send({
  model: 'openai/gpt-5.2',
  messages: [{ role: 'user', content: 'Tell a story' }],
  stream: true,
});

for await (const chunk of stream) {
  const content = chunk.choices?.[0]?.delta?.content;
  if (content) process.stdout.write(content);
  if (chunk.usage) console.log('\nUsage:', chunk.usage);
}
```

## Raw fetch (TS)

```typescript
const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
  method: 'POST',
  headers: { Authorization: `Bearer ${KEY}`, 'Content-Type': 'application/json' },
  body: JSON.stringify({ model, messages, stream: true }),
});

const reader = response.body!.getReader();
const decoder = new TextDecoder();
let buffer = '';

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  buffer += decoder.decode(value, { stream: true });

  while (true) {
    const lineEnd = buffer.indexOf('\n');
    if (lineEnd === -1) break;
    const line = buffer.slice(0, lineEnd).trim();
    buffer = buffer.slice(lineEnd + 1);

    if (!line.startsWith('data: ')) continue;
    const data = line.slice(6);
    if (data === '[DONE]') return;

    try {
      const parsed = JSON.parse(data);
      if (parsed.error) { /* mid-stream error — see below */ break; }
      const content = parsed.choices?.[0]?.delta?.content;
      if (content) process.stdout.write(content);
    } catch { /* skip non-JSON */ }
  }
}
```

## Python raw

```python
import requests, json

with requests.post(url, headers=headers, json=payload, stream=True) as r:
  buffer = ""
  for chunk in r.iter_content(chunk_size=1024, decode_unicode=True):
    buffer += chunk
    while True:
      line_end = buffer.find('\n')
      if line_end == -1: break
      line = buffer[:line_end].strip()
      buffer = buffer[line_end + 1:]
      if line.startswith('data: '):
        data = line[6:]
        if data == '[DONE]': break
        try:
          obj = json.loads(data)
          if 'error' in obj: ...   # mid-stream error
          content = obj["choices"][0]["delta"].get("content")
          if content: print(content, end="", flush=True)
        except json.JSONDecodeError: pass
```

## Recommended SSE clients

- [`eventsource-parser`](https://github.com/rexxars/eventsource-parser)
- OpenAI SDK (npm `openai`)
- Vercel AI SDK (npm `ai`)

Some SSE clients choke on the `: OPENROUTER PROCESSING` keep-alive — pick one of the above.

## Cancellation

`AbortController` for fetch / `signal` option for SDK / close session for Python `requests`. For supported providers, cancellation stops upstream processing and billing.

```typescript
const controller = new AbortController();

const stream = await openRouter.chat.send(
  { model, messages, stream: true },
  { signal: controller.signal },
);
// ...later
controller.abort();
```

**Cancellation supported**: OpenAI, Azure, Anthropic, Fireworks, Mancer, Recursal, AnyScale, Lepton, OctoAI, Novita, DeepInfra, Together, Cohere, Hyperbolic, Infermatic, Avian, XAI, Cloudflare, SFCompute, Nineteen, Liquid, Friendli, Chutes, DeepSeek.

**Not supported** (request continues, billing continues): AWS Bedrock, Groq, Modal, Google, Google AI Studio, Minimax, HuggingFace, Replicate, Perplexity, Mistral, AI21, Featherless, Lynn, Lambda, Reflection, SambaNova, Inflection, ZeroOneAI, AionLabs, Alibaba, Nebius, Kluster, Targon, InferenceNet.

## Error handling

### Pre-stream errors (HTTP status != 200)

Standard `{"error": {"code": ..., "message": ...}}` JSON with the proper status code.

### Mid-stream errors (HTTP 200 already sent)

Final SSE chunk has top-level `error` plus a choice with `finish_reason: "error"`:

```text
data: {"id":"cmpl-abc123","object":"chat.completion.chunk","created":...,"model":"openai/gpt-4o","provider":"openai","error":{"code":"server_error","message":"Provider disconnected unexpectedly"},"choices":[{"index":0,"delta":{"content":""},"finish_reason":"error"}]}
```

```typescript
for await (const chunk of stream) {
  if ('error' in chunk) {
    console.error('Stream error:', chunk.error.message);
    if (chunk.choices?.[0]?.finish_reason === 'error') break;
    return;
  }
  // normal handling
}
```

## Streaming with structured outputs

Add `stream: true` alongside `response_format`. Partial JSON is streamed and forms a valid schema-matching object once complete.

## Streaming with tool calls

`delta.tool_calls` arrives in pieces (function name first, then partial `arguments` string). Accumulate before parsing JSON. `finish_reason: "tool_calls"` ends the model turn — execute tool, append `{role: 'tool', tool_call_id, content}`, send next request.

## Streaming with debug

`debug.echo_upstream_body: true` works **only with streaming** and emits one debug chunk per provider attempt as the first chunk(s) of the stream. See `references/api-reference.md`.
