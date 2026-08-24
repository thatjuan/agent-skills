# AgentMail events: webhooks and WebSockets

Two push transports, plus polling. Choose by whether a public URL exists.

| Transport | Needs | Best for |
|---|---|---|
| Polling | nothing | Local work, tests, CI. The default. |
| WebSocket | an outbound connection | A long-lived local process wanting sub-second delivery behind a NAT. |
| Webhook | a public HTTPS endpoint | Deployed services, and building a handler as the actual task. |

## Event types

| Event | Payload |
|---|---|
| `message.received` | Full `thread` and `message`, bodies included. |
| `message.sent` | Metadata. |
| `message.delivered` | Metadata. |
| `message.bounced` | Metadata. The address is now permanently suppressed. |
| `message.complained` | Metadata. Recipient marked it spam. |
| `message.rejected` | Metadata. Refused before sending. |
| `message.opened` | Metadata. Needs `track_opens` plus a tracking-enabled custom domain. |
| `domain.verified` | Domain record. |

`message.received` is the only event carrying bodies. Any handler for the others that needs content has to fetch the message.

The label-scoped variants `message.received.spam`, `message.received.blocked`, and `message.received.unauthenticated` require the matching `label_*_read` permission on the key that creates the subscription.

## Webhooks

```bash
curl -s -X POST https://api.agentmail.to/v0/webhooks \
  -H "Authorization: Bearer $AGENTMAIL_API_KEY" -H "Content-Type: application/json" \
  -d '{"url":"https://example.com/webhooks/agentmail",
       "event_types":["message.received"],
       "client_id":"my-service-webhook"}'
```

`client_id` makes it idempotent, so a redeploy reuses the subscription instead of stacking duplicates that each fire the handler.

Signatures are Svix-style HMAC. Verify before trusting a payload, using the secret returned when the webhook is created.

Return `200` immediately and do the work off the request path. A handler that replies to the mail inline holds the connection open long enough to be retried, which delivers the same event twice:

```python
from threading import Thread
from flask import Flask, request, Response
from agentmail import AgentMail

app = Flask(__name__)
client = AgentMail()

@app.post("/webhooks")
def webhook():
    Thread(target=handle, args=(request.json,)).start()
    return Response(status=200)

def handle(payload):
    if payload["event_type"] != "message.received":
        return
    msg = payload["message"]
    client.inboxes.messages.reply(
        inbox_id=msg["inbox_id"],
        message_id=msg["message_id"],
        text="Got it, working on this now.",
    )
```

For a local handler, tunnel with ngrok and register the tunnel URL. Recreate the webhook whenever the tunnel URL changes, using the same `client_id` so the old one is replaced rather than left firing into a dead address.

## WebSockets

No public URL, no tunnel, and it survives NAT because the connection is outbound.

```python
import asyncio
from agentmail import AsyncAgentMail, Subscribe, MessageReceivedEvent

client = AsyncAgentMail()

async def main():
    async with client.websockets.connect() as socket:
        await socket.send_subscribe(Subscribe(inbox_ids=["agent@agentmail.to"]))
        async for event in socket:
            if isinstance(event, MessageReceivedEvent):
                print(event.message.subject, event.message.extracted_text)

asyncio.run(main())
```

```typescript
const socket = await client.websockets.connect();
socket.on("open", () => socket.sendSubscribe({ type: "subscribe", inboxIds: ["agent@agentmail.to"] }));
socket.on("message", (event) => {
  if (event.type === "message_received") console.log(event.message.subject);
});
```

Reconnect on close and resubscribe; a dropped socket silently stops delivering.

## Polling

For a one-shot wait, `scripts/wait-for-email.sh` in this skill already does it. Rolling your own is `GET /v0/inboxes/{inbox_id}/messages` with `after` pinned to the moment the wait started, on a 3 to 10 second interval with a hard timeout. Pin `after` rather than tracking seen ids: it is one parameter, and it cannot match a leftover message from a previous run.
