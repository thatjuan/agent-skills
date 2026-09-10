# SDKs

OpenWA ships first-party clients in `sdk/javascript/` (`@openwa/sdk`) and `sdk/python/` (`openwa`). Both wrap the REST API with typed surfaces; for endpoints not yet wrapped, drop down to raw `fetch`/`httpx` with the `X-API-Key` header.

## Contents

- [JavaScript / TypeScript](#javascripttypescript)
- [Python](#python)
- [Generating clients from OpenAPI](#generating-clients-from-openapi)
- [Real-time via socket.io-client](#real-time-via-socketio-client)
- [n8n](#n8n)

## JavaScript / TypeScript

`sdk/javascript/src/index.ts` exports:

```typescript
export interface OpenWAClientConfig {
  baseUrl: string;       // 'http://localhost:2785'
  apiKey: string;
  timeout?: number;      // default 30000 ms
}

export interface MessageResponse { messageId: string; timestamp: number }
export interface Session { id: string; name: string; status: string; phone: string|null; pushName: string|null }

export class OpenWAClient {
  constructor(config: OpenWAClientConfig)
  get sessions(): {
    list(): Promise<Session[]>;
    get(id: string): Promise<Session>;
    create(data: { name: string }): Promise<Session>;
    start(id: string): Promise<Session>;
    stop(id: string): Promise<Session>;
    delete(id: string): Promise<void>;
  }
  get messages(): {
    sendText(sessionId: string, data: { chatId: string; text: string }): Promise<MessageResponse>;
  }
}
export default OpenWAClient;
```

Auth is `X-API-Key: <key>`; transport is `fetch` with `AbortSignal.timeout`.

### Usage

```typescript
import { OpenWAClient } from '@openwa/sdk';

const wa = new OpenWAClient({
  baseUrl: process.env.OPENWA_URL ?? 'http://localhost:2785',
  apiKey: process.env.OPENWA_KEY!,
});

const session = await wa.sessions.create({ name: 'bot-1' });
await wa.sessions.start(session.id);
// poll wa.sessions.get(session.id) until status === 'READY'
await wa.messages.sendText(session.id, {
  chatId: '628123456789@c.us',
  text: 'Hello from OpenWA',
});
```

### Endpoints the typed surface doesn't cover

The hand-written client wraps the most-used endpoints. For everything else (webhooks, media sends, groups, labels, contacts, channels, status, catalog, api-keys, infra, audit), call via `fetch` directly — the API key header is the only auth requirement:

```typescript
async function call(path: string, init: RequestInit = {}) {
  const res = await fetch(`http://localhost:2785${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': process.env.OPENWA_KEY!,
      ...(init.headers ?? {}),
    },
  });
  if (!res.ok) throw new Error(`OpenWA ${res.status}: ${await res.text()}`);
  return res.status === 204 ? null : res.json();
}

await call(`/api/sessions/${id}/webhooks`, {
  method: 'POST',
  body: JSON.stringify({
    url: 'https://example.com/wa',
    events: ['message.received'],
    secret: process.env.WEBHOOK_SECRET,
  }),
});
```

## Python

`sdk/python/openwa/` mirrors the JS shape. Install path (from source):

```bash
pip install -e sdk/python/openwa
```

Sketch:

```python
from openwa import OpenWAClient

wa = OpenWAClient(base_url="http://localhost:2785", api_key=os.environ["OPENWA_KEY"])
session = wa.sessions.create(name="bot-1")
wa.sessions.start(session.id)
wa.messages.send_text(session.id, chat_id="628123456789@c.us", text="hi")
```

For unwrapped endpoints use the same header from `httpx`:

```python
import httpx
client = httpx.Client(base_url="http://localhost:2785",
                     headers={"X-API-Key": os.environ["OPENWA_KEY"]})
client.post(f"/api/sessions/{sid}/webhooks", json={
    "url": "https://example.com/wa",
    "events": ["message.received"],
    "secret": secret,
})
```

## Generating clients from OpenAPI

OpenWA serves OpenAPI 3 at `http://localhost:2785/api/docs-json`. To regenerate a fully-typed client:

```bash
npx @openapitools/openapi-generator-cli generate \
  -i http://localhost:2785/api/docs-json \
  -g typescript-fetch \
  -o ./generated/openwa-client \
  --additional-properties=supportsES6=true,typescriptThreePlus=true
```

For Python:

```bash
npx @openapitools/openapi-generator-cli generate \
  -i http://localhost:2785/api/docs-json \
  -g python \
  -o ./generated/openwa_client \
  --additional-properties=packageName=openwa_client
```

The `@openwa/sdk` package itself is intended to be regenerated from this spec — the hand-written surface is a stopgap.

## Real-time via socket.io-client

The first-party SDKs don't bundle a WebSocket helper yet. Use `socket.io-client` directly:

```typescript
import { io } from 'socket.io-client';

const sock = io('http://localhost:2785/events', {
  auth: { apiKey: process.env.OPENWA_KEY },
});

sock.on('connect', () => {
  sock.emit('message', {
    type: 'subscribe',
    sessionId: '*',
    events: ['message.received'],
  });
});

sock.on('message', (msg) => {
  if (msg.type === 'event' && msg.event === 'message.received') {
    handleIncoming(msg.data);
  }
});
```

Full protocol: [webhooks-and-events.md](webhooks-and-events.md#websocket-events).

## n8n

`docs/22-n8n-integration.md` in the OpenWA repo covers the canonical n8n setup. Two patterns:

1. **Webhook trigger** → n8n receives `message.received` over HTTP. Configure an HTTP node downstream that calls `POST /api/sessions/:id/messages/send-text` (header `X-API-Key`) to reply.
2. **Polling** via `GET /api/sessions/:sessionId/messages?chatId=…` when the network can't accept inbound webhooks.

The Webhook Test endpoint (`POST /api/sessions/:sessionId/webhooks/:id/test`) is handy to fire a synthetic payload at the n8n test URL during workflow development.
