# Plugin Development

Building plugins that extend camofox-browser with new endpoints, background processes, Prometheus metrics, and lifecycle hooks.

## Table of Contents

- [File Layout](#file-layout)
- [`register(app, ctx)` Signature](#registerapp-ctx-signature)
- [Plugin Context (`ctx`)](#plugin-context-ctx)
- [Event Bus (29 events)](#event-bus-29-events)
- [Mutating Hooks](#mutating-hooks)
- [System Deps & Post-Install Hooks](#system-deps--post-install-hooks)
- [Plugin Configuration](#plugin-configuration)
- [Custom Metrics](#custom-metrics)
- [OpenClaw Scanner Isolation](#openclaw-scanner-isolation)
- [Installing Third-Party Plugins](#installing-third-party-plugins)
- [Reference Implementation: YouTube](#reference-implementation-youtube)

## File Layout

```
plugins/
  my-plugin/
    index.js         # Required — exports register(app, ctx)
    apt.txt          # Optional — one system package per line (# comments ok)
    post-install.sh  # Optional — executable hook for binary downloads
    *.test.js        # Optional — Jest tests (auto-discovered)
```

## `register(app, ctx)` Signature

```js
// plugins/my-plugin/index.js
export function register(app, ctx) {
  const { sessions, config, log, events, auth, ensureBrowser, getSession,
          destroySession, withUserLimit, safePageClose, normalizeUserId,
          validateUrl, safeError, buildProxyUrl, proxyPool, failuresTotal,
          createMetric, metricsRegistry } = ctx;

  app.get('/my-endpoint', auth(), async (req, res) => {
    const session = sessions.get(req.params.userId);
    res.json({ ok: true });
  });

  events.on('browser:launched', ({ browser, display }) => {
    log('info', 'browser is up', { display });
  });
}
```

`register` may be `async`. The loader awaits it before moving on to the next plugin.

## Plugin Context (`ctx`)

| Property | Type | Description |
|----------|------|-------------|
| `sessions` | `Map` | Live sessions: `userId → { context, tabGroups, lastAccess }` |
| `config` | `object` | Server CONFIG (port, apiKey, nodeEnv, proxy, etc.) |
| `log` | `function` | `log(level, msg, fields)` — structured JSON logging |
| `events` | `EventEmitter` | Plugin event bus (29 events) |
| `auth` | `function` | `auth()` returns Express middleware enforcing API key / loopback |
| `ensureBrowser` | `async function` | Launch browser if not running, return instance |
| `getSession` | `async function` | `getSession(userId)` — get or create a session |
| `destroySession` | `function` | `destroySession(userId)` |
| `withUserLimit` | `async function` | `withUserLimit(userId, fn)` — per-user concurrency limit |
| `safePageClose` | `async function` | Close a page with timeout guard |
| `normalizeUserId` | `function` | Coerce to string for map keys |
| `validateUrl` | `function` | Returns error string or null |
| `safeError` | `function` | Sanitize error for client response |
| `buildProxyUrl` | `function` | Get proxy URL for external requests |
| `proxyPool` | `object \| null` | Proxy pool (null if no proxy configured) |
| `failuresTotal` | `Counter` | Core Prometheus counter: `failuresTotal.labels(type, action).inc()` |
| `createMetric` | `async function` | Register a Prometheus metric (stubbed when disabled) |
| `metricsRegistry` | `function` | Raw `prom-client` Registry or null |

## Event Bus (29 events)

28 emitted by core + 1 (`session:storage:export`) by plugins.

### Browser lifecycle
| Event | Payload | Mutating |
|-------|---------|----------|
| `browser:launching` | `{ options }` | yes — modify launch options in place |
| `browser:launched` | `{ browser, display }` | |
| `browser:restart` | `{ reason }` | |
| `browser:closed` | `{ reason }` | |
| `browser:error` | `{ error }` | |

### Session lifecycle
| Event | Payload | Mutating |
|-------|---------|----------|
| `session:creating` | `{ userId, contextOptions }` | yes |
| `session:created` | `{ userId, context }` | |
| `session:destroyed` | `{ userId, reason }` | |
| `session:expired` | `{ userId, idleMs }` | |

### Tab lifecycle
| Event | Payload |
|-------|---------|
| `tab:created` | `{ userId, tabId, page, url }` |
| `tab:navigated` | `{ userId, tabId, url, prevUrl }` |
| `tab:destroyed` | `{ userId, tabId, reason }` |
| `tab:recycled` | `{ userId, tabId }` |
| `tab:error` | `{ userId, tabId, error }` |

### Content
| Event | Payload |
|-------|---------|
| `tab:snapshot` | `{ userId, tabId, snapshot }` |
| `tab:screenshot` | `{ userId, tabId, buffer }` |
| `tab:evaluate` | `{ userId, tabId, expression }` |
| `tab:evaluated` | `{ userId, tabId, result }` |

### Input
| Event | Payload |
|-------|---------|
| `tab:click` | `{ userId, tabId, ref, selector }` |
| `tab:type` | `{ userId, tabId, text, ref, mode }` |
| `tab:scroll` | `{ userId, tabId, direction, amount }` |
| `tab:press` | `{ userId, tabId, key }` |

### Downloads
| Event | Payload |
|-------|---------|
| `tab:download:start` | `{ userId, tabId, filename, url }` |
| `tab:download:complete` | `{ userId, tabId, filename, path, size }` |

### Cookies / Auth
| Event | Payload |
|-------|---------|
| `session:cookies:import` | `{ userId, count }` |
| `session:storage:export` | `{ userId }` |

### Server
| Event | Payload |
|-------|---------|
| `server:starting` | `{ port }` |
| `server:started` | `{ port, pid }` |
| `server:shutdown` | `{ signal }` |

## Mutating Hooks

`browser:launching`, `session:creating`, `session:created`, and `session:destroyed` are emitted via `events.emitAsync()` — the server awaits all listeners (including async ones) before proceeding. This makes async work like loading storage state from disk safe. Modify payload objects in place:

```js
events.on('browser:launching', ({ options }) => {
  options.virtual_display_resolution = '1920x1080x24';
});

events.on('session:creating', async ({ userId, contextOptions }) => {
  const saved = await loadStorageState(userId);
  if (saved) contextOptions.storageState = saved;
});
```

Other events use synchronous `events.emit()` — fire-and-forget.

## System Deps & Post-Install Hooks

Plugins that need apt packages list them in `apt.txt`:

```
# plugins/vnc/apt.txt
x11vnc
novnc
python3-websockify
```

Binaries that aren't available via apt go in an executable `post-install.sh`:

```bash
#!/bin/sh
set -e
curl -fL https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp
chmod +x /usr/local/bin/yt-dlp
```

Both run via `scripts/install-plugin-deps.sh` during `docker build`.

## Plugin Configuration

`camofox.config.json`:

```json
{
  "id": "camofox-browser",
  "name": "Camofox Browser",
  "version": "1.5.2",
  "plugins": ["youtube"]
}
```

- `plugins` — array of plugin directory names. Only these load at startup and have deps installed during build.
- Missing file or missing `plugins` key → all plugins in `plugins/` load (backward-compatible).
- Separate from `openclaw.plugin.json`, which tells OpenClaw how to configure camofox as an external service.

## Custom Metrics

`ctx.createMetric()` returns a no-op stub when Prometheus is disabled — no null checks needed.

```js
const transcriptsTotal = await ctx.createMetric('counter', {
  name: 'camofox_youtube_transcripts_total',
  help: 'YouTube transcripts extracted',
  labelNames: ['method'],
});

transcriptsTotal.labels('yt-dlp').inc();
```

Types: `'counter'`, `'histogram'`, `'gauge'`. Options are standard [prom-client](https://github.com/siimon/prom-client) options (`name`, `help`, `labelNames`, `buckets`, …). Metrics auto-register to the shared registry and appear on `/metrics`.

For advanced use, `ctx.metricsRegistry()` returns the raw registry (or `null` when disabled).

## OpenClaw Scanner Isolation

OpenClaw's skill-scanner flags plugins that combine these pairs in one `.js` file. CRITICAL violations block publication.

| Rule | Pattern A | Pattern B | Severity |
|------|-----------|-----------|----------|
| `env-harvesting` | `/process\.env/` | `/\bfetch\b\|\bpost\b\|http\.request/i` | CRITICAL |
| `dangerous-exec` | `child_process` import | `exec` / `spawn` call | CRITICAL |
| `potential-exfiltration` | `readFile` | `fetch` / `post` / `http.request` | WARN |

The `env-harvesting` regex is case-insensitive — string literals like `'POST'` and comments that merely contain `process.env` trigger it.

Required layout:

- `process.env` reads only in `lib/config.js`. Plugins read config via `ctx.config`.
- `child_process` / `execFile` / `spawn` only in `plugins/youtube/youtube.js`, `plugins/vnc/vnc-launcher.js`, and `lib/launcher.js`. Never in a file with route handlers.
- `server.js` has routes but zero `process.env`, zero `child_process`.
- `lib/metrics.js` has no `process.env`, no HTTP method string literals. `prom-client` lazy-loaded only when `PROMETHEUS_ENABLED=1`.
- `lib/request-utils.js` has HTTP method literals but no `process.env`.

History: 1.3.0 shipped with `child_process` in `server.js` (YouTube) — broken, fixed in 1.3.1. 1.4.1 broke again because `metrics.js` had `process.env` in a comment plus `'POST'` in `actionFromReq` — fixed in 1.5.1 by lazy-loading `prom-client` and splitting `actionFromReq` into `lib/request-utils.js`.

For any new feature:
1. Put env reads in `lib/config.js`; import the resulting config object.
2. Put subprocess spawning in a `lib/<name>.js` or `plugins/<name>/<name>-launcher.js`; import only the result.
3. Keep `register()` + route handlers in `plugins/<name>/index.js`.

## Installing Third-Party Plugins

```bash
npm run plugin install https://github.com/user/camofox-screenshot-plugin
npm run plugin install git:github.com/user/my-plugin
npm run plugin install ./path/to/my-plugin
npm run plugin list
npm run plugin remove my-plugin
```

Source shapes accepted:
- Git repo whose root has `index.js` with `register()` — installed as one plugin.
- Git repo with a `plugins/` subdirectory — each subdirectory becomes a separate plugin.
- Local directory with `index.js` and `register()`.

The installer copies the plugin into `plugins/`, adds it to `camofox.config.json`, and runs `npm install` for npm deps. System deps (`apt.txt`, `post-install.sh`) are flagged but require manual install or a rebuild with `--target with-plugins`.

## Reference Implementation: YouTube

`plugins/youtube/` is the canonical example.

```
plugins/
  youtube/
    index.js         # register(app, ctx) — route + browser fallback
    youtube.js       # yt-dlp subprocess + transcript parsing
    youtube.test.js  # parser unit tests
    apt.txt          # python3-minimal
    post-install.sh  # downloads yt-dlp binary
```

Simplified `index.js`:

```js
import { detectYtDlp, hasYtDlp, ensureYtDlp, ytDlpTranscript } from './youtube.js';
import { classifyError } from '../../lib/request-utils.js';

export async function register(app, ctx) {
  const { log, config, sessions, ensureBrowser, getSession,
          withUserLimit, safePageClose, normalizeUserId,
          validateUrl, safeError, buildProxyUrl, proxyPool,
          failuresTotal } = ctx;

  await detectYtDlp(log);

  app.post('/youtube/transcript', ctx.auth(), async (req, res) => {
    // validate URL, extract videoId, try yt-dlp, fall back to browser
  });

  async function browserTranscript(reqId, url, videoId, lang) {
    return await withUserLimit('__yt_transcript__', async () => {
      await ensureBrowser();
      const session = await getSession('__yt_transcript__');
      const page = await session.context.newPage();
      // intercept caption XHRs, parse transcript
      await safePageClose(page);
    });
  }
}
```

Key patterns:

- **Auth**: `ctx.auth()` middleware on the route.
- **Logging**: `ctx.log('info', …)` — never `console.log`.
- **Browser access**: `ctx.ensureBrowser()` + `ctx.getSession()`.
- **Concurrency**: `ctx.withUserLimit()` respects per-user caps.
- **Metrics**: `ctx.failuresTotal.labels(…)` for core, `ctx.createMetric()` for custom.
- **Scanner compliance**: `child_process` in `youtube.js`, routes in `index.js` — separate files.
- **System deps**: `apt.txt` via `scripts/install-plugin-deps.sh`.
