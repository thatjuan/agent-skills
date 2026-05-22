# Architecture

How OpenWA composes its NestJS modules, where its pluggability lives, and how to extend it.

## Contents

- [Module map](#module-map)
- [Pluggable boundaries](#pluggable-boundaries)
- [Engine adapters](#engine-adapters)
- [Plugin hook system](#plugin-hook-system)
- [Sessions are in-memory](#sessions-are-in-memory)
- [Scaling model](#scaling-model)

## Module map

`src/app.module.ts` composes the application. Domain modules (NestJS `@Module`) — each owns a controller, service, entity, and DTOs:

```
core/
  hooks/        — named hook chains (HookService)
  plugins/      — plugin loader, runs at startup if PLUGINS_ENABLED=true
engine/
  interfaces/   — IWhatsAppEngine
  adapters/     — whatsapp-web.js adapter (others can plug in)
  engine.factory.ts  — picks adapter via ENGINE_TYPE
common/
  cache/        — CacheService (memory or Redis, gated by REDIS_ENABLED)
  storage/      — StorageService (local-fs or S3, gated by STORAGE_TYPE)
  services/     — logger, graceful shutdown
modules/
  session       — Session CRUD, engines: Map<sessionId, IWhatsAppEngine>
  message       — send & history; fires hook 'message:sending' before, 'message:sent' after
  webhook       — webhook CRUD + dispatcher; queues to BullMQ when enabled
  events        — Socket.IO gateway @WebSocketGateway('/events')
  auth          — API-key guard, role decorators, key CRUD
  queue         — BullMQ; only loaded if QUEUE_ENABLED=true (conditional require)
  health        — K8s probes
  contact / group / label / channel / status / catalog — WhatsApp object CRUD
  infra / settings / stats / audit / docker / plugins — admin surface
database/       — TypeORM migrations
```

## Pluggable boundaries

Five swap points enforced by interface, not just config:

| Boundary | Interface | Selector |
|---|---|---|
| WhatsApp engine | `IWhatsAppEngine` (`src/engine/interfaces/`) | `ENGINE_TYPE` |
| Object storage | `StorageService` (`src/common/storage/storage.service.ts`) | `STORAGE_TYPE` (`local` / `s3`) |
| Cache | `CacheService` (`src/common/cache/`) | `REDIS_ENABLED` |
| Data DB | TypeORM driver | `DATABASE_TYPE` (`sqlite` / `postgres`) |
| Queue | BullMQ | `QUEUE_ENABLED` (also requires Redis) |

The main DB (API keys, audit) is **not** pluggable — always SQLite, always node-local.

## Engine adapters

`src/engine/engine.factory.ts` picks an adapter by `ENGINE_TYPE`. Today only `whatsapp-web.js` ships. `IWhatsAppEngine` is the contract:

```typescript
interface IWhatsAppEngine {
  start(): Promise<void>;
  stop(): Promise<void>;
  getQR(): Promise<string | null>;          // SVG/base64
  sendTextMessage(chatId: string, text: string): Promise<{messageId: string}>;
  sendMediaMessage(chatId: string, media: MediaInput): Promise<…>;
  // …
  on(event: EngineEvent, handler: (payload) => void): void;
}
```

Adding a Baileys adapter: implement `IWhatsAppEngine`, register in the factory, expose a new `ENGINE_TYPE` value. Sessions remain transport-agnostic.

## Plugin hook system

`src/core/hooks/` provides a named hook chain — multiple handlers per hook, executed in registration order.

Built-in hook points (search `executeHook(` in `src/modules/`):

| Hook | When | Handler signature |
|---|---|---|
| `message:sending` | Before `sendTextMessage` (et al.) — handlers may modify payload or **block** | `(ctx: { sessionId, chatId, payload }) => Promise<void \| { block: true }>` |
| `message:sent` | After WA returns a message id | `(ctx: { sessionId, messageId, payload }) => Promise<void>` |
| `message:received` | When engine emits incoming message | `(ctx) => Promise<void>` |
| `session:status` | On status transitions | `(ctx: { sessionId, status }) => Promise<void>` |

Plugins live under `./plugins/*` (configurable via `PLUGINS_DIR`). The loader (`src/core/plugins/plugin.loader.ts`) scans, instantiates plugin classes, and calls their `register(hookService)` method.

A minimal plugin:

```typescript
// plugins/log-outgoing/index.ts
export default class LogOutgoing {
  register(hooks) {
    hooks.on('message:sending', async (ctx) => {
      console.log('sending', ctx.sessionId, ctx.payload.chatId);
    });
  }
}
```

Plugins are auto-loaded when `PLUGINS_ENABLED=true`. They share the API process, so a buggy plugin can crash the gateway — keep them defensive.

## Sessions are in-memory

`SessionService` holds `engines: Map<string, IWhatsAppEngine>` keyed by session id. This map is the **only** place engines live. Persistence on disk:

- `data/<DATABASE_NAME>.sqlite` — session rows
- `SESSION_DATA_PATH/<sessionId>/` — Puppeteer profile + WhatsApp Web auth blobs

Implications:

- **Process restart drops every engine.** `SessionService` resets all active rows to `DISCONNECTED` on boot. You must call `POST /api/sessions/:id/start` for each session you want back up (no auto-restart by default).
- **Two API processes don't share sessions.** Each has its own `engines` map. Starting the same `sessionId` in two processes is a corruption hazard — only one Puppeteer profile can own a WhatsApp Web auth at a time.
- **Memory roof.** Each engine is one Chromium process; per-session RSS ~80-150 MB.

## Scaling model

Single-node:

```
[clients] → [openwa-api : 2785] → [Chromium × N]
              │
              ├─ data DB (sqlite or external Postgres)
              ├─ main DB (sqlite, local)
              ├─ storage (local or S3)
              └─ Redis (cache + BullMQ, if enabled)
```

Multi-node: there is **no built-in coordinator**. To horizontally scale you must:

1. Run multiple `openwa-api` processes, each on its own node.
2. Give each node its own `SESSION_DATA_PATH` volume (sessions are node-pinned).
3. Share the `data` DB (Postgres) across nodes — sessions, messages, webhooks become globally visible.
4. Route requests for a given `sessionId` to the node that owns it (consistent hash, session affinity in the load balancer, or a custom router).
5. Decide what to do with API keys: either accept per-node key sets (each node's `main` SQLite) or shared-volume the `main` DB on a network FS (risky; the gateway holds locks).

Background reading on this: `docs/13-horizontal-scaling.md` in the OpenWA repo.
