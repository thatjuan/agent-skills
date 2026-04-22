# Deployment & Operations

## Table of Contents

- [Local Dev](#local-dev)
- [Docker via Makefile](#docker-via-makefile)
- [Dockerfile Stages](#dockerfile-stages)
- [Fly.io](#flyio)
- [Railway](#railway)
- [yt-dlp Dependency](#yt-dlp-dependency)
- [Plugin Dependency Installation](#plugin-dependency-installation)
- [Structured Logging](#structured-logging)
- [Prometheus Metrics](#prometheus-metrics)
- [Environment Variables](#environment-variables)

## Local Dev

```bash
git clone https://github.com/jo-inc/camofox-browser
cd camofox-browser
npm install
npm start      # or ./run.sh
```

First run downloads the Camoufox binary (~300 MB). Default port `9377`. Override with `CAMOFOX_PORT` or the platform-friendly `PORT`.

## Docker via Makefile

The Makefile pre-downloads Camoufox and yt-dlp outside the Docker build (into `dist/`) and the Dockerfile bind-mounts them in. Rebuilds are fast (~30 s instead of ~3 min).

| Target | Purpose |
|--------|---------|
| `make up` | Build and start; auto-detects arch (`aarch64` on M1/M2, `x86_64` on Intel) |
| `make down` | Stop and remove the container |
| `make reset` | Clean rebuild (use after upgrading `VERSION`/`RELEASE`) |
| `make fetch` | Only download binaries into `dist/` |
| `make build` | Build only (after `make fetch`) |

Overrides:

```bash
make up ARCH=x86_64
make up VERSION=135.0.1 RELEASE=beta.24
```

Warning: `docker build` called directly fails — the Dockerfile depends on bind-mounted binaries. Always go through `make up` (or `make fetch && make build`).

## Dockerfile Stages

The Dockerfile defines multiple targets:

- **base/default** — production container with `camofox.config.json` plugins pre-installed via `scripts/install-plugin-deps.sh`. Contains Camoufox, yt-dlp, and `apt.txt` packages from every enabled plugin.
- **`with-plugins`** — rebuild target for adding third-party plugins. Re-runs `install-plugin-deps.sh` so new plugin dirs under `plugins/` get their deps installed.

```bash
docker build --target with-plugins -t camofox-browser .
```

Direct docker run:

```bash
docker run -p 9377:9377 \
  -e CAMOFOX_API_KEY="your-generated-key" \
  -v ~/.camofox/cookies:/home/node/.camofox/cookies:ro \
  camofox-browser
```

## Fly.io

`fly secrets set CAMOFOX_API_KEY="your-generated-key"`.

The bind-mount Dockerfile won't work on remote CI — binaries must be downloaded at build time. Reference implementation that does this: [jo-browser](https://github.com/jo-inc/jo-browser).

## Railway

`railway.toml` ships with the repo. Set env vars as Railway variables. Memory is tight on the starter tier — defaults (`MAX_OLD_SPACE_SIZE=128`, idle shutdown) are tuned for it.

## yt-dlp Dependency

The `/youtube/transcript` endpoint prefers `yt-dlp` for speed and reliability. The base Docker image includes it (downloaded by `plugins/youtube/post-install.sh`). For local dev:

```bash
pip install yt-dlp     # or: brew install yt-dlp
```

Without yt-dlp, the endpoint falls back to launching a browser, navigating to the video, and intercepting caption XHRs — slower and foiled by ad pre-rolls.

## Plugin Dependency Installation

`scripts/install-plugin-deps.sh` runs during `docker build`:

1. Parses `camofox.config.json` to find enabled plugin names.
2. For each plugin, reads `plugins/<name>/apt.txt` (one package per line, `#` comments ok) and `apt-get install`s the packages.
3. Executes `plugins/<name>/post-install.sh` if present and executable.

If `camofox.config.json` is missing or has no `plugins` key, every directory under `plugins/` is treated as enabled (backward-compatible).

Third-party plugins installed via `npm run plugin install …` are copied into `plugins/`, added to `camofox.config.json`, and have their `npm` deps installed. System-level deps (`apt.txt`, `post-install.sh`) are flagged but must be installed manually or by rebuilding with `--target with-plugins`.

## Structured Logging

All log output is one JSON object per line:

```json
{"ts":"2026-02-11T23:45:01.234Z","level":"info","msg":"req","reqId":"a1b2c3d4","method":"POST","path":"/tabs","userId":"agent1"}
{"ts":"2026-02-11T23:45:01.567Z","level":"info","msg":"res","reqId":"a1b2c3d4","status":200,"ms":333}
```

`reqId` is stable from request receipt to response. `/health` is excluded to reduce noise. Plugins log via `ctx.log(level, msg, fields)` — never `console.log`.

## Prometheus Metrics

Off by default. Set `PROMETHEUS_ENABLED=1` to enable. `prom-client` is lazy-loaded only when enabled to keep `lib/metrics.js` free of `process.env` references (OpenClaw scanner constraint). Metrics expose on `/metrics`. Plugins can register counters, histograms, and gauges via `ctx.createMetric('counter', { name, help, labelNames })`.

Core counter: `ctx.failuresTotal.labels(type, action).inc()` — type is a classifyError() category, action is `actionFromReq()`.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CAMOFOX_PORT` | Server port | `9377` |
| `PORT` | Fallback port (Fly.io style) | `9377` |
| `CAMOFOX_API_KEY` | Enables cookie import + any `ctx.auth()` route; unset → those routes return 403 | — |
| `CAMOFOX_ADMIN_KEY` | Required for `POST /stop` | — |
| `CAMOFOX_COOKIES_DIR` | Netscape cookie files | `~/.camofox/cookies` |
| `CAMOFOX_PROFILE_DIR` | Persisted session profiles | `~/.camofox/profiles` |
| `MAX_SESSIONS` | Max concurrent sessions | `50` |
| `MAX_TABS_PER_SESSION` | Max tabs per session (oldest recycled beyond limit) | `10` |
| `SESSION_TIMEOUT_MS` | Session inactivity timeout | `1800000` (30 min) |
| `BROWSER_IDLE_TIMEOUT_MS` | Kill browser when idle (0 = never) | `300000` (5 min) |
| `HANDLER_TIMEOUT_MS` | Max time for any handler | `30000` |
| `MAX_CONCURRENT_PER_USER` | Concurrent request cap per user | `3` |
| `MAX_OLD_SPACE_SIZE` | Node V8 heap limit (MB) | `128` |
| `PROXY_STRATEGY` | `backconnect` (rotating sticky) or unset (single endpoint) | — |
| `PROXY_PROVIDER` | Provider session format (e.g. `decodo`) | `decodo` |
| `PROXY_HOST` | Proxy hostname / IP (simple mode) | — |
| `PROXY_PORT` | Proxy port (simple mode) | — |
| `PROXY_USERNAME` | Proxy auth username | — |
| `PROXY_PASSWORD` | Proxy auth password | — |
| `PROXY_BACKCONNECT_HOST` | Backconnect gateway hostname | — |
| `PROXY_BACKCONNECT_PORT` | Backconnect gateway port | `7000` |
| `PROXY_COUNTRY` | Geo-target country | — |
| `PROXY_STATE` | Geo-target state/region | — |
| `TAB_INACTIVITY_MS` | Close tabs idle longer than this | `300000` (5 min) |
| `ENABLE_VNC` | `1` enables VNC plugin | — |
| `VNC_PASSWORD` | Required in production when VNC is on | — |
| `NOVNC_PORT` | noVNC web UI port | `6080` |
| `PROMETHEUS_ENABLED` | `1` exposes `/metrics` and lazy-loads `prom-client` | — |
