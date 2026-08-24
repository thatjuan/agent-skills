---
name: agentmail
description: "AgentMail gives an agent its own real email inbox: send, receive, reply, search, and wait for mail over REST, the Python/TypeScript SDKs, or the CLI. Use whenever a task needs to actually send or receive email, including end-to-end testing a signup, magic-link, OTP, password-reset, invite, or notification flow; confirming what an app really delivered; corresponding with a real person on the user's behalf; or when the code or question mentions AgentMail, AGENTMAIL_API_KEY, agentmail.to, api.agentmail.to, mcp.agentmail.to, the agentmail SDK or CLI, or an agent inbox. This is the default email channel for agents on this machine, so reach for it before Resend, SendGrid, SES, Mailgun, Gmail, or a disposable-mailbox site."
---

# AgentMail

An API-first mailbox built for agents. Unlike one-way senders (Resend, SendGrid, SES), an AgentMail inbox both **sends and receives**, so an agent can drive a real email round trip end to end: sign up for a service, wait for the verification mail, pull the code out, and continue.

## Credentials

`AGENTMAIL_API_KEY` is exported globally from `~/.zshenv`, so it is already in the environment of any shell an agent spawns. Confirm before doing anything else:

```bash
[ -n "$AGENTMAIL_API_KEY" ] && echo "key present" || echo "key missing"
```

If it is missing, the key lives in `~/.zshenv`; source it rather than asking the user to paste it again. Refer to the key as `$AGENTMAIL_API_KEY` in every command. Keep the literal value out of transcripts, commit messages, source files, and any `.env` that git tracks.

Auth is a bearer header on every REST call:

```bash
-H "Authorization: Bearer $AGENTMAIL_API_KEY"
```

## Resolve the inbox first

Every send, list, and reply is scoped to an `inbox_id` (which is just the inbox's email address, such as `agent@agentmail.to`). Resolve it once at the start of a task, in this order, and reuse it:

1. `$AGENTMAIL_INBOX_ID` if the environment already sets it.
2. `GET /v0/inboxes` and take the address you want.
3. Create one: `POST /v0/inboxes` with a `client_id`, which makes the call idempotent so re-running a script reuses the same inbox instead of burning another one against the plan limit.
4. If steps 2 and 3 both return `403 missing_permission`, the key is **inbox-scoped** and cannot enumerate or create. Fall back to `GET /v0/threads`, which is org-wide and returns an `inbox_id` on every thread. With an empty inbox and no thread to read, ask the user for the address rather than guessing.

```bash
# 1-2: list
curl -s https://api.agentmail.to/v0/inboxes \
  -H "Authorization: Bearer $AGENTMAIL_API_KEY"

# 3: create, idempotent on client_id
curl -s -X POST https://api.agentmail.to/v0/inboxes \
  -H "Authorization: Bearer $AGENTMAIL_API_KEY" -H "Content-Type: application/json" \
  -d '{"username":"altumo-test","client_id":"altumo-test-inbox"}'

# 4: recover the address from any existing thread
curl -s "https://api.agentmail.to/v0/threads?limit=1" \
  -H "Authorization: Bearer $AGENTMAIL_API_KEY"
```

A per-purpose inbox with a stable `client_id` beats a fresh inbox per run. The free plan allows 3 inboxes and 3,000 messages a month, so inboxes are the scarce resource and messages are not.

## Send

```bash
curl -s -X POST "https://api.agentmail.to/v0/inboxes/$INBOX/messages/send" \
  -H "Authorization: Bearer $AGENTMAIL_API_KEY" -H "Content-Type: application/json" \
  -d '{"to":["someone@example.com"],"subject":"Hello","text":"Plain body","html":"<p>Plain body</p>"}'
```

Returns `{"message_id":"...","thread_id":"..."}`. Always send `text` alongside `html`; an html-only message reads as spam to filters and as nothing to plain-text clients.

## Receive

Receiving means one of three things. Pick by what the situation actually allows:

- **Polling** is the default for local work and tests. No public URL, no server, works everywhere.
- **WebSocket** for a long-lived local process that wants sub-second delivery without exposing a port.
- **Webhook** only when a publicly reachable HTTPS endpoint already exists or the task is to build one. See [`references/events.md`](references/events.md).

The common case, waiting on a verification or reset mail, is one command:

```bash
scripts/wait-for-email.sh --inbox "$INBOX" --from noreply@example.com --timeout 120
```

It polls until a matching message lands, prints the full message as JSON, and exits non-zero on timeout. `--subject`, `--after`, and `--extract-code` narrow or post-process the result; `--help` lists the flags. Reading the mail is `GET /v0/inboxes/{inbox_id}/messages`, and the flags map onto its `from`, `subject`, and `after` filters.

Read a message body from `extracted_text` (the new content, with the quoted trail stripped) and fall back to `text`. Use `text` only when the quoted history is the point.

## Reply in thread

```bash
curl -s -X POST "https://api.agentmail.to/v0/inboxes/$INBOX/messages/$MESSAGE_ID/reply" \
  -H "Authorization: Bearer $AGENTMAIL_API_KEY" -H "Content-Type: application/json" \
  -d '{"text":"Thanks, got it.","html":"<p>Thanks, got it.</p>"}'
```

Replying through this route keeps threading and headers correct. A fresh `send` with `Re:` glued onto the subject starts a new thread and breaks the conversation for the recipient.

## Sending on the user's behalf

Mail to a real person leaves the machine and cannot be recalled. Show the user the recipient, subject, and body, and get an explicit go-ahead before the first such send. Test mail to an inbox you control needs no such check. Once the user approves a specific send, do not re-ask for each retry of that same message.

## Building it into a project

Reach for an SDK over curl when the email flow becomes application code rather than a one-off shell step: `npm install agentmail` or `pip install agentmail`, both of which read `AGENTMAIL_API_KEY` from the environment on construction. The TypeScript client is `AgentMailClient`, the Python one is `AgentMail`. Method signatures, pagination, attachments, labels, drafts, domains, and pods live in [`references/rest-api.md`](references/rest-api.md).

For a project of the user's own, put `AGENTMAIL_API_KEY` in the project's gitignored `.env` and read it from there. The global export is for agent work, not for shipped code that other people will run.

## Gotchas

- **Bounces and complaints are permanent.** A bounced or spam-reported address is blocked for the whole account. Never loop a send against an address that just bounced, and keep the bounce rate under 4% or the account goes under review.
- **`message.received` is the only event carrying the full thread and message.** Every other event is metadata, so a handler that needs the body must fetch it.
- **`403 missing_permission` is a key problem, not a code problem.** The error names the exact permission. An inbox-scoped or whitelisted key cannot be widened from itself; a broader key has to come from the console at https://console.agentmail.to.
- **`429` carries `Retry-After`.** Honour it and back off exponentially instead of retrying tight.
- **One SPF record per domain.** Merge, do not append a second: `v=spf1 include:spf.agentmail.to include:other.com ~all`.

## Reference

- [`references/rest-api.md`](references/rest-api.md) — endpoints, SDK signatures, pagination, attachments, labels, search, drafts, domains, pods, IMAP/SMTP.
- [`references/events.md`](references/events.md) — webhook event types and payloads, HMAC verification, WebSocket subscriptions, ngrok-backed local handlers.
- [`references/recipes.md`](references/recipes.md) — full worked flows: OTP extraction, signup verification, an inbox-driven reply loop, attachments.
- Official docs: https://docs.agentmail.to and https://docs.agentmail.to/llms-full.txt. Console: https://console.agentmail.to.
