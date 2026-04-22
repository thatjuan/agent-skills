# Errors and rate limits

## Table of contents

- [Error envelope shapes](#error-envelope-shapes)
- [HTTP status codes](#http-status-codes)
- [Common error messages](#common-error-messages)
- [Retry guidance](#retry-guidance)
- [Rate limits](#rate-limits)
- [Idempotency](#idempotency)

## Error envelope shapes

Three distinct shapes appear across the Cloudbeds surface.

### 1. Classic PMS (v1.2 / v1.3)

Flat, `success`-driven, HTTP `200` even on business-logic failures:

```json
{ "success": true,  "data": { /* ... */ } }
{ "success": false, "message": "Descriptive error string" }
```

Handlers check the `success` boolean before treating a 200 as success.

### 2. PMS v2 / newer REST APIs

RFC 7807 `application/problem+json`:

```json
{
  "type": "unauthorized",
  "title": "Unauthorized",
  "status": 401,
  "detail": "401 UNAUTHORIZED"
}
```

Status codes modeled in the spec per endpoint: 400, 401, 403, 404, 500, each with its own schema (`BadRequestResponseSchema`, `ForbiddenResponseSchema` — reused for 401 and 403 — `InternalServerErrorResponseSchema`).

### 3. OAuth / access-token endpoints

OAuth-standard error shape, HTTP `400` / `401`:

```json
{ "error": "server_error",   "error_description": "The authorization code is invalid or has expired." }
{ "error": "access_denied",  "message": "The resource owner or authorization server denied the request." }
{ "error": "invalid_request","message": "The refresh token is invalid." }
```

## HTTP status codes

| Code | Meaning | Guidance |
|---|---|---|
| 200 | Success on REST APIs; ambiguous on classic PMS | Check `success` field on classic responses. |
| 400 | Invalid parameter | Fix the request; no retry. Typical causes: missing `reservationID`, missing `propertyID`, bad date format, unexpected field type. |
| 401 | Invalid / expired OAuth code, invalid API key, revoked key, invalid refresh token | Refresh token once; if still 401, trigger user re-authorization. |
| 403 | Insufficient permission scopes | User re-authorizes with the additional scope, or key is deleted and recreated with new scopes. |
| 404 | Resource not found | Verify IDs and property scope. |
| 500 | Internal server error | Exponential backoff retry acceptable. |
| 429 | Not documented | Cloudbeds rate enforcement is out-of-band (email + IP block); 429 is not a reliable signal. |

`X-Request-ID` is included on every response — capture it into logs for support requests.

## Common error messages

Classic PMS `success: false` messages observed in production:

- `"Please specify \"propertyID\" parameter for this call"` — multi-property key, call missing `propertyID`.
- `"None of the included property id's match the access_token user's property id"` — wrong `propertyID` for this token.
- `"User who approved this connection is not active anymore"` — user who granted consent was deactivated. Property needs someone active to reconnect the app.
- `"Your request could not be fully completed. The property(ies) you are accessing have an invalid status. See details: canceled: XXX"` — property account canceled in Cloudbeds.

PMS v2 validation error shape in practice returns a top-level `detail` string rather than structured field-level errors. Verbose logging of raw 4xx bodies is the fastest debugging path.

## Retry guidance

- **4xx errors are not retried without first fixing the request.** Retrying a 400 will return the same 400.
- **401 is retried once after refreshing the token.** Repeated 401 means the user's grant is revoked — restart authorization.
- **5xx errors are retried with exponential backoff** (e.g. 1s, 2s, 4s, 8s, jittered, capped at 5 attempts).
- **Network errors / timeouts** are treated as transient; retry with backoff.
- **Async operations** (`patchRate`, `putRate`, balance transfers, deposit transfers) return a job reference ID immediately. Subscribe to the corresponding webhook or poll the job endpoint (`getRateJobs` retains jobs for 7 days).

## Rate limits

Documented in the Cloudbeds FAQ:

| User type | Limit |
|---|---|
| Property / group-property users | 5 requests per second |
| Technology partners | 10 requests per second |

Enforcement mechanism:

- HTTP 429 / `Retry-After` / `X-RateLimit-*` headers are **not** in any published spec.
- Cloudbeds emails the partner on sustained violation.
- Credentials may be suspended; source IP may be blocked (blocking can affect the entire myfrontdesk account).
- Repeated offenses (more than twice) revoke API access permanently.

Guidance embedded in docs:

- Subscribe to webhooks and fetch on event rather than polling for changes.
- Cap per-use-case calls at ~6–8 per user action.
- Cache property-level reference data (`getHotelDetails`, `getPaymentMethods`, `getSources`, `getRoomTypes`, `getRatePlans`, `getTaxesAndFees`) aggressively — refresh on webhook or on a daily schedule rather than per-call.

## Idempotency

No `Idempotency-Key` header (or equivalent) is supported on any Cloudbeds POST. Defensive patterns:

- Dedup at the application layer using business keys: `thirdPartyIdentifier` for reservations, your own external ID stored in `customFields`, or a (property, OTA reservation ID) composite.
- Before retrying a failed POST, search for the record (`getReservations` with `thirdPartyIdentifier`, `getGuestsByFilter` with email) to avoid creating a duplicate.
- Webhook delivery guarantees at-least-once with cascades; handlers dedup on `(event, entityID, timestamp)`.

Maximum request size and server-side timeout are not documented. Reasonable client-side defaults: 30-second HTTP timeout, 5-retry exponential backoff for 5xx / network errors.
