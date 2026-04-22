# Agent Usage Patterns

How AI agents drive camofox-browser. Covers the snapshot → ref → click loop, pagination, screenshots, search macros, and OpenClaw tool mapping.

## Table of Contents

- [The Core Loop](#the-core-loop)
- [Element Refs](#element-refs)
- [Accessibility Snapshots](#accessibility-snapshots)
- [Pagination](#pagination)
- [Screenshots](#screenshots)
- [Search Macros](#search-macros)
- [Cookies for Authenticated Sites](#cookies-for-authenticated-sites)
- [OpenClaw Tool Mapping](#openclaw-tool-mapping)

## The Core Loop

```
1. POST /tabs                          → tabId
2. GET  /tabs/:tabId/snapshot          → refs e1, e2, …
3. POST /tabs/:tabId/click  { ref }
   POST /tabs/:tabId/type   { ref }
   POST /tabs/:tabId/navigate
4. go to 2 after any navigation
5. DELETE /tabs/:tabId                 when done
```

`userId` is required on every request. `sessionKey` groups tabs within a session so a conversation's tabs share cookies and can be closed together via `DELETE /tabs/group/:groupId`.

## Element Refs

Refs like `e1`, `e2`, `e3` are assigned by the snapshot endpoint to interactive nodes in the accessibility tree. They are:

- **Stable within a single snapshot response** — the same ref points to the same element.
- **Invalidated on navigation, page reload, or significant DOM mutation** — fetch a fresh snapshot after any such change.
- **Reusable across `/click`, `/type`, `/press`, and `/scroll`** when those routes accept a `ref` parameter.

When refs aren't stable (e.g., SPA re-renders between requests), fall back to `selector`:

```json
{ "userId": "agent1", "selector": "button[data-testid='submit']" }
```

## Accessibility Snapshots

Snapshot strings look like:

```
[heading] Example Domain
[paragraph] This domain is for use in examples.
[link e1] More information...
[button e2] Submit
```

Snapshots are ~90% smaller than raw HTML because only role, name, and a few a11y attributes are kept. Interactive elements get a ref; static content doesn't.

## Pagination

Large pages are automatically truncated. When a snapshot response indicates truncation, continue by passing `offset=N`:

```
GET /tabs/:tabId/snapshot?userId=agent1&offset=2000
```

The response includes enough metadata for the agent to decide whether to page again.

## Screenshots

Inline with snapshot:

```
GET /tabs/:tabId/snapshot?userId=agent1&includeScreenshot=true
```

Returns a base64 PNG alongside the text snapshot. Standalone:

```
GET /tabs/:tabId/screenshot?userId=agent1
```

## Search Macros

Macros bypass search-engine URL construction and avoid brittle query-string encoding:

```json
POST /tabs/:tabId/navigate
{ "userId": "agent1", "macro": "@google_search", "query": "weather tokyo" }
```

Available: `@google_search`, `@youtube_search`, `@amazon_search`, `@reddit_search`, `@reddit_subreddit`, `@wikipedia_search`, `@twitter_search`, `@yelp_search`, `@spotify_search`, `@netflix_search`, `@linkedin_search`, `@instagram_search`, `@tiktok_search`, `@twitch_search`.

Reddit macros return JSON directly instead of HTML:
- `@reddit_search` — search all of Reddit, returns JSON with 25 results.
- `@reddit_subreddit` with `query: "programming"` fetches `/r/programming.json`.

## Cookies for Authenticated Sites

For sites requiring login (LinkedIn, Amazon, etc.), import cookies before creating tabs on that domain:

1. Export Netscape-format cookies via a browser extension.
2. Place the file under `~/.camofox/cookies/` (or `CAMOFOX_COOKIES_DIR`).
3. Call `camofox_import_cookies` (OpenClaw) or POST directly to `/sessions/:userId/cookies`.
4. Subsequent `POST /tabs` on the same `userId` inherits the injected cookies.

Details: [sessions-cookies-proxy.md](sessions-cookies-proxy.md).

## OpenClaw Tool Mapping

The `@askjo/camofox-browser` OpenClaw plugin exposes these tools. Each maps 1:1 to a REST endpoint.

| Tool | Endpoint |
|------|----------|
| `camofox_create_tab` | `POST /tabs` |
| `camofox_list_tabs` | `GET /tabs` |
| `camofox_close_tab` | `DELETE /tabs/:tabId` |
| `camofox_snapshot` | `GET /tabs/:tabId/snapshot` |
| `camofox_click` | `POST /tabs/:tabId/click` |
| `camofox_type` | `POST /tabs/:tabId/type` |
| `camofox_navigate` | `POST /tabs/:tabId/navigate` |
| `camofox_scroll` | `POST /tabs/:tabId/scroll` |
| `camofox_screenshot` | `GET /tabs/:tabId/screenshot` |
| `camofox_import_cookies` | `POST /sessions/:userId/cookies` (reads file, Bearer-auths) |

`CAMOFOX_API_KEY` is read from the OpenClaw host environment by both the plugin (to sign cookie-import requests) and the server (to verify them). Storing it in `openclaw.json` is wrong — the file is plaintext.
