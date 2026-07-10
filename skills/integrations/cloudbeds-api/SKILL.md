---
name: cloudbeds-api
description: Cloudbeds hospitality API expertise for building property-management, booking, payments, accounting, and channel integrations. Use when code calls `api.cloudbeds.com`, `hotels.cloudbeds.com`, `api.payments.cloudbeds.com`, or imports a Cloudbeds SDK; when the user asks about Cloudbeds PMS, reservations, rate plans, webhooks, Pay-By-Link, Payments Vault, Accounting API, Data Insights, Fiscal Documents, or Group Profile APIs; when authenticating with `cbat_`-prefixed API keys or OAuth 2.0 against Cloudbeds; when subscribing to Cloudbeds webhooks or working with `postReservation`, `getAvailableRoomTypes`, `postCharge`, `patchRate`, or similar operations.
---

# Cloudbeds API

Cloudbeds is a hospitality platform (PMS, booking engine, channel manager, payments, BI). Its public API surface spans several REST products that share a common auth system but differ in path style, request format, and error envelope.

## API product inventory

| API | Base URL | Path style | Request body |
|---|---|---|---|
| PMS Classic v1.3 (current) | `https://api.cloudbeds.com/api/v1.3/` | RPC-style (`/postReservation`) | `application/x-www-form-urlencoded` |
| PMS Classic v1.2 | `https://api.cloudbeds.com/api/v1.2/` | RPC-style | form-urlencoded |
| PMS v2 (modular) | `https://api.cloudbeds.com/` | REST (`/addons/v1/addons`) | `application/json` |
| Accounting v1.0 | `https://api.cloudbeds.com/accounting/v1.0/` | REST | JSON |
| Data Insights v1.1 | `https://api.cloudbeds.com/datainsights/v1.1/` | REST | JSON |
| Group Profile v1.0 | `https://api.cloudbeds.com/group-profile/v1/` | REST | JSON |
| Fiscal Documents v1 | `https://api.cloudbeds.com/fiscal-document/v1/` | REST | JSON |
| Pay-By-Link v2 | `https://api.cloudbeds.com/payments/v2/pay-by-link` | REST | JSON |
| Payments Vault v1 | `https://api.payments.cloudbeds.com/vault/v1/` | REST | JSON |
| OTA Build-To-Us v5.3 | partner-hosted (`https://api.your-ota.com/cloudbeds`) | RPC-style | JSON |

PMS v1.1 was retired 2025-03-31. HTTPS is required on every call. Every response carries `X-Request-ID` for support/debugging.

OpenAPI specs for all surfaces live at `https://github.com/cloudbeds/openapi-specs` (one file per product under `src/`). Pin a commit when generating clients.

## Authentication — three paths into one `Authorization: Bearer ...`

Cloudbeds prefers **API keys** (long-lived, prefixed `cbat_`) over OAuth 2.0. Either can be sent as `Authorization: Bearer <token>` or `x-api-key: <token>`.

| Path | When it fits | Detail |
|---|---|---|
| API Key (automatic delivery) | Marketplace / Technology Partner apps | OAuth-like authorize → redirect returns a `code` → exchange for `cbat_` key with `grant_type=urn:ietf:params:oauth:grant-type:api-key` |
| API Key (email delivery) | Simpler partner integrations, Flow A only | User clicks Connect, key emailed to partner inbox, pasted into your system |
| OAuth 2.0 Authorization Code | Legacy / alternative | Access token (`expires_in: 28800` = 8h) + refresh token (365d sliding expiry) |

- `code` from authorize redirect is valid **10 minutes, single use**.
- API keys do **not** expire unless unused for 30 consecutive days.
- Refresh-token-to-API-key migration: `grant_type=refresh_token_exchange` (one-shot).

See [references/authentication.md](references/authentication.md) for the complete OAuth flow, all scope strings, multi-property handling, and the `/userinfo` endpoint.

## Multi-property handling

Every property has a numeric `propertyID` (stringified in payloads). Classic PMS takes `propertyID` as a **query / form parameter** (supports comma-separated lists). PMS v2 and newer APIs take it as a **header** — spelled `x-property-id` in most specs, `X-Property-ID` in the Fiscal Documents spec (HTTP headers are case-insensitive; emit `x-property-id`).

Missing `propertyID` on a multi-property key returns: `{"success": false, "message": "Please specify \"propertyID\" parameter for this call"}`.

A single API key can scope to one property or to an entire organization (association). OAuth token responses include a `resources` array listing `{type: "property"|"association", id}` entries.

## Request format gotchas

- **Classic PMS v1.3 POST/PUT bodies are form-urlencoded, not JSON.** This trips up every new integrator. Use `application/x-www-form-urlencoded` and repeat array keys (`rooms[]=...&rooms[]=...`) for multi-value fields.
- PMS v2 and all newer modules use `application/json`.
- Response bodies are JSON with `Content-Type: application/json`; PMS v2 errors use `application/problem+json` (RFC 7807).

## Error envelopes — two shapes

**Classic PMS** returns HTTP 200 on business errors; check `success`:

```json
{ "success": true,  "data": {...} }
{ "success": false, "message": "Descriptive error" }
```

**PMS v2 / newer APIs** follow RFC 7807:

```json
{ "type": "unauthorized", "title": "Unauthorized", "status": 401, "detail": "401 UNAUTHORIZED" }
```

**OAuth errors** use OAuth-standard shape:

```json
{ "error": "server_error", "error_description": "The authorization code is invalid or has expired." }
```

See [references/errors-and-limits.md](references/errors-and-limits.md) for status-code table and retry guidance.

## Rate limits

- Property / group-property users: 5 req/s.
- Technology partners: 10 req/s.
- Enforcement is **out-of-band**: Cloudbeds emails the partner and may suspend credentials or block the source IP. HTTP 429 / `Retry-After` / `X-RateLimit-*` headers are not documented.
- No `Idempotency-Key` support on POSTs. Dedup using business keys (e.g. `thirdPartyIdentifier` on `postReservation`).
- Guidance: prefer webhooks over polling; keep per-use-case call count below ~8.

## Webhooks

Subscription via PMS endpoints: `postWebhook` (create), `getWebhooks` (list), `deleteWebhook?subscriptionID=...` (remove). Events use `object/action` naming (e.g. `reservation/created`). Scope to subscribe = same scope that reads the entity (e.g. `read:reservation` for all `reservation/*` events).

Delivery guarantees:
- 2xx ACK required from the endpoint.
- Retries: up to 5 attempts, 1 minute apart.
- **Handler responses after 2 seconds are treated as timeouts** and trigger redelivery even if the status is 2xx.
- Order is **not** guaranteed.
- Duplicates are expected (one user action can fire several webhooks; retries after 2s timeouts).
- No HMAC signature header is published. Authenticity relies on (a) HTTPS endpoint URL secrecy, (b) cross-checking the event payload's IDs via a follow-up API call.

See [references/webhooks.md](references/webhooks.md) for the full event catalog with payload shapes and scopes.

## Core domain endpoints (PMS Classic v1.3)

Full catalog in [references/endpoints.md](references/endpoints.md). Most used:

| Domain | Primary endpoints |
|---|---|
| Reservations | `postReservation`, `getReservation`, `getReservations`, `putReservation`, `postRoomCheckIn`, `postRoomCheckOut` |
| Availability | `getAvailableRoomTypes`, `getRoomTypes`, `getRoomsUnassigned` |
| Rates | `getRate`, `getRatePlans`, `patchRate` / `putRate` (async; returns `jobReferenceID`) |
| Guests | `getGuest`, `getGuestList`, `postGuest`, `putGuest`, `postGuestsToRoom` |
| Payments | `getPaymentMethods`, `getPaymentsCapabilities`, `postCharge`, `postPayment`, `postCreditCard`, `postVoidPayment` |
| Property | `getHotels`, `getHotelDetails` (contains `propertyTimezone`, `propertyCurrency`) |
| Housekeeping | `getHousekeepingStatus`, `postHousekeepingStatus`, `postHousekeepingAssignment` |
| Webhooks | `postWebhook`, `getWebhooks`, `deleteWebhook` |

## Data-model pitfalls (high-impact)

- **All IDs are strings.** PMS v1.2 migration converted many integer IDs to strings. Webhook payloads often carry both `propertyID` (int) and `propertyID_str` (string) — use the `_str` variant.
- **`reservationID` is unique per property**, not globally.
- `subReservationID` format is `{reservationID}-{n}`; the primary room's subReservationID equals the reservationID.
- **Date fields** (`startDate`, `endDate`) are property-local calendar dates, `YYYY-MM-DD`, no timezone.
- **Datetime fields** come in pairs: `dateCreated` / `dateCreatedUTC`, `dateModified` / `dateModifiedUTC`. Use the `*UTC` variants for cross-property sync and diffing.
- **Webhook `timestamp`** is UNIX seconds with microsecond decimals (e.g. `1611758157.431234`) — a numeric value, not a string.
- **Money** in classic PMS is a JSON number (decimal); precision loss is a real risk. Fetch `propertyCurrency` from `getHotelDetails` for display formatting.
- Event payloads have inconsistent casing (`propertyID` vs `propertyId`) — parse case-insensitively.
- Pagination varies: classic PMS uses `pageNumber`/`pageSize` or `resultsFrom`/`resultsTo` date bounds; PMS v2 uses `limit` (max 500) / `offset`.

See [references/data-model.md](references/data-model.md) for ID formats, date/timezone rules, and pagination styles per API.

## Things the API cannot do (read-only / missing)

- Create a new rate plan (only read/update existing via `patchRate` / `putRate`).
- Process refunds — manual only in Cloudbeds UI.
- Auto-charge deposits on API-created reservations (deposit rules ignored when `cardToken` sent via `postReservation`).
- Return pending transactions from `getTransactions`.
- True SSO / OpenID Connect — `userinfo` returns identity, but app login credentials are issued by your app.

## Integration patterns

End-to-end reservation creation, payment flows (4 viable options: SDK web component, Vault tokenization, Pay-By-Link, Stripe passthrough), rate batch updates with async job tracking, and multi-island / v1.2 migration gotchas are in [references/integration-patterns.md](references/integration-patterns.md).

## Sandbox and testing

No self-serve sandbox. Access is gated by partnership approval:
1. Submit the "Partner with Us" form at `https://www.cloudbeds.com/partner-with-cloudbeds/`.
2. Email `integrations@cloudbeds.com` with company name, website, and integration category.

Postman collections (public) are linked from `https://developers.cloudbeds.com/docs/postman-api-collection.md`. Webhook endpoint testing is recommended via `https://webhook.site`.

## Agentic resources

Cloudbeds publishes an LLM-first doc surface:
- `https://developers.cloudbeds.com/llms.txt` — full sitemap of `.md` docs.
- Append `.md` to any `/docs/<slug>` or `/reference/<slug>` URL to get markdown.
- **Official MCP server**: `https://developers.cloudbeds.com/mcp` (HTTP transport). Add with `claude mcp add --transport http cloudbeds-developers https://developers.cloudbeds.com/mcp`.

See [references/resources.md](references/resources.md) for the full list of SDKs, Postman collections, and MCP setup.

## SDKs

- **Python (official, auto-generated)**: `https://github.com/cloudbeds/cloudbeds-api-python` — tracks PMS v2, requires Python ≥ 3.9.
- **Payment Element web component (browser)**: `@cloudbeds/payment-element-webcomponent` on GitHub Packages — PCI-safe card capture UI.
- No official JavaScript/TypeScript, PHP, Ruby, Java, or Go REST SDKs. Generate clients from the OpenAPI specs with `openapi-generator-cli`.

## Support

- Email: `integrations@cloudbeds.com` (only official channel).
- Include `X-Request-ID` from response headers when reporting API bugs.
- Stack Overflow tag: `cloudbeds`.
