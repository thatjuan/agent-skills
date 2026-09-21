---
name: forge-suite
description: "Operate the Forge cold-outreach suite (Salesforge, Warmforge, Mailforge) through its REST APIs with curl. Use when managing Salesforge workspaces, contacts, DNC, mailboxes, email or multichannel (email + LinkedIn) sequences, enrollments, Primebox threads and replies, or webhooks; Warmforge mailbox warmup, health, Heat Score, or inbox placement tests; Mailforge domains, DNS, forwarding, masking, mailboxes, or pre-warmed inventory; when code calls `api.salesforge.ai`, `multichannel-api.salesforge.ai`, `api.warmforge.ai`, or `api.mailforge.ai`; or when `SALESFORGE_API_KEY`, `WARMFORGE_API_KEY`, or `MAILFORGE_API_KEY` appears."
---

# Forge Suite

Three products from one vendor, four REST surfaces, three separate API keys. Mailforge provisions domains and mailboxes, Warmforge warms them and reports deliverability, Salesforge sends sequences from them and handles replies.

## API surface map

| Surface | Base URL | Key | Owns |
|---------|----------|-----|------|
| **Salesforge core** | `https://api.salesforge.ai/public/v2` | `SALESFORGE_API_KEY` | Workspaces, contacts, tags, custom vars, DNC, mailboxes, V1 email sequences, threads and replies, Primebox labels, products, webhooks |
| **Salesforge multichannel** | `https://multichannel-api.salesforge.ai/public/multichannel` | `SALESFORGE_API_KEY` (same key) | V2 sequences as a node graph (email + LinkedIn), LinkedIn accounts, sender profiles, validation runs, enrollment preflight, subsequences |
| **Warmforge** | `https://api.warmforge.ai/public/v1` | `WARMFORGE_API_KEY` | Warmup settings and stats, mailbox health (SPF/DKIM/DMARC/MX, blacklists, Heat Score), inbox placement tests |
| **Mailforge** | `https://api.mailforge.ai/public` | `MAILFORGE_API_KEY` | Domain search and purchase, DNS, forwarding, masking, mailboxes and their SMTP/IMAP credentials, pre-warmed inventory, spam check, mailbox analytics |

Each key authenticates only its own product. Each product also keeps its own workspace records, so resolve and store a workspace ID per product; match mailboxes across products by email address.

## Step 1: load the keys

Keys live in a `.env` file. Load only the keys the task needs.

1. Find `.env` in the working directory, then walk up to the repo root. Check for the variable names with `grep -c '^SALESFORGE_API_KEY=' .env` (count only, so the value stays out of the transcript).
2. When the file or a needed variable is missing, ask the user where that key lives: another env file path, a different variable name, or not yet created. Keys are created per product at `app.salesforge.ai`, `app.warmforge.ai`, `app.mailforge.ai` under Settings > API. Ask them to put new keys in `.env` rather than in chat.
3. Load inside every Bash call that needs a key, since shell state does not persist between calls:

```bash
forge_key() { grep -E "^(export )?$1=" "${FORGE_ENV:-.env}" | tail -1 | cut -d= -f2- | sed -e "s/^[\"']//" -e "s/[\"']\$//"; }
SALESFORGE_API_KEY=$(forge_key SALESFORGE_API_KEY)
WARMFORGE_API_KEY=$(forge_key WARMFORGE_API_KEY)
MAILFORGE_API_KEY=$(forge_key MAILFORGE_API_KEY)
```

4. Validate each loaded key once, printing the status code only. `200` means the key is good; `401` means wrong key, wrong product, or a stray `Bearer ` prefix.

```bash
curl -sS -o /dev/null -w 'salesforge %{http_code}\n' https://api.salesforge.ai/public/v2/me -H "Authorization: $SALESFORGE_API_KEY"
curl -sS -o /dev/null -w 'warmforge %{http_code}\n' "https://api.warmforge.ai/public/v1/workspaces?page=1&page_size=1" -H "Authorization: $WARMFORGE_API_KEY"
curl -sS -o /dev/null -w 'mailforge %{http_code}\n' https://api.mailforge.ai/public/workspaces -H "Authorization: $MAILFORGE_API_KEY"
```

5. Confirm `.env` is ignored with `git check-ignore .env`; tell the user when it is tracked or unignored.

Key hygiene: refer to keys by variable name only. Keep `curl` at `-sS` (`-v` prints the `Authorization` header), and read `.env` through `grep -c` or `forge_key`, never `cat`.

## Step 2: make calls

Auth on all four surfaces is the **raw key** in `Authorization`, with `Content-Type: application/json` on bodies:

```bash
curl -sS "https://api.salesforge.ai/public/v2/workspaces" -H "Authorization: $SALESFORGE_API_KEY"
```

A `Bearer ` prefix breaks Salesforge core and Mailforge. Warmforge's docs disagree with each other, so send raw first and retry once with `Bearer ` only on a Warmforge 401.

Resolve the workspace before anything else: `GET /workspaces` on the product you are calling. Then read the reference for that surface before building the request; conventions differ enough between the four that guessing fails.

| Convention | Salesforge core | Multichannel | Warmforge | Mailforge |
|------------|-----------------|--------------|-----------|-----------|
| Pagination | `limit` + `offset` | `page` + `limit` (max 100) | `page` + `page_size` (both required; placement tests use `size`) | None on most lists (bare arrays) |
| List shape | `{data, limit, offset, total}` | named key + `pagination` | named key + page fields | bare array |
| Workspace | in path | in path | in path | body field `workspaceId` on purchases; mailboxes inherit from their domain |
| IDs | prefixed strings (`lead_`, `seq_`) | sequences, nodes, branches, sender profiles, LinkedIn accounts are **integers** | mailbox by URL-encoded email in path, by ID in bodies | strings |
| Errors | `{message, data}` | `{message, data}` with stable codes (`preflight_stale`) | `{message, data}` | `{code, message}` |

Rate limits are undocumented on every surface. Serialize bulk work and back off on 429 and 5xx.

## References

| File | When to read |
|------|--------------|
| [references/salesforge-api.md](references/salesforge-api.md) | Any call to `api.salesforge.ai`: contacts, tags, DNC, mailbox connect (SMTP or OAuth link), V1 sequence build and launch, validation, threads and replies, labels, analytics, webhook creation and signature verification, all enums |
| [references/salesforge-multichannel-api.md](references/salesforge-multichannel-api.md) | Any V2 or LinkedIn work: the node and branch graph model with a worked example, action and condition catalogs, LinkedIn account connect with OTP or magic link, sender profiles, validation runs, enrollment preflight and confirm, launch, subsequences |
| [references/warmforge-api.md](references/warmforge-api.md) | Warmup enable and tuning (single and bulk), warmup stats, health report fields, placement test create and polling, fleet placement results, plus an appendix on the app-only API |
| [references/mailforge-api.md](references/mailforge-api.md) | Domain availability and purchase, registrant contact and ccTLD extra fields, DNS read and replace, forwarding, masking, mailbox create and credential retrieval, pre-warmed inventory, spam check, analytics, and the full money-spending endpoint table |

Each reference names its OpenAPI spec URL. When a call returns an unexpected 400 or 404, fetch that spec and diff the request against it before retrying.

## Capability routing

| Task | Surface and entry point |
|------|-------------------------|
| Add or import contacts, manage tags, DNC | Core: `{ws}/contacts`, `{ws}/contacts/bulk` (100 max, all or nothing), `{ws}/dnc/bulk` |
| Email-only sequence | Core V1: `{ws}/sequences` then steps, schedules, mailboxes, contacts, validation, status |
| Email + LinkedIn sequence, branching logic | Multichannel: sequence, schedule, settings, sender profiles, nodes on branches, enroll, launch |
| Enroll contacts into a V2 sequence | Multichannel: validation run, `enrollments/preflight`, `preflight/{id}/confirm` (15 minute expiry) |
| Connect a LinkedIn sender | Multichannel: `linkedin/accounts` + `otp`, or `linkedin-magic-links` to keep credentials with the owner |
| Read and answer replies | Core: `{ws}/threads`, `{ws}/threads/{id}`, `.../emails/{id}/reply`, `.../linkedin/reply`, `{ws}/threads/{id}/label` |
| React to events | Core: one webhook per event type at `{ws}/integrations/webhooks`; store `signingSecret` from the create response, it is returned once |
| Connect a mailbox for sending | Core: `{ws}/mailboxes` (SMTP/IMAP) or `{ws}/mailboxes/oauth-link` (Google, Outlook; also auto-provisions it in Warmforge) |
| Start, stop, or tune warmup | Warmforge: `PATCH .../mailboxes/{address}` or `mailboxes/bulk-update` with scoped `filters` |
| Judge whether a mailbox is ready to send | Warmforge: mailbox `healthReport` (DNS statuses, blacklists, `heatScore`) + `warmup/stats` + latest placement `result` |
| Test inbox placement | Warmforge: `POST .../placement-tests`, poll until `pendingCount` is 0 |
| Find and buy domains | Mailforge: `check-domain-availability-bulk`, `domains/alternative-domains`, then `POST /domains` |
| Create mailboxes and get SMTP/IMAP credentials | Mailforge: `POST /mailboxes`, `GET /mailboxes?with_credentials=true` |
| Fix DNS | Mailforge: `GET /domains/{id}/dns`, merge, `PUT` the complete set back |
| Check copy for spam signals | Mailforge: `POST /spam-check/is-spam` |

### New sending infrastructure, end to end

1. Mailforge: resolve workspace, check availability, confirm price with the user, `POST /domains`, poll until `active`.
2. Mailforge: `POST /mailboxes`, poll until `active`, read `credentials`.
3. Salesforge core: `POST {ws}/mailboxes` with those SMTP/IMAP credentials, poll until `active`.
4. Warmforge: list the workspace mailboxes and check whether the address already arrived; otherwise `connect-smtp` with the same credentials. Set `warmupEnabled: true` and the ramp settings.
5. Warmforge: hold sending until DNS statuses are all `valid`, no significant blacklist hit, and placement `result` clears the user's bar (the vendor suggests 90).
6. Salesforge: assign the mailbox to a sequence (V1) or a sender profile (V2).

## Confirm first

These calls spend money, reach real people, or cannot be undone. Before each one, show the user exactly what will happen (endpoint, target, counts, price where known) and get a go-ahead. Approval covers that one call.

| Class | Calls |
|-------|-------|
| **Spends money** (Mailforge) | `POST /domains`, `/domains/transfer`, `/domains/pre-warmed` (charges immediately), `/domains/masking`, `POST /mailboxes` (buys slots automatically at the limit), `/adjust-mailbox-topup-amount`, enable autorenew |
| **Spends credits** (Salesforge) | Validation start (core and multichannel), LinkedIn account connect and reconnect |
| **Contacts real people** | V1 `PUT .../status` to `active`, V2 `PATCH .../launch` and resume, enrolling contacts into an already active sequence, email reply, LinkedIn reply, Warmforge placement test send |
| **Destructive** | Any `DELETE` (a Mailforge workspace delete cascades to its domains and mailboxes), `contacts/bulk-delete`, Mailforge `PUT .../dns` and `bulk-dns` (replace, never merge), disable autorenew, Mailforge mailbox `password` change (breaks every connected sender), enrollment `move` confirm, Warmforge `bulk-update` with broad filters |

Reads, drafts, and building an unlaunched sequence need no confirmation.

## Red flags

| Pattern | Risk |
|---------|------|
| `Authorization: Bearer ...` | 401 on Salesforge core and Mailforge |
| One product's key or workspace ID sent to another product | 401 or 404; keys and workspace IDs are per product |
| Creating V2 nodes after launch | Launch locks the graph; build the whole tree first |
| Assuming `yes`/`no` branch order | Branch names are data; re-list branches after every node create |
| V2 `waitDays` on node update | Create takes `waitDays`, update takes `wait_in_minutes`, conditions take `minutesToWait` |
| Holding a `preflightId` across a long task | Expires in 15 minutes (404) and goes stale on any enrollment change (409 carries a replacement in `data`) |
| Sending a delta to V1 `PUT .../steps` or `.../schedules` | Both replace the full collection |
| Mailforge DNS `PUT` without the `editable: false` rows | Drops managed MX/SPF/DKIM and breaks mail |
| Warmforge `bulk-update` with empty `filters` | Can hit every mailbox in the workspace |
| Parsing a Warmforge `202` delete body as JSON | Body is empty; confirm with a follow-up GET |
| Reading a fresh placement test's low `result` as a problem | Tests are async; wait for `pendingCount` 0 |
| Unknown query param on core `GET {ws}/contacts` | 400 rather than ignored |
| Mailforge `/api-keys` with an API key | Needs an app session token and drops the `/public` prefix; key management is a console task |
