---
name: camofox-browser
description: Deploy, configure, and use camofox-browser — the Camoufox-engine anti-detection browser server (REST API on port 9377) for AI agents. Use when code hits `http://localhost:9377/tabs`, `/sessions/:userId/cookies`, or `/youtube/transcript`; when scripts install `@askjo/camofox-browser`, run `npm start` in the `camofox-browser` repo, or call `make up`/`make fetch`; when agents invoke OpenClaw `camofox_*` tools (`create_tab`, `snapshot`, `click`, `type`, `navigate`, `scroll`, `screenshot`, `close_tab`, `list_tabs`, `import_cookies`); when the user asks about Camoufox fingerprint spoofing, bypassing Cloudflare/Google bot detection, element refs (`e1`, `e2`), accessibility snapshots, search macros (`@google_search`, `@reddit_subreddit`), Netscape cookie import, session isolation, backconnect proxy rotation with GeoIP, VNC/noVNC login, writing `plugins/<name>/index.js` with `register(app, ctx)`, `CAMOFOX_*`/`PROXY_*` env vars, or deploying to Docker/Fly.io/Railway.
---

# camofox-browser

Headless browser automation server wrapping [Camoufox](https://camoufox.com) (Firefox fork with C++-level fingerprint spoofing) behind a REST API designed for AI agents. Default port `9377`. Source: https://github.com/jo-inc/camofox-browser

## What It Is

A Node.js/Express server (`server.js`) that exposes a Camoufox browser engine as HTTP endpoints. Agents create tabs, fetch token-efficient accessibility snapshots with stable element refs (`e1`, `e2`, …), and interact by ref rather than by CSS selector or raw coordinates. Cookies, proxies, search macros, YouTube transcript extraction, and session persistence are built in. Plugins extend the server with new routes, lifecycle hooks, and Prometheus metrics.

## Architecture

```
Browser Instance (Camoufox)
└── User Session (BrowserContext)   — isolated cookies/storage per userId
    ├── Tab Group (sessionKey)      — groups tabs by conversation/task
    │   ├── Tab (google.com)
    │   └── Tab (github.com)
    └── Tab Group
        └── Tab
```

Key behaviors:
- Lazy browser launch. Idle browser shuts down after `BROWSER_IDLE_TIMEOUT_MS` (default 5min), relaunches on next request. Idle memory ≈ 40 MB.
- Sessions auto-expire after `SESSION_TIMEOUT_MS` (default 30 min).
- When a session hits `MAX_TABS_PER_SESSION`, the oldest/least-used tab is recycled instead of erroring.
- All logs are one JSON object per line (`{ts, level, msg, reqId, …}`). `/health` is excluded from request logging.

## Install & Run

Standalone:

```bash
git clone https://github.com/jo-inc/camofox-browser
cd camofox-browser
npm install
npm start            # downloads Camoufox on first run (~300MB)
# → http://localhost:9377
```

As an OpenClaw plugin:

```bash
openclaw plugins install @askjo/camofox-browser
```

Docker (uses provided `Makefile`, which pre-downloads Camoufox + yt-dlp outside the build via bind mounts):

```bash
make up              # auto-detects ARCH (aarch64 on M1/M2, x86_64 on Intel)
make down
make reset           # clean rebuild
make fetch           # only download binaries
make up ARCH=x86_64 VERSION=135.0.1 RELEASE=beta.24
```

Never run `docker build` directly — the Dockerfile relies on bind mounts populated by `make fetch`.

Fly.io / Railway: `railway.toml` is included. For Fly.io, use a Dockerfile that downloads binaries at build time (the bind-mount Dockerfile won't work in remote CI). Reference: [jo-browser](https://github.com/jo-inc/jo-browser).

Full deployment details including the `with-plugins` Docker stage, `scripts/install-plugin-deps.sh`, and `railway.toml`: [references/deployment.md](references/deployment.md).

## Core Agent Workflow

```
POST /tabs                          → { tabId }
GET  /tabs/:tabId/snapshot          → accessibility tree with element refs e1, e2, …
POST /tabs/:tabId/click  { ref }    → interact
POST /tabs/:tabId/type   { ref }    → interact
POST /tabs/:tabId/navigate          → URL or search macro
DELETE /tabs/:tabId                 → cleanup
```

Element refs are stable within a snapshot but reset on navigation — always fetch a fresh snapshot after navigating. Snapshots are ~90% smaller than raw HTML because they're accessibility-tree based.

Full workflow patterns (pagination via `offset`, screenshots with `includeScreenshot=true`, CSS-selector fallback, `pressEnter`, etc.): [references/agent-usage.md](references/agent-usage.md).

## Authentication

Two keys, both optional, both read from the environment (never from config files):

| Variable | Enables | Behavior if unset |
|----------|---------|-------------------|
| `CAMOFOX_API_KEY` | Cookie import endpoint (`POST /sessions/:userId/cookies`) and any route using `ctx.auth()` | Server returns `403` on those routes |
| `CAMOFOX_ADMIN_KEY` | `POST /stop` | Endpoint rejected |

Requests authenticate via `Authorization: Bearer <key>`. Loopback (`127.0.0.1`) requests bypass the bearer check. Generate a key with `openssl rand -hex 32`.

## REST API Surface

High-level groups — full schemas and query parameters: [references/api-reference.md](references/api-reference.md).

| Group | Endpoints |
|-------|-----------|
| Tab lifecycle | `POST /tabs`, `GET /tabs`, `GET /tabs/:id/stats`, `DELETE /tabs/:id`, `DELETE /tabs/group/:groupId`, `DELETE /sessions/:userId` |
| Page interaction | `GET /tabs/:id/snapshot`, `POST /tabs/:id/click`, `/type`, `/press`, `/scroll`, `/navigate`, `/wait`, `GET /tabs/:id/links`, `/images`, `/downloads`, `/screenshot`, `POST /tabs/:id/back`, `/forward`, `/refresh` |
| YouTube | `POST /youtube/transcript` (yt-dlp fast path, browser fallback) |
| Sessions | `POST /sessions/:userId/cookies`, `GET /sessions/:userId/storage_state` |
| Server | `GET /health`, `POST /start`, `POST /stop` |

## Search Macros

Navigate via `{"macro": "@<name>", "query": "…"}` instead of constructing search URLs:

`@google_search` · `@youtube_search` · `@amazon_search` · `@reddit_search` · `@reddit_subreddit` · `@wikipedia_search` · `@twitter_search` · `@yelp_search` · `@spotify_search` · `@netflix_search` · `@linkedin_search` · `@instagram_search` · `@tiktok_search` · `@twitch_search`

Reddit macros return JSON directly (no HTML parsing). `@reddit_subreddit` with query `"programming"` fetches `/r/programming.json`.

## Sessions, Cookies, Proxies, VNC

- **Per-user session isolation** via `userId`; tab grouping via `sessionKey` (legacy alias: `listItemId`).
- **Cookie import**: Netscape-format files under `~/.camofox/cookies/` (override with `CAMOFOX_COOKIES_DIR`). Max 500 cookies per request, 5 MB per file, fields sanitized to a Playwright allowlist, path-traversal blocked.
- **Session persistence**: `persistence` plugin writes each user's `storage_state.json` under `~/.camofox/profiles/<hashed-userId>/`. Disable via `"persistence": { "enabled": false }` in `camofox.config.json` or override path with `CAMOFOX_PROFILE_DIR`.
- **Proxy modes**: simple (single endpoint via `PROXY_HOST`/`PROXY_PORT`) or `PROXY_STRATEGY=backconnect` (rotating sticky sessions for Decodo/Bright Data/Oxylabs). Camoufox's GeoIP auto-sets locale, timezone, and geolocation from the proxy's exit IP.
- **VNC interactive login**: set `ENABLE_VNC=1` + `VNC_PASSWORD`. noVNC web UI on `NOVNC_PORT` (default `6080`). Export resulting auth state via `GET /sessions/:userId/storage_state`.

Details (cookie format, backconnect session rotation, storage state reuse, VNC workflow): [references/sessions-cookies-proxy.md](references/sessions-cookies-proxy.md).

## Environment Variables

Full table with defaults: [references/deployment.md](references/deployment.md#environment-variables). Most commonly set:

| Variable | Default |
|----------|---------|
| `CAMOFOX_PORT` / `PORT` | `9377` |
| `CAMOFOX_API_KEY` | unset (cookie import disabled) |
| `MAX_SESSIONS` | `50` |
| `MAX_TABS_PER_SESSION` | `10` |
| `SESSION_TIMEOUT_MS` | `1800000` (30 min) |
| `BROWSER_IDLE_TIMEOUT_MS` | `300000` (5 min) |
| `HANDLER_TIMEOUT_MS` | `30000` |
| `MAX_CONCURRENT_PER_USER` | `3` |
| `MAX_OLD_SPACE_SIZE` | `128` (MB, Node V8 heap) |
| `PROXY_STRATEGY` | unset (simple mode) |
| `PROMETHEUS_ENABLED` | unset (metrics off) |

## Plugin System

Plugins live under `plugins/<name>/index.js` and export `register(app, ctx)`. Loaded per `camofox.config.json` (`{"plugins": ["youtube", …]}`). If the file or `plugins` key is missing, all plugins in `plugins/` load (backward-compatible).

Install third-party plugins via CLI:

```bash
npm run plugin install https://github.com/user/camofox-screenshot-plugin
npm run plugin install git:github.com/user/my-plugin
npm run plugin install ./path/to/my-plugin
npm run plugin list
npm run plugin remove my-plugin
```

Default plugins shipped:

| Plugin | Enabled | Purpose |
|--------|---------|---------|
| `youtube` | yes | `/youtube/transcript` via yt-dlp (fast) or browser fallback |
| `persistence` | yes | Per-user storage state on disk |
| `vnc` | no (requires `ENABLE_VNC=1`) | Interactive browser login via noVNC |

### OpenClaw Scanner Isolation (critical constraint)

The OpenClaw skill-scanner flags any single `.js` file that contains BOTH halves of a rule pair. Violations break publication. Rules:

- `env-harvesting` (CRITICAL): `/process\.env/` + `/\bfetch\b|\bpost\b|http\.request/i` in same file. Regex is case-insensitive — string literals like `'POST'` and comments mentioning `process.env` trigger it.
- `dangerous-exec` (CRITICAL): `child_process` import + `exec`/`spawn` call in same file.
- `potential-exfiltration` (WARN): `readFile` + `fetch`/`post`/`http.request` in same file.

Enforced layout:
- `process.env` reads live only in `lib/config.js`.
- `child_process` / `execFile` / `spawn` live only in `plugins/youtube/youtube.js`, `plugins/vnc/vnc-launcher.js`, and `lib/launcher.js`.
- `server.js` has the routes but zero `process.env` and zero `child_process`.
- `lib/metrics.js` has no `process.env` and no HTTP method string literals; `prom-client` is lazy-loaded only when `PROMETHEUS_ENABLED=1`.
- `lib/request-utils.js` contains HTTP method strings but no `process.env`.

When adding features needing env vars or subprocesses, put that code in a `lib/` module and import the result into `server.js` or the plugin's route file.

Plugin `register(app, ctx)` API, 29-event bus, `ctx.createMetric`, mutating hooks (`browser:launching`, `session:creating`, …), `apt.txt` + `post-install.sh` dependency files, and the `youtube` reference implementation: [references/plugin-development.md](references/plugin-development.md).

## Testing

```bash
npm test               # unit + e2e + plugin
npm run test:e2e       # e2e only
npm run test:live      # hits real sites (Google, macros)
npm run test:debug     # with server stdout
npm run test:plugins   # all plugin tests
npx jest plugins/youtube
```

## Key Files

- `server.js` — Express routes + browser logic (no `process.env`, no `child_process`)
- `lib/config.js` — all env var reads
- `lib/launcher.js` — Camoufox subprocess spawning
- `lib/cookies.js` — cookie file I/O
- `lib/metrics.js` — Prometheus metrics (lazy)
- `lib/request-utils.js` — `actionFromReq`, `classifyError`
- `lib/snapshot.js` — accessibility tree
- `lib/macros.js` — search macro URL expansion
- `lib/plugins.js` — plugin loader + event bus
- `lib/auth.js` — API-key / loopback middleware
- `lib/persistence.js` — atomic storage state
- `lib/inflight.js` — inflight request coalescing
- `lib/tmp-cleanup.js` — orphaned temp file cleanup
- `camofox.config.json` — plugin load list
- `openclaw.plugin.json` — OpenClaw gateway integration manifest (separate from camofox's own config)
- `plugins/youtube/`, `plugins/persistence/`, `plugins/vnc/` — bundled plugins
- `scripts/install-plugin-deps.sh` — Docker build hook for `apt.txt` + `post-install.sh`

## References

| File | When to read |
|------|--------------|
| [api-reference.md](references/api-reference.md) | Exact endpoint schemas, query params, request/response bodies |
| [deployment.md](references/deployment.md) | Docker/Fly/Railway/Make targets, env var table, logging, yt-dlp install |
| [agent-usage.md](references/agent-usage.md) | Snapshot → ref → click flow, pagination, screenshots, macros usage |
| [sessions-cookies-proxy.md](references/sessions-cookies-proxy.md) | Cookie import, session persistence, proxy/GeoIP, VNC login, storage state reuse |
| [plugin-development.md](references/plugin-development.md) | `register(app, ctx)` API, events, scanner isolation, metrics, deps files |
