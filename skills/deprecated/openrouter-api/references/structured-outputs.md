# Structured outputs

## Contents

- [Schema-mode example](#schema-mode-example)
- [TS SDK](#ts-sdk)
- [Best practices](#best-practices)
- [Streaming structured output](#streaming-structured-output)
- [Routing-aware support](#routing-aware-support)
- [Error scenarios](#error-scenarios)
- [Response Healing plugin](#response-healing-plugin)

Two modes of `response_format`:

- `{ "type": "json_object" }` — model returns valid JSON. Instruct the model in the prompt to produce JSON.
- `{ "type": "json_schema", "json_schema": { name, strict, schema } }` — model output matches your JSON Schema exactly.

Filter supporting models: <https://openrouter.ai/models?supported_parameters=structured_outputs>. Native support: OpenAI GPT-4o+, Google Gemini, Anthropic (Sonnet 4.5, Opus 4.1+), most open-source, all Fireworks-hosted.

## Schema-mode example

```json
{
  "model": "openai/gpt-4o",
  "messages": [{ "role": "user", "content": "What's the weather like in London?" }],
  "response_format": {
    "type": "json_schema",
    "json_schema": {
      "name": "weather",
      "strict": true,
      "schema": {
        "type": "object",
        "properties": {
          "location":    { "type": "string", "description": "City or location name" },
          "temperature": { "type": "number", "description": "Temperature in Celsius" },
          "conditions":  { "type": "string", "description": "Weather conditions description" }
        },
        "required": ["location", "temperature", "conditions"],
        "additionalProperties": false
      }
    }
  }
}
```

Response:

```json
{ "location": "London", "temperature": 18, "conditions": "Partly cloudy with light drizzle" }
```

## TS SDK

```typescript
import OpenRouter from '@openrouter/sdk';

const client = new OpenRouter({ apiKey: process.env.OPENROUTER_API_KEY });

const response = await client.chat.send({
  model: 'openai/gpt-4o',
  messages: [{ role: 'user', content: 'Weather in London?' }],
  responseFormat: {
    type: 'json_schema',
    jsonSchema: {
      name: 'weather',
      strict: true,
      schema: {
        type: 'object',
        properties: {
          location:    { type: 'string' },
          temperature: { type: 'number' },
          conditions:  { type: 'string' },
        },
        required: ['location', 'temperature', 'conditions'],
        additionalProperties: false,
      },
    },
  },
});

const data = JSON.parse(response.choices[0].message.content!);
```

## Best practices

- Always set `strict: true` for schema mode.
- Add `description` to every property to guide the model.
- `additionalProperties: false` to prevent hallucinated fields.
- Use `enum` for closed sets, `required` for non-optional fields.
- Make the model's job easier: align property names with how the prompt phrases the data.

## Streaming structured output

Add `stream: true`. Partial JSON streams; assembled output is schema-valid once complete. Useful for incremental UI rendering of partially-built objects.

## Routing-aware support

Combine `structured_outputs` with `provider.require_parameters: true` so OpenRouter only routes to providers that honor the parameter.

```json
{
  "model": "anthropic/claude-sonnet-4.6",
  "response_format": { "type": "json_schema", "json_schema": { ... } },
  "provider": { "require_parameters": true }
}
```

## Error scenarios

- Model lacks structured-output support → request fails.
- Invalid JSON Schema → request fails with schema error.

## Response Healing plugin

For non-streaming `json_schema` requests, enable the [`response-healing` plugin](plugins.md) to repair imperfect JSON output before returning:

```json
{
  "plugins": [{ "id": "response-healing" }],
  "response_format": { "type": "json_schema", "json_schema": { ... } }
}
```

`json_object` mode (no schema) is a fallback when a model rejects `json_schema`. Always instruct the model in the system or user message to "respond in JSON" when using `json_object`.
