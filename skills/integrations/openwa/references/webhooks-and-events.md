# Webhooks & real-time events

OpenWA emits the same event taxonomy through two transports: HTTP webhooks (one POST per event, signed) and Socket.IO on the `/events` namespace (a subscription protocol over a persistent connection).

## Contents

- [Event taxonomy](#event-taxonomy)
- [Webhook entity](#webhook-entity)
- [HTTP delivery headers](#http-delivery-headers)
- [HMAC signing](#hmac-signing)
- [Retries & idempotency](#retries--idempotency)
- [Queue vs sync dispatch](#queue-vs-sync-dispatch)
- [Verifying a signature](#verifying-a-signature)
- [WebSocket events](#websocket-events)

## Event taxonomy

Authoritative list at `src/modules/events/dto/ws-messages.dto.ts` (`SUBSCRIBABLE_EVENTS`):

```
message.received       — incoming WA message
message.sent           — outbound message accepted by WA
message.ack            — delivery/read ack (status 1/2/3)
message.revoked        — message deleted by sender
session.status         — any status transition (CREATED → … → READY etc.)
session.qr             — new QR rendered (rotates ~20 s)
session.authenticated  — QR scanned, WA negotiating
session.disconnected   — engine disconnected
group.join             — participant added
group.leave            — participant removed
group.update           — subject/description/picture change
```

Plus the literal `'*'` for "all events". Webhook `events: ['*']` is supported; WebSocket subscribe with `events: ['*']` likewise.

## Webhook entity

`src/modules/webhook/entities/webhook.entity.ts`:

```typescript
{
  id: UUID,
  sessionId: UUID,
  url: string,
  events: string[],            // SubscribableEvent[]
  secret: string | null,       // HMAC secret (optional)
  headers: Record<string,string> | null,  // additional headers
  active: boolean,
  retryCount: number,          // last attempt count (informational)
  lastTriggeredAt: Date | null,
  createdAt, updatedAt
}
```

Webhook scope is per-session. To deliver one event to N URLs, create N webhook rows for that session.

## HTTP delivery headers

Verified from `src/modules/webhook/webhook.service.ts:124-132` (test send), `:201-213` (real send), `:310-314` (retry), and `src/modules/queue/processors/webhook.processor.ts:47`:

| Header | Source | Notes |
|---|---|---|
| `Content-Type` | always `application/json` | |
| `X-OpenWA-Event` | event name | e.g. `message.received` |
| `X-OpenWA-Delivery-Id` | per-dispatch UUID | |
| `X-OpenWA-Idempotency-Key` | stable per (event, subject) | dedupe key for consumers |
| `X-OpenWA-Retry-Count` | `0` first, then `attemptsMade` | |
| `X-OpenWA-Signature` | `sha256=<hex>` | only when `webhook.secret` set |
| Any keys from `webhook.headers` | per-webhook custom headers | |

Body is the raw JSON event payload — shape depends on the event type. For `message.received`:

```json
{
  "event": "message.received",
  "sessionId": "…",
  "timestamp": 1737054321000,
  "data": {
    "messageId": "false_628…@c.us_3EB0…",
    "chatId": "628123456789@c.us",
    "from": "628123456789@c.us",
    "fromMe": false,
    "type": "chat",
    "body": "hello",
    "hasMedia": false,
    "timestamp": 1737054321
  }
}
```

(Verify exact shape per event in `src/modules/webhook/dto/` and the engine adapter mapping.)

## HMAC signing

`src/modules/webhook/webhook.service.ts:generateSignature()`:

```typescript
crypto.createHmac('sha256', secret).update(body).digest('hex')
// header value:
'X-OpenWA-Signature': `sha256=${hex}`
```

The HMAC input is the **raw JSON string body**, not the parsed object. Consumers must verify against the unparsed request body.

## Retries & idempotency

With `QUEUE_ENABLED=true` (Redis + BullMQ):

- `WEBHOOK_MAX_RETRIES=3` total attempts.
- BullMQ backoff base: `WEBHOOK_RETRY_DELAY=5000` ms.
- Timeout per attempt: `WEBHOOK_TIMEOUT=10000` ms.
- `X-OpenWA-Retry-Count` increments per attempt (starting `0`).
- Job lives in `webhook-delivery` queue; failures land in BullMQ's failed jobs and can be re-driven.

With `QUEUE_ENABLED=false`:

- One attempt, no retry. Failures are logged and dropped.

`X-OpenWA-Idempotency-Key` is **stable across retries of the same event** (so consumers can dedupe), but **shared keys across the lifecycle** (e.g. a `message.received` event has a key derived from `(event, messageId)`). Treat the key as the dedup key in the consumer's storage.

## Queue vs sync dispatch

```
[Engine event]
   ↓
WebhookService.dispatch(event, sessionId, payload)
   ↓
For each active webhook matching event in events[] (or '*'):
   ↓
   if queueEnabled:
      queue.add('webhook-delivery', WebhookJobData)
   else:
      await this.send(...)   ← single-shot, no retry
```

Production deployments without `QUEUE_ENABLED=true` will silently drop webhooks when the receiver is briefly unavailable.

## Verifying a signature

Node.js (express raw body):

```javascript
import crypto from 'node:crypto';

app.post('/openwa-webhook', express.raw({ type: 'application/json' }), (req, res) => {
  const expected = 'sha256=' +
    crypto.createHmac('sha256', SECRET).update(req.body).digest('hex');
  const got = req.headers['x-openwa-signature'];
  if (!got || !crypto.timingSafeEqual(Buffer.from(got), Buffer.from(expected))) {
    return res.status(401).end();
  }
  const event = JSON.parse(req.body.toString());
  // dedupe on req.headers['x-openwa-idempotency-key']
  res.status(200).end();
});
```

Python (FastAPI):

```python
import hmac, hashlib
from fastapi import FastAPI, Request, HTTPException

app = FastAPI()

@app.post("/openwa-webhook")
async def handle(req: Request):
    body = await req.body()
    expected = "sha256=" + hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, req.headers.get("x-openwa-signature", "")):
        raise HTTPException(401)
    event = json.loads(body)
    # dedupe on req.headers["x-openwa-idempotency-key"]
```

## WebSocket events

Same taxonomy, delivered live over Socket.IO on the `/events` namespace.

### Wire protocol

The protocol is **not** stock Socket.IO emit-style. Clients send a JSON envelope under the generic `'message'` event and receive a JSON envelope back. From `src/modules/events/dto/ws-messages.dto.ts`:

**Client → server**:

```typescript
type WSClientMessage =
  | { type: 'subscribe';   sessionId: string; events: string[]; requestId?: string }
  | { type: 'unsubscribe'; sessionId: string;                   requestId?: string }
  | { type: 'ping';                                              requestId?: string }
```

`sessionId` may be `'*'` for "all sessions". `events` may be `['*']`.

**Server → client**:

```typescript
type WSServerMessage =
  | { type: 'subscribed';   sessionId: string; events: string[]; requestId?: string; timestamp: string }
  | { type: 'unsubscribed'; sessionId: string;                   requestId?: string; timestamp: string }
  | { type: 'event';        sessionId: string; event: string;    data: unknown;       timestamp: string }
  | { type: 'error';        message: string;                     requestId?: string;  timestamp: string }
  | { type: 'pong';         timestamp: string;                   requestId?: string }
```

### Authentication

The gateway expects the API key either as a `Socket.IO auth` field or as a query/header. Easiest:

```javascript
import { io } from 'socket.io-client';
const sock = io('http://localhost:2785/events', {
  auth: { apiKey: process.env.OPENWA_KEY },
  // or transports:['websocket'], extraHeaders:{ 'X-API-Key': ... }
});
```

Bad/missing keys are rejected at handshake time.

### Subscribing

```javascript
sock.on('connect', () => {
  sock.emit('message', {
    type: 'subscribe',
    sessionId: '*',
    events: ['message.received', 'session.status'],
    requestId: 'req-1',
  });
});

sock.on('message', (msg) => {
  if (msg.type === 'event') {
    console.log(msg.event, msg.sessionId, msg.data);
  }
});

// keep-alive
setInterval(() => sock.emit('message', { type: 'ping' }), 30_000);
```

### Room layout

Internally the gateway joins each subscribed socket to rooms `session:<sessionId>:<event>` (or `session:*:<event>` / `session:<id>:*`). Broadcasts target the union of matching rooms. This is implementation detail — clients shouldn't depend on the room names; just use `subscribe`.
