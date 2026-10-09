---
name: runaway-cost-audit
description: "Audit a project for runaway cloud bills: self-triggering loops, retry storms, public endpoints with paid side effects, egress-heavy assets, pricing-model traps, and missing spend caps. Use when the user asks about surprise bills, cloud cost risk, spend limits, or a billing review of a serverless, Firebase, Vercel, Netlify, Cloudflare, AWS, GCP, or usage-billed SaaS setup."
---

# Runaway cost audit

A **runaway** is a bill that grows without a human deciding it should: a loop the code feeds itself, traffic someone else sends, or a price the owner never read. Usage billing turns each of these into money within hours, and billing data lags by up to a day, so the owner usually learns from the invoice. This skill finds the runaways a project is exposed to before they fire.

The pattern catalog is [`references/patterns.md`](references/patterns.md). Every pattern there comes from a real bill on [serverlesshorrors.com](https://serverlesshorrors.com/) and carries what to look for, the trigger, and the fix. Read it in full before step 2.

## 1. Map the billing surface

Build a list of everything in the project that charges per use. Look at:

- Deployment and infra config: `vercel.json`, `netlify.toml`, `wrangler.toml`/`wrangler.jsonc`, `firebase.json`, `firestore.rules`, `storage.rules`, `serverless.yml`, SAM/CDK/Terraform/Pulumi, `app.yaml`, Cloud Run/Functions settings, Dockerfiles, CI deploy steps.
- Dependencies and env vars that name metered vendors: email, SMS, LLM, analytics, search, image, storage, payments, maps.
- Code entry points: HTTP routes, webhooks, queue consumers, scheduled jobs, database and storage triggers, Durable Object alarms, client-side fetches and event tracking.
- Public assets: files under `public/`, `static/`, or uploaded to buckets, with their sizes.

For each metered thing, note its billing unit (invocation, GB-second, GB egress, read, write, list op, bytes scanned, email, token) and whether anything caps it.

Done when every metered service and every code path that spends on one is on the list.

## 2. Check every pattern

Walk every pattern in `references/patterns.md` against the map. For each, record one of: **exposed** (with `file:line` evidence), **guarded** (with the guard that stops it), **not applicable**, or **can't tell from code** (account settings, dashboards). Read the code that a hit points to; a grep match alone is a lead, not a finding.

Rate each exposed finding:

- **Critical**: unbounded, and an outsider or a single bug can trigger it (a loop with no exit, a public endpoint that sends paid email, no spend cap behind either).
- **High**: unbounded but needs unusual traffic or a specific bug path.
- **Medium**: bounded, but the bound is far above what the owner expects to pay.
- **Low**: hygiene that widens blast radius (lingering deploys, missing alerts).

Done when every pattern in the catalog has a recorded status.

## 3. Report

Write for the project owner, in plain words. Lead with the worst finding. For each exposed finding:

```
### [Critical] Queue consumer re-enqueues its own job
What could happen: one bad message loops forever and bills KV writes until someone notices.
Trigger: any request sent with mode "async" (src/ingest.ts:88 forwards it back into the queue).
Worst case: millions of writes per hour, no cap on Workers spend.
Fix: force sync mode on internal calls; add a hop counter that drops jobs after N re-queues.
```

Keep each field to a sentence. Name the concrete trigger: who or what starts it, and why nothing stops it. Price the worst case from the provider's unit price when you know it.

After the findings, add:

- **Check in your dashboards**: the "can't tell from code" items, each as one line naming the setting and where it lives.
- **Already guarded**: one line per guard found, so the owner knows what to keep.

## 4. Offer issues

Ask whether to file the findings as GitHub issues. On yes, follow [`capture-issues`](../capture-issues/SKILL.md), with these additions:

- One issue per finding, merging findings only when one change fixes them all. Group them under a `Runaway cost risks` milestone.
- Each issue carries the scenario (what could happen, trigger, worst case), the `file:line` evidence, numbered remediation steps naming the files, settings, and values to change, and a verification step that proves the guard works (a test that the loop terminates, a rate-limit response under load, a quota visible in the console).
- Dashboard-only items go in a single checklist issue.
