# agentmail

Gives an agent a real email inbox. [AgentMail](https://www.agentmail.to) is an API-first mailbox built for agents: unlike one-way senders such as Resend, SendGrid, or SES, an AgentMail inbox both sends and receives, so an agent can complete an email round trip on its own. Sign up for a service, wait for the verification mail, pull the code out, and carry on.

## What it covers

- Resolving or creating an inbox, including the fallback path when the API key is inbox-scoped and cannot list.
- Sending, replying in thread, listing, and full-text search over REST, the Python and TypeScript SDKs, or the CLI.
- Receiving by polling, WebSocket, or webhook, with a decision rule for which one a situation allows.
- `scripts/wait-for-email.sh`, which blocks until a matching message lands and optionally pulls the numeric code out of it.
- The failure modes that bite in practice: permanent bounce suppression, `403 missing_permission` naming the key rather than the code, and the events that carry no body.

## When it fires

Any task that needs to actually send or receive email. Testing a signup, magic-link, OTP, password-reset, invite, or notification flow end to end. Confirming what an app really delivered rather than trusting a 200. Corresponding with a real person on the user's behalf. Or any mention of AgentMail, `AGENTMAIL_API_KEY`, `agentmail.to`, or an agent inbox.

## Setup

The skill expects `AGENTMAIL_API_KEY` in the environment. Get a key from [console.agentmail.to](https://console.agentmail.to) and export it from your shell profile, or put it in a project's gitignored `.env`. An organization-scoped key can list and create inboxes; an inbox-scoped one is limited to the single inbox it was minted for.

## Layout

| Path | Contents |
|---|---|
| `SKILL.md` | The always-loaded surface: credentials, inbox resolution, send, receive, reply, gotchas. |
| `references/rest-api.md` | Endpoints, SDK signatures, permissions, errors, CLI, MCP, IMAP/SMTP, plans. |
| `references/events.md` | Webhook events and payloads, WebSocket subscriptions, polling. |
| `references/recipes.md` | Worked flows: verification codes, magic links, reply loops, attachments, agent toolkits. |
| `scripts/wait-for-email.sh` | Poll an inbox until a matching message arrives. |
