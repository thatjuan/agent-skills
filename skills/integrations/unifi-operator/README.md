# unifi-operator

> Expertise for operating UniFi Network and UniFi Protect through their local APIs on a UDM, Cloud Key, or self-hosted console — official API-key surfaces and the reverse-engineered private controller APIs, plus the realtime WebSocket.

## What it does

`unifi-operator` makes your agent fluent in driving a UniFi OS console over HTTP. Two product apps (Network and Protect) each expose a stable official API and a comprehensive private API, all on one console at port 443 behind a self-signed cert. The skill covers:

- **The API surface map** — official Network/Protect (`/integration/v1`, `X-API-KEY`, stable) vs. private Network/Protect (cookie + CSRF, ~100% coverage but unsupported and version-shifting), and when to drop from one to the other.
- **Authentication** — creating a console-wide API key, the UniFi OS login + CSRF derivation for private calls, and why cloud-SSO/MFA accounts fail for scripted login.
- **Network operations** — clients, devices (gateways/switches/APs), block/unblock, restart, PoE power-cycle, adopt/locate/upgrade, VLANs/WLANs, firewall zones and policies, port-forwards, vouchers, and reports.
- **Protect operations** — the `/bootstrap` full-state read, cameras, live and historical snapshots, recorded-MP4 export, RTSPS, PTZ, smart-detect settings, lights/sensors/chimes/sirens, arm profiles, and the realtime update stream.
- **A capability → endpoint matrix** mapping each task to its official and/or private endpoint, plus copy-pasteable curl recipes and a red-flags table.

It triggers when managing UniFi gateways, switches, APs, clients, firewall, or Protect cameras; when building curl calls to `/proxy/network` or `/proxy/protect`; or when the user mentions UniFi, Ubiquiti, UDM, Cloud Key, UniFi OS, `X-API-KEY`, or controller API keys.

## When to use it

Invoke this skill when you hear:

- *"List every connected client and read one client's session history."*
- *"Block this MAC — the official API doesn't seem to support it."* (drop to the private `cmd/stamgr`)
- *"PoE power-cycle port 5 on this switch."*
- *"Issue 10 hotspot vouchers, 24h, 1 GB cap."*
- *"Snapshot every Protect camera and export the last 10 minutes of video."*
- *"Subscribe to realtime device and smart-detection events."*

## Example walkthrough

Asked to block a client, the skill first notes the official API can't do it, then drops to the private surface: log in to `/api/auth/login`, capture the `x-csrf-token`, and `POST /proxy/network/api/s/<site>/cmd/stamgr` with `{"cmd":"block-sta","mac":...}` — using the site **slug** (`default`), not the UI display name, and including the CSRF header so the mutation isn't silently dropped. Every curl carries `-k` for the console's self-signed cert.

## Installation

```bash
npx skills add thatjuan/agent-skills --skill unifi-operator
```

## Bundled resources

| File | Purpose |
|------|---------|
| `SKILL.md` | API surface map, auth quick-start, capability → endpoint matrix for Network and Protect, essential curl recipes, red-flags table |
| `references/auth-and-conventions.md` | API-key creation, UniFi OS login + CSRF derivation, legacy `:8443`, response envelopes, pagination, the official filter DSL, error tables, reusable shell helpers |
| `references/network-integration-api.md` | Official Network v1 — full endpoint catalog, device/client/port actions, voucher schema, firewall/WLAN/ACL/DNS CRUD |
| `references/network-private-api.md` | Private Network — `stat/*` monitoring, `rest/*` CRUD, every `cmd/*` action and payload, reports, settings keys, backups |
| `references/protect-integration-api.md` | Official Protect v1 — cameras/PATCH, snapshot, RTSPS, PTZ, lights/sensors/chimes/sirens, arm profiles, subscribe WebSocket, alarm webhook |
| `references/protect-private-api.md` | Private Protect — `/bootstrap`, camera control, video export, events/thumbnails/heatmap, the binary realtime WebSocket frame protocol |

## Tips

- **Every curl needs `-k`.** The console serves a self-signed cert; omitting `-k` fails TLS verification.
- **Prefer the official surface first.** The stateless `X-API-KEY` survives upgrades; drop to the private cookie+CSRF surface only for what official omits (client block/unblock, device adopt/locate/speedtest, Protect `/bootstrap`, video export, realtime deltas).
- **Private mutations require `x-csrf-token`.** Without it the call returns 401 and silently does nothing.
- **`<site>` is the slug, not the display name.** Read it from `self/sites[].name` — usually `default`. The UI label yields `api.err.NoSiteContext`.
- **`PUT` updates, `POST` creates.** `POST rest/<resource>/<id>` to "edit" makes a duplicate.
- **Don't poll `/bootstrap` on a timer** — it's a heavy full-state payload; the `/ws/updates` socket delivers deltas instead.
- **Scripted login needs a local, non-MFA admin.** Cloud-SSO and MFA accounts fail `/api/auth/login`.

## Related skills

- None in this repo yet — pair with any home/network automation workflow.
