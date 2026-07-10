# camofox-browser REST API Reference

Full endpoint schemas for the server on `http://<host>:9377` (default). All authenticated routes accept `Authorization: Bearer <CAMOFOX_API_KEY>` or bypass auth on loopback.

## Table of Contents

- [Conventions](#conventions)
- [Tab Lifecycle](#tab-lifecycle)
- [Page Interaction](#page-interaction)
- [Content Extraction](#content-extraction)
- [Navigation History](#navigation-history)
- [Sessions & Cookies](#sessions--cookies)
- [YouTube Transcript](#youtube-transcript)
- [Server](#server)

## Conventions

- `userId` is required on most routes to scope the browser context (query param for GETs, body field for POSTs).
- `sessionKey` groups tabs within a user session (alias: `listItemId` accepted for legacy callers).
- `tabId` values come from `POST /tabs` responses.
- Element `ref` values (`e1`, `e2`, …) come from `/snapshot` responses and reset on navigation.
- Errors are sanitized via `safeError()` before being returned to clients.

## Tab Lifecycle

### `POST /tabs` — create a tab

Request:
```json
{ "userId": "agent1", "sessionKey": "task1", "url": "https://example.com" }
```

Response: `{ "tabId": "abc123", "url": "...", "title": "..." }`

### `GET /tabs?userId=<id>` — list a user's tabs

### `GET /tabs/:tabId/stats` — per-tab stats

Returns tool-call counts and visited URL history for the tab.

### `DELETE /tabs/:tabId?userId=<id>` — close tab

### `DELETE /tabs/group/:groupId` — close all tabs with a given `sessionKey`

### `DELETE /sessions/:userId` — destroy a user's entire session (all tabs, context, cookies in memory)

## Page Interaction

### `GET /tabs/:tabId/snapshot?userId=<id>`

Accessibility snapshot with element refs. Query parameters:

| Param | Type | Purpose |
|-------|------|---------|
| `includeScreenshot` | `true` | Adds a base64 PNG alongside the snapshot |
| `offset` | integer | Paginate large snapshots (server truncates automatically; use `offset` to continue) |

Response includes a string like:
```
[heading] Example Domain
[paragraph] This domain is for use in examples.
[link e1] More information...
```

### `POST /tabs/:tabId/click`

```json
{ "userId": "agent1", "ref": "e1" }
```

Or by CSS selector:
```json
{ "userId": "agent1", "selector": "button.submit" }
```

### `POST /tabs/:tabId/type`

```json
{ "userId": "agent1", "ref": "e2", "text": "hello", "pressEnter": true }
```

### `POST /tabs/:tabId/press`

```json
{ "userId": "agent1", "key": "Enter" }
```

Accepts any Playwright key name (e.g., `ArrowDown`, `Escape`, `Control+A`).

### `POST /tabs/:tabId/scroll`

```json
{ "userId": "agent1", "direction": "down", "amount": 500 }
```

Directions: `up`, `down`, `left`, `right`.

### `POST /tabs/:tabId/navigate`

Direct URL:
```json
{ "userId": "agent1", "url": "https://google.com" }
```

Search macro:
```json
{ "userId": "agent1", "macro": "@google_search", "query": "best coffee beans" }
```

### `POST /tabs/:tabId/wait`

Wait for a selector to appear or a timeout to elapse. Body accepts `selector` (string) and/or `timeout` (ms).

## Content Extraction

### `GET /tabs/:tabId/links?userId=<id>&limit=50`

Returns all links on the page.

### `GET /tabs/:tabId/images`

Lists `<img>` elements. Query parameters:

| Param | Purpose |
|-------|---------|
| `includeData=true` | Inline data URLs |
| `maxBytes=N` | Cap data size |
| `limit=N` | Cap count |

### `GET /tabs/:tabId/downloads`

Returns captured downloads. Query parameters:

| Param | Purpose |
|-------|---------|
| `includeData=true` | Base64 file data |
| `consume=true` | Clear after read |
| `maxBytes=N` | Cap returned size |

### `GET /tabs/:tabId/screenshot?userId=<id>`

Returns a PNG screenshot.

## Navigation History

| Method | Endpoint |
|--------|----------|
| `POST` | `/tabs/:tabId/back` |
| `POST` | `/tabs/:tabId/forward` |
| `POST` | `/tabs/:tabId/refresh` |

All require `{ "userId": "..." }`.

## Sessions & Cookies

### `POST /sessions/:userId/cookies`

Authenticated. Injects Playwright-shaped cookie objects into the user's `BrowserContext`.

```bash
curl -X POST http://localhost:9377/sessions/agent1/cookies \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_CAMOFOX_API_KEY' \
  -d '{"cookies":[{"name":"foo","value":"bar","domain":"example.com","path":"/","expires":-1,"httpOnly":false,"secure":false}]}'
```

Limits: max 500 cookies per request, 5 MB file size, sanitized to the Playwright allowlist.

### `GET /sessions/:userId/storage_state`

Exposed by the `vnc` plugin. Returns `{ cookies, origins }` — the Playwright storage-state shape — suitable for reuse across new sessions.

## YouTube Transcript

### `POST /youtube/transcript`

```json
{ "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "languages": ["en"] }
```

Response:
```json
{
  "status": "ok",
  "transcript": "[00:18] ♪ We're no strangers to love ♪\n...",
  "video_title": "...",
  "total_words": 548
}
```

Uses `yt-dlp` when available (fast, no browser). Falls back to a browser-based caption-intercept path when yt-dlp is missing — slower and less reliable because of YouTube ad pre-rolls.

## Server

| Method | Endpoint | Notes |
|--------|----------|-------|
| `GET` | `/health` | Excluded from request logs |
| `POST` | `/start` | Start the browser engine |
| `POST` | `/stop` | Requires `CAMOFOX_ADMIN_KEY` |
