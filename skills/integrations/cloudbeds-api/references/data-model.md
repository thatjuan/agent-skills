# Cloudbeds data model

## Table of contents

- [ID formats](#id-formats)
- [Dates and timezones](#dates-and-timezones)
- [Money and currency](#money-and-currency)
- [Pagination](#pagination)
- [Filtering and sorting](#filtering-and-sorting)
- [Partial-update semantics](#partial-update-semantics)
- [Split reservations](#split-reservations)
- [Read-only fields](#read-only-fields)

## ID formats

All identifiers are stringified in API v1.2+ even when spec schemas label them `integer`. The v1.2 multi-island migration converted numeric IDs to strings.

| ID | Shape | Notes |
|---|---|---|
| `propertyID` / `propertyId` | digits as string | Event payloads often carry both `propertyId` and `propertyId_str`; the `_str` variant is canonical. |
| `organizationID` | digits as string | Group account identifier. |
| `reservationID` | string | Unique per property, not globally. |
| `subReservationID` | `{reservationID}-{n}` | One per room on multi-room reservations. Primary room's subReservationID equals the reservationID. Not guaranteed contiguous after deletes. |
| `thirdPartyIdentifier` | string | OTA / channel's reservation ID (Booking.com, Expedia, etc.). Used on `postReservation` to link a channel booking. |
| `guestID` | string | Per property. |
| `roomID` | `{roomTypeID}-{n}` | e.g. `123456-1`. |
| `roomTypeID` | string | |
| `sourceID` | string | Primary sources append `-1` (e.g. `s-2-1` for walk-in). |
| `clientID` | `app_...` | The integrating app's client ID, e.g. `app_VisTh9b2YzfjiJJ4Z`. |

Event payloads use inconsistent casing (`propertyID` vs `propertyId`, `guestId` vs `guestID`). Handlers parse keys case-insensitively.

## Dates and timezones

| Field type | Format | Timezone |
|---|---|---|
| `startDate`, `endDate`, `checkInFrom`, `checkInTo`, date-only fields | `YYYY-MM-DD` | Property-local calendar date, no timezone attached. |
| `dateCreated`, `dateModified`, `dateCancelled` | ISO `date-time` | Property-local. |
| `dateCreatedUTC`, `dateModifiedUTC`, `dateCancelledUTC` | ISO `date-time` | UTC. Preferred for cross-property sync and delta queries. |
| `reservationCheckIn`, `reservationCheckOut` | ISO `date-time` | Property-local. |
| Webhook `timestamp` | UNIX seconds with microsecond decimals | e.g. `1611758157.431234`; numeric type, not string. |
| Night audit `completedAt` | `"YYYY-MM-DD HH:MM:SS"` | Property-local, no offset. |

`getHotels` and `getHotelDetails` return `propertyTimezone` per property (IANA TZ name, e.g. `America/Los_Angeles`). Sync logic caches this per property to interpret the local date-time fields.

DST: use the `*UTC` variants when diffing across DST boundaries; local times repeat or skip across DST transitions.

## Money and currency

Classic PMS amounts (`grandTotal`, rates, charges) are JSON numbers (decimal). Float rounding is a real risk — parse amounts into decimal types (e.g. `Decimal` in Python, `BigDecimal` in Java, `decimal.js` in JavaScript) rather than floats for any computation.

`getHotelDetails` returns `propertyCurrency`:

```json
{
  "currencyCode": "USD",
  "currencySymbol": "$",
  "currencyPosition": "before",
  "currencyDecimalSeparator": ".",
  "currencyThousandsSeparator": ","
}
```

`currencyPosition` values: `before`, `after`. Currency codes are ISO 4217.

OTA Build-To-Us spec uses strings for amounts (e.g. `nightly_rate: "123.45"`) to preserve precision across partners.

Accounting API transactions use minor-unit integers in some fields and decimal strings in others; confirm per endpoint against `accounting-v1.0-openapi.json`.

## Pagination

| API | Style | Parameters |
|---|---|---|
| Classic PMS v1.3 (most list endpoints) | Page-based | `pageNumber` (default 1), `pageSize` (default 20). Response includes `count` (this page) and `total`. |
| Classic PMS v1.3 (some reservation endpoints) | Date-bounded | `resultsFrom`, `resultsTo` on booking date (or `modifiedFrom`, `modifiedTo`). |
| PMS v2 modular | Offset-based | `limit` (default 100, max 500), `offset` (default 0). |
| Accounting API | Cursor-based (on `/transactions`, `/pending-transactions`) | `pageToken` in request body, `limit` for page size. |
| Data Insights reports | Limited max records per call | Export 100 000; Preview 100; Run 12 000. |

## Filtering and sorting

Classic PMS takes per-endpoint query parameters (`status`, `modifiedFrom`, `checkInFrom`, etc.). Sort enum values are endpoint-specific — `getAvailableRoomTypes` accepts `sort` ∈ `room_name`, `hotel_name`, `room_price`, `hotel_stars`, and `order` ∈ `asc`, `desc`.

PMS v2 modules use a `filters` query parameter with `;`-separated expressions:

```
filters=field1:value;field2:operator:value
```

Accounting API uses a JSON filter DSL in POST bodies:

```json
{
  "filters": {
    "and": [
      { "operator": "greater_than_or_equal", "value": "2025-01-01T00:00:00Z", "field": "transaction_datetime" },
      { "operator": "equals", "value": "RESERVATION", "field": "source_kind" },
      { "operator": "equals", "value": "123", "field": "source_id" }
    ]
  },
  "limit": 100,
  "pageToken": null,
  "sort": [{ "field": "transaction_datetime", "direction": "asc" }]
}
```

Accounting filter constraints: the request must include one of (`id` with `equals`/`in`) OR (`source_id` + `source_kind`) OR (`external_relation_id` + `external_relation_kind`) OR (`transaction_datetime`).

## Partial-update semantics

- Classic PMS `put*` operations (e.g. `putReservation`, `putGuest`) accept partial payloads — only the fields included in the body are updated. Not true PUT-replace.
- `patchRate` (partial per-day rate updates) and `putRate` (bulk rate updates) are both async. Both return `jobReferenceID` and fire `api_queue_task/rate_status_changed` on completion. `patchRate` is limited to 30 intervals per call.
- Newer REST APIs (Accounting, Doorlocks, PMS v2) use HTTP `PATCH` with strict method semantics.

## Split reservations

When a guest's stay can't fit in a single room type, Cloudbeds may "split" the reservation across multiple rooms for non-overlapping date ranges within the same stay. The subReservation structure reflects this. There is no explicit flag — detect by walking stay-period data per subReservation.

## Read-only fields

Operations the API does not expose:

- **Create a rate plan** — rate plans are created in myfrontdesk; API only reads and updates existing plans (`getRatePlans`, `patchRate`, `putRate`).
- **Process refunds** — manual-only in Cloudbeds UI.
- **Auto-charge deposits on API-created reservations** — deposit rules configured in "Manage → Payment Options → Processing Methods → Mybooking Reservations" are not applied when `cardToken` is sent via `postReservation`. Post the payment manually or via `postCharge` after creating the reservation.
- **Return pending (unposted) transactions via `getTransactions`** — only posted folio transactions appear. Use Accounting API `/pending-transactions` for pending.
- **True SSO / OpenID Connect** — `userinfo` provides identity, but app login credentials are issued by the integrating app.
