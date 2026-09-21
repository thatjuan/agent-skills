# Mailforge Public API

Cold-email infrastructure: workspaces, domain search and purchase, DNS, forwarding, masking, mailboxes, pre-warmed inventory, spam check, mailbox analytics.

## Header

- **Base URL**: `https://api.mailforge.ai/public` (swagger `host: api.mailforge.ai`, `basePath: /public`, `schemes: ["https"]`).
- **Auth header**: `Authorization: <raw key>`. Send the raw key with **no `Bearer ` prefix**. Spec declares `securityDefinitions.ApiKeyAuth = {type: apiKey, name: Authorization, in: header}`. The official guide (mailforge.ai/blog/mailforge-api) uses `--header "Authorization: ${MAILFORGE_API_KEY}"`, and developer.salesforge.ai/authentication states "Bearer authentication and API key authentication are different. Adding `Bearer ` changes the header value and causes Salesforge requests to fail." Same rule here.
- **Where keys come from**: the Mailforge app, **Settings > API**. Each Forge product has its own key. A Salesforge key does not work on `api.mailforge.ai`, and a Mailforge key does not work on Salesforge or Warmforge. Store as `MAILFORGE_API_KEY`.
- **Content type**: `Content-Type: application/json` on every request with a body; `Accept: application/json` on reads. All operations declare `application/json`.
- **MCP alternative**: `https://mcp.salesforge.ai/mcp` with header `X-Mailforge-Key: <key>`. That header name applies to MCP only. Use `Authorization` for REST.
- **Key smoke test** (cheap, read-only):

```bash
curl -sS --request GET \
  --url "https://api.mailforge.ai/public/workspaces" \
  --header "Authorization: ${MAILFORGE_API_KEY}" \
  --header "Accept: application/json"
```

A 200 with a JSON array confirms the key. A 401 means the key is missing, revoked, or prefixed with `Bearer `.

## Conventions

- **Workspace scoping**: the API key scopes to the **account**, not a workspace. Only the three analytics endpoints put the workspace in the path (`/workspaces/{workspaceID}/...`). Everywhere else, pass `workspaceId` as a **body field** on the calls that attach resources to a workspace: `POST /domains`, `POST /domains/transfer`, `POST /domains/pre-warmed`. `GET /domains` and `GET /mailboxes` return the whole account and expose `workspaceId` on each row, so filter client side (or use the `search` query on `/domains`, which matches workspace id). `POST /mailboxes` takes no `workspaceId`: the mailbox inherits the workspace of the domain in its email address.
- **Response envelope**: none for list reads. `GET /workspaces`, `GET /domains`, `GET /mailboxes`, `GET /domains/{id}/dns`, `GET /domains/extra-fields`, `POST /check-domain-availability-bulk`, `POST /domains/alternative-domains`, `POST /domains/masking` return **bare JSON arrays**. Write endpoints wrap results in a named key (`{"domains": [...]}`, `{"mailboxes": [...]}`).
- **Pagination**: only three endpoints paginate.
  - `GET /mailboxes/pre-warmed`: `limit` (1-100, default 100) + `offset`, response carries `pagination {limit, offset, total}`.
  - `GET /workspaces/{id}/mailboxes/analytics/summary`: `page` (1-based, default 1) + `size` (25 or 50, default 25).
  - `.../analytics/recipients`: `recipientsOffset` + `recipientsLimit` (default 10, max 50), response carries `mostContacted.pagination {limit, offset, total, hasMore}`.
  - `GET /domains` and `GET /mailboxes` return everything in one array. Expect large payloads on big accounts.
- **Error body**: `{"code": <integer>, "message": <any>}` (`api.HTTPError`). `message` has no declared type, so treat it as string or object.
- **Status codes**: `200` success with body; `201` workspace created; `202` bulk job accepted and still running; `204` success with no body; `400` invalid request, domain unavailable, bad DNS payload, limit exceeded; `401` missing or invalid key; `402` no payment method on file (domain purchase); `403` workspace scope failure or admin-only endpoint; `404` workspace, domain, or mailbox not found; `429` rate limited; `500`-`503` service failure.
- **Rate limits**: **not documented**. No numeric limit, no `Retry-After` or `X-RateLimit-*` headers in the spec. The guide only says back off on 429. Use exponential backoff.
- **Required fields**: the swagger definitions carry **no `required` arrays** on any request model. Only the body parameter itself is marked required. Required flags below come from endpoint descriptions and semantics. Send the full documented payload and read the 400 message when a field is rejected.
- **Async writes**: `202` responses (`PUT /domains/bulk-dns`, `POST /mailboxes/bulk-forward`) queue work. Poll `GET /domains/{id}/dns` or `GET /mailboxes` to confirm.

## Endpoint catalog

### Workspaces

`GET /workspaces`
List all workspaces on the account. No params. Returns array of `{accountId, id, name, slug}`.

`POST /workspaces`
Create a workspace. Body: `name` (string, required). Returns `201` with `{accountId, id, name, slug}`. Keep `id` for domain purchases.

`PATCH /workspaces/{workspaceID}`
Rename a workspace. Path: `workspaceID` (string, required). Body: `name` (string, required). Returns `204`.

`DELETE /workspaces/{workspaceID}` **DESTRUCTIVE**
Permanently delete a workspace **and all its associated resources** (domains, mailboxes). Path: `workspaceID`. Returns `204`.

### API keys

All four require a **Firebase Bearer token** (the app session token), not a Mailforge API key, and the spec states they **must be called without the `/public` prefix**: use `https://api.mailforge.ai/api-keys`. An agent holding only a Mailforge API key cannot manage keys.

`GET /api-keys`
List keys. Returns array of `{id, accountId, name, isActive, lastUsedAt, createdAt, updatedAt}`. The raw key is never returned here.

`POST /api-keys`
Create a key. Body: `name` (string). Returns `{id, accountId, name, key, isActive, createdAt, updatedAt}`. `key` is the **raw key, shown once**. Capture it immediately.

`PATCH /api-keys/{apiKeyID}`
Toggle a key active or inactive. Path: `apiKeyID`. Body: `isActive` (boolean). Returns the key record.

`DELETE /api-keys/{apiKeyID}` **DESTRUCTIVE**
Permanently delete a key. Any integration using it starts failing with 401. Returns `204`.

### Domain availability

`GET /check-domain-availability`
Check one domain and get its price. Query: `domain` (string, required, e.g. `example.com`). Returns `{available: bool, domain: string, price: number}`. `price` is a decimal in account currency.

`POST /check-domain-availability-bulk`
Check up to **100** domains at once. Body: `domains` (string array, required, **max 100**). Returns array of `{available, domain, price}`. Over 100 returns `400 "Maximum 100 domains allowed"`.

`POST /domains/alternative-domains`
Suggest available alternative names. Does **not** reserve or buy anything, and excludes domains already active on the account. Body: `inputSld` (string, required, the name without the dot-suffix), `outputTld` (string, required, without the leading dot), `count` (integer, required, how many suggestions). Returns array of `{available, domain, price}`. `400` on an unsupported TLD.

`GET /domains/extra-fields`
Return the Enom extended attributes required for the given TLDs, as a union across all requested TLDs. Query: `tlds` (comma-separated, e.g. `eu,de`) **or** `domains` (comma-separated FQDNs, TLDs derived). One of the two is required. Returns array of `{name, description, options: [{name, value, description}]}`, for example `name: "eu_whoispolicy"`. Feed `name` and the chosen option `value` into `contactDetails.extra` on `POST /domains`. **Currently admin-only during rollout**: non-admin callers get `403`.

### Domains

`GET /domains`
List every domain on the account. Query: `status` (enum `active,pending,failed,expired,scheduled_for_deletion,not_paid`), `search` (matches domain id, workspace id, domain name, forward-to domain, or status). Returns array of the domain object: `{id, workspaceId, sld, tld, status, type, priceCents, expiresAt, nameservers[], forwardToDomain, dmarcEmail, mailServerId, setupId, isTransferred, failedReason, autoRenewStatus, autoRenewFailedReason, autoRenewProcessedAt, autoRenewLastProcessedExpiration, createdAt, updatedAt}`. Act on `status`, `id`, `failedReason`, `expiresAt`, `priceCents` (integer cents), `nameservers`.

`POST /domains` **SPENDS MONEY**
Purchase one or more domains, create DNS records, and trigger registration. Contact details go to WHOIS. Body:
- `workspaceId` (string, required) target workspace.
- `domains` (string array, required) fully qualified names to buy.
- `contactDetails` (object, required): `firstName`, `lastName`, `organization`, `jobTitle`, `email`, `phone`, `address1`, `address2`, `city`, `province`, `postalCode`, `country` (all strings), plus `dmarcEmail` (string, where DMARC reports go), `forwardToDomain` (string, where the domain redirects), and `extra` (map of string to string) for TLD-specific Enom attributes.
Returns `{domains: [domain object]}`. `400` when a domain is unavailable or required `contactDetails.extra` keys are missing. `402` when no payment method is on file. Note the spec's rollout caveat: the pre-charge 400 for missing extras is enforced only for global admin users; other callers hit the legacy path and can be charged before the extras failure surfaces.

`POST /domains/transfer` **SPENDS MONEY**
Transfer existing domains into the account. Body: `workspaceId` (string, required), `domains` (string array, required), `dmarcEmail` (string), `forwardToDomain` (string). Returns `{domains: [...], invoice: {id, subTotal, total, amountPaid, creditsApplied, paidAt}, allDomainsAlreadyInWorkspace: bool}`. When every domain already exists in the workspace, no invoice is created (`allDomainsAlreadyInWorkspace: true`) and non-active domains are registered where possible.

`POST /domains/pre-warmed` **SPENDS MONEY**
Buy pre-warmed domains with their bundled mailboxes and attach them to a workspace. **Charges the account directly with no checkout redirect** and requires an active subscription. Body: `workspaceId` (string, required), `domainIds` (string array, required, ids from `GET /mailboxes/pre-warmed`), `dmarcEmail` (string), `forwardToDomain` (string). Returns `{workspaceId, domains: [...], mailboxes: [mailbox object incl. credentials], setup: {id, workspaceId, status, dmarcEmail, forwardToDomain}, invoice: {...}}`. `400` on no active subscription; `404` when workspace or domains are not found.

`PUT /domains/{domainID}/enable-autorenew` **SPENDS MONEY (recurring)**
Turn on automatic renewal, committing the account to a future renewal charge. Path: `domainID`. Returns `204`, `404` if not found.

`PUT /domains/{domainID}/disable-autorenew` **IRREVERSIBLE RISK**
Turn off automatic renewal. The domain expires at `expiresAt` unless renewed manually. Returns `204`.

`POST /domains/bulk-enable-autorenew` **SPENDS MONEY (recurring)**
Body: `domainIds` (string array, required). Returns `204`.

`POST /domains/bulk-disable-autorenew` **IRREVERSIBLE RISK**
Body: `domainIds` (string array, required). Returns `204`.

### DNS

`GET /domains/{domainID}/dns`
Return all DNS records for a domain. Path: `domainID`. Returns array of `{name, type, value, editable}`. `editable: false` marks records Mailforge manages (MX, DKIM, SPF for the mail server); leave those alone.

`PUT /domains/{domainID}/dns` **DESTRUCTIVE**
**Replaces** the domain's DNS records with the set you send. Omitted records are dropped, which can break mail delivery. Body: `records` (array of `{name, type, value, editable}`, required). Read the current set with `GET` first, edit, then send the full list back. Returns `204`; `400` on invalid DNS configuration.

`PUT /domains/bulk-dns` **DESTRUCTIVE**
Update DNS across many domains in one async job. Body:
- `domains` (string array, required) target domain ids.
- `domainRecords` (array of `{name, type, value, editable}`) records to set.
- `cnameRecords` (array of `{hostName, address}`) CNAMEs to add.
- `replacementMXRecord`, `replacementSPFRecord`, `replacementDKIMRecord` (each a `{name, type, value, editable}` object) swap the managed mail records.
- `removeENOMRecords` (boolean) strips registrar default records.
- `dmarcEmail` (string), `dmarcPolicy` (string), `forwardToDomain` (string).
Returns `202 Accepted`. Poll `GET /domains/{id}/dns` to confirm.

### Forwarding and masking

`PATCH /domains/forwards`
Set or update the forwarding address for one or more domains. Body is a **bare JSON array** of `{domainId: string, forwardToDomain: string, domainMasking: boolean}`. Returns `204`.

`POST /domains/masking` **SPENDS MONEY**
Purchase domain masking (SSL redirect) for one or more domains. Body: `domainIds` (string array, required), `purchaseMasking` (boolean, required, true to buy), `isYearly` (boolean, yearly versus monthly billing). Returns array of `{sourceDomain, destinationDomain, masking, forwardingStatus (pending|active|failed), ip, routeInServer}`. `400` on invalid request or no domains found.

`DELETE /domains/{domainID}/masking` **DESTRUCTIVE**
Remove masking/SSL redirect from a domain. Path: `domainID`. Returns `204`.

### Mailboxes

`GET /mailboxes`
List every mailbox on the account. Query: `with_credentials` (boolean) to include IMAP/SMTP secrets. Returns array of the mailbox object: `{id, workspaceId, domainId, domain, email, username, firstName, lastName, signature, status, forwardingEmail, forwardingStatus, isPrewarmed, isTransferred, nameservers[], failedReason, createdAt, updatedAt, credentials}`. `credentials` is `{imapHost, imapPort, imapUsername, imapPassword, smtpHost, smtpPort, smtpUsername, smtpPassword}` (example ports: IMAP 993, SMTP 587).

`GET /mailboxes/{mailboxID}`
Fetch one mailbox. Path: `mailboxID`. Query: `with_credentials` (boolean). Returns the mailbox object; `404` if not found.

`POST /mailboxes` **SPENDS MONEY**
Create one or more mailboxes. **Additional slots are purchased automatically when the account limit is reached**, so this call can trigger a charge without a separate confirmation. Body: `mailboxes` (array, required) of `{email, firstName, lastName, forwardingEmail, signature}`. `email` must sit on a domain the account owns. Returns `{mailboxes: [mailbox object with credentials]}`. `400` on invalid request or mailbox limit exceeded.

`PATCH /mailboxes/{mailboxID}`
Update a mailbox. Path: `mailboxID`. Body: `firstName`, `lastName`, `username`, `password`, `signature`, `forwardingEmail` (all strings, all optional). Changing `password` invalidates the SMTP/IMAP credentials already handed to Salesforge, Warmforge, or any other client. Returns `204`.

`DELETE /mailboxes/{mailboxID}` **DESTRUCTIVE**
Permanently delete a mailbox. Mail and warmup history go with it. Returns `204`.

`POST /mailboxes/bulk-forward`
Set a forwarding address on every mailbox matching a filter, async. Body: `forwardingEmail` (string, required), `search` (string, filter expression), `includedIds` (string array), `excludedIds` (string array). Returns `202`. Send a narrow `includedIds` list rather than a broad `search` to avoid touching unintended mailboxes.

`POST /adjust-mailbox-topup-amount` **SPENDS MONEY (recurring)**
Set how many mailbox slots to purchase automatically when the account runs out. Body: `amount` (integer, required). `0` disables auto top-up. A non-zero value authorizes future automatic charges. Returns `204`.

### Pre-warmed inventory

`GET /mailboxes/pre-warmed`
List available pre-warmed domains with their bundled mailboxes and a flat per-domain price. Query: `search` (domain name), `limit` (integer 1-100, default 100), `offset` (integer). Returns `{domains: [{id, domain, price, mailboxes: [{email, fullName}]}], pagination: {limit, offset, total}}`. Use `domains[].id` as `domainIds` in `POST /domains/pre-warmed`. `400` when `limit` is out of range.

### Spam check

`POST /spam-check/is-spam`
Report whether the email content resembles a known suspicious email. Body: `subject` (string), `body_html` (string), `body_plain` (string). Returns `{is_spam: boolean}`. The spec declares no security block on this operation but documents a `401`, so send the `Authorization` header anyway. Also returns `400` and `500`.

### Mailbox analytics

All three are workspace-scoped in the path and share `period` (string, one of `24h`, `7d`, `30d`, `90d`, `1y`, `all`; default `7d`) and a `degraded` string array flagging partial data sources.

`GET /workspaces/{workspaceID}/mailboxes/analytics/summary`
Per-mailbox sent, received, and daily trend for the mailbox list view. Query: `period`, `page` (integer, 1-based, default 1), `size` (integer, 25 or 50, default 25), `search` (string). Returns `{mailboxes: [{mailboxId, sent, received, replyRate, status, trend: [{date, sent, received}]}], period: {key, days, dataAvailableFrom}, degraded: []}`.

`GET /workspaces/{workspaceID}/mailboxes/{mailboxID}/analytics/activity`
Headline tiles and the activity chart for one mailbox. Query: `period`. Returns `{tiles: {emailsSent, emailsReceived, replyRate}, emailActivity: {buckets: [{date, sent, received}], totalMessages}, mailbox: {id, email, firstName, lastName, status}, domain: {id, domain, status}, period: {...}, degraded: []}`.

`GET /workspaces/{workspaceID}/mailboxes/{mailboxID}/analytics/recipients`
Most-contacted recipients and top recipient domains. Query: `period`, `recipientsOffset` (default 0), `recipientsLimit` (default 10, max 50), `domainsLimit` (default 10, max 50). Returns `{mostContacted: {rows: [{email, contacted, contactedPct, lastSent}], pagination: {limit, offset, total, hasMore}, truncated}, topRecipientDomains: [{domain, sentTo, sentToPct}], period: {...}, degraded: []}`.

## Endpoints that spend money or cannot be undone

Confirm with the user before calling any of these.

| Endpoint | What the spec and docs say |
| --- | --- |
| `POST /domains` | Purchases domains and triggers registration. `402` when no payment method is on file. Domain registration is not refundable. Missing `contactDetails.extra` may fail **after** the charge for non-admin callers. |
| `POST /domains/transfer` | Creates a real invoice (`invoice.total`, `amountPaid`, `creditsApplied`) unless every domain is already in the workspace. |
| `POST /domains/pre-warmed` | "Charges the account directly (no checkout redirect) and requires an active subscription." Returns the resulting invoice. |
| `POST /domains/masking` | Purchases masking/SSL redirect; `isYearly` picks the billing period. |
| `POST /mailboxes` | "Additional slots are purchased automatically if the account's limit is reached." A create can bill without further prompting. |
| `POST /adjust-mailbox-topup-amount` | Authorizes automatic slot purchases whenever the account runs out. `0` disables. |
| `PUT /domains/{id}/enable-autorenew`, `POST /domains/bulk-enable-autorenew` | Commit the account to recurring renewal charges. |
| `PUT /domains/{id}/disable-autorenew`, `POST /domains/bulk-disable-autorenew` | Let domains expire. Losing a domain is effectively irreversible. |
| `PUT /domains/{id}/dns`, `PUT /domains/bulk-dns` | Replace records. Dropping managed MX, SPF, or DKIM records breaks mail delivery. |
| `DELETE /mailboxes/{id}` | "Permanently deletes a mailbox." |
| `DELETE /workspaces/{id}` | "Permanently deletes a workspace and all its associated resources." |
| `DELETE /domains/{id}/masking` | Removes a paid masking product. |
| `DELETE /api-keys/{id}` | "Permanently deletes an API key." Live integrations start returning 401. |
| `PATCH /mailboxes/{id}` with `password` | Rotates SMTP/IMAP credentials and breaks every connected sender. |

## Enumerations

- **Domain status** (`models.DomainStatus`, on domain objects): `draft`, `active`, `pending`, `failed`, `expired`, `warning`, `scheduled_for_deletion`, `not_paid`.
- **Domain status filter** (`GET /domains?status=`, narrower than the response enum): `active`, `pending`, `failed`, `expired`, `scheduled_for_deletion`, `not_paid`. Passing `draft` or `warning` returns `400 Invalid domain status`.
- **Domain auto-renew status** (`models.DomainAutoRenewStatus`): `disabled`, `enabled`, `failed`.
- **Domain type** (`models.DomainType`): `v2` (only value).
- **Mailbox status** (`models.MailboxStatus`): `draft`, `active`, `pending`, `processing`, `failed`, `scheduled_for_deletion`.
- **Forwarding status** (`models.ForwardingStatus`, on mailboxes and masking results): `pending`, `active`, `failed`.
- **Analytics period**: `24h`, `7d`, `30d`, `90d`, `1y`, `all`.
- **Analytics page size**: `25` or `50`.
- **DNS record type**: free-form `string`, not enumerated. Expect the usual `A`, `MX`, `TXT`, `CNAME`, `NS`. Read existing records to match the format the service writes.
- **DMARC policy** (`dmarcPolicy` on bulk DNS): free-form `string`, not enumerated. Use standard values `none`, `quarantine`, `reject`.
- **TLDs**: not enumerated. Discover supported TLDs through `GET /check-domain-availability` and `POST /domains/alternative-domains`; an unsupported TLD returns `400`.
- **Registrant extra fields**: not enumerated. Fetch per-TLD from `GET /domains/extra-fields`; each field returns `name`, `description`, and an `options` list of `{name, value, description}`. Example: `eu_whoispolicy` for `.eu`.

## Workflows

### 1. Find and buy domains

1. `GET /workspaces` to resolve or confirm the target workspace, or `POST /workspaces` to create one.
2. `POST /check-domain-availability-bulk` with up to 100 candidates, or `GET /check-domain-availability` for one.
3. `POST /domains/alternative-domains` with `inputSld` and `outputTld` when the first choices are taken.
4. `GET /domains/extra-fields?tlds=eu,de` when buying a ccTLD, and map each returned `name` to a chosen option `value` inside `contactDetails.extra`. Expect `403` outside admin accounts and be ready to retry the purchase after reading the 400 message.
5. Confirm the total price with the user (`price` per domain from step 2 or 3).
6. `POST /domains` with `workspaceId`, `domains`, and full `contactDetails`. **Spends money.**
7. Poll `GET /domains?search=<name>` until `status` reaches `active`. Read `failedReason` when it reaches `failed`.

### 2. Set DNS and forwarding

1. `GET /domains/{domainID}/dns` to read the current record set, noting `editable: false` rows.
2. `PUT /domains/{domainID}/dns` with the **complete** record list including the managed rows, or `PUT /domains/bulk-dns` across many domains with `replacementMXRecord`, `replacementSPFRecord`, `replacementDKIMRecord`, `dmarcEmail`, and `dmarcPolicy`.
3. On a `202` from bulk DNS, poll `GET /domains/{domainID}/dns` until the change lands.
4. `PATCH /domains/forwards` with `[{domainId, forwardToDomain, domainMasking}]` to point domains at the main site.
5. `POST /domains/masking` with `purchaseMasking: true` when the redirect needs SSL. **Spends money.** Watch `forwardingStatus` in the response.

### 3. Create mailboxes and retrieve credentials

1. `GET /domains?status=active` to confirm the domain is live.
2. `POST /mailboxes` with a `mailboxes` array of `{email, firstName, lastName, forwardingEmail, signature}`. **Spends money** when slots run out.
3. Read `credentials` straight from the `POST` response, or fetch later with `GET /mailboxes?with_credentials=true` or `GET /mailboxes/{mailboxID}?with_credentials=true`.
4. Poll `status` until `active`. `draft`, `pending`, and `processing` mean provisioning is still running; `failed` carries `failedReason`.
5. `POST /mailboxes/bulk-forward` with `includedIds` to route replies to a monitored inbox.

### 4. Hand mailboxes to Salesforge and Warmforge

1. **Native route**: export mailboxes to the target Salesforge workspace from inside the Mailforge app. The guide describes this as an export step, not an API auto-provision. There is no Mailforge endpoint that pushes a mailbox into Salesforge or Warmforge.
2. **Custom route**: call `GET /mailboxes?with_credentials=true`, take `imapHost`, `imapPort`, `imapUsername`, `imapPassword`, `smtpHost`, `smtpPort`, `smtpUsername`, `smtpPassword`, and connect the mailbox manually through the Salesforge or Warmforge API.
3. Warmforge warmup is included with Salesforge at no extra cost for connected mailboxes, per the guide.
4. Verify readiness with `GET /workspaces/{workspaceID}/mailboxes/analytics/summary` before starting campaigns.

### 5. Buy pre-warmed domains and mailboxes

1. `GET /mailboxes/pre-warmed?search=<term>&limit=50` to browse inventory with per-domain `price` and bundled `mailboxes`.
2. Confirm the total with the user.
3. `POST /domains/pre-warmed` with `workspaceId`, `domainIds`, `dmarcEmail`, `forwardToDomain`. **Charges the account immediately and requires an active subscription.**
4. Read `mailboxes[].credentials` and `invoice` straight from the response.

### 6. Spam-check copy

1. `POST /spam-check/is-spam` with `subject`, `body_plain`, and `body_html`.
2. Rewrite and re-check while `is_spam` is `true`. The endpoint returns a boolean only, with no score or reason.

### 7. Read analytics

1. `GET /workspaces/{workspaceID}/mailboxes/analytics/summary?period=30d&size=50` for the per-mailbox roll-up.
2. `GET /workspaces/{workspaceID}/mailboxes/{mailboxID}/analytics/activity?period=30d` for tiles and the sent/received chart.
3. `GET /workspaces/{workspaceID}/mailboxes/{mailboxID}/analytics/recipients?period=30d&recipientsLimit=50` for contact concentration.
4. Check the `degraded` array on every response and treat a non-empty value as partial data.

## Gotchas

- Send the raw key. Adding `Bearer ` produces a 401.
- Use a Mailforge key on `api.mailforge.ai`. Salesforge and Warmforge keys are separate credentials for separate hosts.
- The `/api-keys` endpoints break both rules: they need a Firebase Bearer token and drop the `/public` prefix. Treat key management as an app-console task, not an API task.
- `POST /api-keys` returns the raw `key` exactly once. Nothing retrieves it later.
- `PUT /domains/{id}/dns` **replaces** the record set. Always GET, merge, then PUT, and keep every `editable: false` row.
- `POST /mailboxes` can silently buy more slots. Check `POST /adjust-mailbox-topup-amount` state and confirm before creating in bulk.
- `PATCH /domains/forwards` takes a bare JSON array at the top level, not an object. It is the only body shaped that way.
- `POST /domains` sends `contactDetails` to public WHOIS. Use business contact details the user has approved.
- `GET /domains/extra-fields` is admin-only during rollout. For non-admin accounts, a ccTLD purchase can be charged before the missing-extras error appears.
- `POST /check-domain-availability-bulk` caps at 100 domains. Chunk longer lists.
- The swagger declares no required fields on any request model. A `200` on a partial body is not proof the payload was complete; verify the created resource with a follow-up GET.
- `202` means queued, not done. Poll after bulk DNS and bulk forward.
- `price` in availability responses is a decimal number, while `priceCents` on domain objects is an integer in cents. Do not mix them.
- The `status` filter on `GET /domains` accepts fewer values than the status enum in the response. `draft` and `warning` appear in results but cannot be filtered on.
- `POST /mailboxes` has no `workspaceId` field. The mailbox lands in the workspace that owns its domain, so buy the domain into the right workspace first.
- Rate limits are undocumented. Back off on 429 and keep bulk calls serialized.

## Sources

- OpenAPI 2.0 spec: `https://api.mailforge.ai/swagger/doc.json` (title "Mailforge API", version 1.0). 38 operations, all covered above.
- `https://www.mailforge.ai/blog/mailforge-api` (official guide: base URL, header format, Settings > API, status codes, curl examples, MCP header).
- `https://developer.salesforge.ai/authentication.md` (raw key versus Bearer, 401 and 403 meanings).
- `https://developer.salesforge.ai/overview/workspace.md` and `overview/mailbox.md` (cross-product workspace and mailbox concepts).
