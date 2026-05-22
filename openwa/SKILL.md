---
name: openwa
description: OpenWA self-hosted WhatsApp API Gateway expertise — deployment, sessions, REST API, webhooks, real-time events, SDKs, plugins. Use when working in the OpenWA repo or a gateway based on it; when code hits port `2785`, builds the `openwa-api` Docker service, or fronts the dashboard on `2886`; when scripts send `X-API-Key: owa_k1_…` headers; when configuring `whatsapp-web.js` sessions via `POST /api/sessions/:id/start`, fetching QR via `/api/sessions/:id/qr`, or sending via `POST /api/sessions/:sessionId/messages/send-text`; when subscribing to `message.received`/`message.sent`/`message.ack`/`session.status` webhooks; when handling `X-OpenWA-Event`/`X-OpenWA-Idempotency-Key`/`X-OpenWA-Signature` headers; when using the `/events` Socket.IO namespace, `@openwa/sdk` (JS) or `openwa` (Python); when toggling `DATABASE_TYPE`, `QUEUE_ENABLED`, `REDIS_ENABLED`, `STORAGE_TYPE`, `PUPPETEER_HEADLESS`; when extending via plugin hooks (`message:sending`, `message:sent`) or integrating into n8n.
---

# OpenWA

OpenWA is a self-hosted, open-source WhatsApp API Gateway (MIT, NestJS 11 / TypeScript / Node 22). It wraps `whatsapp-web.js` (Puppeteer + Chromium) behind a REST API on port `2785`, ships a React dashboard on `2886`, and supports multi-session WhatsApp automation with webhooks, Socket.IO real-time events, pluggable storage/cache/database, and a plugin hook system.

## Product surface

| Component | Port | Role |
|---|---|---|
| `openwa-api` (NestJS) | `2785` | REST + WebSocket + webhook dispatcher |
| `dashboard` (React 19 + Vite) | `2886` | Session/API-key/webhook UI |
| Swagger UI | `2785` | `/api/docs` |
| Traefik (optional) | `80`, `8080` | Reverse proxy + dashboard (profile `with-proxy`) |
| PostgreSQL (optional) | `5432` | Profile `postgres` |
| Redis (optional) | `6379` | Profile `redis`, gates BullMQ queue |
| MinIO (optional) | `9000`, `9001` | Profile `minio` (S3-compatible storage) |

Global API prefix is `/api` (`src/main.ts:128` `app.setGlobalPrefix('api')`). All paths below are relative to `<baseUrl>/api`.

## Tech stack — verified

| Layer | Tech | Evidence |
|---|---|---|
| Framework | NestJS 11.x | `package.json` |
| WA engine | `whatsapp-web.js` 1.26.1 (Puppeteer + Chromium) | `package.json`, `src/engine/engine.factory.ts` |
| Main DB | SQLite (always — stores API keys, audit log) | `src/app.module.ts` |
| Data DB | SQLite or PostgreSQL (sessions, messages, webhooks) | `src/app.module.ts` |
| ORM | TypeORM 0.3.x | `package.json` |
| Queue | BullMQ 5.x (gated by `QUEUE_ENABLED`) | `src/app.module.ts:31` |
| Cache | Redis (optional, gated by `REDIS_ENABLED`) | `src/common/cache/` |
| Storage | Local or S3/MinIO | `src/common/storage/` |
| Real-time | Socket.IO 4.8 on namespace `/events` | `src/modules/events/events.gateway.ts` |
| Validation | `class-validator`, `class-transformer` | `package.json` |
| SDK | `@openwa/sdk` (JS/TS) + `openwa` (Python) | `sdk/javascript/`, `sdk/python/` |

## Repository layout

```
src/
  main.ts                    # Boot + .env precedence + first-run API key
  app.module.ts              # Composition; conditional QueueModule
  config/configuration.ts    # Env → config object
  core/{hooks,plugins}/      # Plugin hook system
  engine/                    # IWhatsAppEngine interface + adapters
  modules/
    session/                 # Session CRUD + in-memory engine map
    message/                 # Send & history endpoints
    webhook/                 # Per-session webhook subscriptions
    events/                  # Socket.IO gateway (/events namespace)
    auth/                    # API-key auth + roles
    contact/ group/ label/ channel/ status/ catalog/
    queue/                   # BullMQ jobs (only if QUEUE_ENABLED)
    health/                  # /health, /health/live, /health/ready
    infra/ settings/ stats/ audit/ docker/ plugins/
dashboard/                   # React 19 + Vite SPA
sdk/{javascript,python}/     # Client libraries
traefik/{traefik.yml,dynamic.yml}
docker-compose.yml           # Profiled production stack
docker-compose.dev.yml       # SQLite + local dev quick-start
Dockerfile                   # Multi-stage Node 22-slim + Chromium
docs/                        # 22 markdown design docs
```

## Authentication — `X-API-Key`

Authentication is a hashed API key sent in the `X-API-Key` header (also accepted: `Authorization: Bearer` per `main.ts:122` CORS allow-list). Keys are stored hashed in the main (SQLite) DB and have a role: `ADMIN`, `OPERATOR`, or `VIEWER` (`src/modules/auth/entities/api-key.entity.ts`).

```bash
curl -H "X-API-Key: owa_k1_xxxxxxxx..." http://localhost:2785/api/sessions
```

- **Key format**: `owa_k1_<32 bytes hex>` (`src/modules/auth/auth.service.ts:95`)
- **First-run bootstrap**: if no API keys exist, OpenWA creates one and writes it to `data/.api-key`, then prints it in the startup banner. In dev (`NODE_ENV=development`) the bootstrap key is the literal string `dev-admin-key`.
- **Role gating**: write endpoints carry `@RequireRole(ApiKeyRole.OPERATOR)`; reads are largely public-by-key. ADMIN is required for API-key CRUD.
- **Optional scoping per key**: IP allow-list (`allowedIps`) and session allow-list (`allowedSessions`).

See [authentication & API-key lifecycle](references/operation.md#authentication) for key creation/revocation flows.

## Sessions — multi-account WhatsApp

Each WhatsApp account = one persisted `Session` row + one in-memory engine (`IWhatsAppEngine`) keyed by session id (`src/modules/session/session.service.ts`). Sessions go through:

```
CREATED → INITIALIZING → QR_READY → AUTHENTICATING → READY
                                  ↘ FAILED
   any → DISCONNECTED (also forced on every API restart)
```

Minimum workflow to bring a session live:

```bash
# 1. Create
curl -X POST http://localhost:2785/api/sessions \
  -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"name":"bot-1"}'

# 2. Start (initialises Chromium + WA engine)
curl -X POST http://localhost:2785/api/sessions/$ID/start -H "X-API-Key: $KEY"

# 3. Fetch QR — returns SVG data while status = QR_READY
curl http://localhost:2785/api/sessions/$ID/qr -H "X-API-Key: $KEY"
# … scan with WhatsApp mobile …

# 4. Poll status (or subscribe via /events) until status = READY
curl http://localhost:2785/api/sessions/$ID -H "X-API-Key: $KEY"
```

Chat ids follow WhatsApp Web conventions: `<phone>@c.us` for direct, `<id>@g.us` for groups, `<id>@newsletter` for channels. Invalid format = silent send failure.

Full lifecycle, in-memory engine map, proxy options, and reset-on-restart behaviour: [operation.md](references/operation.md).

## REST API — controller catalog

All routes are mounted under `/api`. Roles in parentheses are required when stricter than the default `VIEWER`-or-higher.

| Domain | Routes | File |
|---|---|---|
| Sessions | `POST /sessions` (OPERATOR), `GET /sessions`, `GET /sessions/:id`, `DELETE /sessions/:id` (OPERATOR), `POST /sessions/:id/start` (OPERATOR), `POST /sessions/:id/stop` (OPERATOR), `GET /sessions/:id/qr`, `GET /sessions/:id/groups`, `GET /sessions/stats/overview` | `session.controller.ts` |
| Messages | `GET /sessions/:sessionId/messages`, `POST /sessions/:sessionId/messages/send-text`, `…/send-image`, `…/send-video`, `…/send-audio`, `…/send-document`, `…/send-location`, `…/send-contact`, `…/send-sticker`, `…/reply`, `…/forward`, `…/react`, `GET …/:chatId/:messageId/reactions`, `POST …/delete`, `POST …/send-bulk`, `GET …/batch/:batchId`, `POST …/batch/:batchId/cancel` | `message.controller.ts` |
| Webhooks | `POST/GET/GET :id/PUT :id/DELETE :id` under `/sessions/:sessionId/webhooks`, plus `POST :id/test` | `webhook.controller.ts` |
| API keys | `POST /auth/api-keys` (ADMIN), `GET`, `GET :id`, `PUT :id`, `DELETE :id`, `POST :id/revoke` | `auth.controller.ts` |
| Auth probe | `GET /auth/validate` (header `X-API-Key`) | `auth-validate.controller.ts` |
| Health | `GET /health`, `GET /health/live`, `GET /health/ready` (public; K8s-shaped) | `health.controller.ts` |
| Contact/Group/Label/Channel/Status/Catalog | Per-module controllers under `/sessions/:sessionId/...` | `modules/<name>/` |
| Infra | Settings, stats, export/import for migration | `modules/infra/` |

Authoritative shapes are the controller files plus the auto-published OpenAPI at `http://localhost:2785/api/docs`. Full route table with role/auth notes: [rest-api.md](references/rest-api.md).

## Webhooks — per-session, signed, retried

Webhooks are created **per session** (`POST /api/sessions/:sessionId/webhooks`) with a URL, an `events` array, and optional `secret`/custom `headers`. Delivery is via BullMQ when `QUEUE_ENABLED=true` (with retries) and **synchronous** otherwise.

Headers emitted on every delivery:

| Header | Meaning |
|---|---|
| `X-OpenWA-Event` | Event name (e.g. `message.received`) |
| `X-OpenWA-Delivery-Id` | Unique per delivery attempt's parent dispatch |
| `X-OpenWA-Idempotency-Key` | Stable per (event × subject) — dedupe key for consumers |
| `X-OpenWA-Retry-Count` | `0` on first attempt, then `attemptsMade` |
| `X-OpenWA-Signature` | `sha256=<hex hmac>` of the JSON body using `webhook.secret` (omitted if no secret) |

Defaults: `WEBHOOK_TIMEOUT=10000` ms, `WEBHOOK_MAX_RETRIES=3`, `WEBHOOK_RETRY_DELAY=5000` ms.

Subscribable event types (also valid on the WebSocket — `src/modules/events/dto/ws-messages.dto.ts`):

`message.received`, `message.sent`, `message.ack`, `message.revoked`, `session.status`, `session.qr`, `session.authenticated`, `session.disconnected`, `group.join`, `group.leave`, `group.update` — plus `*` for all.

Signature verification, delivery flow, queue vs sync, idempotency semantics, retry timing: [webhooks-and-events.md](references/webhooks-and-events.md).

## Real-time — Socket.IO `/events`

Same event taxonomy as webhooks, delivered over Socket.IO on the `/events` namespace. The protocol is custom JSON (not the Socket.IO event emitter): clients send `{type:'subscribe', sessionId, events, requestId?}` and receive `{type:'event', ...}` / `{type:'subscribed', ...}` / `{type:'error', ...}` / `{type:'pong'}` server-side.

```javascript
import { io } from 'socket.io-client';
const sock = io('http://localhost:2785/events', { auth: { apiKey: KEY } });
sock.emit('message', { type: 'subscribe', sessionId: '*', events: ['message.received'] });
sock.on('message', (msg) => { /* handle msg.type === 'event' */ });
```

Wire format, auth modes, room layout (`session:<id>:<event>`), and ping/pong: [webhooks-and-events.md#websocket](references/webhooks-and-events.md#websocket-events).

## Deployment

Three documented paths:

| Path | Command |
|---|---|
| Local dev (SQLite, no Redis/queue, all in one) | `docker compose -f docker-compose.dev.yml up -d` |
| Production basic | `docker compose up -d` |
| Production full stack (Postgres + Redis + MinIO + Traefik + Dashboard) | `docker compose --profile full up -d` |

The image is multi-stage `node:22-slim` with Chromium baked in and `PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium`. Container health check is `node -e "require('http').get('http://localhost:2785/api/health', ...)"` every 30 s.

Compose profiles (`postgres`, `redis`, `minio`, `with-dashboard`, `with-proxy`, `full`), volume layout (`openwa-data:/app/data`), Docker socket mount (`/var/run/docker.sock:ro` — used by `modules/docker` for orchestration), Traefik static/dynamic config, K8s health probes: [deployment.md](references/deployment.md).

## Configuration — env-driven, three-layer precedence

Bootstrapping (`src/main.ts:11-65`) loads dotenv with `override: false` so the **highest priority wins, and it's process env**:

```
process.env  >  ./.env  >  ./data/.env.generated
```

`.env.generated` is the file the dashboard writes; it is the **lowest** priority, not the highest. A common pitfall is expecting dashboard saves to override Docker `environment:` blocks — they don't.

If no `data/.env.generated` exists on first boot, OpenWA writes one with SQLite, local storage, queue disabled, and prints a welcome banner with the API key.

Two TypeORM databases are wired in `app.module.ts`:

- **`main` connection** — always SQLite. Stores API keys, audit log. Stays node-local (don't try to migrate it).
- **`data` connection** — SQLite or PostgreSQL. Stores sessions, messages, webhooks. Synchronize defaults `true` for SQLite, `false` for Postgres (then `npm run migration:run:prod`).

Full env-var reference, `.env.minimal`, dual-DB diagram, and `QUEUE_ENABLED` gating: [configuration.md](references/configuration.md).

## SDKs

```typescript
import { OpenWAClient } from '@openwa/sdk';
const client = new OpenWAClient({ baseUrl: 'http://localhost:2785', apiKey: KEY });
await client.sessions.create({ name: 'bot-1' });
await client.sessions.start(id);
await client.messages.sendText(id, { chatId: '628123456789@c.us', text: 'hi' });
```

The published `@openwa/sdk` ships a minimal hand-written surface (`sdk/javascript/src/index.ts`) and is intended to be regenerated from the OpenAPI spec — for endpoints it doesn't yet wrap, call `client.request('POST', '/api/...', body)` or use `fetch` with `X-API-Key`. A Python SDK lives at `sdk/python/openwa/`.

SDK install, typed wrappers, generation flow, and Python equivalents: [sdk.md](references/sdk.md).

## Architecture & extensibility

OpenWA's pluggability is enforced through interface boundaries, not feature flags alone:

- **`IWhatsAppEngine`** (`src/engine/interfaces/`) — abstracts `whatsapp-web.js`; alternative engines (Baileys, etc.) can be dropped behind it via `engine.factory.ts`. Selected by `ENGINE_TYPE`.
- **`StorageService`** — local-fs or S3/MinIO, swapped via `STORAGE_TYPE`.
- **`CacheService`** — in-memory or Redis, gated by `REDIS_ENABLED`.
- **Plugin hooks** — `core/hooks/` runs named hook chains. The message-send pipeline fires `message:sending` before dispatch (plugins can modify/block) and `message:sent` on success. Plugins are auto-loaded when `PLUGINS_ENABLED=true`.
- **Queue gating** — `QueueModule` is `require`d only when `QUEUE_ENABLED === 'true'` (`src/app.module.ts:31-38`). Without it, webhook retries are best-effort sync only.

Module map, hook list, plugin loader, scaling model (engines pinned to nodes; API keys stay local; data DB can be shared): [architecture.md](references/architecture.md).

## Gotchas

A handful of behaviours that bite people who read the docs but skip the code:

1. `.env.generated` is the **lowest** precedence, not the highest.
2. Every API restart force-resets all `READY/INITIALIZING/QR_READY/AUTHENTICATING` sessions to `DISCONNECTED` (engines are in-memory; restart loses them).
3. `QUEUE_ENABLED=false` (the default) means **webhooks have no retry** — synchronous best-effort dispatch.
4. `synchronize: true` is the SQLite default and is **dangerous in production**; flip to migrations for Postgres.
5. API keys live in the SQLite `main` DB. Switching the `data` DB to Postgres doesn't move them.
6. `phone` and `pushName` are `null` until the session reaches `READY`.
7. Chat-id format must be `<phone>@c.us` / `<id>@g.us` — wrong format = silent failure.
8. Chromium is mandatory; the Docker image hard-codes `PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium`.

Full annotated list with file:line references: [gotchas.md](references/gotchas.md).

## Reference index

| Reference | What's inside |
|---|---|
| [deployment.md](references/deployment.md) | Dockerfile stages, compose profiles, Traefik, K8s probes, volumes |
| [configuration.md](references/configuration.md) | Env-var reference, precedence, dual-DB layout, queue gating |
| [operation.md](references/operation.md) | Session lifecycle, QR auth, API-key bootstrap & lifecycle, dashboard |
| [rest-api.md](references/rest-api.md) | Full controller→route catalog, role decorators, request/response shapes |
| [webhooks-and-events.md](references/webhooks-and-events.md) | Webhook headers, HMAC, retries, idempotency, Socket.IO `/events` wire format |
| [sdk.md](references/sdk.md) | JS/TS and Python client usage, raw `fetch` fallback, regeneration notes |
| [architecture.md](references/architecture.md) | Module map, engine/storage/cache pluggability, plugin hooks, scaling |
| [gotchas.md](references/gotchas.md) | Non-obvious behaviours verified against the source |
