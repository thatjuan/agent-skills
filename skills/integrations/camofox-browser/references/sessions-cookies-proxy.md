# Sessions, Cookies, Proxies & VNC

Operational details for per-user isolation, authenticated browsing, proxy/GeoIP routing, and interactive login via noVNC.

## Table of Contents

- [Session Model](#session-model)
- [Session Persistence](#session-persistence)
- [Cookie Import](#cookie-import)
- [Proxy Modes](#proxy-modes)
- [Backconnect Rotation](#backconnect-rotation)
- [GeoIP](#geoip)
- [VNC Interactive Login](#vnc-interactive-login)
- [Storage State Export & Reuse](#storage-state-export--reuse)

## Session Model

```
Browser (one Camoufox process)
└── Session (BrowserContext keyed by userId)   — cookies, localStorage, fingerprint
    └── Tab Group (sessionKey / listItemId)    — logical grouping within a session
        └── Tab (Page)
```

- `userId` → one `BrowserContext` with isolated storage. Different users never share cookies or fingerprints.
- `sessionKey` (alias `listItemId`) → logical tab group within a user, for bulk closure.
- Sessions expire after `SESSION_TIMEOUT_MS` of inactivity (default 30 min).
- Max `MAX_SESSIONS` (default 50) concurrent contexts. Max `MAX_TABS_PER_SESSION` (default 10) tabs — oldest recycled beyond the limit.
- Per-user concurrent requests capped by `MAX_CONCURRENT_PER_USER` (default 3) — enforced via `ctx.withUserLimit(userId, fn)`.

## Session Persistence

The `persistence` plugin hooks `session:creating` to load and `session:destroyed` to save each user's Playwright storage state. Layout:

```
~/.camofox/
├── cookies/              # Netscape bootstrap files you drop in
└── profiles/             # Managed by the persistence plugin
    └── <hashed-userId>/
        └── storage_state.json
```

`userId`s are hashed before being used as directory names to avoid filesystem issues. Override the base directory with `CAMOFOX_PROFILE_DIR`. Disable the plugin by editing `camofox.config.json`:

```json
{ "plugins": ["youtube"] }
```

Or set `"persistence": { "enabled": false }` if the plugin supports runtime config. Atomic writes via `lib/persistence.js` prevent half-written state files.

## Cookie Import

Netscape-format cookie files under `~/.camofox/cookies/` (override via `CAMOFOX_COOKIES_DIR`) are imported on demand.

End-to-end flow:

```
~/.camofox/cookies/linkedin.txt          (Netscape format, on disk)
        │
        ▼
camofox_import_cookies (OpenClaw tool)   (parses file, filters by domain)
        │
        ▼  POST /sessions/:userId/cookies
        │  Authorization: Bearer $CAMOFOX_API_KEY
        │  Body: { cookies: [Playwright cookie objects] }
        ▼
camofox server                           (validates, sanitizes, injects)
        │
        ▼  context.addCookies(...)
        ▼
Camoufox session                         (authenticated browsing)
```

Constraints:

- `cookiesPath` resolves relative to the cookies directory. Path traversal outside it is blocked.
- Max 500 cookies per request.
- Max 5 MB file size.
- Each cookie object is sanitized to an allowlist of Playwright fields (`name`, `value`, `domain`, `path`, `expires`, `httpOnly`, `secure`, `sameSite`).

Cookie-import is disabled if `CAMOFOX_API_KEY` is unset — the endpoint returns `403`.

Direct server usage (no OpenClaw):

```bash
curl -X POST http://localhost:9377/sessions/agent1/cookies \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_CAMOFOX_API_KEY' \
  -d '{"cookies":[{"name":"foo","value":"bar","domain":"example.com","path":"/","expires":-1,"httpOnly":false,"secure":false}]}'
```

## Proxy Modes

### Simple (single endpoint)

```bash
export PROXY_HOST=166.88.179.132
export PROXY_PORT=46040
export PROXY_USERNAME=myuser
export PROXY_PASSWORD=mypass
npm start
```

All browser traffic routes through one endpoint. Good for static exit IPs.

### Backconnect (rotating sticky sessions)

Providers like Decodo, Bright Data, or Oxylabs offer a single gateway with session-based sticky IPs — each logical session resolves to a different exit IP:

```bash
export PROXY_STRATEGY=backconnect
export PROXY_BACKCONNECT_HOST=gate.provider.com
export PROXY_BACKCONNECT_PORT=7000
export PROXY_USERNAME=myuser
export PROXY_PASSWORD=mypass
export PROXY_PROVIDER=decodo          # session-format identifier
npm start
```

Each `BrowserContext` (i.e., each `userId`) gets a unique sticky session token, so different users get different IP addresses. Sessions rotate on proxy errors or Google-block responses.

`PROXY_COUNTRY` and `PROXY_STATE` narrow the pool to specific geos.

## Backconnect Rotation

Failure triggers (observed in `lib/` proxy pool) for rotating a sticky session:

- Proxy tunnel errors (connection refused, timeout).
- Google bot-detection pages (`/sorry/index`, reCAPTCHA walls).
- Explicit block status codes from upstream.

Rotated sessions invalidate the cached session token for that `userId` so the next request gets a fresh exit IP.

## GeoIP

When a proxy is configured, Camoufox's built-in GeoIP derives from the proxy's exit IP:

- `locale` — e.g., `en-US`, `ja-JP`
- `timezone` — e.g., `Asia/Tokyo`
- `geolocation` — lat/long coordinates

This keeps the browser fingerprint (language, timezone, coords) consistent with the proxy's apparent location — a site that checks timezone vs. IP geolocation won't see a mismatch.

Without a proxy, defaults: `en-US`, `America/Los_Angeles`, San Francisco coordinates.

## VNC Interactive Login

Use when a site requires a flow the agent can't automate (e.g., CAPTCHA, 2FA prompt). A human drives the browser through noVNC, then the resulting cookies/localStorage are exported and reused by agents.

Enable:

```bash
export ENABLE_VNC=1
export VNC_PASSWORD="strong-password"  # required in production
# Optional: export NOVNC_PORT=6080
```

Docker:

```bash
docker run -p 9377:9377 -p 6080:6080 \
  -e ENABLE_VNC=1 -e VNC_PASSWORD="strong-password" \
  camofox-browser
```

The `vnc` plugin hooks `browser:launching` to set `virtual_display_resolution` (e.g., `1920x1080x24`) and exposes noVNC at `http://<host>:<NOVNC_PORT>/`.

Implementation lives in two files to respect the OpenClaw scanner:
- `plugins/vnc/index.js` — route registration, no `child_process`.
- `plugins/vnc/vnc-launcher.js` — `x11vnc` / `websockify` spawning.

## Storage State Export & Reuse

After a VNC-driven login, export the resulting state:

```bash
GET /sessions/:userId/storage_state
```

Returns the Playwright `{ cookies, origins }` shape. Persist it (agent-side) and later inject it into fresh sessions by either:

- Relying on the `persistence` plugin to auto-restore via `session:creating` (default).
- Manually mutating `contextOptions.storageState` in a custom plugin's `session:creating` listener:

```js
events.on('session:creating', ({ userId, contextOptions }) => {
  const saved = loadStorageState(userId);
  if (saved) contextOptions.storageState = saved;
});
```

`session:creating` is emitted via `emitAsync()` — the server awaits async listeners before creating the context, so loading from disk is safe.
