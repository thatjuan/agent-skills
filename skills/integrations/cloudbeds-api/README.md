# cloudbeds-api

> Expertise for the Cloudbeds hospitality platform APIs — property management, booking, payments, accounting, and channel integrations across a family of REST products that share one auth system.

## What it does

`cloudbeds-api` makes your agent fluent in Cloudbeds' public API surface, which spans several REST products (PMS Classic, PMS v2, Accounting, Data Insights, Payments, Fiscal Documents, and more) that share a common auth system but differ in path style, request format, and error envelope. The skill covers:

- **The product inventory** — base URLs, path style (RPC vs. REST), and body format per API, plus which versions are current and which are retired.
- **Authentication** — the three paths that all resolve to `Authorization: Bearer ...` (automatic-delivery API keys, email-delivery keys, and OAuth 2.0), token lifetimes, and the refresh-token-to-API-key migration.
- **Multi-property handling** — `propertyID` as a query/form param in Classic PMS vs. the `x-property-id` header in newer APIs, and organization-scoped keys.
- **Request and error gotchas** — Classic PMS bodies are form-urlencoded (not JSON), Classic returns HTTP 200 on business errors (check `success`), while v2 uses RFC 7807 problem+json.
- **Webhooks** — the `object/action` event model, the 2-second handler timeout that triggers redelivery, at-least-once delivery with no HMAC signature, and dedup strategy.
- **Data-model pitfalls** — string IDs, per-property `reservationID` uniqueness, property-local dates vs. `*UTC` datetime pairs, numeric webhook timestamps, and money-as-JSON-number precision risk.
- **What the API can't do** — no rate-plan creation, no API refunds, no auto-charge deposits.

It triggers when code calls `api.cloudbeds.com`, `hotels.cloudbeds.com`, or `api.payments.cloudbeds.com`, when authenticating with `cbat_`-prefixed keys or OAuth, or when the user asks about Cloudbeds PMS, reservations, rate plans, webhooks, Pay-By-Link, or the Accounting/Data Insights/Fiscal Documents APIs.

## When to use it

Invoke this skill when you hear:

- *"Create a reservation and take a payment through Cloudbeds."*
- *"Why is my `postReservation` call rejecting the JSON body?"* (Classic PMS wants form-urlencoded)
- *"Subscribe to `reservation/created` webhooks and handle duplicates safely."*
- *"Sync availability across three properties on one API key."*
- *"Batch-update rate plans and track the async job."*
- *"Exchange this OAuth refresh token for a long-lived API key."*

## Example walkthrough

Asked to create a reservation, the skill flags the two traps up front: Classic PMS v1.3 wants an `application/x-www-form-urlencoded` body with repeated array keys (`rooms[]=...`), and a "failure" comes back as HTTP 200 with `success: false` rather than a 4xx. It routes multi-property calls through the right mechanism (query param for Classic, `x-property-id` header for v2), uses `thirdPartyIdentifier` for idempotency since there's no `Idempotency-Key`, and reads back the `*UTC` datetime fields for any cross-property diffing.

## Installation

```bash
npx skills add thatjuan/agent-skills --skill cloudbeds-api
```

## Bundled resources

| File | Purpose |
|------|---------|
| `SKILL.md` | API product inventory, auth paths, multi-property handling, request/error gotchas, rate limits, webhooks, core endpoints, data-model pitfalls, API limits, sandbox access, SDKs |
| `references/authentication.md` | Complete OAuth flow, all scope strings, multi-property handling, the `/userinfo` endpoint |
| `references/data-model.md` | ID formats, date/timezone rules, pagination styles per API |
| `references/endpoints.md` | Full PMS Classic endpoint catalog by domain |
| `references/errors-and-limits.md` | Status-code table, error envelopes, retry guidance |
| `references/integration-patterns.md` | End-to-end reservation creation, the four payment flows, async rate updates, v1.2 migration gotchas |
| `references/resources.md` | SDKs, Postman collections, MCP server setup |
| `references/webhooks.md` | Full event catalog with payload shapes and required scopes |

## Tips

- **Classic PMS POST/PUT bodies are form-urlencoded, not JSON** — the trap that catches every new integrator. Repeat array keys for multi-value fields.
- **Classic PMS returns HTTP 200 on business errors** — always check the `success` field; don't rely on status codes for Classic. PMS v2 uses RFC 7807 problem+json instead.
- **All IDs are strings, and `reservationID` is unique per property, not globally.** Prefer the `_str` variants in webhook payloads.
- **Use `*UTC` datetime fields for sync.** Plain `dateCreated`/`dateModified` are property-local; `dateCreatedUTC`/`dateModifiedUTC` are what you diff on.
- **There's no `Idempotency-Key`.** Dedup POSTs with a business key like `thirdPartyIdentifier` on `postReservation`.
- **Prefer webhooks over polling, but design for duplicates and reordering** — delivery is at-least-once, unordered, and handler responses after 2 seconds count as timeouts.

## Related skills

- None in this repo yet — pair with any payments or accounting integration work.
