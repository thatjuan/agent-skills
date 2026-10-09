# runaway-cost-audit

> Scans a project for the ways its cloud bill could run away, explains each risk in plain terms with the scenario that would trigger it, and offers to file GitHub issues with the fix.

## What it does

Usage-billed platforms (Vercel, Netlify, Cloudflare Workers, Firebase, Cloud Run, AWS, BigQuery, email, analytics, and AI APIs) turn a loop, a bot, or a misread price into a five- or six-figure bill within hours. Billing data lags by up to a day, and most of these platforms have no hard spending cap, so owners usually find out from the invoice.

`runaway-cost-audit` checks a project against a catalog of patterns drawn from every case on [serverlesshorrors.com](https://serverlesshorrors.com/), grouped in four families:

- **Loops** the code feeds itself: recursive invocations, queue consumers that re-enqueue, self-rescheduling alarms, retry storms, unbounded writes, expensive fallbacks on hot paths, analytics floods.
- **Outside traffic** someone else sends: large files on metered bandwidth, cache bypass and exposed origins, per-request rendering on viral pages, public forms that send paid email or create paid objects, resources billed even when access is denied.
- **Pricing traps**: paid tiers mistaken for free ones, pay-per-scan queries, usage-billed features that stay on, production scaling defaults on test deploys, forgotten resources.
- **Missing guardrails**: no hard spend cap, no rate limiting, unreviewed changes to hot paths, single-vendor dependence.

It works in four steps:

1. **Map the billing surface**: every metered service and every code path that spends on one.
2. **Check every pattern**: each one is marked exposed (with `file:line` evidence), guarded, not applicable, or "check your dashboard".
3. **Report**: each finding states what could happen, what would trigger it, the worst case, and the fix, ranked Critical to Low.
4. **Offer issues**: on a yes, files one GitHub issue per finding under a `Runaway cost risks` milestone, with numbered remediation steps and a way to verify the guard, following [`capture-issues`](../capture-issues/).

## When to use it

- *"Could we get a surprise bill from this?"*
- *"Audit our Vercel/Firebase/Cloudflare setup for cost risks."*
- *"We're about to launch. What happens to our bill if this goes viral or gets DDoSed?"*
- *"Do we have spend limits on everything?"*

## Example finding

```
### [Critical] Signup form sends paid email with no bot protection
What could happen: a bot submits the signup form in a loop and every submission sends a verification email you pay for.
Trigger: POST /api/signup (app/api/signup/route.ts:14) has no CAPTCHA or rate limit and calls Resend on every request.
Worst case: hundreds of thousands of emails per day, plus a burned sending domain.
Fix: Turnstile verified server-side, per-IP rate limit, daily sending cap in Resend.
```

## Install

```bash
npx skills add thatjuan/agent-skills --skill runaway-cost-audit
```
