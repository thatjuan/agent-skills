# Protect — Private (Reverse-Engineered) API

The internal API the Protect web UI uses, at `https://<host>/proxy/protect/api/...`, plus the realtime updates WebSocket. **Unsupported and version-dependent** — field names and routes shift across Protect releases; a few actions (PTZ actuation, talkback, mic-disable) have migrated to the official v1 API in current libraries. Paths corroborated from hjdhjd/unifi-protect and uilibs/uiprotect. Login/CSRF: `auth-and-conventions.md`.

## Contents

- [Conventions](#conventions)
- [Bootstrap & NVR](#bootstrap--nvr)
- [Cameras](#cameras)
- [Video export](#video-export)
- [Lights, sensors, chimes, viewers, locks](#lights-sensors-chimes-viewers-locks)
- [Liveviews & users](#liveviews--users)
- [Events & smart detection](#events--smart-detection)
- [Realtime WebSocket protocol](#realtime-websocket-protocol)
- [Other sockets](#other-sockets)
- [Gotchas](#gotchas)
- [Examples](#examples)

## Conventions

- Paths are **relative to `/proxy/protect/api`** unless marked `[v1]` (official `/proxy/protect/integration/v1`, `X-API-KEY`) or shown at the UniFi-OS root (`/api/...`).
- Cookie `TOKEN` on every request; `X-CSRF-Token` header on every mutation; roll forward `X-Updated-CSRF-Token`.
- A **local** Protect/admin account is required; cloud SSO and MFA-enabled accounts break scripted login.

## Bootstrap & NVR

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/bootstrap` | **Entire system state in one call** + `lastUpdateId` (seeds the WebSocket) |
| GET | `/nvr` | NVR/console object only |
| PATCH | `/nvr` | NVR settings (`recordingRetentionDurationMs`, `name`, …) |
| POST | `/nvr/reboot` | Reboot the console |

`/bootstrap` top-level keys: `nvr`, `cameras[]`, `lights[]`, `sensors[]`, `chimes[]`, `viewers[]`, `liveviews[]`, `users[]`, `groups[]`, `bridges[]`, `doorlocks[]`, `accessKey`, `authUserId`, **`lastUpdateId`**.

Key `camera` fields: `id`, `mac`, `host`, `name`, `type` (model), `state` (`CONNECTED`/`DISCONNECTED`), `isAdopted`, `isRecording`, `isMotionDetected`, `lastMotion`, `lastRing`, `upSince`, `channels[]` (`id,name,width,height,fps,bitrate,rtspAlias,isRtspEnabled`), `featureFlags` (`hasPackageCamera,hasLcdScreen,hasSpeaker,hasLedStatus,smartDetectTypes[],isPtz,canOpticalZoom`), `ledSettings.isEnabled`, `osdSettings`, `recordingSettings` (`mode:always|never|detections|motion`, `prePaddingSecs`, `postPaddingSecs`, `retentionDurationMs`), `smartDetectSettings.objectTypes[]`, `smartDetectZones[]`, `motionZones[]`, `speakerSettings`, `talkbackSettings`, `ispSettings`.

## Cameras

| Method | Path | Purpose | Params/body |
|--------|------|---------|-------------|
| GET | `/cameras/{id}` | Single camera | — |
| PATCH | `/cameras/{id}` | Update settings | `name`, `recordingSettings`, `smartDetectSettings.objectTypes`, `ledSettings.isEnabled`, `osdSettings`, `motionZones`, `smartDetectZones`, `micVolume`, `chimeDuration`, `speakerSettings`, `lcdMessage` |
| GET | `/cameras/{id}/snapshot` | Live JPEG | `?ts=<epoch_ms>&force=true&w=<px>&h=<px>` |
| GET | `/cameras/{id}/recording-snapshot` | Historical JPEG | `?ts=<epoch_ms>&w=&h=` |
| GET | `/cameras/{id}/package-snapshot` | Package-cam JPEG | `?ts=<epoch_ms>&force=true` (needs `hasPackageCamera`) |
| POST | `/cameras/{id}/reboot` | Reboot camera | — |
| GET | `/cameras/{id}/ptz/preset` | List PTZ presets | — |
| GET | `/cameras/{id}/ptz/patrol` | List PTZ patrols | — |
| POST | `/v1/cameras/{id}/ptz/goto/{slot}` `[v1]` | Move to preset | actuation via official API |
| POST | `/v1/cameras/{id}/ptz/patrol/start/{slot}` `[v1]` | Start patrol | |
| POST | `/v1/cameras/{id}/talkback-session` `[v1]` | Two-way audio session | returns stream URL + AAC/ADTS config |
| POST | `/v1/cameras/{id}/disable-mic-permanently` `[v1]` | Disable mic (irreversible) | |

`recordingSettings.mode`: `always` (continuous), `detections` (smart-detect), `motion`, `never`.

## Video export

`GET /video/export` streams a recorded MP4:

| Param | Meaning |
|-------|---------|
| `camera` | camera id |
| `start`, `end` | epoch **milliseconds** of the clip window |
| `channel` | stream index (`0`=high, higher=lower quality) |
| `lens=2` | use **instead of** `channel` for the package/3rd lens |
| `type=timelapse&fps=<n>` | timelapse export — UI presets: 60×→`fps=4`, 120×→`fps=8`, 300×→`fps=20`, 600×→`fps=40` |

Long ranges stream large bodies and can time out — chunk the window and write with `-o`.

## Lights, sensors, chimes, viewers, locks

| Method | Path | Purpose |
|--------|------|---------|
| GET/PATCH | `/lights/{id}` | `lightModeSettings`, `lightDeviceSettings`, `isLightForceOn`, `ledLevel` |
| GET/PATCH | `/sensors/{id}` | `motionSettings`, `temperatureSettings`, `humiditySettings`, `lightSettings`, `alarmSettings`, `mountType` |
| POST | `/sensors/{id}/clear-tamper-flag` | Clear tamper state |
| GET/PATCH | `/chimes/{id}` | `ringSettings`, `cameraIds`, `volume` |
| POST | `/chimes/{id}/play-speaker` | Trigger chime ringtone |
| POST | `/chimes/{id}/play-buzzer` | Buzzer |
| GET/PATCH | `/viewers/{id}` | Assigned `liveview` |
| POST | `/doorlocks/{id}/open` · `/close` | Lock control |
| PATCH/POST/DELETE | `/{model}s/{id}` · `/{model}s/{id}/reboot` | Generic update / reboot / delete; `{model}` ∈ camera, light, sensor, chime, viewer, bridge, doorlock |

## Liveviews & users

| Method | Path | Purpose |
|--------|------|---------|
| GET/POST | `/liveviews` | List / create (`name,isDefault,isGlobal,owner,layout,slots[]`; each slot = `cameras[]` + cycle settings) |
| GET/PATCH/DELETE | `/liveviews/{id}` | Get / update / delete |
| GET | `/api/users/self` | Current user + permissions (UniFi-OS root) |
| GET | `/users` | All Protect users (also in `/bootstrap`) |

## Events & smart detection

| Method | Path | Params | Notes |
|--------|------|--------|-------|
| GET | `/events` | `start=<ms>&end=<ms>&types=<csv>&smartDetectTypes=<csv>&orderDirection=ASC\|DESC&withoutDescriptions=&allCameras=&limit=&offset=` | If `start` is set, also send `end` or `limit` (else `400`); default ≈ recent window |
| GET | `/events/{id}` | — | Fields: `id,type,start,end,camera,score,smartDetectTypes[],smartDetectEvents[],thumbnail,heatmap,metadata` |
| GET | `/events/{id}/thumbnail` | `?w=&h=` | JPEG; generated **only after the event ends** — retry with backoff |
| GET | `/events/{id}/animated-thumbnail` | `?w=&h=&speedup=<n>` | GIF, post-event |
| GET | `/events/{id}/heatmap` | — | PNG; heatmap id often `e-{eventId}` (strip `e-`); post-event |
| GET | `/events/{id}/smartDetectTrack` | — | Detection track/path |

Event `type` values: `motion`, `ring`, `smartDetectZone`, `smartDetectLine`, `disconnect`, `nvrPowerCycle` (+ version-dependent others). Filter by camera client-side (`allCameras=true` + local filter) — the server `cameras=` param is unreliable across builds.

Smart-detect object types (`smartDetectTypes` / `smartDetectSettings.objectTypes`): `person`, `vehicle`, `animal`, `package`, `licensePlate`, `face` (gated by `featureFlags.smartDetectTypes`). Configure detection/motion zones via `PATCH /cameras/{id}` (`smartDetectZones`, `motionZones`, `smartDetectSettings`).

## Realtime WebSocket protocol

```
wss://<host>/proxy/protect/ws/updates?lastUpdateId=<uuid>
```

Seed `lastUpdateId` from the `/bootstrap` you just fetched; send the `TOKEN` cookie on the upgrade. The stream delivers device health/stat changes and event add/updates as **binary** messages.

**Each logical update = two frames** (action then data), and **each frame has its own 8-byte header**: one message on the wire = `[header(8)][action payload][header(8)][data payload]`.

**8-byte header (big-endian):**

| Offset | Size | Field | Values |
|--------|------|-------|--------|
| 0 | 1 | Packet type | `1`=action frame · `2`=data frame |
| 1 | 1 | Payload format | `1`=JSON · `2`=UTF-8 string · `3`=raw buffer |
| 2 | 1 | Deflated | `0`=plain · `1`=zlib-deflated (inflate first) |
| 3 | 1 | Reserved | `0` |
| 4–7 | 4 | Payload size | uint32 BE — bytes of payload following this header |

- **Action frame** (JSON): `{"action":"add"|"update","newUpdateId":"<uuid>","modelKey":"<model>","id":"<deviceId>"}`.
- **Data frame**: the **changed fields only** (delta), JSON matching that model's bootstrap shape (may be zlib-deflated — check byte 2).
- **`modelKey` values:** `camera`, `light`, `sensor`, `chime`, `viewer`, `liveview`, `bridge`, `group`, `user`, `nvr`, `event` (`event` add = a new detection/ring/motion).

**Decode sketch (Python-ish):**

```python
buf = ws_recv()                                   # one binary message
aT,aF,aD,_,aSz = struct.unpack('>BBBBI', buf[0:8])
a = buf[8:8+aSz]; a = zlib.decompress(a) if aD else a
action = json.loads(a)                            # {action,newUpdateId,modelKey,id}
o = 8+aSz
dT,dF,dD,_,dSz = struct.unpack('>BBBBI', buf[o:o+8])
d = buf[o+8:o+8+dSz]; d = zlib.decompress(d) if dD else d
delta = json.loads(d)                             # changed fields only
# deep-merge delta onto bootstrap[modelKey+'s'][action['id']]; for action=='add' insert new.
lastUpdateId = action['newUpdateId']              # advance cursor for reconnect
```

Maintain state by deep-merging each delta onto the matching bootstrap object. On reconnect, resume with the latest `lastUpdateId`; if the server rejects it as stale, re-fetch `/bootstrap` and reconnect with the fresh id.

## Other sockets

| WS URL | Purpose |
|--------|---------|
| `wss://<host>/proxy/protect/api/ws/livestream?...` | Per-camera H.264 fMP4 live (URL from `GET …/ws/livestream`) ⚠️ params vary |
| `wss://<host>/proxy/protect/api/ws/talkback?camera={id}` | Two-way AAC/ADTS audio out (current libs create the session via `[v1] talkback-session`) |
| `…/proxy/protect/integration/v1/subscribe/{devices,events}` `[v1]` | Official JSON event/device streams (API-key) — see `protect-integration-api.md` |

## Gotchas

| Pattern | Risk |
|---------|------|
| Polling `/bootstrap` on a timer | Heavy full-state payload — fetch once, then track via `/ws/updates` deltas; re-bootstrap only on WS resync |
| Cloud-SSO / MFA login | Scripted `/api/auth/login` fails — use a local non-MFA admin |
| Mutating without `X-CSRF-Token` (or stale token) | `401`; roll forward `X-Updated-CSRF-Token` |
| Fetching a thumbnail/heatmap mid-event | `404` until the event ends — retry with backoff |
| `/events?start=` without `end`/`limit` | `400` |
| Long `/video/export` range | Times out — chunk the window, stream to file |
| Assuming a field name across versions | `recordingSettings`, `smartDetectSettings`, PTZ/talkback routes drift — validate against the console's Protect version |

## Examples

```bash
# (after uni_login; CSRF + /tmp/uni.jar set)
PP="https://$HOST/proxy/protect/api"; CURL=(curl -ksS -b /tmp/uni.jar)

# Cameras + recording mode from one bootstrap
"${CURL[@]}" "$PP/bootstrap" | jq -r '.cameras[] | "\(.name)\t\(.state)\t\(.recordingSettings.mode)"'

# Set a camera to smart-detect recording for person+vehicle, LED off
CAM=$("${CURL[@]}" "$PP/bootstrap" | jq -r '.cameras[0].id')
"${CURL[@]}" -H "x-csrf-token: $CSRF" -H "Content-Type: application/json" -X PATCH \
  "$PP/cameras/$CAM" -d '{"recordingSettings":{"mode":"detections"},
    "smartDetectSettings":{"objectTypes":["person","vehicle"]},"ledSettings":{"isEnabled":false}}'

# Export the last 5 minutes of high-quality video
NOW=$(($(date +%s)*1000)); AGO=$((NOW-300000))
"${CURL[@]}" "$PP/video/export?camera=$CAM&start=$AGO&end=$NOW&channel=0" -o clip.mp4

# List person smart-detections in the last 24h
END=$(($(date +%s)*1000)); START=$((END-86400000))
"${CURL[@]}" "$PP/events?start=$START&end=$END&types=smartDetectZone&smartDetectTypes=person" \
  | jq -r '.[] | "\(.start)\t\(.camera)\t\(.smartDetectTypes|join(\",\"))"'
```
