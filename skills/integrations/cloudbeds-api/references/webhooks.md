# Cloudbeds Webhooks

## Table of contents

- [Subscribe / list / unsubscribe](#subscribe--list--unsubscribe)
- [Delivery semantics](#delivery-semantics)
- [Authenticity / signature verification](#authenticity--signature-verification)
- [Payload envelope](#payload-envelope)
- [Event catalog](#event-catalog)
- [Handler patterns](#handler-patterns)

## Subscribe / list / unsubscribe

Subscription endpoints are part of PMS Classic v1.3:

```bash
# Subscribe
curl -X POST 'https://hotels.cloudbeds.com/api/v1.3/postWebhook' \
  -H 'Authorization: Bearer cbat_...' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'endpointUrl=https://your.app/webhooks/cloudbeds' \
  -d 'object=reservation' \
  -d 'action=created'
# Optional: ?propertyID=12345 appended to the URL for multi-property keys.

# List
curl 'https://hotels.cloudbeds.com/api/v1.3/getWebhooks' \
  -H 'Authorization: Bearer cbat_...'

# Unsubscribe
curl -X DELETE 'https://hotels.cloudbeds.com/api/v1.3/deleteWebhook?subscriptionID=do30k8kafl59zd' \
  -H 'Authorization: Bearer cbat_...'
```

`getWebhooks` response shape:

```json
{
  "success": true,
  "data": [
    {
      "id": "do30k8kafl59zd",
      "key": { "type": "property", "id": 12345 },
      "event": { "entity": "reservation", "action": "created" },
      "subscriptionType": "webhook",
      "subscriptionData": { "url": "https://your.app/webhooks/cloudbeds" }
    }
  ]
}
```

Subscription scope matches the read scope for the entity (e.g. `read:reservation` to subscribe to `reservation/*`).

When a user disconnects the app in Cloudbeds, all subscriptions are auto-deleted.

## Delivery semantics

- Delivery is HTTP `POST` with JSON body to your endpoint URL.
- 2xx response ACKs the event. Any non-2xx triggers retry.
- **Retry policy: up to 5 attempts at 1-minute intervals**, then abandoned for that event.
- **Handler responses after 2 seconds are treated as timeouts.** A 200 returned past the 2-second deadline triggers redelivery.
- Event order is **not** guaranteed.
- Duplicates are expected from two sources:
  1. Retries after the 2-second "timeout success" edge case.
  2. Cascading events — a single user action can fire multiple webhooks (e.g. `accommodation_type_changed` also triggers `accommodation_changed` and `assigned`).
- Cloudbeds de-dupes at delivery time, but your handler still receives duplicates for the reasons above.

## Authenticity / signature verification

**Cloudbeds does not publish an HMAC signature header.** No `X-Signature`, `X-Cloudbeds-Signature`, `X-Hub-Signature`, or equivalent is documented.

Trust model available to integrators:

- The endpoint URL is treated as a shared secret. Rotation = unsubscribe + resubscribe with a new URL via `postWebhook`.
- The payload's `propertyID` is validated against a known list.
- For high-stakes events, a follow-up API call (e.g. `getReservation` with the event's `reservationID`) confirms the referenced entity exists on the expected property.

IP allowlists for Cloudbeds senders are not published.

## Payload envelope

Every event includes at minimum:

| Field | Type | Notes |
|---|---|---|
| `version` | string | Major bump = breaking change; minor = additive. |
| `event` | string | `"object/action"`, e.g. `"reservation/created"`. |
| `timestamp` | number | UNIX seconds with microsecond decimals, e.g. `1611758157.431234`. |
| `propertyID` / `propertyId` | number or string | Case is event-specific. |
| `propertyID_str` / `propertyId_str` | string | Stringified property ID; preferred for storage. |

**Casing inconsistency is documented by Cloudbeds.** Some events emit `propertyId`, others `propertyID`. Handlers parse keys case-insensitively.

Key-spelling quirks to watch for:

- Allotment-block events: the event string in some examples is `allotmenBlock` (missing `t`). Parse both `allotmentBlock/*` and `allotmenBlock/*` spellings.
- Numeric vs string IDs: both forms appear; the `_str` variant is the canonical string.

## Event catalog

### Reservations (scope `read:reservation`)

| Event | Payload extras |
|---|---|
| `reservation/created` | `reservationID`, `startDate`, `endDate` |
| `reservation/status_changed` | `status` ∈ `in_progress`, `confirmed`, `not_confirmed`, `canceled`, `checked_in`, `checked_out`, `no_show`; `actor: {type, id}` |
| `reservation/dates_changed` | `subReservations[]`, `startDate`, `endDate` |
| `reservation/accommodation_status_changed` | `roomId`, `status` ∈ `occupied`, `unoccupied` |
| `reservation/accommodation_type_changed` | `subReservationId`, `roomTypeId` |
| `reservation/accommodation_changed` | `roomId`, `roomIdPrev`, `subReservationId` |
| `reservation/deleted` | `reservationId` |
| `reservation/notes_changed` | `reservationId`, `notes` |
| `reservation/custom_fields_changed` | `createdCustomFields[]`, `updatedCustomFields[{id, name, old_value, new_value}]`, `deletedCustomFields[]` |

### Guests (scope `read:guest`)

| Event | Payload extras |
|---|---|
| `guest/created` | `guestId` |
| `guest/assigned` | `guestId`, `reservationId`, `roomID` |
| `guest/removed` | `guestId`, `reservationId`, `roomID` |
| `guest/details_changed` | `guestId` |
| `guest/accommodation_changed` | `guestId`, `subReservationId`, `roomId`, `roomIdPrev` |

Modifications to guest-associated custom fields fire `guest/details_changed`, not `custom_fields_changed`.

### Integration

| Event | Scope | Extras |
|---|---|---|
| `integration/appstate_changed` | none | `clientID`, `oldState`, `newState` ∈ `enabled`, `pending`, `disabled`, `installing` |
| `integration/appsettings_changed` | `read:appPropertySettings` | `clientID`, `propertyId` |

### Room blocks (scope `read:roomBlock`)

| Event | Extras |
|---|---|
| `roomblock/created` | `roomBlockID`, `roomBlockType` ∈ `blocked_dates`, `out_of_service`; `roomBlockReason`; `startDate`; `endDate`; `rooms[{roomID, roomTypeID}]` |
| `roomblock/removed` | same |
| `roomblock/details_changed` | same |

### Allotment blocks (scope `read:allotmentBlock`)

`allotmentBlock/created`, `allotmentBlock/updated`, `allotmentBlock/deleted`, `allotmentBlock/capacity_changed_for_reservation`. Spec includes the typo `allotmenBlock` in some examples; handlers accept both spellings.

### Rate jobs (scope `read:rate`)

`api_queue_task/rate_status_changed` — `queueTaskId` (matches `jobReferenceID` from `patchRate`/`putRate`), `status` ∈ `in_progress`, `completed`, `error`.

### Housekeeping (scope `read:housekeeping`)

- `housekeeping/housekeeping_reservation_status_changed`
- `housekeeping/housekeeping_room_occupancy_status_changed`
- `housekeeping/room_condition_changed` — `condition` ∈ `dirty`, `clean`, `inspected`.

### Night audit (scope `read:nightAudit`)

`night_audit/completed` — `completedAt` is `"YYYY-MM-DD HH:MM:SS"` in property-local time (no offset).

### Custom fields (scope `read:reservation`)

See `reservation/custom_fields_changed` above.

### Accounting

`accounting/transaction` — `{internalTransactionCode, serviceDate, transactionDateTime, transactionId, parentTransactionId}`. Fired on posted transactions.

### Door locks (scope `read:doorLockKey`)

`doorLockKey/key_requested`, `doorLockKey/key_cancelled`.

### Fiscal documents (scope `read:payment`)

`fiscal_document/create`, `fiscal_document/update` — `{propertyId, documentKind, id, event, status}`.

## Handler patterns

A viable handler pattern that survives the 2-second deadline, duplicates, and out-of-order delivery:

1. Respond `200 OK` immediately with an empty body or a minimal JSON ack.
2. Enqueue the raw payload to a durable queue (SQS, Redis, Postgres LISTEN/NOTIFY, etc.).
3. A worker dedupes on a synthetic key, for example:
   - `reservation/*` → `(event, reservationID, propertyID_str, timestamp)`.
   - `guest/*` → `(event, guestId, propertyID_str, timestamp)`.
   - `roomblock/*` → `(event, roomBlockID, propertyID_str, timestamp)`.
4. On process, the worker fetches the canonical state from Cloudbeds (e.g. `getReservation`) rather than trusting the payload — order is not guaranteed, so the webhook carries only the "something happened" signal.
5. Token refreshes are scheduled outside the webhook path; concurrent refreshes can invalidate each other.

Testing endpoint: `https://webhook.site` creates a unique URL on page load and shows request/response for each POST.
