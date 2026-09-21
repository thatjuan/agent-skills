# Warmforge Public API

Email warmup, mailbox health, and inbox placement testing. Source of truth: `https://api.warmforge.ai/public/swagger/doc.json` (Swagger 2.0, `info.title` "Warmforge API", `info.description` "Warmforge Public API", version 1.0).

## Header

- Base URL: `https://api.warmforge.ai/public/v1` (spec `host: api.warmforge.ai`, `basePath: /public/v1`, `schemes: [https]`).
- Auth: API key in the `Authorization` header. Spec declares `securityDefinitions.ApiKeyAuth = {type: apiKey, name: Authorization, in: header}`, which carries no `Bearer` prefix.
  - Send the raw key first: `-H "Authorization: $WARMFORGE_API_KEY"`. The shared Forge authentication doc states: "Send the raw API key in the `Authorization` header. Do not add a `Bearer ` prefix." (https://developer.salesforge.ai/authentication.md)
  - The Warmforge API blog post instead shows `-H "Authorization: Bearer $WARMFORGE_API_KEY"` (https://www.warmforge.ai/blog/warmforge-api). Treat `Bearer` as the fallback: if the raw key returns 401, retry once with the prefix.
  - Live probe (unauthenticated) confirms the presence check only: an empty or whitespace header returns `{"message":"missing api key"}`, and any non-empty value, with or without `Bearer`, returns `{"message":"invalid api key"}`. Both forms reach the key lookup, so a valid key settles which one the backend accepts.
- Key creation: `app.warmforge.ai > Settings > API` (per the Forge MCP server README, https://github.com/SalesforgeAI/forge-mcp). The blog shows keys shaped like `wf_live_...`.
- The Warmforge key is separate from the Salesforge and Mailforge keys. Each Forge product issues its own key from its own app, and the Forge MCP server takes them as distinct headers (`X-Warmforge-Key`, `X-Salesforge-Key`, `X-Mailforge-Key`). Never send a Salesforge key to `api.warmforge.ai`.
- Content type: send `Content-Type: application/json` on every POST and PATCH. All responses are `application/json`.
- Cheap key validation call (also yields the workspace IDs every other call needs):

```bash
curl -sS "https://api.warmforge.ai/public/v1/workspaces?page=1&page_size=25" \
  -H "Authorization: $WARMFORGE_API_KEY"
```

## Conventions

- Workspace scoping: every resource except `GET|POST /workspaces` lives under `/workspaces/{workspaceID}/...`. Resolve the workspace ID once and cache it.
- Pagination differs per endpoint. Read carefully:
  - `GET /workspaces`: `page` and `page_size`, both required.
  - `GET /workspaces/{workspaceID}/mailboxes`: `page` and `page_size`, both required.
  - `GET /workspaces/{workspaceID}/placement-tests`: `page` and `size`, both required. The second param is `size`, not `page_size`.
  - Omitting a required pagination param risks a 400 or a silently empty page. Always send both.
- Response envelopes are per-resource, not uniform. Each body is an object holding one named array:
  - Workspaces: `{workspaces: [...], currentPage, totalCount, totalPages}`.
  - Mailboxes list: `{mailboxes: [...], page, pageSize, totalPages}`. Note `page`/`pageSize` here and no `totalCount`.
  - Bulk mailbox update: `{mailboxes: [...]}` with no pagination.
  - Placement tests list: `{placementTests: [...], currentPage, totalCount, totalPages}`.
  - Warmup stats: `{stats: [...]}`.
  - Latest placement results: `{results: [...]}`.
  - Single mailbox, single workspace, single placement test: the bare object, no wrapper.
- Mailbox addressing: single-mailbox routes address the mailbox by its email address in the path, `{address}`, not by ID. URL-encode the address so `@` becomes `%40`, for example `/mailboxes/jane.doe%40acme.com`. Use `--data-urlencode` or encode ahead of time.
- Mailbox IDs still matter: `bulk-update` filters, `placement-results/latest`, and `placement-tests` creation all take mailbox **IDs** (`id` from a mailbox object), not addresses. Fetch the list first to map address to ID.
- Error body: `{"message": "<text>", "data": <any, often absent>}` (`errors.Error`). Read `message` for the reason.
- Status codes in use: 200 OK, 201 Created (workspace create only), 202 Accepted (both deletes, empty body), 400 Bad Request, 401 Unauthorized, 404 Not Found, 409 Conflict (mailbox already connected in another workspace), 500 Internal Server Error.
- Every response carries an `x-request-id` header. Capture it when reporting a failure.
- Rate limits: not documented. The spec defines no limit headers and the blog states the live API reference is the final word on limits. Assume modest concurrency, keep bulk operations to one request at a time, and back off on 429 or 500.
- Dates: `from` and `to` on warmup stats use `YYYY-MM-DD` (spec examples `2025-09-01`, `2025-09-11`). Timestamps in responses (`lastCheckedAt`, `date`, `receivedAt`, `warmupStartDate`, `warmupEndDate`) are strings; the spec gives no format, so parse defensively.

## Endpoint catalog

### Workspaces

**`GET /workspaces`**: List workspaces for the account tied to the API key.
- Query: `page` (integer, required), `page_size` (integer, required).
- Returns `{workspaces: [{id, name, slug, accountID}], currentPage, totalCount, totalPages}`. Act on `id`.

**`POST /workspaces`**: Create a workspace on the account tied to the API key.
- Body: `name` (string, **required**, 1 to 50 chars).
- Returns 201 with `{id, name, slug, accountID}`.

### Mailboxes

**`GET /workspaces/{workspaceID}/mailboxes`**: List mailboxes with their embedded health reports.
- Path: `workspaceID` (string, required).
- Query: `page` (integer, required), `page_size` (integer, required), `search` (string), `external_reference` (string), `status` (enum: `warm`, `pending`, `disconnected`, `suspended`, `all`).
- Returns `{mailboxes: [MailboxResponse], page, pageSize, totalPages}`.
- **MailboxResponse** fields to act on: `id`, `address`, `workspaceID`, `provider` (enum), `status` (enum), `warm` (boolean), `warmupEnabled` (boolean), `warmupStartDate`, `warmupEndDate`, `warmupDaysCompleted` (integer), `warmupDaysLeft` (integer), `warmupCode` (string), `minEmailsPerDay`, `maxEmailsPerDay`, `emailRampUp`, `replyRatePercent` (integers), `firstName`, `lastName`, `signature`, and `healthReport`.
- **healthReport** (`MailboxHealthResponse`): `id`, `address`, `domain`, `heatScore` (integer, Warmforge Heat Score, 100 is optimal), `warmupDays` (integer), `lastCheckedAt` (string), `spf` / `dmarc` / `mx` (each `{status, value, error}` where `status` is the DNS enum), `dkim` (`{selector, status, value, error}`), and `blacklists` (`{detectedCount: integer, checks: [{id, name, detected: boolean, significant: boolean}]}`).

**`GET /workspaces/{workspaceID}/mailboxes/{address}`**: Fetch one mailbox plus its health report.
- Path: `workspaceID`, `address` (URL-encoded email).
- Returns a `MailboxResponse`. 404 when the address is not in this workspace.

**`PATCH /workspaces/{workspaceID}/mailboxes/{address}`**: Update one mailbox's warmup settings and identity.
- Path: `workspaceID`, `address` (URL-encoded email). Body `UpdateMailboxRequest`, all fields optional:
  - `warmupEnabled` (boolean): start or stop warmup.
  - `warmupStartDate` (string), `warmupEndDate` (string).
  - `minEmailsPerDay` (integer, min 1, max 20).
  - `maxEmailsPerDay` (integer, max 20).
  - `emailRampUp` (integer, 0 to 20): daily increase step.
  - `replyRatePercent` (integer, 0 to 50).
  - `firstName` (string, 1 to 255), `lastName` (string, 1 to 255), `signature` (string, max 1000).
- Returns the updated `MailboxResponse`.

**`DELETE /workspaces/{workspaceID}/mailboxes/{address}`**: Remove a mailbox from the workspace.
- Path: `workspaceID`, `address` (URL-encoded email). Returns 202 with an empty body. Treat as irreversible.

**`POST /workspaces/{workspaceID}/mailboxes/connect-smtp`**: Connect a mailbox over SMTP plus IMAP.
- Body `ConnectSMTPMailboxRequest`. Required: `address`, `firstName`, `lastName`, `smtpHost`, `smtpPort` (integer), `smtpUsername`, `smtpPassword`, `imapHost`, `imapPort` (integer), `imapUsername`, `imapPassword`. Optional: `warmupEnabled` (boolean), `signature` (string, max 1000), `externalReference` (string, 1 to 255).
- Returns the connected `MailboxResponse`. 409 when the address is already connected in another workspace.

**`POST /workspaces/{workspaceID}/mailboxes/connect-oauth2`**: Connect a Gmail or Outlook mailbox with tokens you already hold.
- Body `ConnectOAuth2MailboxAlternativeRequest`. Required: `email`, `provider` (enum: `gmail`, `outlook`), `clientId`, `clientSecret`, `accessToken`, `refreshToken`, `expiresIn` (integer, seconds). Optional: `externalReference` (string, 1 to 255).
- Returns the connected `MailboxResponse`. 409 on cross-workspace duplicate. This route takes tokens directly and runs no browser redirect, so complete the OAuth dance yourself first.

**`POST /workspaces/{workspaceID}/mailboxes/bulk-update`**: Apply one settings patch across a filtered set of mailboxes.
- Body `UpdateMailboxesRequest`: `{data: UpdateMailboxRequest, filters: UpdateMailboxesFilters}`. Both keys are optional in the schema, so send both to get a predictable result.
  - `data` takes the same fields and limits as the single-mailbox PATCH.
  - `filters`: `includedIds` (array of mailbox ID strings), `excludedIds` (array of mailbox ID strings), `search` (string), `specialStatus` (enum: `warm`, `pending`, `disconnected`, `suspended`, `all`).
- Returns `{mailboxes: [MailboxResponse]}` holding the updated mailboxes. 404 when a referenced mailbox is missing.
- Send `includedIds` to target an explicit set. Send `specialStatus` plus `excludedIds` to target a cohort minus exceptions. An empty `filters` object risks matching the whole workspace, so always scope it.

**`GET /workspaces/{workspaceID}/mailboxes/{address}/warmup/stats`**: Daily warmup activity for one mailbox.
- Path: `workspaceID`, `address` (URL-encoded email). Query: `from` (date `YYYY-MM-DD`, required), `to` (date `YYYY-MM-DD`, required).
- Returns `{stats: [{date, sentCount, replyCount, spamCount, providerStats}]}`, one entry per day.
- `providerStats` is a map keyed by provider name to `{primaryCount, replyCount, spamCount}`. Compute the spam rate as `spamCount / sentCount` per day, and per provider when you need to see which ESP is filtering.

**`POST /workspaces/{workspaceID}/mailboxes/placement-results/latest`**: Latest completed placement result for each of many mailboxes, in one call.
- Body: `mailboxIds` (array of strings, **required**, 1 to 100 items).
- Returns `{results: [{mailboxId, address, provider, placementTest}]}`.
- `placementTest` (`LatestMailboxPlacementTestResponse`): `id`, `placementTestId`, `placementTestGroupId`, `placementTestGroupName`, `date`, `subject`, `body`, `emailSent` (integer), `result` (integer, the inbox placement percentage), `inboxCountGmail`, `spamCountGmail`, `inboxCountOutlook`, `spamCountOutlook`, `pendingCount`, `missingCount` (all integers).
- Use this for dashboards and alerting. It is the cheapest way to read placement across a fleet.

### Placement tests

**`POST /workspaces/{workspaceID}/placement-tests`**: Create and run a placement test.
- Body `CreatePlacementTestRequest`. Required: `subject` (string), `body` (string). Optional: `name` (string), `mailboxes` (array of mailbox ID strings, minimum 1 item when present), `externalReference` (string, 1 to 255).
- Returns a `PlacementTestResponse`. Counts start at `pendingCount` and settle as seed inboxes receive the message, so poll rather than reading the create response as final.
- Omitting `mailboxes` leaves the target set to the workspace default. Send explicit IDs when you care which mailboxes run.

**`GET /workspaces/{workspaceID}/placement-tests`**: List placement tests.
- Query: `page` (integer, required), `size` (integer, required), `search` (string), `external_reference` (string).
- Returns `{placementTests: [PlacementTestResponse], currentPage, totalCount, totalPages}`.

**`GET /workspaces/{workspaceID}/placement-tests/{placementTestID}`**: Fetch one placement test with per-mailbox detail.
- Returns `PlacementTestResponse`: `id`, `name`, `workspaceId`, `date`, `mailboxCount`, `emailSent`, `result` (integer percentage), `inboxCountGmail`, `spamCountGmail`, `inboxCountOutlook`, `spamCountOutlook`, `pendingCount`, `missingCount`, and `tests`.
- `tests[]` (`PlacementTestsTestResponse`): `id`, `mailboxId`, `address`, `provider`, `date`, `subject`, `body`, `emailSent`, `result` (integer percentage), the same four inbox/spam counts, `pendingCount`, `missingCount`, and `targets`.
- `tests[].targets[]` (`PlacementTestsTestTargetResponse`): `address` (the seed inbox), `provider`, `receivedAt`, `result` (enum: `pending`, `inbox`, `spam`, `unknown`, `missing`), and `headers` (map of header name to array of string values, useful for reading SPF, DKIM, DMARC, and spam-filter verdicts).
- Read the test as finished when `pendingCount` reaches 0.

**`DELETE /workspaces/{workspaceID}/placement-tests/{placementTestID}`**: Delete a placement test.
- Returns 202 with an empty body. 404 when the ID is unknown.

## Enumerations

- `models.MailboxStatus` (mailbox `status`): `active`, `access_lost`, `pending`, `suspended`.
- `models.MailboxSpecialStatus` (list `status` filter and bulk-update `filters.specialStatus`): `warm`, `pending`, `disconnected`, `suspended`, `all`.
- `models.MailboxProvider` (`provider`): `gmail`, `outlook`, `smtp`.
- `connect-oauth2` `provider` (narrower than the model): `gmail`, `outlook`.
- `models.MailboxDNSStatus` (`spf.status`, `dkim.status`, `dmarc.status`, `mx.status`): `valid`, `invalid`, `missing`, `unknown`.
- `models.PlacementTestResult` (per seed-inbox `targets[].result`): `pending`, `inbox`, `spam`, `unknown`, `missing`.
- Warmup state is not an enum. Derive it from `warmupEnabled` (boolean), `warm` (boolean), `warmupDaysCompleted`, and `warmupDaysLeft`.
- Numeric limits worth enforcing client-side: `minEmailsPerDay` 1 to 20, `maxEmailsPerDay` max 20, `emailRampUp` 0 to 20, `replyRatePercent` 0 to 50, `signature` max 1000 chars, `externalReference` 1 to 255 chars, workspace `name` 1 to 50 chars, `mailboxIds` max 100 per request.

## Workflows

### Connect a mailbox and start warmup

1. `GET /workspaces?page=1&page_size=25` to resolve `workspaceID`.
2. `POST /workspaces/{workspaceID}/mailboxes/connect-smtp` with SMTP and IMAP credentials, or `POST .../connect-oauth2` with Gmail or Outlook tokens. Set `externalReference` to your own record ID so you can find the mailbox later with the `external_reference` query param. Handle 409 as "already connected in another workspace".
3. Set `warmupEnabled: true` at connect time (SMTP route) or with `PATCH /workspaces/{workspaceID}/mailboxes/{address}`.
4. `PATCH` the ramp settings: `minEmailsPerDay`, `maxEmailsPerDay`, `emailRampUp`, `replyRatePercent`, `warmupStartDate`.
5. `GET /workspaces/{workspaceID}/mailboxes/{address}` and confirm `status: active`, `warmupEnabled: true`, and a `healthReport` with `spf.status`, `dkim.status`, `dmarc.status`, and `mx.status` all `valid`.

### Tune warmup settings in bulk

1. `GET /workspaces/{workspaceID}/mailboxes?page=1&page_size=100&status=warm` to collect `id` values and current settings.
2. Decide the target cohort: explicit `includedIds`, or `specialStatus` plus `excludedIds` for the exceptions.
3. `POST /workspaces/{workspaceID}/mailboxes/bulk-update` with `{data: {...}, filters: {...}}`.
4. Read the returned `{mailboxes: [...]}` and confirm the new values landed on the count of mailboxes you expected.

### Read warmup stats and health

1. `GET /workspaces/{workspaceID}/mailboxes/{address}/warmup/stats?from=2025-09-01&to=2025-09-30`.
2. Per day, compute `spamCount / sentCount`. Break it down through `providerStats` to see which ESP is filtering.
3. Read `healthReport.heatScore` from the mailbox object for the single rolled-up signal, 100 being optimal.
4. Check `healthReport.blacklists.detectedCount` and, inside `checks[]`, the entries where `detected` and `significant` are both true.
5. Raise `maxEmailsPerDay` only when status is `active`, SPF, DKIM, DMARC, and MX are all `valid`, no significant blacklist hit is detected, and the latest placement `result` sits at or above your threshold. The Warmforge blog uses 90 percent.

### Run an inbox placement test and read results

1. `GET /workspaces/{workspaceID}/mailboxes?page=1&page_size=100` to collect mailbox IDs.
2. `POST /workspaces/{workspaceID}/placement-tests` with `subject`, `body`, `mailboxes` (IDs), and optionally `name` and `externalReference`. Keep the returned `id`.
3. Poll `GET /workspaces/{workspaceID}/placement-tests/{id}` until `pendingCount` reaches 0.
4. Read `result` for the group percentage, then `tests[]` per mailbox, then `tests[].targets[]` for each seed inbox verdict (`inbox`, `spam`, `missing`) and its `headers`.
5. For fleet monitoring afterwards, call `POST /workspaces/{workspaceID}/mailboxes/placement-results/latest` with up to 100 `mailboxIds` instead of fetching each test.

### How Warmforge workspaces relate to Salesforge and Mailforge

1. A workspace is the shared Forge scope concept: access control is evaluated at workspace level and almost every API operation is workspace-scoped (https://developer.salesforge.ai/overview/workspace.md). Each product keeps its own workspace records, so a Salesforge workspace ID is not a Warmforge workspace ID. Resolve IDs per product and store them separately.
2. A mailbox is likewise a shared concept with a different job per product: Salesforge sends sequences from it, Mailforge and Infraforge own the domain and DNS infrastructure under it, and Warmforge tracks its warmup and placement metrics (https://developer.salesforge.ai/overview/mailbox.md).
3. Mailboxes can arrive in Warmforge without a Warmforge API call. The Salesforge "Create mailbox OAuth link" endpoint states that after the user authorizes, "the mailbox is auto-provisioned in Warmforge under the matching workspace". Before connecting a mailbox through `connect-smtp` or `connect-oauth2`, list the Warmforge workspace and check whether the address is already present.
4. Match provisioned mailboxes across products by email address, and carry your own ID in `externalReference` on both sides so joins stay stable.
5. Operate the loop across products: Mailforge or Infraforge provisions domains and mailboxes, Warmforge warms them and reports health plus placement, and Salesforge sends from the mailboxes whose Heat Score and placement clear your bar. Warmforge itself cannot send campaigns, buy domains, provision infrastructure, or edit DNS records. It reports SPF, DKIM, DMARC, MX, and blacklist signals, and you fix them in the product that owns the DNS.

## Gotchas

- Use the raw API key in `Authorization` first, per the Forge authentication doc. Retry once with `Bearer ` only on 401, because the blog documents that form and the server accepts either header shape at the presence check.
- Do not reuse the Salesforge or Mailforge key against `api.warmforge.ai`. Warmforge issues its own key at `app.warmforge.ai > Settings > API`.
- Single-mailbox routes key on the email address, so URL-encode `@` as `%40`. Every other mailbox reference in the API uses the mailbox **ID**, so keep both.
- Pagination params are required and inconsistent: `page_size` on workspaces and mailboxes, `size` on placement tests.
- Pagination response keys are inconsistent too: `page`/`pageSize`/`totalPages` on mailboxes, `currentPage`/`totalCount`/`totalPages` on workspaces and placement tests. The mailboxes list returns no total count, so page until a short page comes back.
- `bulk-update` with empty or missing `filters` risks touching every mailbox in the workspace. Always send `includedIds` or a `specialStatus`.
- Daily send caps top out at 20 (`minEmailsPerDay`, `maxEmailsPerDay`, `emailRampUp`). Sending a larger value fails validation. Warmforge warmup volume is deliberately small and separate from your Salesforge campaign volume.
- `placement-results/latest` caps at 100 `mailboxIds`. Chunk larger fleets.
- Both DELETE routes return 202 with an empty body. Do not parse the response as JSON, and confirm with a follow-up GET.
- Placement tests are asynchronous. A fresh test reports high `pendingCount` and a low `result`, which is not a deliverability problem. Poll until `pendingCount` reaches 0.
- Placement `result` is typed as a bare integer with no description in the spec. Read it as an inbox placement percentage and confirm it against the inbox and spam counts before alerting on it.
- Connecting an address already attached to another workspace returns 409, not 200. Handle it as a routing decision, not a retry.
- `connect-oauth2` takes `clientId`, `clientSecret`, `accessToken`, and `refreshToken` in the request body. Keep those values out of logs and transcripts.
- Rate limits are not documented. Serialize bulk work and back off on 500.
- The public API exposes no "re-check health now" route. `healthReport.lastCheckedAt` tells you how stale the data is; the refresh triggers live in the app API only.

## Appendix: the Warmforge app API (session bearer auth, unverified for API keys)

`https://api.warmforge.ai/swagger/doc.json` describes a second, larger surface at `basePath: /` on the same host. Its security definition is named `Bearer` (still `apiKey` in the `Authorization` header) and it carries the web app's session and billing operations, which the public API deliberately omits. Treat it as the app's own API. Whether a Warmforge API key authenticates against it is **not verified**, and nothing in the specs or docs says it does. Prefer the `/public/v1` surface. Reach here only when an operation has no public equivalent, and confirm auth against a single read call first.

Note the different addressing: these routes use `{mailboxID}` and `{mailboxPlacementTestGroupID}`, not the public API's `{address}` and `{placementTestID}`.

- `GET /me`: current user.
- `GET|POST /workspaces`, `PATCH|DELETE /workspaces/{workspaceID}`: full workspace lifecycle, including update and delete, which the public API lacks.
- `GET|POST /workspaces/{workspaceID}/admin/users`, `DELETE .../admin/users/{userID}`, `POST .../admin/users/invite`: workspace membership.
- `POST /workspaces/{workspaceID}/validate-invitation`, `POST .../complete-invitation`: invitation acceptance. These two declare no security and are the public halves of the invite flow.
- `GET|PUT /workspaces/{workspaceID}/billing/warmup`: read and change the warmup subscription (slot count).
- `GET|PUT /workspaces/{workspaceID}/billing/placement-tests`: read and change the placement test subscription.
- `POST /workspaces/{workspaceID}/billing/portal`: get a subscription portal link.
- `GET /workspaces/{workspaceID}/mailboxes`, `GET|PATCH|DELETE .../mailboxes/{mailboxID}`: mailbox CRUD by ID.
- `POST /workspaces/{workspaceID}/mailboxes/add/smtp`, `.../add/bulk-smtp`, `.../add/oauth2/{provider}`, `.../add/test-smtp`: connect one or many SMTP mailboxes, connect OAuth2 by provider, and test SMTP credentials before saving.
- `POST /workspaces/{workspaceID}/mailboxes/check-health`, `POST .../mailboxes/{mailboxID}/check-health`: trigger a health re-check, which has no public equivalent.
- `PUT /workspaces/{workspaceID}/mailboxes/{mailboxID}/dkim`: trigger a DKIM check.
- `PUT /workspaces/{workspaceID}/mailboxes/{mailboxID}/reconnect`, `PUT .../mailboxes/reconnect`: reconnect one or many mailboxes after access loss.
- `POST /workspaces/{workspaceID}/mailboxes/bulk-update`, `POST .../mailboxes/bulk-delete`: bulk settings change and bulk delete.
- `GET /workspaces/{workspaceID}/mailboxes/count`, `GET .../mailboxes/status-counts`: counts for dashboards.
- `GET /workspaces/{workspaceID}/mailboxes/warmup-codes`: warmup codes used to verify warmup mail.
- `GET /workspaces/{workspaceID}/mailboxes/{mailboxID}/warmup-stats`: warmup stats by mailbox ID.
- `GET|PUT /workspaces/{workspaceID}/notification-preferences`: alerting preferences.
- `GET|POST /workspaces/{workspaceID}/placement-tests`, `GET|PATCH|DELETE .../placement-tests/{mailboxPlacementTestGroupID}`: placement test groups, including update.
- `GET /workspaces/{workspaceID}/placement-tests/{mailboxPlacementTestGroupID}/tests`, `.../tests/{mailboxPlacementTestID}`, `.../tests/count`: individual tests inside a group.
- `POST /workspaces/{workspaceID}/placement-tests/bulk-delete`, `GET .../placement-tests/count`: bulk delete and count.
- `POST /workspaces/{workspaceID}/placement-tests/generate-copy`: generate placement test subject and body copy.

## Source URLs checked

- https://api.warmforge.ai/public/swagger/doc.json: full public spec, 15 operations. Primary source.
- https://api.warmforge.ai/swagger/doc.json: app API spec, 50 operations across 37 paths. Appendix source.
- https://developer.salesforge.ai/authentication.md: raw key, no `Bearer` prefix, 401 and 403 meanings. Content confirmed.
- https://developer.salesforge.ai/overview/workspace.md and https://developer.salesforge.ai/overview/mailbox.md: shared workspace and mailbox concepts. Content confirmed.
- https://developer.salesforge.ai/llms.txt: confirms Salesforge OAuth mailbox links auto-provision the mailbox in Warmforge.
- https://www.warmforge.ai/blog/warmforge-api: key creation path, `Bearer` header example, `wf_live_` key shape, rate limits undocumented, workflow patterns. Content confirmed.
- https://www.warmforge.ai/: Heat Score, placement tests, warmup pool. Content confirmed.
- https://github.com/SalesforgeAI/forge-mcp: per-product keys, `app.warmforge.ai > Settings > API`, 15 Warmforge tools. Content confirmed.
- https://help.warmforge.ai/: does not resolve (DNS).
- help.salesforge.ai search for Warmforge API: no matching articles.
