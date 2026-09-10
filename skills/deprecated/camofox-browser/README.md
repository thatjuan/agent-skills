# camofox-browser

> Expertise for camofox-browser — the Camoufox-engine anti-detection browser server (REST API on port 9377) built for AI agents to deploy, configure, and drive.

## What it does

`camofox-browser` makes your agent fluent in the self-hosted browser server that wraps [Camoufox](https://camoufox.com) (a Firefox fork with C++-level fingerprint spoofing) behind an HTTP API designed for agents. Instead of CSS selectors or raw coordinates, agents fetch token-efficient accessibility snapshots with stable element refs (`e1`, `e2`, …) and interact by ref. The skill covers:

- **Architecture** — the browser → user session (`userId`) → tab group (`sessionKey`) → tab hierarchy, lazy launch, idle shutdown, session expiry, and tab recycling.
- **The core agent workflow** — `POST /tabs` → `GET /snapshot` → `click`/`type`/`navigate` by ref, with fresh snapshots after every navigation.
- **Deployment** — standalone (`npm start`), OpenClaw plugin, and the `Makefile`-driven Docker flow (`make up`/`make fetch`, never bare `docker build`), plus Fly.io/Railway.
- **Sessions, cookies, proxies, VNC** — per-user isolation, Netscape cookie import, storage-state persistence, simple vs. backconnect proxy modes with GeoIP, and interactive noVNC login.
- **Search macros** — `@google_search`, `@reddit_subreddit`, and the rest, so agents navigate by macro instead of building search URLs.
- **Plugin system** — `register(app, ctx)` modules, the event bus, Prometheus metrics, and the OpenClaw scanner-isolation constraints that dictate where `process.env` and `child_process` may live.

It triggers when code hits `localhost:9377`, scripts install `@askjo/camofox-browser` or run `make up`/`make fetch`, agents invoke OpenClaw `camofox_*` tools, or the user asks about Camoufox fingerprint spoofing, element refs, cookie import, proxy rotation, or plugin development.

## When to use it

Invoke this skill when you hear:

- *"Stand up camofox-browser in Docker and fetch a page that blocks bots."*
- *"Import Netscape cookies for a logged-in session, then scrape behind the login."*
- *"Rotate residential proxies with backconnect and let GeoIP set the locale."*
- *"Write a plugin that adds a `/screenshot-annotated` route with a Prometheus metric."*
- *"Get the transcript for this YouTube video."*
- *"Do an interactive login over noVNC, then export the storage state."*

## Example walkthrough

Asked to fetch a bot-protected page, the skill drives the ref-based loop: `POST /tabs` for a `tabId`, `GET /tabs/:id/snapshot` for the accessibility tree with `e1`/`e2` refs, then `click`/`type` by ref — fetching a fresh snapshot after each navigation because refs reset. For deployment it steers you to `make up` (which pre-downloads Camoufox and yt-dlp via bind mounts) and warns off a bare `docker build`, which the Dockerfile can't satisfy.

## Installation

```bash
npx skills add thatjuan/agent-skills --skill camofox-browser
```

## Bundled resources

| File | Purpose |
|------|---------|
| `SKILL.md` | What it is, architecture, install/run, core agent workflow, auth, REST surface, search macros, sessions/cookies/proxies/VNC, env vars, plugin system, scanner-isolation constraints, key files |
| `references/api-reference.md` | Exact endpoint schemas, query parameters, request/response bodies |
| `references/deployment.md` | Docker/Fly/Railway/Make targets, full env-var table, logging, yt-dlp install |
| `references/agent-usage.md` | Snapshot → ref → click flow, pagination, screenshots, CSS-selector fallback, macro usage |
| `references/sessions-cookies-proxy.md` | Cookie import, session persistence, proxy/GeoIP, VNC login, storage-state reuse |
| `references/plugin-development.md` | `register(app, ctx)` API, the 29-event bus, scanner isolation, metrics, dependency files |

## Tips

- **Fetch a fresh snapshot after every navigation.** Element refs are stable within a snapshot but reset when the page changes.
- **Use `make`, never bare `docker build`.** The Dockerfile relies on bind mounts that `make fetch` populates with Camoufox and yt-dlp.
- **Respect scanner isolation when writing plugins.** The OpenClaw skill-scanner flags any single `.js` file that reads `process.env` and makes an HTTP call, or imports `child_process` and calls `exec`/`spawn`. Put env reads and subprocess calls in `lib/` modules and import the result.
- **Both API keys are optional but gate real routes.** `CAMOFOX_API_KEY` unlocks cookie import; `CAMOFOX_ADMIN_KEY` unlocks `/stop`. Loopback requests bypass the bearer check.
- **Reddit macros return JSON directly** — `@reddit_subreddit` fetches `/r/<name>.json`, no HTML parsing needed.

## Related skills

- [`browserbase-sdk`](../browserbase-sdk/) — a cloud alternative when you don't want to self-host the browser
- [`openwa`](../openwa/) — another self-hosted, Docker-deployed service with a plugin/webhook model
