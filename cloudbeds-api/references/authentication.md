# Cloudbeds Authentication

## Table of contents

- [Token types](#token-types)
- [API key (automatic delivery) flow](#api-key-automatic-delivery-flow)
- [OAuth 2.0 authorization code flow](#oauth-20-authorization-code-flow)
- [Refresh token behavior](#refresh-token-behavior)
- [OAuth → API-key migration](#oauth--api-key-migration)
- [Redirect URI rules](#redirect-uri-rules)
- [Scopes](#scopes)
- [Multi-property / association access](#multi-property--association-access)
- [/userinfo](#userinfo)
- [App states and disconnection](#app-states-and-disconnection)
- [Credential storage rules](#credential-storage-rules)

## Token types

| Token | Prefix | Lifetime | Where sent |
|---|---|---|---|
| API key | `cbat_` | Unlimited; dies after 30 days of non-use | `Authorization: Bearer cbat_...` or `x-api-key: cbat_...` |
| OAuth access token | none documented | 8 hours (`expires_in: 28800`) | `Authorization: Bearer <token>` |
| OAuth refresh token | none documented | 365 days, sliding (resets on each use) | `POST /access_token` form body |
| Authorization code | none | 10 minutes, single-use | `POST /access_token` form body |

## API key (automatic delivery) flow

Used by marketplace / technology-partner apps. The flow mimics OAuth authorize-redirect but the final exchange returns an API key, not an access token.

1. Cloudbeds redirects the user back to your `redirect_uri` with `?code=...&state=...` after the user clicks "Allow Access" on the marketplace connect screen.
2. Exchange the code for an API key:

```bash
curl -X POST 'https://hotels.cloudbeds.com/api/v1.1/access_token' \
  --form 'grant_type=urn:ietf:params:oauth:grant-type:api-key' \
  --form 'client_id=myApp_xxxxx' \
  --form 'client_secret=myclientsecret' \
  --form 'redirect_uri=https://your.app/oauth/callback' \
  --form 'code=EXAMPLE_AUTHORIZATION_CODE'
```

3. Response body (`200 OK`, `application/json`):

```json
{ "access_token": "cbat_EXAMPLE_API_KEY_REPLACE_ME" }
```

Store the `cbat_...` value; that **is** the long-lived API key.

The property-level (self-service) dashboard path for generating keys: log in at `https://signin.cloudbeds.com/` → **Account → Apps & Marketplace → API Credentials → + New Credentials**. Tick "Enable for entire organization" to scope the key across all properties of a group.

## OAuth 2.0 authorization code flow

| Endpoint | URL |
|---|---|
| Authorize (browser) | `https://hotels.cloudbeds.com/api/v1.3/oauth?client_id=...&redirect_uri=...&response_type=code&scope=...&state=...` |
| Token exchange | `POST https://hotels.cloudbeds.com/api/v1.3/access_token` |
| Userinfo | `GET https://hotels.cloudbeds.com/api/v1.3/userinfo` |

Supported `grant_type` values (from the PMS v1.3 OpenAPI `PostAccessTokenRequest` schema):

- `authorization_code`
- `refresh_token`
- `urn:ietf:params:oauth:grant-type:api-key`
- `refresh_token_exchange` (OAuth → API-key migration; not in spec but documented)

Example token exchange:

```bash
curl -X POST 'https://hotels.cloudbeds.com/api/v1.3/access_token' \
  -d 'grant_type=authorization_code' \
  -d 'client_id=myApp_xxxxx' \
  -d 'client_secret=myclientsecret' \
  -d 'redirect_uri=https://your.app/oauth/callback' \
  -d 'code=EXAMPLE_AUTHORIZATION_CODE'
```

Successful response (`PostAccessTokenResponse`):

```json
{
  "access_token": "EXAMPLE_OAUTH_ACCESS_TOKEN",
  "token_type": "Bearer",
  "expires_in": 28800,
  "refresh_token": "0987654edcba...",
  "resources": [
    { "type": "property",    "id": "12345" },
    { "type": "association", "id": "999" }
  ]
}
```

The `resources` array lists what the user consented to. `type` values: `property`, `association`.

## Refresh token behavior

Refresh flow:

```bash
curl -X POST 'https://hotels.cloudbeds.com/api/v1.3/access_token' \
  -d 'grant_type=refresh_token' \
  -d 'client_id=myApp_xxxxx' \
  -d 'client_secret=myclientsecret' \
  -d 'refresh_token=0987654edcba...'
```

- Refresh tokens have a 365-day expiration that **slides forward on every successful use**. A token unused for 365 days dies and a re-authorization is required.
- The response includes a `refresh_token` field. Persist whatever is returned (rotation-on-refresh is not explicitly documented, but treat the returned value as authoritative).
- Concurrent refresh calls can race and invalidate each other — webhook handlers avoid triggering a refresh; they schedule refreshes elsewhere.

## OAuth → API-key migration

One-shot exchange:

```bash
curl -X POST 'https://hotels.cloudbeds.com/api/v1.2/access_token' \
  -d 'grant_type=refresh_token_exchange' \
  -d 'client_id=br**_xxxxx' \
  -d 'client_secret=123456abcd' \
  -d 'refresh_token=0987654edcba'
# → {"access_token": "cbat_xyz123"}
```

After this exchange, the old refresh token is dead; reusing it invalidates the new API key.

## Redirect URI rules

- `https://` is mandatory. Non-TLS redirect URIs are rejected.
- Subdomains are accepted.
- Wildcards are not accepted (cannot register `https://*.mydomain.com`).
- Dynamic query parameters are not accepted, except `state` which is passed through intact.
- `localhost` is accepted, enabling desktop/CLI clients.

## Scopes

Full scope list from `pms-v1.3-openapi.yaml`:

**Read** (20): `read:allotmentBlock`, `read:appPropertySettings`, `read:communication`, `read:currency`, `read:customFields`, `read:dashboard`, `read:group`, `read:guest`, `read:hotel`, `read:houseAccount`, `read:housekeeping`, `read:item`, `read:package`, `read:payment`, `read:rate`, `read:reservation`, `read:room`, `read:roomblock`, `read:taxesAndFees`, `read:user`.

**Write** (17): `write:adjustment`, `write:allotmentBlock`, `write:appError`, `write:appPropertySettings`, `write:communication`, `write:customFields`, `write:group`, `write:guest`, `write:hotel`, `write:houseAccount`, `write:housekeeping`, `write:item`, `write:payment`, `write:rate`, `write:reservation`, `write:room`, `write:roomblock`.

**Delete** (3): `delete:adjustment`, `delete:appPropertySettings`, `delete:roomblock`.

**Additional** (appearing on newer APIs/webhooks): `read:addon` (PMS v2 addons), `read:doorLockKey` (PMS v2 doorlocks), `read:nightAudit` (night_audit webhook), `read:roomBlock` (room-block webhooks).

Webhook subscriptions require the same scope that reads the entity. Subscribing to `reservation/created` requires `read:reservation`.

Adding scopes after the key is issued requires regenerating the key (delete and recreate with the new scope set).

## Multi-property / association access

Classic PMS v1.3: `propertyID` is a **query or form parameter**.

- Single: `?propertyID=12345`.
- Multiple: `?propertyID=37,345,89`.
- Some endpoints accept the plural form `propertyIDs`.

PMS v2 and newer APIs: `propertyID` is a **header**.

- Most specs: `x-property-id` (lowercase).
- Fiscal Documents spec: `X-Property-ID` (PascalCase). HTTP headers are case-insensitive; emit `x-property-id`.
- Accepts a comma-separated list of property IDs.

Group / association support is **off by default** for partner apps. Enable it via `integrations@cloudbeds.com`. Once enabled, enumerate properties via `getHotels` and loop calls with explicit `propertyID` per property. Call `postAppState` per property when the app connects.

Error returned by multi-property keys missing `propertyID`:

```json
{ "success": false, "message": "Please specify \"propertyID\" parameter for this call" }
```

## /userinfo

```
GET https://hotels.cloudbeds.com/api/v1.3/userinfo
Authorization: Bearer <token>
```

Optional query: `property_id=<id>`, `role_details=true`.

Response fields: `user_id`, `first_name`, `last_name`, `email`, `acl[]`, `roles[]`. Returns the human who granted consent. True OpenID Connect / SSO is not supported; app login credentials are issued by the integrating app.

## App states and disconnection

- `getAppState` / `postAppState` set/read app state per property: `enabled`, `pending`, `disabled`, `installing`.
- When the user disconnects the app in Cloudbeds, subscriptions are auto-deleted and API calls return `401` / `access_denied`.
- An in-app disconnect button triggers `postAppState` with `state=disabled` to mirror the state on Cloudbeds' side.
- Webhook `integration/appstate_changed` notifies of state transitions.

## Credential storage rules

From the API Security Standards doc:

- Cloudbeds user passwords, credit card numbers, and financial information are out of scope for integration storage per the security standards.
- Cloudbeds Access Credentials (API keys, client secrets, refresh tokens) are confidential per the security standards — stored encrypted at rest, excluded from logs, kept server-side only.
