# openwa

> Expert on the OpenWA self-hosted WhatsApp API Gateway — deployment, sessions, REST API, webhooks, real-time events, SDKs, plugins, and the non-obvious behaviours you only learn by reading the source.

## What it does

`openwa` makes Claude fluent in **OpenWA** — the open-source NestJS + `whatsapp-web.js` WhatsApp gateway that runs on port 2785 with a React dashboard on 2886. The skill covers:

- **Deployment** — Dockerfile stages, compose profiles (`postgres`, `redis`, `minio`, `with-dashboard`, `with-proxy`, `full`), Traefik, K8s probes.
- **Operation** — session lifecycle (`CREATED → QR_READY → AUTHENTICATING → READY`), QR auth flow, API-key bootstrap and roles (`VIEWER`/`OPERATOR`/`ADMIN`), dashboard.
- **REST API** — the full controller→route catalog, verified against `src/modules/*/*.controller.ts` decorators, with role-gating notes and request/response shapes.
- **Webhooks & events** — `X-OpenWA-Event` / `X-OpenWA-Signature` / `X-OpenWA-Idempotency-Key` headers, HMAC SHA-256 verification, BullMQ retries (gated by `QUEUE_ENABLED`), and the Socket.IO `/events` subscription protocol.
- **SDKs** — `@openwa/sdk` (JS/TS) and the `openwa` Python package, plus OpenAPI regeneration from `/api/docs-json`.
- **Architecture** — `IWhatsAppEngine` adapter boundary, plugin hooks (`message:sending`, `message:sent`), dual-DB layout (`main` SQLite for API keys, `data` SQLite/Postgres for everything else), scaling constraints.
- **Gotchas** — the surprises: `.env.generated` is the *lowest* precedence, restarts force-disconnect every session, `QUEUE_ENABLED=false` means zero webhook retries, `synchronize: true` on Postgres is dangerous, dev mode bootstraps the literal key `dev-admin-key`.

The skill is grounded in primary-source code reads (`src/`, `docker-compose*.yml`, `Dockerfile`, `sdk/`, `dashboard/`) — not just the `docs/` directory — so file:line citations and the gotchas list are accurate against the running implementation.

## When to use it

- *"Deploy OpenWA with PostgreSQL and Redis behind Traefik."*
- *"Set up a webhook that fires on `message.received` and verify the signature in Node."*
- *"How do I scale OpenWA to 50 WhatsApp accounts?"*
- *"Write a TypeScript client that subscribes to all `message.*` events for all sessions."*
- *"Add a plugin that blocks outgoing messages containing a banned word."*
- *"Why does OpenWA disconnect every session when I restart the container?"*

**Not the right skill if** the task is generic WhatsApp Business Cloud API work (that's Meta's official API, totally different surface), or `whatsapp-web.js`-as-a-library work *outside* OpenWA (use the upstream docs directly — OpenWA wraps it, doesn't replace it).

## Example walkthrough

**Prompt**

> Set up OpenWA with Postgres + Redis + S3 (MinIO) behind Traefik, then write a TypeScript service that listens for `message.received` over WebSocket and replies "got it" via REST.

**What the skill does**

1. **Stack up** — recommends `docker compose --profile full up -d`, points at the relevant volumes (`openwa-data`, `postgres-data`, etc.), reminds the user to set `QUEUE_ENABLED=true` and `DATABASE_SYNCHRONIZE=false` for the Postgres production deploy.
2. **API key** — surfaces that the first key is printed in the API startup banner and written to `data/.api-key`; not the dashboard.
3. **Session bring-up** — `POST /api/sessions` → `POST /api/sessions/:id/start` → `GET /api/sessions/:id/qr` → poll until `READY`.
4. **Listener service** — generates a Node script using `socket.io-client` on `http://host:2785/events` with the custom JSON envelope (`{type:'subscribe', sessionId:'*', events:['message.received']}`), and a `fetch` call to `POST /api/sessions/:id/messages/send-text` with `chatId: '<from>@c.us'` for the reply.
5. **Gotcha** — flags that `chatId` must be the raw `<phone>@c.us` form (no `+`, no leading zero) or the send silently fails.

## Installation

```bash
npx skills add thatjuan/agent-skills --skill openwa
```

## Bundled resources

| File | Purpose |
|------|---------|
| `SKILL.md` | Tech stack, repo layout, auth, sessions, REST API summary, deployment paths, configuration overview, gotchas, reference index |
| `references/deployment.md` | Dockerfile stages, compose profiles, volume layout, Traefik config, K8s probes, local non-Docker dev |
| `references/configuration.md` | Full env-var reference, dotenv precedence, `.env.minimal`, dual-DB architecture, queue gating |
| `references/operation.md` | API-key lifecycle and roles, session state machine, QR auth flow, dashboard, audit log, multi-session sizing |
| `references/rest-api.md` | Verified controller→route catalog (sessions, messages, webhooks, api-keys, health, aux domains), Swagger location |
| `references/webhooks-and-events.md` | Webhook entity, headers, HMAC signing, retries/idempotency, queue vs sync, Socket.IO `/events` protocol |
| `references/sdk.md` | `@openwa/sdk` usage, Python equivalent, OpenAPI client regeneration, `socket.io-client` for real-time, n8n integration |
| `references/architecture.md` | Module map, pluggable boundaries, engine adapter interface, plugin hooks, scaling model |
| `references/gotchas.md` | 13 verified surprises with file:line citations |

## Tips

- **Always set `QUEUE_ENABLED=true` for production.** Webhook retries are off by default. The cost is one Redis instance.
- **Treat the OpenAPI spec as the source of truth.** Hit `http://localhost:2785/api/docs-json` to regenerate clients — the hand-written `@openwa/sdk` only wraps a subset.
- **Pin session ids to nodes if you scale horizontally.** No built-in coordinator; two processes touching the same session id will corrupt the Puppeteer profile.
- **Back up `data/` as a whole.** Losing the `main` SQLite means losing every API key. Losing `sessions/` means a fresh QR scan for every account.
- **Use `POST /api/sessions/:sid/webhooks/:wid/test`** during integration — it fires a synthetic payload with all the real headers (`X-OpenWA-Signature`, idempotency key, etc.) so consumers can be verified offline.
- **Watch `message.ack` events**, not the send response. The REST send returns once the message is queued to the engine; final delivery state lands on the event stream.
- **Don't expose `NODE_ENV=development` publicly** — first-boot bootstrap creates the literal key `dev-admin-key`.

## Related skills

- [`drizzle-orm`](../drizzle-orm/) — alternative TypeORM-style integrations if you're swapping out OpenWA's persistence (OpenWA itself uses TypeORM)
- [`heroui`](../heroui/) — if you're building a custom OpenWA front-end alongside or in place of the bundled React dashboard
- [`temporal`](../temporal/) — durable orchestration over OpenWA webhooks for long-running WhatsApp workflows
