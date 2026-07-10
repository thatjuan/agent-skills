# Deployment

How OpenWA gets onto a host, runs in Docker, fronts itself with Traefik, and exposes Kubernetes-shaped probes.

## Contents

- [Docker image](#docker-image)
- [Compose stacks](#compose-stacks)
- [Profiles](#profiles)
- [Volumes & state](#volumes--state)
- [Traefik](#traefik)
- [Health probes](#health-probes)
- [Kubernetes notes](#kubernetes-notes)
- [Local non-Docker development](#local-non-docker-development)

## Docker image

`Dockerfile` is a two-stage build on `node:22-slim`:

**Stage 1 — builder** (`Dockerfile:5-26`)
- Installs `python3`, `make`, `g++` for native modules.
- Runs `npm ci && npm run build` → emits `/app/dist`.

**Stage 2 — runtime** (`Dockerfile:29-90`)
- Installs Chromium and its libs (`chromium`, `libnss3`, `libatk-bridge2.0-0`, fonts, …).
- Sets:
  ```
  PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium
  PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
  ```
- Entrypoint: `dumb-init` (proper PID-1 signal handling).
- Exposes port `2785`.
- Built-in healthcheck: `node -e "require('http').get('http://localhost:2785/api/health', r => process.exit(r.statusCode === 200 ? 0 : 1))"` — interval 30 s, timeout 10 s.
- Non-root user is **commented out** because `modules/docker` needs to read `/var/run/docker.sock`.

## Compose stacks

Two compose files. Both default the API to `127.0.0.1:2785` (loopback) so Traefik or a host firewall fronts it.

### `docker-compose.dev.yml` — quick start

Single `openwa` + `dashboard` service. SQLite for both DBs, local storage, no Redis, no profiles.

```bash
docker compose -f docker-compose.dev.yml up -d
open http://localhost:2886    # dashboard
open http://localhost:2785/api/docs  # Swagger
```

### `docker-compose.yml` — production

Service map (`docker-compose.yml`):

| Service | Always on? | Notes |
|---|---|---|
| `openwa-api` | yes | Builds from `./Dockerfile`. Mounts `openwa-data:/app/data` and `/var/run/docker.sock:ro`. |
| `dashboard` | profile `with-dashboard` | Builds from `./dashboard/Dockerfile.traefik`. Exposes `2886`. |
| `traefik` | profile `with-proxy` | `traefik:v3.0`. Dashboard on `:8080`, entrypoint `web` on `:80`. |
| `postgres` | profile `postgres` | `postgres:16-alpine`, healthcheck `pg_isready`. |
| `redis` | profile `redis` | `redis:7-alpine`, healthcheck `redis-cli ping`. |
| `minio` | profile `minio` | `minio/minio`, ports `9000` (S3) + `9001` (console). |

Most production envs run with at least `postgres,redis`. The `full` profile turns everything on.

## Profiles

Compose profiles are how OpenWA opts services in. Combine with `--profile`:

```bash
# Built-in Postgres + Redis only
docker compose --profile postgres --profile redis up -d

# Everything (Postgres, Redis, MinIO, dashboard, Traefik)
docker compose --profile full up -d
```

When using **external** Postgres/Redis/S3, leave their profiles off and point `DATABASE_HOST` / `REDIS_HOST` / `STORAGE_S3_ENDPOINT` at the external endpoints.

## Volumes & state

| Volume | Mount | Holds |
|---|---|---|
| `openwa-data` | `/app/data` inside `openwa-api` | SQLite DBs, `.env.generated`, session data (`/app/data/sessions/<id>/` — Puppeteer profile + WhatsApp web auth) |
| `postgres-data` | `/var/lib/postgresql/data` | Postgres files (profile `postgres`) |
| `redis-data` | `/data` | Redis AOF (profile `redis`) |
| `minio-data` | `/data` | S3 bucket files (profile `minio`) |
| `traefik-acme` | `/letsencrypt` | ACME storage (profile `with-proxy`) |

**Back up `openwa-data` always.** Losing `sessions/` means every WhatsApp account has to re-scan its QR. Losing the SQLite `main` DB means losing all API keys.

The `docker.sock:ro` mount is intentional — `modules/docker` introspects the running stack from inside the API container. If you run on a host without Docker (bare metal Node), set `DOCKER_ENABLED=false`.

## Traefik

`traefik/traefik.yml` (static):

```yaml
api:
  dashboard: true
  insecure: true            # only safe behind a private network
log:
  level: INFO
entryPoints:
  web:
    address: ':80'
providers:
  file:
    filename: /etc/traefik/dynamic.yml
    watch: true
```

`traefik/dynamic.yml` defines routers/services pointing at `openwa-api:2785` and `dashboard:2886`. For TLS in production, switch `api.insecure: false`, add a `websecure` entrypoint, and configure ACME with `TRAEFIK_ACME_EMAIL` + `TRAEFIK_ACME_STORAGE`.

## Health probes

`src/modules/health/health.controller.ts` exposes three public endpoints:

| Path | Purpose | Shape |
|---|---|---|
| `GET /api/health` | Basic liveness | `{status, uptime, timestamp, version}` |
| `GET /api/health/live` | K8s `livenessProbe` — process is running | `{status:'ok'}` |
| `GET /api/health/ready` | K8s `readinessProbe` — DB reachable, ready to serve | `{status, checks}` |

Kubernetes manifest skeleton:

```yaml
livenessProbe:
  httpGet: { path: /api/health/live, port: 2785 }
  initialDelaySeconds: 30
  periodSeconds: 10
readinessProbe:
  httpGet: { path: /api/health/ready, port: 2785 }
  initialDelaySeconds: 15
  periodSeconds: 5
```

## Kubernetes notes

OpenWA is not pure stateless. Two constraints:

1. **Session affinity.** The in-memory `engines: Map<sessionId, IWhatsAppEngine>` lives in a single process. A given session must be served by the same pod that started it. Solutions: (a) one pod handles all sessions (vertical scale) or (b) shard sessions across pods with an external router and pin each session to a pod (custom). There is no built-in cluster coordination.
2. **`openwa-data` persistence.** The Puppeteer profile dir under `/app/data/sessions/<id>/` must persist across pod restarts, or each restart will require a fresh QR scan. Use a PersistentVolumeClaim with `ReadWriteOnce`.

Horizontal scaling depth: `docs/13-horizontal-scaling.md` in the OpenWA repo.

## Local non-Docker development

```bash
git clone <openwa-repo>
cd OpenWA
npm install
cp .env.example .env       # or skip; first boot writes data/.env.generated
npm run dev                # API + dashboard concurrently
```

`npm run dev` boots the NestJS API on `2785` and Vite dev server on `2886`. Chromium needs to be installed locally — either:

```bash
npx puppeteer browsers install chromium
# or set PUPPETEER_EXECUTABLE_PATH to your existing Chrome/Chromium
```

Hot-reload is enabled (`ts-node-dev`); session data lands in `./data/sessions/`.
