# Cloudbeds endpoint catalog

## Table of contents

- [PMS Classic v1.3 — RPC-style](#pms-classic-v13--rpc-style)
- [PMS v2 — modular REST](#pms-v2--modular-rest)
- [Accounting API v1.0](#accounting-api-v10)
- [Data Insights API v1.1](#data-insights-api-v11)
- [Group Profile API v1.0](#group-profile-api-v10)
- [Fiscal Documents API v1](#fiscal-documents-api-v1)
- [Payments surface](#payments-surface)
- [OTA Build-To-Us v5.3](#ota-build-to-us-v53)

Authoritative specs: `https://github.com/cloudbeds/openapi-specs` (`src/*.yaml|json`).

## PMS Classic v1.3 — RPC-style

Base: `https://api.cloudbeds.com/api/v1.3/`. Operation IDs are embedded in the path (e.g. `POST /postReservation`). Request bodies are `application/x-www-form-urlencoded`.

### Reservations

| Method | Path | Purpose |
|---|---|---|
| POST | `/postReservation` | Create reservation. Required: `startDate`, `endDate`, `guestFirstName`, `guestLastName`, `guestCountry` (ISO-2), `guestZip`, `guestEmail`, `rooms[]`, `adults[]`, `children[]`, `paymentMethod`. |
| GET  | `/getReservation` | Fetch one by `reservationID`. |
| GET  | `/getReservations` | Search (`status`, `resultsFrom/To`, `modifiedFrom/To`, `checkInFrom/To`, `checkOutFrom/To`, `pageNumber`, `pageSize`, `includeGuestsDetails`). |
| GET  | `/getReservationsWithRateDetails` | Same plus per-night rate breakdown. |
| GET  | `/getReservationAssignments` | Room assignments. |
| GET  | `/getReservationRoomDetails` | Per-room stay details. |
| PUT  | `/putReservation` | Partial update (dates, status, room type — reprices on type change). |
| POST | `/postReservationNote` | Add note. |
| GET  | `/getReservationNotes` | List notes. |
| PUT  | `/putReservationNote` | Edit note. |
| DELETE | `/deleteReservationNote` | Remove note. |
| POST | `/postReservationDocument` | Attach document. |
| POST | `/postRoomCheckIn` | Check in. |
| POST | `/postRoomCheckOut` | Check out. |
| POST | `/postRoomAssign` | Assign room. |

### Guests

`/getGuest`, `/getGuestList`, `/getGuestsModified`, `/getGuestsByStatus`, `/getGuestsByFilter`, `/postGuest`, `/putGuest`, `/postGuestsToRoom`, `/postGuestDocument`, `/postGuestPhoto`, `/postGuestNote`, `/getGuestNotes`, `/putGuestNote`, `/deleteGuestNote`.

### Rooms / room types / availability

| Method | Path | Notes |
|---|---|---|
| GET | `/getAvailableRoomTypes` | Availability search. Required: `startDate`, `endDate`, `rooms`, `adults`, `children`. Optional: `promoCode`, `detailedRates`, `includeSharedRooms`, `sort` ∈ {`room_name`,`hotel_name`,`room_price`,`hotel_stars`}, `order`, `minRate`, `maxRate`, `pageNumber`, `pageSize`. |
| GET | `/getRoomTypes` | Room-type catalog. |
| GET | `/getRooms` | All rooms. |
| GET | `/getRoomsUnassigned` | Rooms with no assignment. |
| GET | `/getRoomsFeesAndTaxes` | Fees + taxes per room. |
| POST | `/postRoomBlock` | Block rooms. |
| GET | `/getRoomBlocks` | List blocks. |
| PUT | `/putRoomBlock` | Edit block. |
| DELETE | `/deleteRoomBlock` | Remove block. |

### Rates

| Method | Path | Notes |
|---|---|---|
| GET | `/getRate` | Rate for a room type + date range. |
| GET | `/getRatePlans` | Rate plan catalog (filter by room type, promo code). |
| GET | `/getRateJobs` | Job tracker for async rate updates (jobs retained 7 days). |
| POST | `/patchRate` | Partial rate update. Async — returns `jobReferenceID`. Limit: 30 intervals per call. |
| POST | `/putRate` | Full rate update. Async — returns `jobReferenceID`. |

Subscribe to webhook `api_queue_task/rate_status_changed` for async completion. `jobReferenceID` == `queueTaskId` in the webhook.

### Payments (classic)

`/postPayment`, `/postCharge`, `/postCustomPaymentMethod`, `/getPaymentMethods`, `/getPaymentsCapabilities`, `/postVoidPayment`, `/postCreditCard`.

### Housekeeping

`/getHousekeepingStatus`, `/postHousekeepingStatus`, `/postHousekeeper`, `/putHousekeeper`, `/getHousekeepers`, `/postHousekeepingAssignment`.

### Properties / hotels

| Method | Path | Returns |
|---|---|---|
| GET | `/getHotels` | Array: `propertyID`, `propertyName`, `propertyTimezone`, `propertyCurrency[]`. |
| GET | `/getHotelDetails` | Single-property: `propertyAddress`, `propertyCurrency{currencyCode, currencySymbol, currencyPosition, currencyDecimalSeparator, currencyThousandsSeparator}`, `propertyPolicy{propertyCheckInTime, propertyCheckOutTime, ...}`, `propertyAmenities[]`, `taxID`, `taxID2`, `companyLegalName`, `organizationID`, `propertyPrimaryLanguage`. |

### Users / auth

`/oauth/metadata`, `/access_token`, `/userinfo`, `/getUsers`.

### Webhooks (subscription)

`POST /postWebhook` — params: `object`, `action`, `endpointUrl`, optional `?propertyID=`. `GET /getWebhooks`. `DELETE /deleteWebhook?subscriptionID=...`.

### Adjustments / house accounts / groups / items / other

- Adjustments: `/postAdjustment`, `/deleteAdjustment`.
- Allotment blocks: `/createAllotmentBlock`, `/deleteAllotmentBlock`, `/getAllotmentBlocks`, `/updateAllotmentBlock`, notes CRUD.
- App property settings: `/getAppPropertySettings`, `/postAppPropertySettings`, `/putAppPropertySettings`, `/deleteAppPropertySettings`.
- App state: `/getAppState`, `/postAppState`.
- App errors: `/postAppError`.
- Custom fields: `/getCustomFields`, `/postCustomField`.
- Currency: `/getCurrencySettings`.
- Dashboard: `/getDashboard`.
- Email: `/getEmailTemplates`, `/postEmailTemplate`, `/getEmailSchedule`, `/postEmailSchedule`.
- Files: `/postFile`, `/getFiles`.
- Government receipts: `/postGovernmentReceipt`.
- Groups: `/getGroups`, `/putGroup`, `/patchGroup`, `/postGroupNote`, `/getGroupNotes`.
- House accounts: `/getHouseAccountList`, `/postNewHouseAccount`, `/putHouseAccountStatus`.
- Items/inventory: `/getItem`, `/getItems`, `/postItem`, `/postCustomItem`, `/appendCustomItem`, `/postVoidItem`, `/postItemsToInventory`, `/putItemToInventory`, `/getItemCategories`, `/postItemCategory`.
- Packages: `/getPackages`, `/getPackageNames`.
- Sources: `/getSources` (primary sources use `-1` suffix on their IDs for `postReservation`).
- Taxes & fees: `/getTaxesAndFees`.

## PMS v2 — modular REST

Base: `https://api.cloudbeds.com/`. Each module has its own path-embedded version. `application/json` throughout. Property via `x-property-id` header (comma-separated for multi-property). Pagination: `limit` (default 100, max 500), `offset`. Filtering: `filters=field:value;field:op:value`.

| Module | Paths |
|---|---|
| Addons | `GET /addons/v1/addons` |
| Amenities | `GET /amenities/v1/catalogs/amenities`, `GET /amenities/v1/catalogs/categories` |
| Connected applications | `GET /integration/v1/connected-applications` |
| Doorlocks | `GET /doorlock/v1/keys` (scope `read:doorLockKey`) |
| Events v2 | `GET /events/v2/events` |
| Integration events | `GET /integration/v1/events` |
| Items | `GET /item/v1/items`, `POST /item/v1/custom-items` |
| Market segmentation | `GET /market-segmentation/v1/groups`, `GET /market-segmentation/v1/segments` |
| Property system | `GET /property/v1/system` |
| Rooms out-of-service | `GET /rooms/v1/out-of-service` |
| Smart policies | `GET /smart-policies/v1/exceptions`, `POST /smart-policies/v1/exceptions/eligible-rates/search` |

## Accounting API v1.0

Base: `https://api.cloudbeds.com/accounting/v1.0/`. JSON. Supersedes classic `/getTransactions` for new accounting integrations.

| Area | Endpoints |
|---|---|
| Accounts-receivable ledgers | `GET/POST /accounts-receivable-ledgers`, `GET /accounts-receivable-ledgers/{id}`, `PATCH /accounts-receivable-ledgers`, `GET /accounts-receivable-ledgers/totals`, `GET /accounts-receivable-ledgers/{id}/transactions` |
| Balance transfers (async) | `POST` / `DELETE /accounts-receivable-ledgers/{id}/reservation/{reservationId}/balance-transfer`, `POST /accounts-receivable-ledgers/{id}/group-profile/{groupProfileId}/balance-transfer` |
| Folios | `GET/POST/PATCH/DELETE /folios`, `POST /folios/transactions/move|route|unroute`, `GET /folios/transactions`, `GET /folios/rules`, `POST /folios/configurations/{id}/set-default`, `POST /folios/configurations/sources` |
| Routing rules | `POST /routing-rules`, `GET /routing-rules`, etc. |
| Transactions | `POST /transactions` (search with filter body), `POST /pending-transactions` (search) |
| Transaction codes | `GET /internal-transaction-codes`, `GET /custom-transaction-codes`, `PUT /custom-transaction-codes`, `POST /custom-transaction-codes/initialize`, `GET /custom-general-ledger-codes`, `PUT /custom-general-ledger-codes` |
| Deposits | `POST /deposits/transfer` (async), `GET /deposits/balance`, `GET /deposits/transactions` |
| Trial balance | `GET /trial-balance/configuration`, `POST /trial-balance/configuration` (once-per-property), `POST /trial-balance/configuration/calculate` (preview), `GET /trial-balance/configuration/status`, `GET /trial-balance/report` |
| Source balances | `GET /source-balances/{sourceKind}/{sourceId}`, `GET /source-balances/snapshots/{reservationId}` |
| Settings | `GET /settings`, `PATCH /settings` |

Transaction search filter DSL (POST body) supports AND/OR nesting with operators (`equals`, `in`, `greater_than_or_equal`, etc.). Filters must include one of: `id` + `equals|in`, `source_id` + `source_kind`, `external_relation_id` + `external_relation_kind`, or `transaction_datetime`.

Canonical internal transaction codes (partial): `1000` Room Rate, `1000A` Adjustment, `1000V` Void, `1100` Room Revenue, `1200` No Show. Full list at `https://myfrontdesk.cloudbeds.com/hc/en-us/articles/36232286180763`.

## Data Insights API v1.1

Base: `https://api.cloudbeds.com/datainsights/v1.1/`. 91 endpoints.

| Area | Endpoints |
|---|---|
| Charts | `/charts`, `/charts/{id}` |
| Datasets | `/datasets`, `/datasets/{id}`, `/datasets/{id}/multi_levels` |
| CDFs (Custom Data Fields) | `/datasets/{id}/cdfs`, `/datasets/{id}/cdfs/{cdfId}` |
| Folders | `/folders`, `/folders/{id}`, `/folders/{id}/reports` |
| Hubs | `/hubs`, `/hubs/{id}/cards` |
| Reports | `/reports`, `/reports/{id}`, `/reports/{id}/data`, `/reports/{id}/summary`, `/reports/{id}/export`, `/reports/query/data`, `/reports/query/summary`, `/reports/query/export`, `/reports/{id}/export/async`, `/reports/export/async`, `/reports/filters/relative_dates`, `/reports/limits`, `/reports/formats` |
| Schedules | `/schedules`, `/schedules/{id}/run` |
| Stock reports | `/stock_reports`, `/stock_reports/{id}/data` |

Spec-declared limits: export 100 000 records max; preview data/summary 100 records; run data/summary 12 000 records.

## Group Profile API v1.0

Base: `https://api.cloudbeds.com/group-profile/v1/`. Profile kinds: `Company`, `Group`, `TravelAgent`.

| Method | Path |
|---|---|
| GET/POST | `/profiles` |
| GET/PATCH/DELETE | `/profiles/{profileId}` |
| GET/POST | `/profiles/{profileId}/persons` |
| GET/POST | `/profiles/{profileId}/contact-persons` |
| GET/POST/DELETE | `/profiles/{profileId}/notes` |
| GET/POST/DELETE | `/profiles/{profileId}/tags` |
| GET/POST/DELETE | `/profiles/{profileId}/documents` |

## Fiscal Documents API v1

Base: `https://api.cloudbeds.com/fiscal-document/v1/`. Rolling out through Q1 2026 region by region.

| Area | Endpoints |
|---|---|
| Registration rules | `GET /fiscalization/registration/rules`, `POST /fiscalization/registration/validate` |
| Providers / credentials | `GET /providers`, `GET/POST /providers/{providerId}/credentials` |
| Series / sequences | `GET/POST /series` |
| Documents | `POST /documents`, `GET /documents/{id}`, `POST /documents/{id}/cancel` |
| Tax rules | `GET /tax-rules` |

Header: `X-Property-ID` (PascalCase in spec; case-insensitive in HTTP).

## Payments surface

| Product | Base | Endpoints |
|---|---|---|
| Payments Vault (tokenization) | `https://api.payments.cloudbeds.com/vault/v1/` | `POST /tokens/card` → returns token `id` usable as `paymentMethodId` in `postCreditCard`/`postCharge` |
| Pay-By-Link | `https://api.cloudbeds.com/payments/v2/pay-by-link` | `POST /`, `GET /{uuid}`. Requires `payByLink: true` in `getPaymentsCapabilities`. |
| Payment Element web component | n/a | `@cloudbeds/payment-element-webcomponent` — browser PCI-safe card widget. Demo: `https://payment-element.cloudbeds.com/0.5.9/demo/index.html` |
| Classic PMS payments | `https://api.cloudbeds.com/api/v1.3/` | `postCharge`, `postCreditCard`, `postPayment`, `postVoidPayment`, `getPaymentMethods`, `getPaymentsCapabilities` |

## OTA Build-To-Us v5.3

Partners (OTAs) host this API; Cloudbeds is the **client**. Base: `https://api.your-ota.com/cloudbeds/v5.3` (partner-hosted; auth via `shared_secret` query param).

| Method | Purpose |
|---|---|
| `HealthCheck` | Is the OTA reachable |
| `SetupProperty` | Associate Cloudbeds property with OTA |
| `GetRoomTypes`, `GetRatePlans` | Pull OTA structures |
| `ARIUpdate` | Push availability, rates, restrictions from Cloudbeds to OTA |
| `GetBookingList`, `GetBookingId` | Pull new / specific bookings |
| `AckBooking` | Acknowledge receipt |
| `CancelBooking` | Cancel |
| `CheckAvailability`, `BookingCreate` | Availability-check and booking push (rare direction) |
| `NotifyBooking` | Inbound push notification |
| `CreateGroup`, `GetSubProperties`, `ChannelList` | Group/sub-property management |

Partner onboarding: `https://www.cloudbeds.com/partner-with-cloudbeds/`.
