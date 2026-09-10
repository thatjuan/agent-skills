# REST API

Full controller-to-route catalog, verified against the NestJS decorators in `src/modules/*/`. All paths are mounted under the global prefix `/api` (`src/main.ts:128`). Every endpoint except `/api/health*` and `/api/docs` requires `X-API-Key`.

## Contents

- [Conventions](#conventions)
- [Sessions](#sessions)
- [Messages](#messages)
- [Webhooks](#webhooks)
- [API keys](#api-keys)
- [Health](#health)
- [Contacts, Groups, Labels, Channels, Status, Catalog](#auxiliary-domains)
- [Swagger UI](#swagger-ui)

## Conventions

- **Base URL**: `http://<host>:2785/api`
- **Auth**: `X-API-Key: owa_k1_…`
- **Content-Type**: `application/json` (file upload endpoints accept `multipart/form-data`)
- **Role gating**: `@RequireRole(ApiKeyRole.OPERATOR | ADMIN)` decorators apply to writes; reads default to any active key (`VIEWER`+)
- **IDs**: session `id` is a UUID; chat ids follow WhatsApp Web (`<phone>@c.us`, `<id>@g.us`, `<id>@newsletter`); WA message ids are opaque strings

## Sessions

`@Controller('sessions')` → `src/modules/session/session.controller.ts`.

| Method | Path | Role | Purpose |
|---|---|---|---|
| `POST` | `/sessions` | OPERATOR | Create session row. Body: `{name, config?, proxyUrl?, proxyType?}` |
| `GET` | `/sessions` | any | List all sessions (incl. status) |
| `GET` | `/sessions/:id` | any | One session |
| `DELETE` | `/sessions/:id` | OPERATOR | Stop engine and delete row |
| `POST` | `/sessions/:id/start` | OPERATOR | Start engine (launches Chromium) |
| `POST` | `/sessions/:id/stop` | OPERATOR | Graceful disconnect, status → `DISCONNECTED` |
| `GET` | `/sessions/:id/qr` | any | SVG QR while status = `QR_READY` |
| `GET` | `/sessions/:id/groups` | any | List WA groups for session |
| `GET` | `/sessions/stats/overview` | any | Aggregate stats across sessions |

Create + start in two calls — start is async, the session reaches `QR_READY` then `READY` over the next 5-30 s.

## Messages

`@Controller('sessions/:sessionId/messages')` → `src/modules/message/message.controller.ts`.

| Method | Path | Role | Purpose |
|---|---|---|---|
| `GET` | `/` | any | History with filters: `?chatId=&limit=&offset=&before=` |
| `POST` | `/send-text` | OPERATOR | Body: `{chatId, text}` → `{messageId, timestamp}` |
| `POST` | `/send-image` | OPERATOR | Body: `{chatId, url\|base64, caption?}` |
| `POST` | `/send-video` | OPERATOR | Body: `{chatId, url\|base64, caption?}` |
| `POST` | `/send-audio` | OPERATOR | Body: `{chatId, url\|base64, ptt?}` (`ptt` = voice note) |
| `POST` | `/send-document` | OPERATOR | Body: `{chatId, url\|base64, filename?}` |
| `POST` | `/send-location` | OPERATOR | Body: `{chatId, latitude, longitude, name?, address?}` |
| `POST` | `/send-contact` | OPERATOR | Body: `{chatId, contactId\|vcard}` |
| `POST` | `/send-sticker` | OPERATOR | Body: `{chatId, url\|base64}` |
| `POST` | `/reply` | OPERATOR | Body: `{chatId, quotedMessageId, text}` |
| `POST` | `/forward` | OPERATOR | Body: `{chatId, messageId}` |
| `POST` | `/react` | OPERATOR | Body: `{messageId, emoji}` |
| `GET` | `/:chatId/:messageId/reactions` | any | List reactions |
| `POST` | `/delete` | OPERATOR | Body: `{messageId, forEveryone?}` |
| `POST` | `/send-bulk` | OPERATOR | Body: `{messages: [{chatId,text,…}, …]}` → `{batchId}` |
| `GET` | `/batch/:batchId` | any | Bulk progress |
| `POST` | `/batch/:batchId/cancel` | OPERATOR | Cancel a pending bulk batch |

Send returns once the message is queued to the engine; final delivery state is reported via `message.ack` events (status 1 = sent, 2 = delivered, 3 = read).

## Webhooks

`@Controller('sessions/:sessionId/webhooks')` → `src/modules/webhook/webhook.controller.ts`.

| Method | Path | Role | Purpose |
|---|---|---|---|
| `POST` | `/` | OPERATOR | Create. Body: `{url, events: string[], secret?, headers?, active?}` |
| `GET` | `/` | any | List webhooks for the session |
| `GET` | `/:id` | any | One webhook |
| `PUT` | `/:id` | OPERATOR | Update mutable fields |
| `POST` | `/:id/test` | OPERATOR | Send a synthetic delivery to the configured URL |
| `DELETE` | `/:id` | OPERATOR | Delete |

`events` valid values are in [webhooks-and-events.md](webhooks-and-events.md).

## API keys

`@Controller('auth/api-keys')` → `src/modules/auth/auth.controller.ts`. **All require role `ADMIN`.**

| Method | Path | Body / notes |
|---|---|---|
| `POST` | `/` | `{name, role, allowedIps?, allowedSessions?, expiresAt?}` → returns `{id, key, …}` once |
| `GET` | `/` | list (no plaintext) |
| `GET` | `/:id` | one |
| `PUT` | `/:id` | update mutable fields (not the key itself) |
| `DELETE` | `/:id` | delete |
| `POST` | `/:id/revoke` | soft revoke (sets `isActive=false`) |

Plus the public probe `GET /api/auth/validate` (header `X-API-Key`) → `{valid, role?}`.

## Health

`@Controller('health')` → `src/modules/health/health.controller.ts`. Public.

| Method | Path | Use |
|---|---|---|
| `GET` | `/health` | basic — process up |
| `GET` | `/health/live` | K8s `livenessProbe` |
| `GET` | `/health/ready` | K8s `readinessProbe` — verifies DB reachability |

## Auxiliary domains

Modules are wired via NestJS `imports` in `src/app.module.ts`. Patterns mirror `messages`:

| Module | Mount | Examples |
|---|---|---|
| Contacts | `/sessions/:sessionId/contacts` | `GET /`, `GET /:id`, `POST /block`, `POST /unblock` |
| Groups | `/sessions/:sessionId/groups` | `POST /` (create), `POST /:id/participants/add`, `POST /:id/participants/remove`, `POST /:id/invite-link/revoke`, `PUT /:id/subject`, `PUT /:id/description` |
| Labels | `/sessions/:sessionId/labels` | WA Business label CRUD + assign/unassign to chats |
| Channels | `/sessions/:sessionId/channels` | WA channels/newsletters (read-only on most accounts) |
| Status | `/sessions/:sessionId/status` | Stories/status posts |
| Catalog | `/sessions/:sessionId/catalog` | WA Business product catalog |
| Infra | `/infra` | Settings, stats, export/import for DB migration |
| Settings | `/settings` | Per-installation key/value |
| Stats | `/stats` | Aggregate counters |
| Audit | `/audit` | Audit log query |
| Docker | `/docker` | Stack introspection via mounted `docker.sock` |
| Plugins | `/plugins` | List/enable/disable installed plugins |

Final source of truth for parameters is the per-controller file under `src/modules/<name>/<name>.controller.ts` plus its DTOs in `dto/`.

## Swagger UI

`src/main.ts:4` imports `SwaggerModule`. Live docs at:

```
http://localhost:2785/api/docs           # interactive Swagger UI
http://localhost:2785/api/docs-json      # raw OpenAPI 3 JSON
```

`/api/docs-json` is what to feed into `openapi-generator-cli` when regenerating SDKs.
