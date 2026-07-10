# Tool calling

## Contents

- [Schema](#schema)
- [Three-step pattern](#three-step-pattern)
- [Python end-to-end (OpenRouter SDK)](#python-end-to-end-openrouter-sdk)
- [Agentic loop](#agentic-loop)
- [Agent SDK (`@openrouter/agent`)](#agent-sdk-openrouteragent)
- [Streaming with tool calls](#streaming-with-tool-calls)
- [Interleaved thinking](#interleaved-thinking)
- [MCP servers as OpenRouter tools](#mcp-servers-as-openrouter-tools)
- [Best-practice tool definitions](#best-practice-tool-definitions)
- [Forcing tool use / disabling tools](#forcing-tool-use--disabling-tools)

Filter tool-supporting models: <https://openrouter.ai/models?supported_parameters=tools>. OpenRouter standardizes the OpenAI tool-call shape across providers — for non-OpenAI providers it transforms or maps; for providers without tool support it converts the schema into a YAML template.

## Schema

```typescript
type Tool = {
  type: 'function';
  function: { name: string; description?: string; parameters: object /* JSON Schema */ };
};

type ToolChoice =
  | 'none'      // disable tools
  | 'auto'      // default — model decides
  | 'required'  // must call ≥1 tool
  | { type: 'function'; function: { name: string } }; // force a specific tool
```

`parallel_tool_calls: false` forces sequential single-tool turns.

## Three-step pattern

1. Send request with `tools`. Model returns `finish_reason: "tool_calls"` and `message.tool_calls[]`.
2. Execute the tool locally.
3. Send a second request: original messages + the assistant's tool_call message + a `{role: "tool", tool_call_id, content}` message. **Include `tools` in every request** — the router validates the schema each call.

### Step 1 — request

```json
{
  "model": "google/gemini-3-flash-preview",
  "messages": [{ "role": "user", "content": "What are the titles of some James Joyce books?" }],
  "tools": [{
    "type": "function",
    "function": {
      "name": "search_gutenberg_books",
      "description": "Search for books in the Project Gutenberg library",
      "parameters": {
        "type": "object",
        "properties": {
          "search_terms": { "type": "array", "items": { "type": "string" }, "description": "List of search terms" }
        },
        "required": ["search_terms"]
      }
    }
  }]
}
```

### Step 3 — request with tool result

```json
{
  "model": "google/gemini-3-flash-preview",
  "messages": [
    { "role": "user", "content": "What are the titles of some James Joyce books?" },
    {
      "role": "assistant",
      "content": null,
      "tool_calls": [{
        "id": "call_abc123",
        "type": "function",
        "function": {
          "name": "search_gutenberg_books",
          "arguments": "{\"search_terms\": [\"James\", \"Joyce\"]}"
        }
      }]
    },
    {
      "role": "tool",
      "tool_call_id": "call_abc123",
      "content": "[{\"id\":4300,\"title\":\"Ulysses\",\"authors\":[{\"name\":\"Joyce, James\"}]}]"
    }
  ],
  "tools": [ /* same tools */ ]
}
```

`tool_call_id` must match the assistant's `tool_calls[].id` exactly. `function.arguments` is a **JSON-encoded string**, not an object — `JSON.parse` it before use.

## Python end-to-end (OpenRouter SDK)

```python
from openrouter import OpenRouter
import json, requests, os

client = OpenRouter(api_key=os.getenv("OPENROUTER_API_KEY"))

def search_gutenberg_books(search_terms):
    r = requests.get("https://gutendex.com/books", params={"search": " ".join(search_terms)})
    return [{"id": b["id"], "title": b["title"], "authors": b["authors"]} for b in r.json().get("results", [])]

TOOL_MAPPING = {"search_gutenberg_books": search_gutenberg_books}

tools = [{
    "type": "function",
    "function": {
        "name": "search_gutenberg_books",
        "description": "Search Project Gutenberg",
        "parameters": {
            "type": "object",
            "properties": {"search_terms": {"type": "array", "items": {"type": "string"}}},
            "required": ["search_terms"],
        },
    },
}]

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "James Joyce books?"},
]

resp = client.chat.send(model="google/gemini-3-flash-preview", tools=tools, messages=messages).choices[0].message
messages.append(resp)

for tc in resp.tool_calls or []:
    args = json.loads(tc.function.arguments)
    result = TOOL_MAPPING[tc.function.name](**args)
    messages.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(result)})

final = client.chat.send(model="google/gemini-3-flash-preview", tools=tools, messages=messages)
print(final.choices[0].message.content)
```

## Agentic loop

```python
MAX_ITERATIONS = 10
for _ in range(MAX_ITERATIONS):
    resp = client.chat.send(model=MODEL, tools=tools, messages=messages)
    msg = resp.choices[0].message
    messages.append(msg)
    if not msg.tool_calls:
        break
    for tc in msg.tool_calls:
        args = json.loads(tc.function.arguments)
        result = TOOL_MAPPING[tc.function.name](**args)
        messages.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(result)})
```

For TS, prefer `@openrouter/agent` `callModel` which handles the loop, tool execution, and state automatically.

## Agent SDK (`@openrouter/agent`)

```typescript
import { callModel, tool } from '@openrouter/agent';
import { z } from 'zod';

const weatherTool = tool({
  name: 'get_weather',
  description: 'Get the current weather for a location',
  inputSchema: z.object({ location: z.string().describe('City name') }),
  execute: async ({ location }) => ({ temperature: 72, condition: 'sunny', location }),
});

const result = await callModel({
  model: 'anthropic/claude-sonnet-4',
  messages: [{ role: 'user', content: 'Weather in San Francisco?' }],
  tools: [weatherTool],
});

console.log(await result.getText());
```

Sends, receives the tool call, executes `get_weather`, feeds the result back, returns final text — one invocation. Supports stop conditions, streaming, dynamic parameters; full docs: <https://openrouter.ai/docs/agent-sdk/overview>.

## Streaming with tool calls

`delta.tool_calls` arrives incrementally. Accumulate `function.name` and `function.arguments` (string) across deltas, then parse JSON once `finish_reason: "tool_calls"` arrives.

```typescript
let toolCalls: any[] = [];
for await (const chunk of stream) {
  const delta = chunk.choices[0].delta;
  if (delta.tool_calls) {
    for (const tc of delta.tool_calls) {
      toolCalls[tc.index] ??= { id: '', type: 'function', function: { name: '', arguments: '' } };
      if (tc.id) toolCalls[tc.index].id = tc.id;
      if (tc.function?.name) toolCalls[tc.index].function.name += tc.function.name;
      if (tc.function?.arguments) toolCalls[tc.index].function.arguments += tc.function.arguments;
    }
  }
  if (chunk.choices[0].finish_reason === 'tool_calls') {
    // execute toolCalls, send next request
  }
}
```

## Interleaved thinking

Some reasoning models (e.g., Claude Sonnet 4.5+) reason **between** tool calls. Multi-step research/agent flows benefit. Higher token usage and latency. Quality of intermediate reasoning depends on model. Provide rich tool descriptions and well-typed parameters so the model can reason about which tool to invoke.

## MCP servers as OpenRouter tools

MCP (Model Context Protocol) tools are convertible to OpenAI tool definitions:

```python
def convert_tool_format(tool):
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": {
                "type": "object",
                "properties": tool.inputSchema["properties"],
                "required": tool.inputSchema["required"],
            },
        },
    }
```

Then standard tool-call loop. Use `mcp.ClientSession` for stateful MCP session management. Full example: <https://openrouter.ai/docs/use-cases/mcp-servers>.

## Best-practice tool definitions

- Specific names: `get_weather_forecast`, not `weather`.
- Detailed descriptions including supported input formats and edge cases.
- `enum` for closed sets, `default` for optional params, `required` array.
- Multi-tool flows benefit from naturally-chainable verbs: `search_products` → `get_product_details` → `check_inventory`.

```json
{
  "type": "function",
  "function": {
    "name": "get_weather_forecast",
    "description": "Get current weather and 5-day forecast. Supports cities, zip codes, coordinates.",
    "parameters": {
      "type": "object",
      "properties": {
        "location": { "type": "string", "description": "City, zip, or 'lat,lng'" },
        "units": { "type": "string", "enum": ["celsius", "fahrenheit"], "default": "celsius" }
      },
      "required": ["location"]
    }
  }
}
```

## Forcing tool use / disabling tools

```json
// disable
{ "tool_choice": "none" }

// require any tool
{ "tool_choice": "required" }

// force a specific tool
{ "tool_choice": { "type": "function", "function": { "name": "search_database" } } }
```
