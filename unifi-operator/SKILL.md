---
name: unifi-operator
description: "Operate UniFi Network and UniFi Protect through their local APIs on a UDM/UDM-Pro/Cloud Key/self-hosted console. Use when managing UniFi gateways, switches, access points, clients, firewall, VLANs/WLANs, port-forwards, hotspot vouchers, or Protect cameras, recordings, events, lights, sensors, chimes, and alarms; when building curl calls to /proxy/network or /proxy/protect; or when the user mentions UniFi, Ubiquiti, UDM, Cloud Key, UniFi OS, X-API-KEY, or controller API keys. Covers both the official API-key integration APIs and the reverse-engineered private controller/Protect APIs plus the realtime WebSocket."
---

# UniFi Operator

Operate a UniFi OS console (UDM, UDM-Pro/SE, UDR, UCG, Cloud Key Gen2+, or self-hosted Network/Protect) over HTTP. Two product apps, each with a stable official API and a comprehensive private API:

- **Network** — gateways, switches, APs, clients, VLANs, WLANs, firewall, routing, port-forwards, DPI, guest/hotspot, device adoption & lifecycle.
- **Protect** — cameras, recordings, snapshots, smart-detection events, lights, sensors, chimes, sirens, viewers, alarm manager, realtime updates.

All four surfaces live on **one console at port 443** behind a **self-signed TLS cert** (every `curl` uses `-k`). Cloud Site Manager (`api.ui.com`) is out of scope — this skill is local-console only.

## API surface map

| Surface | Base path | Auth | Stability | Coverage |
|---------|-----------|------|-----------|----------|
| **Network — official** | `/proxy/network/integration/v1` | `X-API-KEY` header (stateless) | GA, stable | ~60% — sites, devices, clients, vouchers, networks, WLANs, firewall, ACL, DNS |
| **Network — private** | `/proxy/network/api/s/<site>` | Cookie `TOKEN` + `x-csrf-token` | Unsupported, shifts across versions | ~100% — everything the web UI does (stats, `rest/*` CRUD, `cmd/*` actions) |
| **Protect — official** | `/proxy/protect/integration/v1` | `X-API-KEY` header (stateless) | GA, stable (Protect 5.3+) | ~70% — cameras, snapshot, RTSPS, PTZ, lights/sensors/chimes, arm profiles, WS |
| **Protect — private** | `/proxy/protect/api` | Cookie `TOKEN` + `X-CSRF-Token` | Unsupported, shifts across versions | ~100% — `/bootstrap`, video export, events/thumbnails, realtime delta WebSocket |

Pick the **official** surface first (stateless API key, survives upgrades). Drop to the **private** surface for anything official omits: firewall/WLAN CRUD on older firmware, client block/unblock, device adopt/locate/speedtest, full Protect bootstrap, recorded-video export, and the realtime updates socket.

## References

| File | When to read |
|------|--------------|
| [references/auth-and-conventions.md](references/auth-and-conventions.md) | API-key creation, UniFi OS login + CSRF derivation, legacy `:8443`, response envelopes, pagination, the official filter DSL, error tables, reusable shell helpers |
| [references/network-integration-api.md](references/network-integration-api.md) | Official Network v1 — full endpoint catalog, device/client/port actions, voucher schema, firewall/WLAN/ACL/DNS CRUD |
| [references/network-private-api.md](references/network-private-api.md) | Private Network — `stat/*` monitoring, `rest/*` CRUD, every `cmd/*` action + payload, reports, settings keys, backups |
| [references/protect-integration-api.md](references/protect-integration-api.md) | Official Protect v1 — cameras/PATCH, snapshot, RTSPS, PTZ, lights/sensors/chimes/sirens, arm profiles, subscribe WebSocket, alarm webhook |
| [references/protect-private-api.md](references/protect-private-api.md) | Private Protect — `/bootstrap`, camera control, video export, events/thumbnails/heatmap, the binary realtime WebSocket frame protocol |

## Environment & auth quick-start

```bash
HOST="192.168.1.1"          # console IP or hostname
CURL=(curl -ksS)            # -k self-signed, -s quiet, -S show errors
```

### Official APIs — API key (stateless)

One console-wide key (created in **Settings → Control Plane → Integrations** in either Network or Protect; inherits the creating admin's permissions). Same key works for both Network and Protect on that console.

```bash
KEY="paste-api-key"
H=(-H "X-API-KEY: $KEY" -H "Accept: application/json")

"${CURL[@]}" "${H[@]}" "https://$HOST/proxy/network/integration/v1/info"      # Network version
"${CURL[@]}" "${H[@]}" "https://$HOST/proxy/protect/integration/v1/meta/info" # Protect version
```

### Private APIs — login + CSRF (cookie session)

Login once; reuse the cookie jar. Mutating calls (POST/PUT/PATCH/DELETE) require the CSRF token returned by login. A **local** admin account is required — Ubiquiti cloud SSO logins and MFA-enabled accounts do not work for scripted login (see [auth reference](references/auth-and-conventions.md)).

```bash
CSRF=$("${CURL[@]}" -c /tmp/uni.jar -D - -o /dev/null \
  -X POST "https://$HOST/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"secret"}' \
  | awk 'tolower($1)=="x-csrf-token:"{print $2}' | tr -d '\r')

S=("${CURL[@]}" -b /tmp/uni.jar)                          # authenticated GET
M=("${CURL[@]}" -b /tmp/uni.jar -H "x-csrf-token: $CSRF") # authenticated mutation

"${S[@]}" "https://$HOST/proxy/network/api/self/sites"    # list sites -> use .name as <site>
"${S[@]}" "https://$HOST/proxy/protect/api/bootstrap"     # entire Protect state
```

`<site>` in private Network paths is the internal **slug** (often `default`), from `self/sites[].name` — not the display label. Response envelope is `{"meta":{"rc":"ok"},"data":[...]}`; `rc:"error"` carries `meta.msg`.

## Capability → endpoint matrix

### Network

| Capability | Surface · Endpoint |
|-----------|-------------------|
| List connected clients | official `GET .../clients` · private `GET stat/sta` |
| Client detail / history | private `GET stat/user/<mac>`, `POST stat/session` |
| Authorize / unauthorize **guest** | official `POST .../clients/{id}/actions` `{AUTHORIZE_GUEST_ACCESS}` |
| **Block / unblock** a client | private `POST cmd/stamgr` `{block-sta\|unblock-sta, mac}` |
| Reconnect (kick) a client | private `POST cmd/stamgr` `{kick-sta, mac}` |
| Forget a client | private `POST cmd/stamgr` `{forget-sta, macs:[...]}` |
| List devices (gw/sw/ap) | official `GET .../devices` · private `GET stat/device` |
| Device stats snapshot | official `GET .../devices/{id}/statistics/latest` |
| Restart a device | official `POST .../devices/{id}/actions` `{RESTART}` · private `cmd/devmgr` `{restart, mac}` |
| PoE power-cycle a port | official `POST .../ports/{idx}/actions` `{POWER_CYCLE}` · private `cmd/devmgr` `{power-cycle, mac, port_idx}` |
| Adopt / forget device | official `POST/DELETE .../devices` · private `cmd/devmgr` `{adopt}` |
| Locate (blink LED) | private `cmd/devmgr` `{set-locate\|unset-locate, mac}` |
| Upgrade firmware | private `POST cmd/devmgr/upgrade` `{mac}` |
| Run speedtest / spectrum scan | private `cmd/devmgr` `{speedtest}` / `{spectrum-scan, mac}` |
| Site health / sysinfo | private `GET stat/health`, `stat/sysinfo`, `stat/dashboard` |
| Events / alarms / IPS | private `GET stat/event`, `list/alarm`, `stat/ips/event` |
| Usage reports (5m/hr/day) | private `POST stat/report/<interval>.<scope>` |
| DPI by app/category | private `POST stat/sitedpi`, `GET stat/dpi` |
| Networks / VLANs | official CRUD `.../networks` · private `rest/networkconf` |
| WLANs / SSIDs | official CRUD `.../wifi/broadcasts` · private `rest/wlanconf` |
| Firewall zones/policies | official CRUD `.../firewall/zones`, `.../firewall/policies` (+`/ordering`) |
| Firewall groups/rules (legacy) | private `rest/firewallgroup`, `rest/firewallrule` |
| Port forwarding | private `rest/portforward`; toggle via `PUT` `{enabled}` |
| Static routes | private `rest/routing` |
| Hotspot vouchers | official `GET/POST/DELETE .../hotspot/vouchers` · private `cmd/hotspot` `{create-voucher}` |
| Per-client fixed IP / name | private `PUT rest/user/<id>` |
| Site / admin management | private `cmd/sitemgr` `{add-site, invite-admin, move-device, ...}` |
| Backups | private `cmd/backup` `{backup, list-backups}`, `GET /dl/backup/...` |

### Protect

| Capability | Surface · Endpoint |
|-----------|-------------------|
| Entire system state | private `GET /bootstrap` (cameras, nvr, lights, sensors, users, `lastUpdateId`) |
| List cameras | official `GET /cameras` · private from `/bootstrap.cameras[]` |
| Live snapshot (JPEG) | official `GET /cameras/{id}/snapshot?highQuality=true` · private `?ts=<ms>&force=true` |
| Historical snapshot | private `GET /cameras/{id}/recording-snapshot?ts=<ms>` |
| **Export recorded MP4** | private `GET /video/export?camera={id}&start=<ms>&end=<ms>&channel=0` |
| RTSPS stream URL | official `GET/POST/DELETE /cameras/{id}/rtsps-stream` |
| Rename / OSD / LED / HDR / video mode | official `PATCH /cameras/{id}` · private `PATCH /cameras/{id}` |
| Recording mode | private `PATCH /cameras/{id}` `{recordingSettings:{mode}}` |
| Smart-detect object types | official/private `PATCH /cameras/{id}` `{smartDetectSettings:{objectTypes}}` |
| Doorbell LCD message | official `PATCH /cameras/{id}` `{lcdMessage}` |
| PTZ preset / patrol | official `POST /cameras/{id}/ptz/goto/{slot}`, `/ptz/patrol/start/{slot}` |
| Two-way talkback | official `POST /cameras/{id}/talkback-session` |
| List / filter events | private `GET /events?start=&end=&types=&smartDetectTypes=` |
| Event thumbnail / heatmap | private `GET /events/{id}/thumbnail`, `/animated-thumbnail`, `/heatmap` |
| Lights / sensors / chimes | official+private `GET/PATCH /lights\|sensors\|chimes/{id}` |
| Trigger chime / siren | private `POST /chimes/{id}/play-speaker` · official `POST /sirens/{id}/play` |
| Arm / disarm alarms | official `POST /arm-profiles/enable\|disable`, `PATCH /arm-profiles/settings` |
| Trigger alarm via webhook | official `POST /alarm-manager/webhook/{id}` |
| Realtime device/event stream | official `WS /subscribe/devices`, `/subscribe/events` (JSON) · private `WS /ws/updates` (binary delta) |
| Reboot camera / NVR | private `POST /cameras/{id}/reboot`, `POST /nvr/reboot` |

## Essential recipes

```bash
# --- Network: official ---
NB="https://$HOST/proxy/network/integration/v1"
SITE=$("${CURL[@]}" "${H[@]}" "$NB/sites" | jq -r '.data[0].id')   # most consoles: one site

# Find a noisy guest and read its detail
"${CURL[@]}" "${H[@]}" --get "$NB/sites/$SITE/clients" \
  --data-urlencode "filter=name.like('guest*')" --data-urlencode "limit=50" | jq

# PoE power-cycle port 5 of a switch (deviceId from /devices)
"${CURL[@]}" "${H[@]}" -H "Content-Type: application/json" -X POST \
  "$NB/sites/$SITE/devices/$DEVICE/interfaces/ports/5/actions" -d '{"action":"POWER_CYCLE"}'

# Issue 10 lobby vouchers, 24h, 1 GB cap
"${CURL[@]}" "${H[@]}" -H "Content-Type: application/json" -X POST \
  "$NB/sites/$SITE/hotspot/vouchers" \
  -d '{"name":"Lobby","count":10,"timeLimitMinutes":1440,"dataUsageLimitMBytes":1024}'

# --- Network: private (block a client the official API can't) ---
NP="https://$HOST/proxy/network/api/s/default"
"${M[@]}" -H "Content-Type: application/json" -X POST \
  "$NP/cmd/stamgr" -d '{"cmd":"block-sta","mac":"aa:bb:cc:dd:ee:ff"}'

# --- Protect: snapshot every camera ---
PB="https://$HOST/proxy/protect/integration/v1"
for id in $("${CURL[@]}" "${H[@]}" "$PB/cameras" | jq -r '.[].id'); do
  "${CURL[@]}" "${H[@]}" "$PB/cameras/$id/snapshot?highQuality=true" -o "cam-$id.jpg"
done

# --- Protect: export last 10 minutes of recorded video (private) ---
NOW=$(($(date +%s)*1000)); AGO=$((NOW-600000))
"${S[@]}" "https://$HOST/proxy/protect/api/video/export?camera=$CAM&start=$AGO&end=$NOW&channel=0" -o clip.mp4
```

## Red flags

| Pattern | Risk |
|---------|------|
| Omitting `-k` on curl | TLS verify fails on the console's self-signed cert |
| Mutating private endpoint without `x-csrf-token` | `401`; the call silently does nothing |
| Using the UI display name as `<site>` | `api.err.NoSiteContext`; the slug (`default`) is required |
| `POST rest/<resource>/<id>` to edit | Creates a duplicate; `PUT` updates, `POST` creates |
| Polling `GET /bootstrap` on a timer | Heavy full-state payload; the `/ws/updates` socket delivers deltas instead |
| Logging in with a cloud-SSO or MFA account | Scripted `/api/auth/login` fails; a local non-MFA admin is required |
| Assuming private paths are stable | `rest/routing`, `rest/tag` and others return `500`/`Invalid` on some firmware (see references) |
| Hardcoding `siteId` across consoles | Official `siteId` is a per-console UUID, not the `default` slug |
| Treating official API as complete | No client block/unblock, no Protect `/bootstrap`, no video export — drop to private |
