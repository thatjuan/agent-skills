# Network — Official Integration API (v1)

Stable, API-key, stateless REST API at `https://<host>/proxy/network/integration/v1`. GA since Network app ~9.3; catalog below reflects spec 10.4.57. Older consoles expose a subset — call `GET /v1/info` to read the running `applicationVersion`. Auth/pagination/filter/error details: `auth-and-conventions.md`.

## Contents

- [Conventions](#conventions)
- [Console-level resources](#console-level-resources)
- [Devices](#devices)
- [Clients](#clients)
- [Hotspot vouchers](#hotspot-vouchers)
- [Networks, WiFi, Firewall, DNS, ACL](#networks-wifi-firewall-dns-acl)
- [WAN, VPN, switching, RADIUS, tags](#wan-vpn-switching-radius-tags)
- [Examples](#examples)

## Conventions

- Header `X-API-KEY`; `Accept: application/json`; writes add `Content-Type: application/json`.
- List endpoints take `offset`, `limit`, `filter`; return `{offset,limit,count,totalCount,data}`. Single GETs return the object.
- `{siteId}` is a per-console UUID from `GET /v1/sites` (`data[].id`) — not the `default` slug.
- Action endpoints discriminate on the `action` field in the POST body.

## Console-level resources

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/v1/info` | Application version `{applicationVersion}` — connectivity smoke test |
| GET | `/v1/sites` | List sites → grab `data[].id` as `{siteId}` |
| GET | `/v1/pending-devices` | Devices awaiting adoption (console-wide) |
| GET | `/v1/dpi/categories` | DPI category reference data |
| GET | `/v1/dpi/applications` | DPI application reference data |
| GET | `/v1/countries` | Country reference data |

## Devices

Base: `/v1/sites/{siteId}/devices`

| Method | Path | Purpose | Body |
|--------|------|---------|------|
| GET | `/devices` | List adopted devices (summary) | — |
| POST | `/devices` | Adopt pending device(s) | adoption request (MAC; ignore-device-limit flag) |
| GET | `/devices/{deviceId}` | Full device detail | — |
| DELETE | `/devices/{deviceId}` | Forget / unadopt device | — |
| GET | `/devices/{deviceId}/statistics/latest` | Latest metrics (uptime, CPU, mem, throughput) | — |
| POST | `/devices/{deviceId}/actions` | Device action | `{"action":"RESTART"}` |
| POST | `/devices/{deviceId}/interfaces/ports/{portIdx}/actions` | Port action | `{"action":"POWER_CYCLE"}` |

- **Device action enum:** `RESTART`.
- **Port action enum:** `POWER_CYCLE` (PoE power-cycle). `portIdx` is the 1-based port index.

## Clients

Base: `/v1/sites/{siteId}/clients`

| Method | Path | Purpose | Body |
|--------|------|---------|------|
| GET | `/clients` | List connected clients (supports `filter`) | — |
| GET | `/clients/{clientId}` | Client detail | — |
| POST | `/clients/{clientId}/actions` | Guest action | see below |

**Client action enum:** `AUTHORIZE_GUEST_ACCESS`, `UNAUTHORIZE_GUEST_ACCESS`.

`AUTHORIZE_GUEST_ACCESS` body (all extra fields optional; resets traffic counters):

```json
{ "action":"AUTHORIZE_GUEST_ACCESS",
  "timeLimitMinutes":1440, "dataUsageLimitMBytes":1024,
  "rxRateLimitKbps":5000, "txRateLimitKbps":5000 }
```

`UNAUTHORIZE_GUEST_ACCESS` body: `{"action":"UNAUTHORIZE_GUEST_ACCESS"}`.

> The v1 API has **no generic block/unblock** for non-guest clients — use the private `cmd/stamgr` (`block-sta`/`unblock-sta`) in `network-private-api.md`.

## Hotspot vouchers

Base: `/v1/sites/{siteId}/hotspot/vouchers` (list default `limit` 100, max 1000)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/hotspot/vouchers` | List vouchers |
| POST | `/hotspot/vouchers` | Create voucher batch (returns generated codes) |
| GET | `/hotspot/vouchers/{voucherId}` | One voucher |
| DELETE | `/hotspot/vouchers/{voucherId}` | Delete one |
| DELETE | `/hotspot/vouchers` | Bulk delete — **`filter` query is required** (guards against wiping all) |

Create body:

| Field | Type | Req | Range | Meaning |
|-------|------|-----|-------|---------|
| `name` | string | yes | len ≥1 | Note on all generated vouchers |
| `timeLimitMinutes` | int | yes | 1–1,000,000 | Access duration from first authorization |
| `count` | int | no | 1–1000 (default 1) | How many to generate |
| `authorizedGuestLimit` | int | no | ≥1 | Max distinct guests per voucher |
| `dataUsageLimitMBytes` | int | no | 1–1,048,576 | Data cap (MB) |
| `rxRateLimitKbps` | int | no | 2–100,000 | Download cap |
| `txRateLimitKbps` | int | no | 2–100,000 | Upload cap |

## Networks, WiFi, Firewall, DNS, ACL

Full CRUD on configuration objects (verbs: `GET` list, `GET /{id}` read, `POST` create, `PUT /{id}` replace, `DELETE /{id}`).

| Resource | Base path | Verbs |
|----------|-----------|-------|
| Networks (VLANs) | `/v1/sites/{siteId}/networks` | GET, POST, GET/PUT/DELETE `/{id}`; `GET /{id}/references` |
| WiFi broadcasts (WLANs) | `/v1/sites/{siteId}/wifi/broadcasts` | GET, POST, GET/PUT/DELETE `/{id}` |
| Firewall zones | `/v1/sites/{siteId}/firewall/zones` | GET, POST, GET/PUT/DELETE `/{id}` |
| Firewall policies | `/v1/sites/{siteId}/firewall/policies` | GET, POST, GET/PUT/DELETE/PATCH `/{id}` |
| Firewall policy order | `/v1/sites/{siteId}/firewall/policies/ordering` | GET, PUT |
| DNS policies | `/v1/sites/{siteId}/dns/policies` | GET, POST, GET/PUT/DELETE `/{id}` |
| ACL rules | `/v1/sites/{siteId}/acl-rules` | GET, POST, GET/PUT/DELETE `/{id}` |
| ACL rule order | `/v1/sites/{siteId}/acl-rules/ordering` | GET, PUT |
| Traffic-matching lists | `/v1/sites/{siteId}/traffic-matching-lists` | GET, POST, GET/PUT/DELETE `/{id}` |

> The zone-based firewall (`firewall/zones` + `firewall/policies`) is the modern model on Network 9+. Older rule/group firewalls live only in the private API (`rest/firewallrule`, `rest/firewallgroup`).

## WAN, VPN, switching, RADIUS, tags

Read-oriented in current spec:

| Resource | Path |
|----------|------|
| WAN interfaces | `GET /v1/sites/{siteId}/wans` |
| Site-to-site VPN tunnels | `GET /v1/sites/{siteId}/vpn/site-to-site-tunnels` |
| VPN servers | `GET /v1/sites/{siteId}/vpn/servers` |
| Switch stacks | `GET /v1/sites/{siteId}/switching/switch-stacks` (+ `/{id}`) |
| MC-LAG domains | `GET /v1/sites/{siteId}/switching/mc-lag-domains` (+ `/{id}`) |
| LAGs | `GET /v1/sites/{siteId}/switching/lags` (+ `/{id}`) |
| RADIUS profiles | `GET /v1/sites/{siteId}/radius/profiles` |
| Device tags | `GET /v1/sites/{siteId}/device-tags` |

## Examples

```bash
KEY="paste-key"; HOST="192.168.1.1"
NB="https://$HOST/proxy/network/integration/v1"
H=(-H "X-API-KEY: $KEY" -H "Accept: application/json")

SITE=$(curl -ksS "${H[@]}" "$NB/sites" | jq -r '.data[0].id')

# Restart a device
curl -ksS "${H[@]}" -H "Content-Type: application/json" -X POST \
  "$NB/sites/$SITE/devices/$DEVICE/actions" -d '{"action":"RESTART"}'

# Authorize a guest client for 2 hours
curl -ksS "${H[@]}" -H "Content-Type: application/json" -X POST \
  "$NB/sites/$SITE/clients/$CLIENT/actions" \
  -d '{"action":"AUTHORIZE_GUEST_ACCESS","timeLimitMinutes":120}'

# Page through all clients
off=0
while :; do
  page=$(curl -ksS "${H[@]}" "$NB/sites/$SITE/clients?offset=$off&limit=200")
  echo "$page" | jq -c '.data[]'
  tot=$(echo "$page" | jq .totalCount); off=$((off+200)); [ "$off" -ge "$tot" ] && break
done

# Bulk-delete expired vouchers (filter required)
curl -ksS "${H[@]}" -X DELETE --get "$NB/sites/$SITE/hotspot/vouchers" \
  --data-urlencode "filter=name.like('Lobby*')"
```
