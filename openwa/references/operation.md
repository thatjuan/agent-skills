# Operation

Day-2: running OpenWA, managing API keys, bringing sessions up, and using the dashboard.

## Contents

- [Authentication](#authentication)
- [API-key lifecycle](#api-key-lifecycle)
- [Session lifecycle](#session-lifecycle)
- [QR authentication flow](#qr-authentication-flow)
- [Dashboard](#dashboard)
- [Audit log](#audit-log)
- [Multi-session at scale](#multi-session-at-scale)

## Authentication

OpenWA authenticates every API call with a key in the `X-API-Key` header (the `Authorization: Bearer <key>` form is also accepted via CORS allow-list, `src/main.ts:122`).

```bash
curl -H "X-API-Key: owa_k1_..." http://localhost:2785/api/sessions
```

Validation lives in `src/modules/auth/guards/api-key.guard.ts`. The guard:

1. Reads `x-api-key` (case-insensitive).
2. Hashes and looks up the key in the `main` (SQLite) DB.
3. Checks `isActive`, `expiresAt`, IP allow-list, session allow-list.
4. Enforces the role requirement set by `@RequireRole(...)` on the handler.
5. Updates `lastUsedAt`, increments `usageCount`.

Public endpoints (no key required):

- `GET /api/health`, `/api/health/live`, `/api/health/ready`
- `GET /api/docs` (Swagger UI)

Probe a key without consuming a real endpoint:

```bash
curl -i -H "X-API-Key: $KEY" http://localhost:2785/api/auth/validate
# 200 { "valid": true, "role": "OPERATOR" }
```

## API-key lifecycle

`src/modules/auth/entities/api-key.entity.ts` columns: `id`, `name`, `keyHash`, `keyPrefix`, `role`, `allowedIps?`, `allowedSessions?`, `isActive`, `expiresAt?`, `lastUsedAt?`, `usageCount`, timestamps.

**Roles** (`api-key.entity.ts`):

| Role | Allows |
|---|---|
| `VIEWER` | Read-only endpoints |
| `OPERATOR` | All read endpoints + session CRUD + send messages + webhook CRUD |
| `ADMIN` | All of OPERATOR + API-key CRUD |

**Endpoints** (require `ADMIN`, mounted at `/api/auth/api-keys`):

| Method | Path | Body |
|---|---|---|
| `POST` | `/` | `{name, role, allowedIps?, allowedSessions?, expiresAt?}` → returns `{id, key, ...}` once (only chance to copy) |
| `GET` | `/` | list (no plaintext keys, only prefixes) |
| `GET` | `/:id` | one key |
| `PUT` | `/:id` | update mutable fields |
| `DELETE` | `/:id` | hard delete |
| `POST` | `/:id/revoke` | soft revoke (sets `isActive=false`) |

The plaintext key is returned **only** on creation. Lose it and the only recovery is to revoke and recreate.

## Session lifecycle

`src/modules/session/entities/session.entity.ts` columns: `id` (uuid), `name` (unique), `status`, `phone?`, `pushName?`, `config` (JSON), `proxyUrl?`, `proxyType?`, `connectedAt?`, `lastActiveAt?`, timestamps.

```
status enum:
  CREATED        — row exists, no engine started
  INITIALIZING   — engine.start() called, Chromium launching
  QR_READY       — Puppeteer reached WA Web login screen, QR available
  AUTHENTICATING — QR scanned, WA negotiating
  READY          — connected; phone & pushName populated
  DISCONNECTED   — manual stop, or restart reset, or WA logout
  FAILED         — engine.start() threw
```

Transitions are driven by `SessionService` and the engine adapter's event stream. **All `READY`/`INITIALIZING`/`QR_READY`/`AUTHENTICATING` rows are flipped to `DISCONNECTED` on every API restart** (`src/modules/session/session.service.ts:52-70`):

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

Reason: engines live in `engines: Map<sessionId, IWhatsAppEngine>` in process memory. On boot there are no engines, so any "active" row in the DB would be a lie.

Restart behaviour you need to handle:

- After process restart, **call `POST /api/sessions/:id/start` for each session you want back up.** Authenticated sessions don't need a fresh QR scan because the WhatsApp Web auth lives on disk under `SESSION_DATA_PATH/<id>/`. If that directory is intact, `start` will reach `READY` without QR. If you wiped the volume, QR is required again.

## QR authentication flow

```bash
# 1. Create the session row
RESP=$(curl -s -X POST http://localhost:2785/api/sessions \
  -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"name":"bot-1"}')
ID=$(echo "$RESP" | jq -r .id)

# 2. Start: spawns Chromium, opens web.whatsapp.com
curl -s -X POST http://localhost:2785/api/sessions/$ID/start -H "X-API-Key: $KEY"

# 3. Poll for QR_READY (or subscribe to session.qr / session.status on /events)
curl -s -H "X-API-Key: $KEY" http://localhost:2785/api/sessions/$ID
# { "id":"...", "status":"QR_READY", ... }

# 4. Pull the QR (SVG)
curl -s -H "X-API-Key: $KEY" http://localhost:2785/api/sessions/$ID/qr > qr.svg
open qr.svg     # scan with WhatsApp mobile → Linked devices → Link a device

# 5. Status transitions to AUTHENTICATING then READY; phone/pushName populated
```

QR codes rotate every ~20 s server-side; re-fetch if the user is slow.

## Dashboard

`/Users/user/work/playground/OpenWA/dashboard/` — React 19 + Vite + TanStack Query, served on port `2886` (compose service `dashboard`).

What it exposes:

- **Sessions**: list, create, start/stop, view QR, see live status (driven by Socket.IO `/events`).
- **API keys**: create/revoke, view usage counts and last-used timestamps.
- **Webhooks**: per-session create/edit/test/delete.
- **Infrastructure** (`src/modules/infra/`): database type, storage backend, Redis status, queue toggle. Saving writes to `data/.env.generated`.
- **Audit log** + **Stats**.
- **i18n**: language switcher (`i18next`).

The dashboard talks to the API over the same `X-API-Key` header — the first key generated on boot is shown in the API startup banner and stored in `data/.api-key`. Paste it into the dashboard's "Connect" prompt.

## Audit log

`AuditLog` entity in the `main` (SQLite) DB captures mutating actions (session create/start/stop/delete, API-key CRUD, webhook CRUD). Surface via `src/modules/audit/audit.controller.ts`. Useful for forensics; not a substitute for `LOG_LEVEL=debug`.

## Multi-session at scale

Each session = its own Chromium process via Puppeteer. Footprint per session ≈ 80-150 MB RSS, depending on chat volume. Practical limits per node (no scientific guarantee):

| Hardware | Concurrent sessions |
|---|---|
| 2 vCPU / 4 GB | 3-6 |
| 4 vCPU / 8 GB | 8-15 |
| 8 vCPU / 16 GB | 20-30 |

If you cross those limits the symptoms are Chromium crashes, `QR_READY` taking minutes, and engine timeouts. Sharding: run multiple OpenWA pods, route session ids deterministically to pods (e.g. consistent hash on session id at an upstream proxy). The codebase does **not** ship a built-in cluster coordinator.
