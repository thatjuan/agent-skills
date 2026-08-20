# fal at runtime

Only the app flow reads this. A site that reaches this file took the wrong branch.

## The shape

```
browser ──▶ your server route ──▶ fal queue ──▶ result
              (holds FAL_KEY,
               auth + allowlist + quota)
```

The browser never holds `FAL_KEY` and never talks to fal directly. Everything else about the app is a consequence of that one line.

## Client

```bash
pnpm add @fal-ai/client        # the current package; @fal-ai/serverless-client is the retired name
```

```ts
import { fal } from '@fal-ai/client'

fal.config({ proxyUrl: '/api/fal' })   // browser: no credentials, calls go through your route

const { data, requestId } = await fal.subscribe('fal-ai/flux/dev', {
  input: { prompt, image_size: 'landscape_16_9' },
  logs: true,
  onQueueUpdate: (update) => setStatus(update),
})
```

On the server the same import reads `FAL_KEY` from the environment automatically — no `fal.config` call, and no `credentials` literal in source.

## The route

`@fal-ai/server-proxy` ships adapters that stand up the route for you:

```ts
// Next App Router — app/api/fal/proxy/route.ts
import { route } from '@fal-ai/server-proxy/nextjs'
export const { GET, POST } = route
```

Adapters exist for express, remix, svelte, hono and others; check the package's exports for the framework in play, and set `proxyUrl` on the client to whatever path you mounted.

**The stock proxy forwards whatever model id the browser sends.** That is fine while prototyping and a billing hole in production: anyone who finds the endpoint can run `veo3` on the user's key. Ship a route you own instead, which is barely more code:

```ts
// server route
import { fal } from '@fal-ai/client'
import { type } from 'arktype'

const MODELS = {
  portrait: { id: 'fal-ai/flux/dev', max: { num_images: 2 } },
  clip:     { id: 'fal-ai/kling-video/v2.5-turbo/pro', max: { duration: 5 } },
} as const

const Body = type({ model: "'portrait' | 'clip'", prompt: 'string <= 600' })

export async function POST(req: Request) {
  const body = Body(await req.json())
  if (body instanceof type.errors) return Response.json({ error: body.summary }, { status: 400 })

  const user = await requireUser(req)
  if (!(await withinQuota(user))) return Response.json({ error: 'quota' }, { status: 429 })

  const model = MODELS[body.model]
  const { request_id } = await fal.queue.submit(model.id, {
    input: { prompt: body.prompt, ...model.max },
    webhookUrl: `${process.env.PUBLIC_URL}/api/fal/webhook`,
  })
  return Response.json({ requestId: request_id })
}
```

The `as const` registry is the point: model ids stay in one server-side place, the union of keys is what the client is allowed to ask for, and the type follows the registry when a model changes.

## Queue

Everything generative is slow enough to queue. Pick by expected duration:

- **Under ~60s and the user is watching** — `fal.subscribe`, which submits and streams queue updates until the result arrives. Simplest path, and the one most image apps want.
- **Longer, or the user may close the tab** — `fal.queue.submit` with a `webhookUrl`, persist `request_id` against the user, and let the webhook write the result. Video belongs here.
- **Polling** — `fal.queue.status(model, { requestId, logs: true })` then `fal.queue.result(model, { requestId })`, when a webhook has nowhere to land (local dev, no public URL).

Webhook deliveries carry the request id, a status, and the payload, and are signed — verify the signature before trusting the body, and treat delivery as at-least-once by keying on `request_id`.

## Inputs from the user

```ts
const url = await fal.storage.upload(file)   // browser File → fal URL, then pass it as image_url
```

Validate type and size before uploading, and remember an uploaded URL is as public as an unguessable link gets.

## Results expire

fal result URLs are temporary. An app that shows a result once and forgets it can use them directly. An app with a history, a gallery, a share link, or a download button copies the bytes into its own storage (R2, S3, Supabase) the moment the result lands, stores that key, and never persists a `fal.media` URL in the database.

## What the UI has to handle

The generation states are the app, so build them before the pretty parts:

- **Queued** — position and elapsed time; a spinner with no numbers reads as broken at 40 seconds.
- **Running** — stream `logs` when the model emits them.
- **Failed** — model errors, validation errors, and timeouts all surface differently; show what went wrong and keep the prompt so the user does not retype it.
- **Rejected** — safety filters reject prompts and inputs. Say so plainly rather than reporting a generic failure.
- **Cancel** — long jobs need an out; `fal.queue.cancel` on the server, and stop billing.
- **Retry** — reuse the same seed to iterate on a prompt, a new seed to reroll the same prompt. Expose both.

## Cost control

The user pays for every generation their visitors trigger, so the guardrails are product requirements:

- Allowlist models server-side, and cap resolution, duration, and `num_images` per model.
- Per-user quota with a stated limit, enforced before submit.
- `estimate_cost` on video-class models, surfaced before the user commits.
- Rate limit by user and by IP; an unauthenticated generate button is a public faucet on a metered account.
