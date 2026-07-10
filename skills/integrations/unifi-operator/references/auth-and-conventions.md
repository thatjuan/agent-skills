# Auth & Conventions

Shared foundation for all four UniFi surfaces: credentials, base URLs, the cookie/CSRF login flow, response envelopes, pagination, the official filter DSL, error formats, and reusable shell helpers.

## Contents

- [API key creation (official APIs)](#api-key-creation-official-apis)
- [Official auth — X-API-KEY](#official-auth--x-api-key)
- [Private auth — UniFi OS login + CSRF](#private-auth--unifi-os-login--csrf)
- [Private auth — legacy controller (:8443)](#private-auth--legacy-controller-8443)
- [Account requirements & TLS](#account-requirements--tls)
- [Site identifier](#site-identifier)
- [Response envelopes](#response-envelopes)
- [Pagination](#pagination)
- [Official filter DSL](#official-filter-dsl)
- [Error formats](#error-formats)
- [Reusable shell helpers](#reusable-shell-helpers)

## API key creation (official APIs)

One console-wide key authenticates both the Network and Protect official APIs.

- **In Network app:** Settings → Control Plane → Integrations → Create New API Key.
- **In Protect app:** Settings → Control Plane → Integrations → API Keys → Create.
- **In UniFi OS / unifi.ui.com:** Control Plane → Admins & Users → (your admin) → Create API Key.

The key is shown once. It inherits the creating admin's permissions — a read-only admin yields a read-only key. It is scoped to the console (usable across that console's sites).

> A **Site Manager cloud key** generated at `unifi.ui.com → API` is a *different* key for the cloud base URL `https://api.ui.com` and does not apply to these local surfaces.

## Official auth — X-API-KEY

Stateless. No login, no cookies, no CSRF — ideal for cron/CI.

| Item | Value |
|------|-------|
| Header | `X-API-KEY: <key>` (+ `Accept: application/json`; `Content-Type: application/json` on writes) |
| Network base | `https://<host>/proxy/network/integration/v1` |
| Protect base | `https://<host>/proxy/protect/integration/v1` |
| Port | 443 |
| TLS | self-signed → `curl -k` |

## Private auth — UniFi OS login + CSRF

The internal API the web UI uses, on UDM / UDM-Pro/SE / UDR / UCG / UX / Cloud Key Gen2+.

1. **Login:** `POST https://<host>/api/auth/login` with JSON `{"username","password"}` (add `"token":"<otp>"` only if the account has MFA; `"rememberMe":true` optional).
2. **Capture** the `Set-Cookie: TOKEN=<jwt>` (the session; some builds name it `UOS_TOKEN`) **and** the `X-CSRF-Token` response header.
3. **Subsequent calls** go to `https://<host>/proxy/network/api/...` or `/proxy/protect/api/...`, sending the `TOKEN` cookie. Mutations (POST/PUT/PATCH/DELETE) also send header `x-csrf-token: <token>`. GETs do not need CSRF.
4. **Roll forward:** the server may rotate the token and return `X-Updated-CSRF-Token` on a response — carry that value into later mutations.
5. **Expiry:** `401` means the cookie/token expired — log in again.
6. **Logout:** `POST https://<host>/api/auth/logout` (with the CSRF header).

**Two ways to obtain the CSRF token:**

- **From the login response header** (simplest in shell): grab `X-CSRF-Token` from the response headers of the login call.
- **Decode the `TOKEN` JWT** (fallback when no header is present): the cookie value is a JWT; base64url-decode the middle segment (between the two `.`) and read `.csrfToken`.

```bash
# JWT-decode fallback
JWT=$(awk '/\tTOKEN\t/{print $7}' /tmp/uni.jar)        # cookie value from jar
PAYLOAD=$(printf '%s' "$JWT" | cut -d. -f2 | tr '_-' '/+')
CSRF=$(printf '%s==' "$PAYLOAD" | base64 -d 2>/dev/null | jq -r .csrfToken)
```

If a request is sent before any CSRF token is known, a plain `GET https://<host>/` returns an `X-CSRF-Token` header to seed login.

## Private auth — legacy controller (:8443)

Self-hosted Network controllers not on UniFi OS.

| Step | Request | Notes |
|------|---------|-------|
| Login | `POST https://<host>:8443/api/login` JSON `{"username","password","remember":true}` | Sets a `unifises` cookie. **No CSRF header needed.** |
| Requests | `https://<host>:8443/api/s/<site>/...` | No `/proxy/network` prefix |
| Logout | `POST https://<host>:8443/logout` | Legacy path |
| Status (no auth) | `GET https://<host>:8443/status` | Server version/health |

Auto-detect mode: a `GET https://<host>/` returning HTTP 200 (or a `TOKEN` cookie) indicates UniFi OS; otherwise legacy. Legacy issues `unifises`; UniFi OS issues `TOKEN`.

## Account requirements & TLS

- **Local admin only.** Scripted `/api/auth/login` requires a **local** UniFi OS / Protect account. Ubiquiti cloud-SSO (Ubiquiti-account) logins redirect and are unreliable for automation.
- **MFA off** for the automation account, or pass the current OTP in the `token` field each login.
- **Full read/write** of all device settings requires an admin-level local role.
- **Self-signed cert** on `https://<host>` — disable verification (`curl -k`) or pin the CA.

## Site identifier

A console hosts one or more **sites**. Paths differ by surface:

- **Private Network** uses the internal **slug** (a short name like `default`) in `/api/s/<slug>/...`. List slugs: `GET /proxy/network/api/self/sites` → each object's `name` is the slug; `desc` is the display label. `GET /proxy/network/api/stat/sites` adds health rollups.
- **Official Network** uses a per-console **UUID** `siteId` in `/v1/sites/{siteId}/...`. List: `GET /proxy/network/integration/v1/sites` → `data[].id`.
- **Protect** has no site slug — the console is a single Protect instance.

## Response envelopes

| Surface | Shape |
|---------|-------|
| Official (list) | `{ "offset":0, "limit":25, "count":25, "totalCount":142, "data":[...] }` |
| Official (single) | the object directly (no wrapper) |
| Private Network | `{ "meta":{ "rc":"ok" }, "data":[...] }` — `rc:"error"` carries `meta.msg`; a `meta.count` indicates `data` was truncated |
| Private Protect | the object/array directly (e.g. `/bootstrap` returns one big object) |

## Pagination

- **Official:** query params `offset` (default 0) and `limit` (default 25, max 200; vouchers default 100, max 1000). Read `totalCount` to know when to stop.
- **Private `stat/*`:** params `_start`, `_limit`, `_sort` (e.g. `_sort=-assoc_time`). Many `stat/*` reads accept a **POST JSON body** `{start, end, attrs, macs, type}` where `start`/`end` are **Unix milliseconds** (`stat/report/*`, `stat/session`, `stat/authorization`).

## Official filter DSL

List endpoints accept a `filter` query param: `<property>.<function>(<args>)`, combinable with `and(...)`, `or(...)`, `not(...)`. URL-encode it.

| Functions | Types |
|-----------|-------|
| `isNull`, `isNotNull`, `eq`, `ne`, `gt`, `ge`, `lt`, `le`, `like`, `in`, `notIn`, `isEmpty`, `contains`, `containsAny`, `containsAll`, `containsExactly` | STRING `'single-quoted'` (`''` escapes), INTEGER, DECIMAL, TIMESTAMP (ISO 8601), BOOLEAN, UUID, SET `[a,b,c]` |

`like` patterns: `.` = one char, `*` = any chars, `\` escapes. Examples:

```
id.eq(123)
name.like('guest*')
and(name.isNull(), createdAt.gt(2025-01-01T00:00:00Z))
not(name.like('guest*'))
```

```bash
curl -ksS "${H[@]}" --get "$NB/sites/$SITE/clients" \
  --data-urlencode "filter=or(name.like('lobby*'),name.like('guest*'))"
```

## Error formats

**Official** — JSON body plus HTTP status:

```json
{ "statusCode":401, "statusName":"UNAUTHORIZED",
  "code":"api.authentication.missing-credentials", "message":"Missing credentials",
  "timestamp":"2024-11-27T08:13:46.966Z", "requestPath":"/integration/v1/sites/123",
  "requestId":"3fa85f64-5717-4562-b3fc-2c963f66afa6" }
```

| Code | Meaning |
|------|---------|
| 200 | OK |
| 400 | Validation / malformed filter |
| 401 | Missing/invalid `X-API-KEY` (official) or expired cookie (private) |
| 403 | Key/role lacks permission |
| 404 | Unknown site/resource |
| 429 | Throttled (no published local rate limit; back off) |
| 500 | Server error — quote `requestId` when checking console logs |

**Private Network** — HTTP 200 with `meta.rc:"error"` and `meta.msg` such as `api.err.LoginRequired`, `api.err.NoSiteContext`, `api.err.InvalidObject`, `api.err.Invalid`. A `meta.rc` of `"ok"` marks success; any other value is a failure regardless of the `200` status.

## Reusable shell helpers

Drop-in bash for an operator session against one console:

```bash
HOST="192.168.1.1"
CURL=(curl -ksS)
JAR=/tmp/uni.jar

uni_login() {  # uni_login <user> <pass> [otp]
  CSRF=$("${CURL[@]}" -c "$JAR" -D - -o /dev/null -X POST \
    "https://$HOST/api/auth/login" -H "Content-Type: application/json" \
    -d "{\"username\":\"$1\",\"password\":\"$2\",\"token\":\"${3:-}\"}" \
    | awk 'tolower($1)=="x-csrf-token:"{print $2}' | tr -d '\r')
  export CSRF
}

uget() { "${CURL[@]}" -b "$JAR" "https://$HOST$1"; }                       # private GET
umut() { "${CURL[@]}" -b "$JAR" -H "x-csrf-token: $CSRF" \
           -H "Content-Type: application/json" "$@"; }                     # private mutation
oget() { "${CURL[@]}" -H "X-API-KEY: $KEY" -H "Accept: application/json" "$@"; } # official

# usage
uni_login admin 'secret'
uget /proxy/network/api/self/sites | jq -r '.data[].name'
umut -X POST "https://$HOST/proxy/network/api/s/default/cmd/stamgr" \
     -d '{"cmd":"kick-sta","mac":"aa:bb:cc:dd:ee:ff"}'
```

`jq` is assumed for JSON handling. Snapshots/exports are binary — write with `-o file` and skip `jq`.
