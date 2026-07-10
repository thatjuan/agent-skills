# Network — Private (Reverse-Engineered) API

The internal API the Network web UI calls. UniFi OS: `https://<host>/proxy/network/api/s/<site>/...`. Legacy controller: `https://<host>:8443/api/s/<site>/...`. **Unsupported and version-dependent** — some `rest/*` reads return `500`/`Invalid` on certain firmware (flagged below). Endpoint→behavior mapping is taken from the Art-of-WiFi `Client.php` source (1:1 method↔endpoint). Login/CSRF/envelope: `auth-and-conventions.md`.

## Contents

- [Conventions](#conventions)
- [Stat / monitoring](#stat--monitoring)
- [Reports](#reports)
- [List / config-read](#list--config-read)
- [REST CRUD (`rest/*`)](#rest-crud-rest)
- [Settings sub-keys](#settings-sub-keys)
- [cmd reference (all commands)](#cmd-reference-all-commands)
- [Guest / hotspot / vouchers](#guest--hotspot--vouchers)
- [Device lifecycle / firmware](#device-lifecycle--firmware)
- [Site & admin management](#site--admin-management)
- [Events, alarms, backups](#events-alarms-backups)
- [v2 API endpoints](#v2-api-endpoints)
- [Examples](#examples)

## Conventions

- Paths below are **relative to `/api/s/<site>`**. On UniFi OS prepend `/proxy/network`; on legacy use `:8443` and no prefix. Paths shown starting with `/api/...` are console-scoped (no site).
- Envelope `{"meta":{"rc":"ok"},"data":[...]}`; check `rc`. A `meta.count` means `data` was truncated (e.g. events/alarms cap ~3000).
- REST verbs: `GET`=list, `GET/{id}`=read, **`POST`=create**, **`PUT/{id}`=update**, `DELETE/{id}`=delete. POSTing to edit creates a duplicate.
- `stat/*` reads take `_start`/`_limit`/`_sort` or a POST JSON body `{start,end,attrs,macs,type}` with **millisecond** timestamps.
- `<site>` is the slug (`default`), from `/api/self/sites[].name`.

## Stat / monitoring

| Method | Path | Purpose | Params/body |
|--------|------|---------|-------------|
| GET | `stat/health` | Per-subsystem site health | — |
| GET | `stat/dashboard` | Dashboard time-series | `?scale=5minutes` |
| GET | `stat/sysinfo` | Controller/site info | — |
| GET | `stat/sta` | **Active clients** | — |
| GET | `stat/sta/<mac>` | One active client | — |
| GET | `stat/user/<mac>` | Stored per-client stats | — |
| GET | `stat/alluser` | Clients seen in window | `{type,conn,within}` (hrs) |
| GET | `stat/guest` | Active guest authorizations | — |
| GET/POST | `stat/device` | **Device list / detail** | POST `{macs:[...]}`; or `stat/device/<mac>` |
| GET | `stat/device-basic` | Lightweight device list | — |
| POST | `stat/session` | Client sessions | `{type,start,end,mac,_limit,_sort:"-assoc_time"}` |
| POST | `stat/authorization` | Guest authorizations in window | `{start,end}` (ms) |
| GET | `stat/event` | Events, newest first (~3000 cap) | `{_start,_limit,within}` |
| GET | `list/alarm` | Alarms | `{archived:false}` |
| GET | `cnt/alarm` | Alarm count | `{archived:false}` |
| GET | `stat/dpi` | Aggregate DPI | — |
| GET/POST | `stat/sitedpi` | Site DPI, filterable | POST `{type:"by_app"\|"by_cat"}` |
| GET/POST | `stat/stadpi` | Per-client DPI | POST `{macs,by_app/by_cat}` ⚠️ |
| GET | `stat/portforward` | Port-forward runtime stats | — |
| POST | `stat/rogueap` | Neighboring/rogue APs | `{within:<hrs>}` |
| GET | `stat/spectrum-scan/<mac>` | AP spectrum-scan results | — |
| GET | `stat/current-channel` | Allowed channels for country | — |
| GET | `stat/ccode` | Country codes | — |
| GET | `stat/voucher` | Hotspot vouchers | `{create_time}` |
| GET | `stat/payment` | Hotspot payments | — |
| GET | `stat/ips/event` | IPS/IDS events | `{start,end,_limit}` |
| GET | `stat/fwupdate/latest-version` | Latest available firmware | — |

## Reports

`POST stat/report/<interval>.<scope>` with body `{attrs:[...], start, end, macs?}` (ms). Intervals: `5minutes`, `hourly`, `daily`, `monthly`. Scopes: `site`, `ap`, `user`, `gw`. Plus `stat/report/archive.speedtest` for stored speedtest results.

Common `attrs`: `bytes`, `wan-tx_bytes`, `wan-rx_bytes`, `rx_bytes`, `tx_bytes`, `num_sta`, `time`.

## List / config-read

| Path | Returns |
|------|---------|
| `list/user` | Known/configured clients |
| `list/usergroup` | Bandwidth user groups |
| `list/wlangroup` | WLAN groups |
| `list/portforward` | Port-forward rules |
| `list/portconf` | Switch port profiles |
| `list/extension` | Telephony extensions |
| `get/setting` | All site settings (every sub-key) |
| `self` | Current admin's context for this site |
| `/api/self/sites` | All sites (slug `name` + label `desc`) |
| `/api/stat/sites` | Sites + health/alert rollups |
| `/api/stat/admin` | All admins |

## REST CRUD (`rest/*`)

| Resource | Path | Verbs | Notes |
|----------|------|-------|-------|
| WLAN config | `rest/wlanconf` | GET, GET/`{id}`, PUT/`{id}`; create via `POST add/wlanconf` | enable/disable, MAC-filter via PUT |
| Network config | `rest/networkconf` | GET, GET/`{id}`, POST, PUT/`{id}`, DELETE/`{id}` | full CRUD (VLANs) |
| Firewall group | `rest/firewallgroup` | GET, GET/`{id}`, POST, PUT/`{id}`, DELETE/`{id}` | address/port groups |
| Firewall rule | `rest/firewallrule` | GET, PUT/`{id}` | create/delete ⚠️ not in client |
| Port forward | `rest/portforward` | GET, PUT/`{id}` `{enabled}` | toggle/edit |
| Routing (static) | `rest/routing` | GET, GET/`{id}` | ⚠️ `500` on v7.1.66+ |
| User (client) | `rest/user` | GET/`{id}`, PUT/`{id}`; create via `POST group/user` | fixed-IP, name, note |
| Usergroup | `rest/usergroup` | POST, PUT/`{id}`, DELETE/`{id}` | bandwidth limits |
| Dynamic DNS | `rest/dynamicdns` | GET, POST, PUT/`{id}` | |
| RADIUS profile | `rest/radiusprofile` | GET, POST | |
| RADIUS account | `rest/account` | GET, POST, PUT/`{id}`, DELETE/`{id}` | |
| Hotspot operator | `rest/hotspotop` | GET, POST | |
| Tag | `rest/tag` | GET, GET/`{id}`, POST, PUT/`{id}`, DELETE/`{id}` | ⚠️ `Invalid` on v7.1.66+ |
| Known rogue AP | `rest/rogueknown` | GET | |
| Device config | `rest/device/<id>` | PUT/`{id}` | disable AP, LED override, radio settings |
| Setting (per key) | `rest/setting/<key>/<id>` | GET, PUT | see settings keys |

> Plausible but **unverified** in maintained clients (use cautiously): `rest/scheduletask`, `rest/broadcastgroup`, `rest/spatialrecord`, `rest/dhcpoption`, `rest/dpiapp`, `rest/dpigroup`, `rest/portconf`.

## Settings sub-keys

Two forms: `POST set/setting/<key>` (posts a settings blob) and `PUT rest/setting/<key>/<id>` (updates a specific settings object). Verified keys: `mgmt`, `guest_access`, `country`, `locale`, `snmp`, `ntp`, `connectivity`, `ips`, `super_mgmt`, `super_smtp`, `super_identity`, `element_adopt`. `get/setting` returns all keys (also `usg`, `rsyslogd`, `dpi`, `porta`, `lcm`, …).

## cmd reference (all commands)

`POST cmd/<mgr>` with body `{"cmd":"<value>", ...}`. Mutations need the CSRF header on UniFi OS.

| Manager | `cmd` values | Common extra fields |
|---------|--------------|---------------------|
| `cmd/stamgr` | `authorize-guest`, `unauthorize-guest`, `kick-sta`, `block-sta`, `unblock-sta`, `forget-sta` | `mac` (or `macs:[]` for forget); guest: `minutes`, `up`, `down`, `bytes`, `ap_mac` |
| `cmd/devmgr` | `adopt`, `adv-adopt`, `migrate`, `cancel-migrate`, `restart`, `force-provision`, `set-locate`, `unset-locate`, `power-cycle`, `spectrum-scan`, `speedtest`, `speedtest-status`, `unset-rollupgrade` | `mac`; `power-cycle` adds `port_idx`; `migrate` adds `inform_url`; `restart` adds `reboot_type` |
| `cmd/sitemgr` | `add-site`, `delete-site`, `update-site`, `get-admins`, `invite-admin`, `grant-admin`, `update-admin`, `revoke-admin`, `revoke-super-admin`, `move-device`, `delete-device` | `desc`, `site`, `mac`, `site_id`, `name`, `email`, `role` |
| `cmd/hotspot` | `create-voucher`, `delete-voucher`, `extend` | see vouchers below |
| `cmd/backup` | `backup`, `list-backups`, `export-site`, `delete-backup` | `days`, `filename` |
| `cmd/evtmgr` | `archive-all-alarms`, `archive-alarm` | `_id` |
| `cmd/system` | `reboot`, `check-firmware-update` | — |
| `cmd/firmware` | `list-available`, `list-cached` | — |
| `cmd/stat` | `clear-dpi` ⚠️ | — |

Device-upgrade sub-paths (no `cmd` body needed): `POST cmd/devmgr/upgrade` `{mac}`, `cmd/devmgr/upgrade-all`, `cmd/devmgr/upgrade-external` `{mac,url}`, `cmd/devmgr/set-rollupgrade`.

## Guest / hotspot / vouchers

| Method | Path | Body | Purpose |
|--------|------|------|---------|
| POST | `cmd/hotspot` | `{cmd:"create-voucher", expire:<min>, n:<count>, quota:<0=multi\|1=single>, note?, up?, down?, bytes?}` | Create vouchers |
| POST | `cmd/hotspot` | `{cmd:"delete-voucher", _id}` | Revoke voucher |
| POST | `cmd/hotspot` | `{cmd:"extend", _id}` | Extend authorization |
| GET | `stat/voucher` | `{create_time?}` | List vouchers |
| GET | `stat/payment` | — | List payments |
| POST | `cmd/stamgr` | `{cmd:"authorize-guest", mac, minutes, up?, down?, bytes?, ap_mac?}` | Authorize guest |
| POST | `cmd/stamgr` | `{cmd:"unauthorize-guest", mac}` | Unauthorize guest |

`up`/`down` are kbps rate limits; `bytes` is a data quota; `quota` is uses-per-voucher (`0`=multi-use).

## Device lifecycle / firmware

| Method | Path | Body | Purpose |
|--------|------|------|---------|
| POST | `cmd/devmgr` | `{cmd:"adopt", mac}` | Adopt |
| POST | `cmd/devmgr` | `{cmd:"restart", mac, reboot_type?}` | Restart (soft `reboot_type:"soft"`) |
| POST | `cmd/devmgr` | `{cmd:"force-provision", mac}` | Re-push config |
| POST | `cmd/devmgr` | `{cmd:"set-locate"\|"unset-locate", mac}` | LED locate on/off |
| POST | `cmd/devmgr` | `{cmd:"power-cycle", mac, port_idx}` | PoE port cycle |
| POST | `cmd/devmgr` | `{cmd:"spectrum-scan", mac}` | AP RF scan (poll via `stat/spectrum-scan/<mac>`) |
| POST | `cmd/devmgr` | `{cmd:"speedtest"}` / `{cmd:"speedtest-status"}` | Run / poll gateway speedtest |
| POST | `cmd/devmgr` | `{cmd:"migrate", mac, inform_url}` / `{cmd:"cancel-migrate", mac}` | Set inform URL |
| PUT | `rest/device/<id>` | `{disabled}` / `{led_override}` / radio fields | Per-device config |

## Site & admin management

| Method | Path | Body | Purpose |
|--------|------|------|---------|
| POST | `cmd/sitemgr` | `{cmd:"add-site", desc}` | Create site |
| POST | `cmd/sitemgr` | `{cmd:"delete-site", site:<id>}` | Delete site |
| POST | `cmd/sitemgr` | `{cmd:"update-site", desc}` | Rename/describe |
| POST | `cmd/sitemgr` | `{cmd:"invite-admin", name, email, role}` | Invite admin |
| POST | `cmd/sitemgr` | `{cmd:"move-device", mac, site_id}` | Move device between sites |
| POST | `/api/system/reboot` / `/api/system/poweroff` | — (CSRF + super-admin) | Reboot/poweroff the console |

## Events, alarms, backups

| Method | Path | Body | Purpose |
|--------|------|------|---------|
| POST | `cmd/evtmgr` | `{cmd:"archive-all-alarms"}` | Archive all alarms |
| POST | `cmd/evtmgr` | `{cmd:"archive-alarm", _id}` | Archive one |
| POST | `cmd/backup` | `{cmd:"backup", days}` | Generate `.unf` backup |
| POST | `cmd/backup` | `{cmd:"list-backups"}` | List autobackups |
| POST | `cmd/backup` | `{cmd:"export-site"}` | Export site |
| GET | `/dl/backup/...`, `/dl/autobackup/autobackup_<ver>_<date>_<time>.unf` | — | Download backup file |

## v2 API endpoints

A few features live under `/v2/api/site/<site>/...` (no `/api/s/` prefix):

| Method | Path | Purpose |
|--------|------|---------|
| GET/POST/PUT/DELETE | `/v2/api/site/<site>/trafficrules` (+ `/{id}`) | Traffic rules (PUT returns 201) |
| GET/POST/PUT/DELETE | `/v2/api/site/<site>/apgroups` (+ `/{id}`) | AP groups |
| POST | `/v2/api/site/<site>/system-log/<class>` | System log query |
| GET | `/v2/api/fingerprint_devices/<source>` | Client fingerprint DB |

## Examples

```bash
# (after uni_login from auth-and-conventions.md; CSRF + /tmp/uni.jar set)
NP="https://$HOST/proxy/network/api/s/default"; CURL=(curl -ksS -b /tmp/uni.jar)

# Top 10 talkers right now
"${CURL[@]}" "$NP/stat/sta" | jq -r '.data | sort_by(-.tx_bytes-.rx_bytes)[:10]
  | .[] | "\(.hostname // .mac)\t\(((.tx_bytes+.rx_bytes)/1e6|floor))MB"'

# Block, then later unblock, a client
"${CURL[@]}" -H "x-csrf-token: $CSRF" -H "Content-Type: application/json" -X POST \
  "$NP/cmd/stamgr" -d '{"cmd":"block-sta","mac":"aa:bb:cc:dd:ee:ff"}'

# Toggle a port-forward off (read id from list/portforward)
"${CURL[@]}" -H "x-csrf-token: $CSRF" -H "Content-Type: application/json" -X PUT \
  "$NP/rest/portforward/$PF_ID" -d '{"enabled":false}'

# Daily site usage for the last 7 days
END=$(($(date +%s)*1000)); START=$((END-7*86400000))
"${CURL[@]}" -H "x-csrf-token: $CSRF" -H "Content-Type: application/json" -X POST \
  "$NP/stat/report/daily.site" \
  -d "{\"attrs\":[\"wan-tx_bytes\",\"wan-rx_bytes\",\"time\"],\"start\":$START,\"end\":$END}" | jq
```
