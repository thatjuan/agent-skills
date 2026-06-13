# Protect — Official Integration API (v1)

Stable, API-key, stateless REST + WebSocket at `https://<host>/proxy/protect/integration/v1`. GA since Protect 5.3 (min 5.3.38); catalog reflects spec 7.1.46. Newer device types gate on Protect version — call `GET /v1/meta/info` for `applicationVersion`. Auth/TLS: `auth-and-conventions.md`.

## Contents

- [Conventions](#conventions)
- [Console / NVR / users](#console--nvr--users)
- [Cameras](#cameras)
- [Camera PATCH fields](#camera-patch-fields)
- [PTZ](#ptz)
- [Lights, sensors, chimes](#lights-sensors-chimes)
- [Viewers & live views](#viewers--live-views)
- [Sirens & speakers](#sirens--speakers)
- [Alarm hardware](#alarm-hardware)
- [Arm profiles](#arm-profiles)
- [Files / assets](#files--assets)
- [WebSocket subscriptions](#websocket-subscriptions)
- [Alarm Manager webhook](#alarm-manager-webhook)
- [Examples](#examples)

## Conventions

- Header `X-API-KEY`; JSON in/out; snapshots return `image/jpeg`; uploads are `multipart/form-data`.
- Lists return arrays directly (no envelope). Mutations are `PATCH` on the resource.
- For things the official API omits — `/bootstrap`, recorded-video export, event thumbnails, historical snapshots, the binary delta socket — see `protect-private-api.md`.

## Console / NVR / users

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/v1/meta/info` | App version `{applicationVersion}` |
| GET | `/v1/nvrs` | NVR/console object |
| GET | `/v1/users` · `/v1/users/{id}` | Protect users |
| GET | `/v1/ulp-users` · `/v1/ulp-users/{id}` | UniFi Identity (ULP) users |

## Cameras

| Method | Path | Purpose | Params / body |
|--------|------|---------|---------------|
| GET | `/v1/cameras` | All cameras | — |
| GET | `/v1/cameras/{id}` | Camera detail | — |
| PATCH | `/v1/cameras/{id}` | Update settings | see [PATCH fields](#camera-patch-fields) |
| GET | `/v1/cameras/{id}/snapshot` | Live JPEG | `?channel=main\|package&highQuality=true\|false`; `503` if offline |
| GET | `/v1/cameras/{id}/rtsps-stream` | Get RTSPS URLs | returns `{high,medium,low,package}` (`rtsps://…:7441/…?enableSrtp` or null) |
| POST | `/v1/cameras/{id}/rtsps-stream` | Enable channel(s) | `{"qualities":["high","medium","low","package"]}` (≥1) |
| DELETE | `/v1/cameras/{id}/rtsps-stream` | Disable channel(s) | `?qualities=high` (array/single) |
| POST | `/v1/cameras/{id}/talkback-session` | Start two-way audio | empty body → `{url,codec,samplingRate,bitsPerSample}`; push audio to `url` |
| POST | `/v1/cameras/{id}/disable-mic-permanently` | Permanently disable mic | irreversible without reset |

Camera object fields include: `id, modelKey, state, name, mac, isMicEnabled, osdSettings, ledSettings, lcdMessage, micVolume, activePatrolSlot, videoMode, hdrType, featureFlags, smartDetectSettings, hasPackageCamera`.

## Camera PATCH fields

```json
{
  "name": "Front Door",
  "osdSettings": { "isNameEnabled": true, "isDateEnabled": true, "isLogoEnabled": false,
                   "isDebugEnabled": false, "overlayLocation": "topLeft" },
  "ledSettings": { "isEnabled": false, "welcomeLed": false, "floodLed": false },
  "micVolume": 80,
  "videoMode": "default",
  "hdrType": "auto",
  "smartDetectSettings": { "objectTypes": ["person","vehicle"], "audioTypes": ["smoke_cmonx"] },
  "lcdMessage": { "type": "LEAVE_PACKAGE_AT_DOOR", "resetAt": null }
}
```

- `overlayLocation`: `topLeft|topMiddle|topRight|bottomLeft|bottomMiddle|bottomRight`
- `videoMode`: `default|highFps|sport|slowShutter|lprReflex|lprNoneReflex`
- `hdrType`: `auto|on|off`
- `lcdMessage.type` (doorbells): `DO_NOT_DISTURB`, `LEAVE_PACKAGE_AT_DOOR`, or custom `{type,text,resetAt}`; `resetAt` = epoch ms or `null` (forever).

## PTZ

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/v1/cameras/{id}/ptz/goto/{slot}` | Move to preset (`-1`=home, `≥0`=preset slot) |
| POST | `/v1/cameras/{id}/ptz/patrol/start/{slot}` | Start patrol (slot `0`–`4`) |
| POST | `/v1/cameras/{id}/ptz/patrol/stop` | Stop active patrol |

Presets are configured in the Protect app first. There is **no continuous/relative move** in v1 — control is preset/patrol-based.

## Lights, sensors, chimes

| Method | Path | PATCH body highlights |
|--------|------|------------------------|
| GET/PATCH | `/v1/lights/{id}` | `name`, `isLightForceEnabled`, `lightModeSettings:{mode,enableAt}`, `lightDeviceSettings:{isIndicatorEnabled,pirDuration,pirSensitivity,ledLevel}` |
| GET/PATCH | `/v1/sensors/{id}` | `name`, `lightSettings`, `humiditySettings`, `temperatureSettings`, `motionSettings`, `alarmSettings` |
| GET/PATCH | `/v1/chimes/{id}` | `name`, `cameraIds:[]`, `ringSettings:[]` |

(`GET /v1/lights`, `/v1/sensors`, `/v1/chimes` list all.)

## Viewers & live views

| Method | Path | Purpose |
|--------|------|---------|
| GET/PATCH | `/v1/viewers/{id}` | Assign a liveview to a viewport (`{name, liveview}`) |
| GET | `/v1/liveviews` · `/v1/liveviews/{id}` | List / detail |
| POST | `/v1/liveviews` | Create `{id,modelKey,name,isDefault,isGlobal,owner,layout,slots[]}` |
| PATCH | `/v1/liveviews/{id}` | Update (same shape) |

## Sirens & speakers

| Method | Path | Purpose | Body |
|--------|------|---------|------|
| GET/PATCH | `/v1/sirens/{id}` | List/detail/update | siren config |
| POST | `/v1/sirens/{id}/play` | Activate | `{duration}` |
| POST | `/v1/sirens/{id}/stop` | Deactivate | — |
| POST | `/v1/sirens/{id}/test-sound` | Test | test params |
| GET/PATCH | `/v1/speakers/{id}` | List/detail/update | speaker config |
| POST | `/v1/speakers/{id}/test-sound` | Test | `{volume}` |

## Alarm hardware

Fobs, relays, bridges, link-stations, alarm-hubs each support `GET` (list + `/{id}`) and `PATCH /{id}`. Output control:

| Method | Path | Body |
|--------|------|------|
| POST | `/v1/relays/{id}/outputs/{outputId}/activate` | `{state:"on"\|"off", pulseDuration}` |
| POST | `/v1/alarm-hubs/{id}/outputs/{outputId}/trigger` | `{enable, delay, duration}` |

## Arm profiles

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/v1/arm-profiles` | List |
| POST | `/v1/arm-profiles` | Create `{name, automations[], schedules[], recordEverything, activationDelay}` |
| PATCH/DELETE | `/v1/arm-profiles/{id}` | Update / delete |
| PATCH | `/v1/arm-profiles/settings` | Set active profile |
| POST | `/v1/arm-profiles/enable` · `/disable` | Arm / disarm |

## Files / assets

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/v1/files/{fileType}` | List assets (`fileType` currently `animations`) |
| POST | `/v1/files/{fileType}` | Upload (`multipart/form-data`; `image/gif|jpeg|png`, `audio/mpeg|mp4|wave|x-caf`) — doorbell LCD images / alarm sounds |

## WebSocket subscriptions

WS-upgrade GETs; connect `wss://` with the `X-API-KEY` header on the handshake (clients that can't set headers fail).

| WS URL | Broadcasts | Message |
|--------|-----------|---------|
| `…/v1/subscribe/devices` | device add/update/remove | `{"type":"add\|update\|remove","item":{...device}}` |
| `…/v1/subscribe/events` | Protect events | `{"type":<event>,"item":{...}}` |

Event `type` values include `motion`, `ring`, `smartDetectZone`, `smartDetectLine`, `smartDetectLoiterZone`, `smartAudioDetect`, `lightMotion`, `nfcCardScanned`, `fingerprintIdentified`, plus the sensor/alarm-hub family (`sensorOpened/Closed/Motion/Alarm/Tamper/WaterLeak/BatteryLow`, `alarmHubEntryOpened/Closed/Smoke/GlassBreak/...`).

> These are **JSON** messages — unlike the private `/ws/updates` socket, which is a binary delta protocol (see `protect-private-api.md`).

## Alarm Manager webhook

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/v1/alarm-manager/webhook/{id}` | Fire a webhook that triggers a configured Alarm Manager automation (`204` on success) |

The outbound side (Alarm Manager calling *your* URL on an event) is configured in the Protect UI, not via this API.

## Examples

```bash
KEY="paste-key"; HOST="192.168.1.1"
PB="https://$HOST/proxy/protect/integration/v1"
H=(-H "X-API-KEY: $KEY")

curl -ksS "${H[@]}" "$PB/meta/info"                                  # version
curl -ksS "${H[@]}" "$PB/cameras" | jq -r '.[] | "\(.id)\t\(.name)"' # camera ids

# Snapshot, rename + LED off, enable RTSPS
curl -ksS "${H[@]}" "$PB/cameras/$CAM/snapshot?highQuality=true" -o cam.jpg
curl -ksS "${H[@]}" -H "Content-Type: application/json" -X PATCH "$PB/cameras/$CAM" \
  -d '{"name":"Front Door","ledSettings":{"isEnabled":false}}'
curl -ksS "${H[@]}" -H "Content-Type: application/json" -X POST "$PB/cameras/$CAM/rtsps-stream" \
  -d '{"qualities":["high","medium"]}'
curl -ksS "${H[@]}" "$PB/cameras/$CAM/rtsps-stream" | jq   # read URLs back

# Point a PTZ camera at preset 0, then patrol
curl -ksS "${H[@]}" -X POST "$PB/cameras/$CAM/ptz/goto/0"
curl -ksS "${H[@]}" -X POST "$PB/cameras/$CAM/ptz/patrol/start/0"
```
