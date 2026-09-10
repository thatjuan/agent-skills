# Gotchas

Verified non-obvious behaviours. Each cites file:line so you can confirm before relying on it.

## 1. `.env.generated` is the **lowest** precedence layer

`src/main.ts:11-65` loads dotenv with `override: false`. Reading order:

```
process.env  >  ./.env  >  ./data/.env.generated
```

The dashboard's "Settings" UI writes `data/.env.generated`. People expect that to be the source of truth and are surprised when a Docker `environment:` block silently keeps winning. To make a dashboard-saved value take effect, remove the matching key from process env and `.env`.

## 2. Every API restart force-disconnects active sessions

`src/modules/session/session.service.ts:52-70` on boot:

```typescript
const activeStatuses = [
  SessionStatus.READY, SessionStatus.INITIALIZING,
  SessionStatus.QR_READY, SessionStatus.AUTHENTICATING,
];
await this.sessionRepository.update(
  { status: In(activeStatuses) },
  { status: SessionStatus.DISCONNECTED },
);
```

Reason: engines live in `engines: Map<sessionId, IWhatsAppEngine>` in memory. On boot the map is empty, so any row marked `READY` would be a lie. There is **no auto-restart loop** — you must `POST /api/sessions/:id/start` for every session you want back online. The WhatsApp Web auth on disk persists, so this usually reaches `READY` without a fresh QR scan (assuming `SESSION_DATA_PATH/<id>/` survived).

## 3. `QUEUE_ENABLED=false` means webhooks have no retry

`src/app.module.ts:31-38`:

```typescript
if (process.env.QUEUE_ENABLED === 'true') {
  const queueModule = require('./modules/queue/queue.module');
  queueModules.push(queueModule.QueueModule);
}
```

`WebhookService` then checks `this.queueEnabled` and falls back to sync `await this.send(...)`. Single shot. Failure or timeout = dropped delivery. `WEBHOOK_MAX_RETRIES=3` only applies when the queue is wired up. Default is `QUEUE_ENABLED=false` — production deployments need to flip this **and** enable Redis.

## 4. `synchronize: true` on Postgres is a footgun

`src/app.module.ts:88-108`:

```typescript
synchronize: configService.get<boolean>('dataDatabase.synchronize', true),
migrationsRun: !configService.get<boolean>('dataDatabase.synchronize', true),
```

Default-`true` is fine for SQLite (auto-creates dev schema). With Postgres in production, `synchronize: true` lets TypeORM rewrite the schema on every boot — schema drift, data loss in the worst case. Explicitly set `DATABASE_SYNCHRONIZE=false` for Postgres and rely on migrations (`npm run migration:run:prod`).

## 5. API keys live in a different DB than your data

`src/app.module.ts` configures two TypeORM connections:

- `main` — always SQLite — holds `ApiKey`, `AuditLog`
- `data` — SQLite or Postgres — holds `Session`, `Message`, `Webhook`, …

Moving the `data` DB to Postgres does **not** move API keys. Two consequences:

- Multi-node deploys have per-node key sets (unless you share `main.sqlite` on a network FS, which is risky).
- Backing up "the database" must include `main.sqlite` or you lose all API keys on restore.

## 6. `phone` and `pushName` are `null` until `READY`

`src/modules/session/entities/session.entity.ts:30-31`:

```typescript
@Column({ type: 'varchar', length: 20, nullable: true })
phone: string | null;
```

Both fields are populated by the engine after WhatsApp authentication succeeds. Filtering sessions by phone (`?phone=628…`) won't match any session in `CREATED`/`QR_READY`/`AUTHENTICATING`.

## 7. Chat-id format is unforgiving

WhatsApp Web expects:

- `<phone>@c.us` for direct chats — digits only, country code included, no `+`, no leading zero
- `<id>@g.us` for groups — id is opaque, you get it from `GET /sessions/:id/groups`
- `<id>@newsletter` for channels

Wrong format = **silent failure**. `whatsapp-web.js` returns no error; the message just never sends. Consequence: ack the `messageId` returned by send, but **do not** trust the send unless you see a subsequent `message.ack` event with `status >= 2`.

## 8. Chromium is non-negotiable

The Dockerfile hard-codes `PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium` and `PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true`. Local non-Docker runs need:

```bash
npx puppeteer browsers install chromium
# or
export PUPPETEER_EXECUTABLE_PATH=$(which chromium || which chrome)
```

Firefox / WebKit are not supported by the current `whatsapp-web.js` integration.

## 9. The CORS `X-API-Key` allow-list is permissive

`src/main.ts:122`:

```typescript
allowedHeaders: ['Content-Type', 'X-API-Key', 'Authorization', 'X-Request-ID'],
```

`X-API-Key` is exposed cross-origin. If you put OpenWA on the open internet and set `CORS_ORIGINS=*`, any page in any browser can attempt key-stuffing. Lock `CORS_ORIGINS` to your admin origins, and require API keys to be scoped (`allowedIps`).

## 10. The dev bootstrap key is a fixed string

`src/modules/auth/auth.service.ts` first-run logic uses `dev-admin-key` literally when `NODE_ENV=development`. Anyone who knows the OpenWA codebase will guess that key on a dev-mode public deployment. **Never** expose `NODE_ENV=development` to the internet.

## 11. `WebhookService` shares the API process

Webhook dispatch (sync mode) runs on the request thread. A slow receiver delays the engine event loop. Even in queue mode, the worker runs in the same process by default. For high-volume use, scale the gateway vertically (more vCPU) or run a dedicated worker process (custom — not shipped).

## 12. `engines` map is unsynchronized across processes

There is no Redis-based lock or election to prevent two nodes from starting the same session id. If you horizontally scale without session-affinity routing, two Chromium processes will fight over the same WhatsApp Web auth dir and at least one will fail. Always pin a session id to a node at the load balancer.

## 13. Docker socket mount is required by default

`docker-compose.yml` mounts `/var/run/docker.sock:ro` into `openwa-api`. `src/modules/docker` uses it to introspect the stack from the dashboard. If you don't want that surface (or you're not running in Docker), set `DOCKER_ENABLED=false` and remove the mount — otherwise the module logs errors on every refresh attempt.
