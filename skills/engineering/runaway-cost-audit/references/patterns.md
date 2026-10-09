# Runaway patterns

Each pattern names the bills it caused (from [serverlesshorrors.com](https://serverlesshorrors.com/)), what to look for, the trigger, and the fix. Patterns fall into four families: **loops** the code feeds itself, **outside traffic** someone else sends, **pricing traps** in the billing model, and **missing guardrails** that let any of the others run to the invoice.

Refunds were common but discretionary: several owners paid in full, and one lost the product anyway. Treat every pattern as real money.

## Loops

### L1. Recursive or self-invoking compute

**Bills:** Cloud Run + Firestore, $72k. A scraper POSTed each found URL to a new Cloud Run instance with no exit and no visited set; back links cycled, 1,000 instances did 116 billion Firestore reads in hours. Cloudflare Workers, $36k: the ingest consumer forwarded the caller's `write_mode: "async"` into its own internal call, so every job re-queued itself (3.13B KV writes). Vercel, $3k in six hours on an unlaunched test site: a top-level `await fetch()` of the app's own API sat in a bundle shared by every endpoint, so each invocation fetched the API, which evaluated the same top-level code and fetched again, with no browser open.

**Look for:** server code that fetches its own API over HTTP instead of importing the data layer; top-level `await` or side effects in modules shared by many routes; a function that calls its own URL or a sibling's; a queue consumer or Pub/Sub subscriber that publishes to the queue it consumes; a storage or database trigger that writes to the path or collection it listens on (Lambda on S3 put writing to the same bucket, Firestore `onWrite` updating the same document); request flags passed through to internal calls; crawlers and graph walks without a visited set, depth limit, or budget.

**Trigger:** one input that takes the cyclic path. Growth is often exponential.

**Fix:** a hop counter or depth field that every re-entry increments and checks; dedupe on a visited key; split trigger and output paths; force internal calls to the terminal mode; call the data layer directly instead of the app's own URL; cap max instances and duration (see P4).

### L2. Self-rescheduling timers

**Bills:** Cloudflare Durable Objects, $10.8k, paid in full. In an unused test project, an AI-written patch made `runAlarm` reschedule from a checkpoint-refresh field; once the checkpoint entered its refresh window the alarm looped for 13 days (a claimed 6 trillion reads and writes). Support declined credit because the loop was customer code. Cloudflare, $8.8k: two Durable Objects deep in the stack looped, almost all of it ($8.7k) storage rows read; "we found out by getting the bill."

**Look for:** `setAlarm` inside `alarm()`; `setTimeout`/`setInterval` that re-arms in long-lived workers; scheduled jobs that enqueue more scheduled jobs; two objects or services that call each other on every event.

**Trigger:** the reschedule condition is always true, or an error path reschedules immediately.

**Fix:** reschedule only on a condition that eventually turns false, with a minimum interval and a max-run counter persisted in storage; alarm on invocation rate.

### L3. Retry storms

**Bills:** Vercel, $23k. Bots created tens of thousands of trial signups, each produced Stripe events, and Stripe retried every webhook against a handler with no rate limit that ran to the 60-second timeout, so each retry billed a full minute of compute.

**Look for:** retry loops without backoff or a max attempt count; client code that refetches on error (`useEffect` with an unstable dependency, SWR/React Query with aggressive retry and refetch-on-focus against a failing endpoint); queue consumers that throw on a poison message and get redelivered forever (no dead-letter queue, no `maxRetries`); webhook handlers that do slow work inline, time out, or return 5xx on bad input, inviting the sender to retry; long function timeouts.

**Trigger:** any persistent error on a hot path.

**Fix:** exponential backoff with a cap; dead-letter queues; webhook handlers that verify, enqueue, and return 2xx at once; return 4xx for inputs that will never succeed; short function timeouts; error boundaries that stop refetching.

### L4. Unbounded writes and storage growth

**Bills:** Firebase/GCS, $70k on a $50/month project. A contractor's bug stored about 1 PB in a day; the owner learned from a $61k card decline, spent another $7k the day of the fix, and the credit request was rejected. Cloudflare Workers, $36k: 12 unbatched Durable Object `storage.put()` calls per logical write (4B rows written).

**Look for:** writes inside loops or render paths; per-item writes that could be one batch; uploads without a size limit; storage rules that let any client write anywhere (`allow write: if true`, or any signed-in user to any path); data without TTL or lifecycle rules.

**Trigger:** a bug or a client that writes in a loop, or a user who uploads without limits.

**Fix:** batch writes; enforce size and count limits in code and in storage rules; TTLs and lifecycle policies; alert on storage growth rate.

### L5. Expensive fallbacks on the hot path

**Bills:** Cloudflare Workers, $36k. An auth fallback ran `kv.list()` whenever hashed and prefix lookups missed; legacy keys always missed, so it ran on 95% of requests (574M list ops at $5 per million).

**Look for:** list, scan, or full-table queries in request handlers, especially in fallback, legacy, or "not found" branches; N+1 reads per request; reads of whole collections where a keyed get would do.

**Trigger:** the fallback becomes the common path once real data arrives. In practice it runs on every request.

**Fix:** remove or flag off the fallback; migrate legacy data to the indexed shape; cache negative lookups.

### L6. Event and analytics floods

**Bills:** PostHog, $733 (plus the agent's subscription, $1,273 in all): an AI coding agent added a `capture` on a banner component's mount, which fired 6.6 million events in a week. PostHog, $530: events flooded in from a bug.

**Look for:** `capture`/`track` calls inside render, effects without stable dependencies, scroll or mousemove handlers, loops, or polling; autocapture and session replay on high-traffic pages; logging and tracing at per-request volume to metered sinks.

**Trigger:** a re-render loop or a busy page.

**Fix:** move tracking to discrete user actions; dedupe and sample; set billing limits in the analytics product; keep a chart of event volume by event name to catch one that runs away.

## Outside traffic

### O1. Large static files on metered bandwidth

**Bills:** Netlify, $104.5k in 4 days. A DDoS hammered one 3.44 MB sound file on a ~200-visitors-a-day site (190 TB). Framer: an agency site used 408 GB against a 100 GB plan and had to upgrade to $250/month; removing most images and videos cut usage 90%. Webflow: $1,189 twice against a normal $49/month, a $1,140 bandwidth add-on for a gallery whose ~1 MB images made a short scroll download ~20 MB.

**Look for:** large files (audio, video, PDFs, unoptimized images, downloads, model weights) served from a host that bills egress per GB; no CDN with free or flat egress in front; no rate limiting on asset paths.

**Trigger:** a bot, a scraper, or a hotlinking site requests the file in a loop.

**Fix:** move large media to flat-egress storage (Cloudflare R2, Bunny) or a media host; compress and resize images; turn on the host's bot and DDoS protection; set a bandwidth spend cap.

### O2. Cache bypass and exposed origins

**Bills:** Firebase/GCS, $100k, refunded but the product shut down. Behind Cloudflare, an attacker found an uncached object and hit it 100M+ times, then found the public origin bucket and hit it directly. Billing lagged so far that service continued through failed card charges of $8k, $20k, and $20k. Vercel, $620: a 1.5 KB `sitemap.txt` requested 378,000+ times.

**Look for:** responses without cache headers; cache keys that vary on query strings an attacker controls; origin buckets or functions reachable by their own public URL (`*.appspot.com`, `*.web.app`, `storage.googleapis.com/...`, `*.s3.amazonaws.com`, `*.vercel.app`, `*.workers.dev`); public-read buckets.

**Trigger:** an attacker or a misbehaving crawler targets whatever the CDN does not absorb.

**Fix:** cache headers on every static and cacheable response; ignore unknown query params in the cache key; make the origin private and reachable only through the CDN (signed URLs, origin auth, disabling default `*.workers.dev`/`*.vercel.app` routes where possible); WAF and rate limits on hot paths.

### O3. Per-request compute on popular pages

**Bills:** Vercel, $96k: cara.app grew to 500k users in days on legitimate traffic and function execution reached 242x the included amount; twelve usage alerts went unread because they looked like routine mail. Vercel, $46k: Jmail crossed 450M pageviews, even after cache work.

**Look for:** pages rendered per request that could be static or ISR; middleware matching every route; image optimization on every request with large `remotePatterns`/unbounded sizes; API routes called on every page view; long function durations and high memory settings (waiting on slow upstreams bills GB-hours).

**Trigger:** success. A launch, a viral post, or a crawler multiplies cost per view by millions of views.

**Fix:** static or ISR rendering for public pages; narrow middleware matchers; long-lived cache headers; pre-optimized images; spend caps; know the cost per 1M views.

### O4. Public endpoints with paid side effects

**Bills:** Mailgun, $11k at list price ($1.5k invoiced after Gmail rejected 87%): a spam script registered 11 million accounts in five days from a single IP, each sending a confirmation email, on an app that normally sent 200 a month. Cloudflare sat in front and did not stop it, and the cleanup emptied the database while broken backups were a year old. Vercel, $23k: bot signups created Stripe trials, whose webhooks ran up compute (see L3). Mintlify, $383: a docs AI assistant billed per question.

**Look for:** unauthenticated or cheaply authenticated routes that send email or SMS, call an LLM, create payment objects, start trials, call paid APIs, or enqueue paid work. Signup, invite, password reset, magic link, OTP, contact forms, newsletter forms, chat widgets, search.

**Trigger:** a bot submits the form in a loop. One request costs the attacker nothing and costs you one paid action, sometimes a cascade of them.

**Fix:** CAPTCHA or Turnstile verified server-side; per-IP and per-identity rate limits; create paid objects (Stripe customers, trials) only after verification; provider-side sending limits and daily caps; per-user quotas on LLM features.

### O5. Billed even when denied

**Bills:** AWS S3, $1,300. A private, empty bucket received 100M PUT requests because a popular open-source tool's default config used the same bucket name; S3 billed the 403s, and requests without a region were redirected from us-east-1 at extra cost, over half the bill. CloudFront and WAF cannot shield the S3 API; deleting the bucket was the only stop. AWS stopped billing most unauthorized S3 requests in 2024, but the shape recurs anywhere a resource bills per request before or regardless of auth.

**Look for:** generic or guessable resource names (bucket, queue, function, subdomain); names shipped in public repos or default configs; endpoints that bill per request whether auth passes or fails.

**Trigger:** misconfigured third parties or attackers hit the name.

**Fix:** add a random suffix to resource names; keep names out of public defaults; reject unauthenticated traffic at the CDN or WAF before the metered service.

## Pricing traps

### P1. Paid tier when the owner thinks it is free

**Bills:** AWS, $103: Aurora PostgreSQL (not free tier) enabled for a one-day test instead of RDS PostgreSQL on a micro instance (free tier), left running after the test, with no warning. Firebase + Cloud Run, $72k: linking Cloud Run upgraded the free Spark project to pay-as-you-go Blaze. Webflow: auto-migrated to an enterprise plan on high bandwidth.

**Look for:** IaC or setup docs that pick a service or instance class outside the free tier; projects linked to a billing account; plan auto-upgrades in vendor terms.

**Trigger:** the first deploy, or a usage threshold.

**Fix:** pin free-tier-eligible services and sizes in IaC; separate billing accounts for experiments; read the upgrade terms.

### P2. Pay-per-scan queries

**Bills:** BigQuery, $22.6k from 10–20 queries on a public dataset with no quota.

**Look for:** BigQuery, Athena, Snowflake, or similar scan-priced engines; `SELECT *`; `LIMIT` used to make a query "small" (it does not reduce bytes scanned); queries over unpartitioned tables; user-controlled queries; no `maximumBytesBilled`.

**Trigger:** one query over a petabyte-scale table.

**Fix:** `maximumBytesBilled` on every job; custom per-day and per-user quotas; dry runs before running; select only needed columns; partition and cluster.

### P3. Usage-billed features that stay on

**Bills:** Mintlify, $383 on top of a $150 plan: the AI assistant kept billing after the owner asked for it to be disabled. Cloudflare Images, $400/month instead of $110: each capacity upgrade billed the new tier in full while the credit for the old one arrived a cycle later.

**Look for:** third-party features with per-use billing (AI assistants, search, image transforms, translation, session replay) enabled by default or impossible to turn off; prepaid capacity tiers.

**Trigger:** normal usage of a feature nobody budgeted for.

**Fix:** list every usage-billed feature and its owner; disable what you do not need and verify it in the next invoice; prefer plans with hard caps.

### P4. Production defaults on test deploys

**Bills:** Cloud Run, $72k. Default max instances (1,000) and concurrency (80) turned a test into ~9M requests per minute of capacity. Max instances of 2 would have cost about $144. Vercel's $23k webhook bill was multiplied by a 60-second default function timeout.

**Look for:** missing `max_instances`/`maxScale`, `reservedConcurrentExecutions`, or concurrency limits in function and container config; autoscaling with no upper bound; function timeouts (`maxDuration`, `timeoutSeconds`) left at or raised to the maximum.

**Trigger:** any loop or traffic spike scales to the platform's default ceiling.

**Fix:** set max instances, concurrency, and timeouts to what the workload needs, lowest on non-production.

### P5. Lingering resources

**Bills:** Cloud Run, $72k: old service revisions kept running and scaling after logs went quiet. Cloudflare, $10.8k: the looping alarm lived in an unused test project. AWS, $4.2k: a service tried once and "paused, not used at all" kept billing. AWS, $103: test databases left on after the test.

**Look for:** preview and test deployments, old revisions, unused projects, functions, cron jobs, and buckets still attached to a billing account; scheduled jobs nobody owns.

**Trigger:** a forgotten resource meets a loop or an attacker.

**Fix:** delete what you are done with (paused or stopped is not deleted); auto-expire preview deploys; one owner per project.

## Missing guardrails

### G1. No hard spend cap

**Bills:** nearly all of them. Cloudflare Workers has no hard spending cap. AWS and GCP budgets alert but do not stop spend. Billing data lags by up to a day (Firebase's dashboard lagged 24+ hours during the $72k run; Cloud Monitoring alerts lag 3–4 minutes). Vercel, $738 against a $120 "limit": the owner had set a spend amount, which notifies at 100% but pauses projects only if a pause action or webhook is configured. Cara ignored 12 Vercel usage alerts whose subjects read like routine mail.

**Look for:** whether the platform supports a hard cap (Vercel Spend Management, Netlify usage caps, provider sending limits, analytics billing limits) and whether it is on; budget alerts and who receives them; a kill switch (GCP budget → Pub/Sub → function that detaches billing; Vercel pause on cap). Most of this is **can't tell from code**: list it for the dashboard check.

**Trigger:** any other pattern firing.

**Fix:** turn on hard caps where they exist; budget alerts at low thresholds to a channel someone reads, tested once to prove they arrive; an automated kill switch where caps do not exist; per-service quotas. Confirm the cap actually stops spend rather than only notifying. Weigh the tradeoff: a cap that trips takes the app offline, which most of these owners would have preferred.

### G2. No rate limiting or bot protection on metered paths

**Bills:** Netlify $104.5k, Firebase $100k, Mailgun $11k, Vercel $23k. Cloudflare, $36k: the owner wrote a rate limiter during a rushed migration but never wired it in, and bots drove most of the usage.

**Look for:** rate limiting middleware, WAF rules, bot protection, per-user quotas on every route that spends money.

**Fix:** rate limits keyed on IP and identity at the edge; bot protection on forms; quotas on expensive features. Check that each limiter is registered on the routes it guards; a limiter that exists in the code but is not applied guards nothing.

### G3. Unreviewed changes to hot paths

**Bills:** Cloudflare $10.8k ("vibe coding failed me"), PostHog $733 (an AI agent's unreviewed change), Firebase $70k (a contractor's bug).

**Look for:** recent commits by agents or contractors that touch loops, triggers, queue consumers, alarms, tracking, or storage writes without tests that bound their call counts.

**Fix:** review and test any change to a trigger, loop, or metered call; a test that asserts the number of calls to a paid API per operation.

### G4. Vendor concentration

**Bills:** Cloudflare, $120k/year Enterprise contract demanded in 24 hours; hours after the customer mentioned Fastly, its domains, DNS records, cache rules, rate limits, and Access config were purged, with hours of outage and weeks of internal recovery.

**Look for:** DNS, hosting, and storage with one vendor whose terms allow unilateral plan changes.

**Fix:** keep the registrar with a separate provider; keep DNS, cache, rate-limit, and auth config in code (DNSControl, Terraform) so it can move in hours; know the exit path before you need it. Report this as Low unless the project depends on one vendor for DNS and serving.
