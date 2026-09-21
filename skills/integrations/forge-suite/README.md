# forge-suite

> Expertise for operating the Forge cold-outreach suite (Salesforge, Warmforge, Mailforge) through its REST APIs: sending infrastructure, warmup and deliverability, and email + LinkedIn sequences, with every endpoint cataloged.

## What it does

`forge-suite` makes your agent fluent in driving three products that share a vendor but not an API. Mailforge provisions domains and mailboxes, Warmforge warms them and reports health, Salesforge sends sequences and handles replies. The skill covers:

- **The API surface map.** Four REST surfaces (Salesforge core, Salesforge multichannel, Warmforge, Mailforge), which key each takes, and how their pagination, list shapes, ID types, and error bodies differ.
- **Key loading.** Reads `SALESFORGE_API_KEY`, `WARMFORGE_API_KEY`, and `MAILFORGE_API_KEY` from `.env` without printing them, validates each with a cheap call, and asks where a key lives when it is missing.
- **Salesforge.** Contacts, tags, DNC, mailbox connect, V1 email sequences, V2 multichannel sequences built as a node and branch graph, LinkedIn accounts with OTP or magic link, sender profiles, validation runs, enrollment preflight, Primebox threads and replies, webhooks with signature verification.
- **Warmforge.** Warmup enable and tuning, warmup stats, health reports (SPF, DKIM, DMARC, MX, blacklists, Heat Score), inbox placement tests.
- **Mailforge.** Domain search and purchase, DNS, forwarding, masking, mailboxes and SMTP/IMAP credentials, pre-warmed inventory, spam check, analytics.
- **A confirm-first list.** Every call that spends money, contacts real people, or cannot be undone requires a go-ahead from the user first.

It triggers when managing any of the three products, when code calls `api.salesforge.ai`, `multichannel-api.salesforge.ai`, `api.warmforge.ai`, or `api.mailforge.ai`, or when one of the three key names appears.

## When to use it

Invoke this skill when you hear:

- *"Buy five lookalike domains, put two mailboxes on each, and start warming them."*
- *"Which of our mailboxes are healthy enough to send from?"*
- *"Build a sequence that messages on LinkedIn when there's a profile and emails otherwise."*
- *"Import these leads and enroll them, but don't pull anyone out of a sequence they've replied in."*
- *"Show me unread positive replies and draft answers."*
- *"Run a placement test on this copy before we launch."*

## Example walkthrough

Asked to enroll a tagged list into a multichannel sequence, the skill loads `SALESFORGE_API_KEY` from `.env`, resolves the workspace, and starts a validation run on the tag filter (after confirming, since validation spends credits). Once the run completes it creates an enrollment preflight, reads the conflict summary, and presents the skip versus move decision to the user. It confirms within the 15 minute preflight window, and on a `409 preflight_stale` it reviews the replacement preflight from the error body instead of retrying blindly.

## Installation

```bash
npx skills add thatjuan/agent-skills --skill forge-suite
```

## Setup

Create one key per product (each app, Settings > API) and put them in `.env`:

```bash
SALESFORGE_API_KEY=...
WARMFORGE_API_KEY=...
MAILFORGE_API_KEY=...
```

Only the keys for the products you use are needed. Keep `.env` out of git.

## Bundled resources

| File | Purpose |
|------|---------|
| `SKILL.md` | Surface map, key loading, cross-surface conventions, capability routing, the end-to-end infrastructure workflow, confirm-first list, red flags |
| `references/salesforge-api.md` | Salesforge core v2: all 61 operations, enums, webhook signature verification, V1 sequence and reply workflows |
| `references/salesforge-multichannel-api.md` | Salesforge multichannel: all 50 operations, the node graph model with a worked example, LinkedIn connect, enrollment preflight, subsequences |
| `references/warmforge-api.md` | Warmforge public v1: all 15 operations, health and placement fields, warmup workflows, app-API appendix |
| `references/mailforge-api.md` | Mailforge public: all 38 operations, the money-spending endpoint table, domain, DNS, and mailbox workflows |

## Tips

- **Raw key, no `Bearer`.** A `Bearer ` prefix fails on Salesforge core and Mailforge.
- **Keys and workspace IDs are per product.** Match mailboxes across products by email address.
- **Multichannel launch locks the graph.** Build every node before launching.
- **Mailforge DNS `PUT` replaces the record set.** Read, merge, write back, and keep the managed rows.
- **`POST /mailboxes` on Mailforge can buy slots on its own.** Check the limit and confirm first.
- **Rate limits are undocumented everywhere.** Serialize bulk work and back off on 429 and 5xx.

## Related skills

- None in this repo yet. Pairs well with `clean-writing` for sequence copy.
