# App flow

A product whose users generate media. fal runs on the user's traffic and the user's bill, so the contract with fal is the architecture — settle it before any UI exists.

## 1. Scope

Intake already asked which media, whether results persist, and whether generation sits behind login or a quota. Close the remaining gaps in one batch: what a user hands in (prompt, image, both), what they get back, and what happens to it afterwards (view once, saved gallery, share link, download).

## 2. Model contract

Read [`fal-runtime.md`](fal-runtime.md).

Pick the models by role, then run `find` on each one to pin its actual input schema — parameter names and enums are the part that drifts, and guessing them costs a debugging cycle per model. Write the result as the server-side `as const` registry: id, the caps you enforce, and the fixed inputs. That registry is the single source of truth for what the app can run.

Validate the request body against a schema (ArkType, or zod where the perf cost is irrelevant) and let the types be inferred from it. No `any` on the boundary where user text meets a metered API.

## 3. Server route

Stand up the route that holds `FAL_KEY`: validate, authenticate, check quota, submit to the queue, return the request id. Wire the env var for local dev and document the one the user sets in their host's dashboard.

The stock `@fal-ai/server-proxy` route is the prototyping path only — anything users can reach gets the owned route with the allowlist, for the reason spelled out in `fal-runtime.md`.

## 4. Generation UX

Build the queued / running / failed / rejected / cancel / retry states first, against a real slow model rather than a mock. They are most of what the app feels like, and retrofitting them onto a happy-path UI means rewriting the screen.

Then the result surface: how the media is displayed at its real aspect ratio, what the user can do with it, and where it goes. Copy results out of fal's temporary URLs the moment an app keeps them.

## 5. Shell

Load the `frontend-design` skill and give the app a real visual identity — palette tokens, type scale, a layout that fits the generation loop (a prompt bar, a result canvas, a history rail is the usual shape). Its own brand art, icons, and empty-state illustration are generated at build time per [`generation.md`](generation.md), landed into `public/generated/`, and manifested like a site's kit.

## 6. Cover and metadata

[`cover-and-meta.md`](cover-and-meta.md). Same rule as a site: it ships with the build, not after it.

## 7. Gate

Every line is a build failure until it passes:

- `FAL_KEY` appears nowhere in client code, in a `VITE_`/`NEXT_PUBLIC_` var, or in the built bundle — grep the build output to prove it.
- The model registry is server-side, and a request naming a model outside it is rejected.
- Quota and rate limiting are enforced before submit, not after.
- A failed generation, a rejected prompt, and a cancel each produce a sensible screen.
- Persisted results point at the app's own storage, not `fal.media`.
- Build succeeds; meta fields filled; cover image exists.

Close with the run command, the local URL, the env vars the user must set, and one line on what was built.
