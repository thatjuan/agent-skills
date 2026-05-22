# Configuration

Environment-variable reference and how OpenWA loads them.

## Contents

- [Loading precedence](#loading-precedence)
- [First-boot bootstrap](#first-boot-bootstrap)
- [Env-var reference](#env-var-reference)
- [Dual-database architecture](#dual-database-architecture)
- [Queue gating](#queue-gating)
- [Rate limiting](#rate-limiting)
- [`.env.minimal`](#envminimal)

## Loading precedence

`src/main.ts:11-65` loads dotenv with `override: false`. **The first source to set a variable wins.** The order is:

```
process.env            (highest — Docker `environment:`, shell, systemd)
  ↓
./.env                 (project root, user-committed)
  ↓
./data/.env.generated  (lowest — written by the dashboard's settings UI)
```

This is the opposite of what most people expect. Dashboard saves are the lowest-priority layer, not the highest. To make a dashboard-saved value win, remove the matching key from `process.env` and `.env`.

## First-boot bootstrap

If `./data/.env.generated` does not exist on boot, OpenWA writes one (`src/main.ts:29-65`) with safe defaults:

```env
PORT=2785
NODE_ENV=production
DATABASE_TYPE=sqlite
DATABASE_NAME=./data/openwa.sqlite
DATABASE_SYNCHRONIZE=true
ENGINE_TYPE=whatsapp-web.js
SESSION_DATA_PATH=./data/sessions
PUPPETEER_HEADLESS=true
STORAGE_TYPE=local
STORAGE_LOCAL_PATH=./data/media
REDIS_ENABLED=false
QUEUE_ENABLED=false
```

If no API keys exist in the DB, `auth.service.ts` creates one and writes its plaintext to `./data/.api-key`, then prints it in the startup banner. In `NODE_ENV=development` the bootstrap key is the literal `dev-admin-key` (no random hex) — never run dev mode on the public internet.

## Env-var reference

### Core

| Var | Default | Notes |
|---|---|---|
| `NODE_ENV` | `production` | `development` enables verbose logs and the literal `dev-admin-key` bootstrap key |
| `PORT` | `2785` | API listener |
| `LOG_LEVEL` | `info` | `error\|warn\|info\|debug` |
| `BASE_URL` | — | Used in the startup banner; no functional effect on routing |
| `DASHBOARD_URL` | — | Banner only |
| `CORS_ORIGINS` | `*` | Comma-separated. `*` is rejected with credentials |
| `DASHBOARD_ENABLED` | `true` | Toggles compose service |
| `PROXY_ENABLED` | `true` | Toggles Traefik service |

### Engine (WhatsApp)

| Var | Default | Notes |
|---|---|---|
| `ENGINE_TYPE` | `whatsapp-web.js` | Only one adapter ships today |
| `SESSION_DATA_PATH` | `./data/sessions` | Per-session Puppeteer profile + WA auth |
| `PUPPETEER_HEADLESS` | `true` | Set `false` to debug locally |
| `PUPPETEER_ARGS` | `--no-sandbox,--disable-setuid-sandbox,--disable-dev-shm-usage,--disable-gpu` | Comma-separated; passed to Chromium |
| `PUPPETEER_EXECUTABLE_PATH` | `/usr/bin/chromium` (Docker) | Path to Chromium binary |

### Data database (sessions, messages, webhooks)

Connection name `data` in `app.module.ts`.

| Var | Default | Notes |
|---|---|---|
| `DATABASE_TYPE` | `sqlite` | or `postgres` |
| `DATABASE_NAME` | `./data/openwa.sqlite` | SQLite path **or** Postgres db name |
| `DATABASE_HOST` | — | Postgres only |
| `DATABASE_PORT` | `5432` | Postgres only |
| `DATABASE_USERNAME` | — | Postgres only |
| `DATABASE_PASSWORD` | — | Postgres only |
| `DATABASE_SSL` | `false` | Postgres TLS |
| `DATABASE_POOL_SIZE` | `10` | Postgres pool |
| `DATABASE_SYNCHRONIZE` | `true` for SQLite, `false` for Postgres | **Never `true` in prod Postgres** |
| `DATABASE_LOGGING` | `false` | TypeORM query log |
| `POSTGRES_BUILTIN` | `false` | Set `true` to enable the built-in compose Postgres service |

### Main database (API keys, audit)

Connection name `main` — always SQLite. Path is fixed (no env var). Stays node-local.

### Redis + queue

| Var | Default | Notes |
|---|---|---|
| `REDIS_ENABLED` | `false` | Master switch for Redis cache + queue |
| `REDIS_BUILTIN` | `false` | Use compose `redis` service |
| `REDIS_HOST` | `localhost` | |
| `REDIS_PORT` | `6379` | |
| `REDIS_PASSWORD` | — | |
| `QUEUE_ENABLED` | `false` | Conditionally loads `QueueModule`. **Required for webhook retries** |

### Storage

| Var | Default | Notes |
|---|---|---|
| `STORAGE_TYPE` | `local` | `local` or `s3` |
| `STORAGE_LOCAL_PATH` | `./data/media` | Local media path |
| `STORAGE_S3_BUCKET` | — | S3 bucket name |
| `STORAGE_S3_REGION` | `us-east-1` | |
| `STORAGE_S3_ENDPOINT` | — | For MinIO/Cloudflare R2 |
| `STORAGE_S3_ACCESS_KEY` | — | |
| `STORAGE_S3_SECRET_KEY` | — | |
| `STORAGE_S3_FORCE_PATH_STYLE` | `false` | MinIO needs `true` |
| `MINIO_BUILTIN` | `false` | Use compose `minio` service |

### Webhooks

| Var | Default | Notes |
|---|---|---|
| `WEBHOOK_TIMEOUT` | `10000` | ms per delivery attempt |
| `WEBHOOK_MAX_RETRIES` | `3` | Only effective with `QUEUE_ENABLED=true` |
| `WEBHOOK_RETRY_DELAY` | `5000` | ms; backoff base |

### Rate limiting (`src/config/configuration.ts`)

Three-tier `@nestjs/throttler` config:

| Var | Default | Window |
|---|---|---|
| `RATE_LIMIT_SHORT_TTL` | `1000` | per second |
| `RATE_LIMIT_SHORT_LIMIT` | `10` | |
| `RATE_LIMIT_MEDIUM_TTL` | `60000` | per minute |
| `RATE_LIMIT_MEDIUM_LIMIT` | `100` | |
| `RATE_LIMIT_LONG_TTL` | `3600000` | per hour |
| `RATE_LIMIT_LONG_LIMIT` | `1000` | |

### Plugins

| Var | Default | Notes |
|---|---|---|
| `PLUGINS_ENABLED` | `true` | Toggles plugin auto-discovery in `core/plugins` |
| `PLUGINS_DIR` | `./plugins` | Where the loader scans |

## Dual-database architecture

```
src/app.module.ts
  TypeOrmModule.forRootAsync({ name: 'main', ... })   ← SQLite, always
    Entities: ApiKey, AuditLog
  TypeOrmModule.forRootAsync({ name: 'data', ... })   ← SQLite or Postgres
    Entities: Session, Message, Webhook, …
```

Implications:

- API keys are **not** shared across nodes. If you front two OpenWA processes with a load balancer, each has its own key set. Either co-locate keys (shared volume for `main.sqlite`) or accept per-node keys.
- Switching `data` from SQLite to Postgres is a database migration — the `main` DB is untouched.
- The two connections are independent: a transient Postgres outage breaks data writes but doesn't kick out API auth.

## Queue gating

The conditional import in `src/app.module.ts:31-38`:

```typescript
const queueModules: Array<Type | DynamicModule> = [];
if (process.env.QUEUE_ENABLED === 'true') {
  const queueModule = require('./modules/queue/queue.module');
  queueModules.push(queueModule.QueueModule);
}
```

When `QUEUE_ENABLED=false` (default), `WebhookService` checks `this.queueEnabled` and dispatches webhooks synchronously with no retry. For any production deployment that depends on webhook delivery, set `REDIS_ENABLED=true` + `QUEUE_ENABLED=true`.

## `.env.minimal`

The minimum that boots OpenWA standalone (SQLite, no Redis, no S3, no queue):

```env
NODE_ENV=development
PORT=2785
DATABASE_TYPE=sqlite
DATABASE_NAME=./data/openwa.sqlite
DATABASE_SYNCHRONIZE=true
ENGINE_TYPE=whatsapp-web.js
SESSION_DATA_PATH=./data/sessions
PUPPETEER_HEADLESS=true
STORAGE_TYPE=local
STORAGE_LOCAL_PATH=./data/media
REDIS_ENABLED=false
QUEUE_ENABLED=false
```

Use as `.env` for first-run experimentation. Promote to Postgres + queue + Redis before going to production.
