# AgentMail REST and SDK reference

Base URL `https://api.agentmail.to` (EU region: `https://api.agentmail.eu`). Every request carries `Authorization: Bearer $AGENTMAIL_API_KEY`. `{inbox_id}` is the inbox's email address, such as `agent@agentmail.to`.

## Resource model

```
Organization
└── Pod (optional, multi-tenant isolation)
    └── Inbox (agent@agentmail.to)
        └── Thread (conversation, created automatically)
            └── Message
                └── Attachment
```

## Endpoints

### Inboxes

| Method | Path | Notes |
|---|---|---|
| `GET` | `/v0/inboxes` | Needs `inbox_read`. |
| `POST` | `/v0/inboxes` | Body: `username?`, `domain?`, `display_name?`, `client_id?`. |
| `GET` | `/v0/inboxes/{inbox_id}` | |
| `DELETE` | `/v0/inboxes/{inbox_id}` | |

Omitting `username` gets a generated address on `agentmail.to`, which needs no domain verification. `client_id` makes the create idempotent: the same `client_id` returns the existing inbox rather than a second one.

### Messages

| Method | Path | Notes |
|---|---|---|
| `GET` | `/v0/inboxes/{inbox_id}/messages` | Newest first. |
| `GET` | `/v0/inboxes/{inbox_id}/messages/{message_id}` | Full body and attachments. |
| `GET` | `/v0/inboxes/{inbox_id}/messages/search?q=` | Relevance-ranked full text. `limit` caps at 100. |
| `POST` | `/v0/inboxes/{inbox_id}/messages/send` | |
| `POST` | `/v0/inboxes/{inbox_id}/messages/{message_id}/reply` | Add `"reply_all": true` to include every original recipient. |
| `PATCH` | `/v0/inboxes/{inbox_id}/messages/{message_id}` | `add_labels`, `remove_labels`. |
| `DELETE` | `/v0/inboxes/{inbox_id}/messages/{message_id}` | |

List query parameters: `limit`, `page_token`, `labels`, `before`, `after`, `ascending`, `from`, `to`, `subject`, and the `include_spam` / `include_blocked` / `include_unauthenticated` / `include_trash` switches. `from`, `to`, and `subject` are repeatable substring filters and every value must match. Any filtered request is served by search, which caps `limit` at 100.

Send and reply bodies accept `to`, `cc`, `bcc`, `reply_to` (each a string or a list), `subject`, `text`, `html`, `labels`, `headers`, `attachments`, and `track_opens`. Both return `{"message_id", "thread_id"}`.

A listed message carries `inbox_id`, `thread_id`, `message_id`, `labels`, `timestamp`, `from`, `to`, `cc`, `bcc`, `subject`, `preview`, `size`, and attachment metadata. Fetching one message adds the bodies: `text`, `html`, `extracted_text`, `extracted_html`. The extracted pair strips the quoted reply trail, so parse those and fall back to `text`.

### Threads

| Method | Path | Notes |
|---|---|---|
| `GET` | `/v0/threads` | Org-wide across every inbox the key can see. |
| `GET` | `/v0/threads/{thread_id}` | |
| `GET` | `/v0/inboxes/{inbox_id}/threads` | |
| `GET` | `/v0/inboxes/{inbox_id}/threads/search?q=` | |

Threads hold no permissions of their own: reads need `message_read`, label updates need `message_update`, and deleting a thread needs `message_delete`. Filters mirror the message list, with `senders` and `recipients` in place of `from` and `to`.

`GET /v0/threads` is the one listing an inbox-scoped key can reach without `inbox_read`, which makes it the fallback for discovering an inbox address.

### Drafts, webhooks, domains, pods, lists

| Resource | Path | Permission prefix |
|---|---|---|
| Drafts | `/v0/inboxes/{inbox_id}/drafts` | `draft_*`, plus `draft_send` |
| Webhooks | `/v0/webhooks` | `webhook_*` |
| Domains | `/v0/domains` | `domain_*` |
| Pods | `/v0/pods` | `pod_*` |
| Lists | `/v0/lists` | `list_entry_*` |
| API keys | `/v0/api-keys` | `api_key_*` |

Drafts back a human-in-the-loop flow: create, let a person read it, then send. A pod isolates a tenant, stage, or customer; an inbox cannot move between pods, and a pod holding resources cannot be deleted.

### Attachments

Up to 30MB, any MIME type. Each attachment is `{filename, content_type, content_disposition?, content_id?, content}` with `content` base64-encoded, or `{url}` to have AgentMail fetch it. Download a received one from `/v0/inboxes/{inbox_id}/messages/{message_id}/attachments/{attachment_id}`.

## Permissions

A key with no `permissions` object has full access inside its scope. Supplying one switches the key to whitelist mode, where anything not set to `true` is denied. Effective access is the intersection of scope and whitelist, so an inbox-scoped key never gains `inbox_create` however the whitelist reads. A key cannot mint a child with permissions it lacks, so widening happens at the console.

Permission names: `inbox_*`, `message_read|send|update|delete`, `draft_*`, `webhook_*`, `domain_*`, `pod_*`, `list_entry_*`, `metrics_read`, `api_key_*`, and the label-visibility set `label_spam_read`, `label_blocked_read`, `label_unauthenticated_read`, `label_trash_read`. A denied label permission hides those items from every listing and returns not-found on direct access, and it also blocks subscribing to the matching `message.received.*` event.

## Errors

| Status | Meaning |
|---|---|
| `400` | Validation. Check parameter names and shapes. |
| `403` | Wrong key, out-of-scope resource, missing permission, or a suppressed recipient. The `fix` field names the exact permission. |
| `404` | Unknown id, or an id the credential's scope hides. |
| `429` | Rate limited. Honour `Retry-After`, then back off exponentially. |

Every error is JSON with `name`, `code`, `message`, `fix`, and `docs`. Read `fix` before changing code; it usually says the key is wrong rather than the request.

## SDKs

```bash
npm install agentmail     # TypeScript/Node, client: AgentMailClient
pip install agentmail     # Python, client: AgentMail / AsyncAgentMail
```

Both read `AGENTMAIL_API_KEY` from the environment when constructed with no argument. Method names mirror the paths: `client.inboxes.create`, `client.inboxes.messages.send(inboxId, {...})`, `client.inboxes.messages.reply(inboxId, messageId, {...})`, `client.inboxes.messages.list(inboxId, {...})`, `client.threads.list()`. Python is snake_case (`inbox_id`, `client_id`, `add_labels`), TypeScript is camelCase (`inboxId`, `clientId`, `addLabels`). Both throw on any 4xx or 5xx; the detail is at `error.body.message` in TypeScript and `e.body.message` in Python.

`agentmail-toolkit` (`pip install agentmail-toolkit`) wraps the client as tool definitions for OpenAI Agents and LangChain, via `AgentMailToolkit(client).get_tools()`.

## CLI

`npx agentmail-cli@latest` exposes the same surface as `agentmail <resource> <action>`, reading `AGENTMAIL_API_KEY` from the environment:

```bash
npx agentmail-cli@latest --format json inboxes list
npx agentmail-cli@latest inboxes:messages send --inbox-id agent@agentmail.to \
  --to someone@example.com --subject "Hello" --text "Body"
```

Useful when a shell already has Node and the alternative is hand-rolling several curl calls. For one or two calls, curl is fewer moving parts.

## MCP server

A first-party hosted server at `https://mcp.agentmail.to/mcp` (Streamable HTTP) exposes inbox, message, thread, draft, and attachment tools.

```bash
claude mcp add --transport http agentmail https://mcp.agentmail.to/mcp
```

OAuth-capable clients (Claude Code, Claude Desktop, Claude.ai) sign in interactively and need no key. Key-based clients send the header `x-api-key: $AGENTMAIL_API_KEY`. It is **not** installed on this machine by default, since curl covers the same ground without adding tool definitions to every session. Add it when a task involves enough back-and-forth email that native tools beat shell calls.

## IMAP and SMTP

| Protocol | Host | Port | Credentials |
|---|---|---|---|
| IMAP | `imap.agentmail.to` | 993 (SSL) | inbox address + API key |
| SMTP | `smtp.agentmail.to` | 465 (SSL) | inbox address + API key |

For pointing an existing mail client or a library that only speaks these protocols at an agent inbox.

## Plans

Free is 3 inboxes, 3,000 messages a month, 3GB. Developer at $20/month is 10 inboxes, 10,000 messages, 10 custom domains. Inboxes run out long before messages do, so reuse them by `client_id`.
