# Integration patterns

## Table of contents

- [Create reservation end-to-end](#create-reservation-end-to-end)
- [Availability and pricing search](#availability-and-pricing-search)
- [Payment flows (four options)](#payment-flows-four-options)
- [Rate batch updates](#rate-batch-updates)
- [Multi-property orchestration](#multi-property-orchestration)
- [Disconnection / app teardown](#disconnection--app-teardown)
- [v1.2 migration gotchas](#v12-migration-gotchas)

## Create reservation end-to-end

Steps:

### 1. Fetch property context (cache per property)

- `GET /getHotelDetails` → `propertyTimezone`, `propertyCurrency`, check-in/check-out times, policies.
- `GET /getPaymentMethods` → valid `paymentMethod` values (`cash`, `credit`, `ebanking`, `pay_pal`, plus custom methods).
- `GET /getPaymentsCapabilities` → gateway type, `payByLink: boolean`, `cloudbedsPayments: boolean`.
- `GET /getSources` → valid `sourceID` values (primary sources suffixed `-1`).
- `GET /getRoomTypes` → room type IDs and capacity.
- `GET /getRatePlans` → `roomRateID` values available.
- `GET /getTaxesAndFees` → for price preview math.

### 2. Availability search

```http
GET /api/v1.3/getAvailableRoomTypes?
    startDate=2026-05-01&endDate=2026-05-03
    &rooms=1&adults=2&children=0
    &detailedRates=true
    &propertyID=12345
Authorization: Bearer cbat_...
```

If a rate plan returns with `roomsAvailable: 0`, the plan is not applicable (LOS, occupancy, date constraint violated) — filter out client-side.

### 3. Create reservation

`POST /postReservation` with `application/x-www-form-urlencoded` body:

Required fields:

| Field | Example |
|---|---|
| `startDate` | `2026-05-01` |
| `endDate` | `2026-05-03` |
| `guestFirstName` | `Alex` |
| `guestLastName` | `Morgan` |
| `guestCountry` | `US` |
| `guestZip` | `94103` |
| `guestEmail` | `alex@example.com` |
| `rooms[]` | JSON-encoded `[{"roomTypeID":"...","quantity":1,"roomID":"...","roomRateID":"..."}]` |
| `adults[]` | `[{"roomTypeID":"...","quantity":2}]` |
| `children[]` | `[{"roomTypeID":"...","quantity":0}]` |
| `paymentMethod` | `credit`, `cash`, `ebanking`, `pay_pal`, or a custom method ID |

Optional high-value fields:

- `sourceID` — booking source (include `-1` for primary sources).
- `thirdPartyIdentifier` — OTA reservation ID. Use as the dedup key.
- `cardToken` — Stripe Customer ID (or Vault token). Requires `paymentMethod=credit`.
- `paymentAuthorizationCode` — Stripe Charge ID. Requires `cardToken` and Stripe gateway.
- `promoCode` — needs corresponding `rateID`.
- `allotmentBlockCode` — to book against an allotment.
- `groupCode` — to associate with a group booking.
- `estimatedArrivalTime` — ISO 8601 time.
- `dateCreated` — overrides default "now".
- `sendEmailConfirmation` — defaults to `true`.
- `customFields[]` — `[{"id": "...", "value": "..."}]`.

Multi-room reservations repeat `rooms`, `adults`, `children` entries — one per additional room, indices aligned.

### 4. Response shape

```json
{
  "success": true,
  "reservationID": "884565856563",
  "status": "confirmed",
  "guestID": "35436",
  "guestEmail": "alex@example.com",
  "startDate": "2026-05-01",
  "endDate": "2026-05-03",
  "dateCreated": "2026-04-20T14:31:02-07:00",
  "grandTotal": 321.40,
  "unassigned": []
}
```

`unassigned[]` lists subReservations that could not auto-assign to a specific room (feature gated on "MyBookings" settings). Call `postRoomAssign` or `postRoomCheckIn` to resolve.

### 5. Post-create actions

- `postCreditCard` with `paymentMethodId` (from Vault or Payment Element) — store card on file.
- `postCharge` — take a deposit. Parameters include `amount`, `paymentMethodId`, `isDeposit=true`, optional `returnUrl` for 3DS redirect.
- `postReservationNote` — attach internal notes.
- `postGuestsToRoom` — add secondary guests.
- `postHousekeepingStatus` — pre-stay room cleanup state.

### 6. Dedup / idempotency

No Cloudbeds-side idempotency key. Prevent duplicate reservations by searching first:

```http
GET /getReservations?thirdPartyIdentifier=XYZ123&propertyID=12345
```

If a match exists, skip `postReservation` and use the existing `reservationID`.

## Availability and pricing search

`getAvailableRoomTypes` response groups by room type. Per-type fields include:

- `roomTypeID`, `roomTypeName`, `roomTypeDescription`, `maxGuests`.
- `roomsAvailable` — count.
- `roomTypePhotos[]`.
- `roomRate` or `detailedRates` (when `detailedRates=true`) — per-night pricing.
- `rates[]` — each with `roomRateID`, `name`, `totalPriceWithTaxesFees`, `cancelationPolicy`, restrictions.

Flow for a booking funnel:

1. Availability scan: `getAvailableRoomTypes` with `startDate`/`endDate`.
2. Room-type pick: cached `getRoomTypes` for names, photos, descriptions.
3. Rate detail: `getRate` or embedded `detailedRates`.
4. Tax preview: `getRoomsFeesAndTaxes` for itemized breakdown.

## Payment flows (four options)

| Option | Use case | Primary call |
|---|---|---|
| Cloudbeds Payment SDK web component | Modern PCI-safe card capture in your own UI | Embed `@cloudbeds/payment-element-webcomponent`, pass returned `paymentMethodId` to `postCreditCard` / `postCharge`. |
| Payments Vault tokenization | Server-side card tokenization | `POST https://api.payments.cloudbeds.com/vault/v1/tokens/card` → returned token `id` used as `paymentMethodId` in `postCreditCard` / `postCharge`. |
| Pay-By-Link | Email guest a payment link | `POST https://api.cloudbeds.com/payments/v2/pay-by-link`. Requires `getPaymentsCapabilities.payByLink = true` (Cloudbeds Payments gateway). |
| Stripe token passthrough | Deposit captured in your own booking engine | Pass `cardToken` (Stripe Customer ID) + `paymentAuthorizationCode` (Stripe Charge ID) on `postReservation`. Stripe gateway required. |

Refunds are not API-accessible — they are processed manually in Cloudbeds.

Reservations created with `cardToken` do not auto-charge the configured deposit. `postCharge` is required if a deposit is needed immediately.

## Rate batch updates

`patchRate` and `putRate` are async:

1. POST the update. Response includes `jobReferenceID`.
2. Either subscribe to `api_queue_task/rate_status_changed` (scope `read:rate`) and wait for status `completed` or `error`; or poll `getRateJobs` (jobs retained 7 days).
3. `patchRate` is capped at 30 intervals per request.

Derived rates are not updatable — requests to `patchRate` / `putRate` against derived rates return an error.

## Multi-property orchestration

For partner apps authorized against an organization:

1. Enumerate properties: `GET /getHotels` — returns array of `{propertyID, propertyName, propertyTimezone, propertyCurrency[]}`.
2. Per property, call `postAppState` to set state `enabled` (establishes per-property session).
3. For each subsequent call, include `propertyID` (classic PMS) or `x-property-id` header (PMS v2+).
4. On disconnect, set each property's state to `disabled`.

Association-level access is off by default — enable via `integrations@cloudbeds.com`.

## Disconnection / app teardown

App states: `enabled`, `pending`, `disabled`, `installing`. Transitions emit `integration/appstate_changed`.

When a user disconnects the app in Cloudbeds:

- Webhook subscriptions are auto-deleted.
- Subsequent API calls return `401` / `access_denied`.
- `integration/appstate_changed` webhook fires with `newState: "disabled"` (subscribe before disconnect to receive it).

An in-app "Disconnect" button mirrors the state by calling `postAppState` with `state=disabled` to avoid orphan subscriptions on Cloudbeds' side.

## v1.2 migration gotchas

The "Multi-Island" (v1.2) migration introduced several compat risks:

- Many previously integer IDs became strings (`propertyID`, `reservationID`, `guestID`, `roomID`, `roomTypeID`). Data models store them as strings universally.
- Webhook payloads include both `propertyID` (int) and `propertyID_str` (string). The `_str` variant is canonical.
- Some endpoints accept both singular `propertyID` and plural `propertyIDs` — specs differ per endpoint.
- v1.1 is retired (2025-03-31). v1.1 is no longer callable; v1.2+ is the only live path.
- New endpoints are added to v1.2+ only — no backports.
