# Salesforge Multichannel API (Sequencing V2)

Email + LinkedIn sequences as a DAG. Sender profiles, LinkedIn accounts, nodes, branches, enrollments, validation runs, subsequences.

## Header

- Base URL: `https://multichannel-api.salesforge.ai/public`
- Every path in this file starts with `/multichannel/...`, so a full URL looks like
  `https://multichannel-api.salesforge.ai/public/multichannel/workspaces/$WORKSPACE_ID/sequences`
- Auth header: `Authorization: $SALESFORGE_API_KEY`. Send the raw key. The docs say: "Send the raw API key in the `Authorization` header. Do not add a `Bearer ` prefix." Multichannel endpoints additionally accept `Bearer <key>`, but Salesforge core does not, so always send raw and the same call style works on both services.
- Same key as the Salesforge core API (`https://api.salesforge.ai/public/v2`). Docs: "Salesforge public API endpoints and multichannel sequencing endpoints use the same Salesforge API key."
- Content type: `Content-Type: application/json` on every request with a body. Responses are JSON.
- Spec: `https://multichannel-api.salesforge.ai/public/multichannel/swagger/doc.json` (OpenAPI 3.1.0), security scheme `ApiKeyAuth` = apiKey in header `Authorization`.

Skeleton call:

```bash
curl -sS -X POST "https://multichannel-api.salesforge.ai/public/multichannel/workspaces/$WORKSPACE_ID/sequences" \
  -H "Authorization: $SALESFORGE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name":"Q3 outbound","timezone":"America/New_York"}'
```

## Conventions

- Pagination: query `page` (integer, min 1) and `limit` (integer, 1-100). List responses carry a sibling `pagination` object: `{page, limit, total, totalPages, hasNext}`. Subsequence members default to page 1, limit 100.
- Response envelope: none. Successful bodies are the resource itself or a named collection key (`actions`, `conditions`, `profiles`, `sequences`, `nodes`, `branches`, `members`, `parents`, `triggers`, `results`) plus `pagination` where paged.
- Error body: `{"message": string, "data": object|null}`. `message` is human text for generic failures and a stable machine code for the documented cases below. `data` shape depends on the code.
- Stable error codes to branch on: `preflight_stale` (409), `validation_run_not_completed` (409), `validation_run_failed` (409), `validation_run_selection_empty` (400), `enrollment_confirmation_busy` (423), `insufficient remaining active credits balance` (422), `validation-all-contacts-excluded` (400, in `data.code`), `validation-scope-empty` (400, in `data.code`).
- Status codes: 200 OK, 201 Created (creates, plus preflight confirm returns 200 not 201), 204 No Content (deletes, disconnect, remove enrollments, deactivate magic link), 400 bad request, 401 missing or invalid key, 403 key valid but out of scope, 404 not found or expired preflight, 402 insufficient credits (LinkedIn connect/reconnect, validation start), 409 conflict (stale preflight, validation run not ready, LinkedIn account already attached, LinkedIn checkpoint conflict), 422 account contact limit, 423 another enrollment confirmation in flight.
- ID formats:
  - `workspaceID`: string (UUID) in the path.
  - `sequenceID`, `nodeID`, `senderProfileID`, `linkedinAccountID`, `subsequenceID`, `branchId`, `actionId`, `conditionId`: integers.
  - `leadIds` / contact IDs, `mailboxIds`, `labelId`, `validationRunId`, `preflightID`, magic-link `token`: strings.
- Timestamps are RFC 3339 strings. Analytics date params are `YYYY-MM-DD`.
- Timezones accept IANA names only, for example `America/New_York`.
- Rate limits: not documented. No 429 appears in the spec and no limit is published. Add your own backoff.

## Endpoint catalog

### Catalogs (workspace-independent)

| Endpoint | Purpose |
| --- | --- |
| `GET /multichannel/actions` | List the action catalog. Query: `channel` (`email`\|`linkedin`), `name`, `page`, `limit`. Returns `actions[]` of `{id, name, channel, branchingType, description}`. Resolve `id` by `name`, never hardcode. |
| `GET /multichannel/conditions` | List the condition catalog. Same query params. Returns `conditions[]` of `{id, name, channel, branchingType, description}`. |

### LinkedIn magic links

Use these to let a person connect their own LinkedIn account without handing credentials to your integration.

| Endpoint | Purpose |
| --- | --- |
| `GET /multichannel/workspaces/{workspaceID}/linkedin-magic-links` | Return the active magic link, or null when none exists. Returns `{id, token, url, expiresAt}`. |
| `POST /multichannel/workspaces/{workspaceID}/linkedin-magic-links` | Create a magic link and replace any active one. No body. 201 with `{id, token, url, expiresAt}`. Links expire after 7 days. Share `url`. |
| `DELETE /multichannel/workspaces/{workspaceID}/linkedin-magic-links/{token}` | Deactivate a link. 204. |
| `POST /multichannel/workspaces/{workspaceID}/linkedin-magic-links/{token}/extend` | Extend expiry by 7 days from now. Returns the link object. |

### LinkedIn accounts

| Endpoint | Purpose |
| --- | --- |
| `POST /multichannel/workspaces/{workspaceID}/linkedin/accounts` | Connect an account with credentials. Body `requests.ConnectLinkedinAccountRequest`. 201 with the account. 402 when credits are short, 409 on conflict. |
| `GET /multichannel/workspaces/{workspaceID}/linkedin/accounts/{linkedinAccountID}` | Read current state. Poll this while waiting on OTP. |
| `POST /.../linkedin/accounts/{linkedinAccountID}/otp` | Submit the 2FA code. Body `{"code": "123456"}`, 4-10 chars, required. Returns the account. |
| `POST /.../linkedin/accounts/{linkedinAccountID}/reconnect` | Reconnect with new credentials, preserving ID, limits, history and sender-profile link. Body `requests.ReconnectLinkedinAccountRequest`. Complete any returned checkpoint through the same OTP endpoint. |
| `POST /.../linkedin/accounts/{linkedinAccountID}/disconnect` | Remove the provider connection, keep the local account, history and sender-profile association. 204. Repeated disconnects succeed. |

Connect body fields:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `email` | string | yes | LinkedIn login email. |
| `password` | string | yes | LinkedIn login password. |
| `firstName`, `lastName` | string | no | Recorded on the account. |
| `linkedinUrl` | string | no | Public profile URL. |
| `skipSenderProfile` | boolean | no | Default false, which auto-creates a draft sender profile linked to the account. Set true to connect standalone, then attach via `POST /sender-profiles` or `PATCH /sender-profiles/{id}` with `linkedinAccountId`. |
| `proxy` | object | no | `{host (required, min 1), port (required, int), username, password}`. Host with an explicit scheme such as `socks5://` selects the protocol, otherwise http. Recommended for account stability. |

Reconnect body: `password` required; `email` optional but must match the existing account when supplied; `firstName`, `lastName`, `proxy` optional.

Account response fields to act on: `id`, `state`, `status`, `isConnected`, `requires2fa`, `checkpoint {type, data, publicKey}`, plus profile data `firstName`, `lastName`, `linkedinUrl`, `profilePictureUrl`, `premiumType`.

### Sender profiles

| Endpoint | Purpose |
| --- | --- |
| `GET /multichannel/workspaces/{workspaceID}/sender-profiles` | List profiles. Query `page`, `limit`. Returns `profiles[]` + `pagination`. |
| `POST /multichannel/workspaces/{workspaceID}/sender-profiles` | Create one profile. Body `{name (required), mailboxIds[] (strings), linkedinAccountId (int)}`. 201. A profile with no sender attached is created in `draft` status. 404 when the LinkedIn account is not in the workspace, 409 when it is already attached elsewhere. |
| `POST /multichannel/workspaces/{workspaceID}/sender-profiles/bulk` | Create up to 100 profiles. Body `{profiles: [CreateSenderProfileEntry]}` with 1-100 entries. 201 with `results[]` of `{index, profile?, error?}`, one per entry in request order. Entries apply independently, so a failure does not block the rest. |
| `PATCH /multichannel/workspaces/{workspaceID}/sender-profiles/{senderProfileID}` | Update `name`, `mailboxIds`, or attach `linkedinAccountId` to an unlinked profile. Repeating the same account ID succeeds. Replacing a different account returns 409. Omitted or null `linkedinAccountId` and omitted `mailboxIds` leave associations unchanged. |
| `DELETE /multichannel/workspaces/{workspaceID}/sender-profiles/{senderProfileID}` | Delete a profile. 204. |

Profile response: `{id, name, status, mailboxes: [{id, address}], linkedinAccount: {id, name, linkedinUrl, profilePictureUrl, premium, status}}`.

### Sequences

| Endpoint | Purpose |
| --- | --- |
| `GET /multichannel/workspaces/{workspaceID}/sequences` | List sequences. Query `page`, `limit`, `status` (`draft`\|`active`\|`completed`\|`paused`). Each item carries `analytics`, `schedule`, `settings`, `senderProfiles[]`. |
| `POST /multichannel/workspaces/{workspaceID}/sequences` | Create a sequence. Body `{name (required), description, timezone (IANA), kind (primary\|subsequence)}`. 201 with `{id, name, description, status, timezone, kind}`. Status starts as `draft` and the root node is created for you. |
| `GET /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}` | Full detail: `{sequence, nodes[], branches[], activeEnrollmentCount, completedLeadCount, totalLeadCount}`. Use this to inspect the graph in one call. |
| `PATCH /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}` | Update `name`, `description`, `timezone`. Returns the full sequence. |
| `DELETE /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}` | Delete the sequence. 204. |
| `PATCH /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/launch` | Launch. No body. Returns the sequence with `status: "active"` and `launchedAt` set. |
| `PATCH /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/status` | Pause or resume. Body `{"status": "active"\|"paused"}`. Returns the full sequence. |
| `GET /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/analytics` | Per-day and aggregate email metrics. Query `from_date` (required, `YYYY-MM-DD`), `to_date` (required), `timezone` (IANA, default UTC). Returns `{from_date, to_date, timezone, days: {"YYYY-MM-DD": day}, stats}`. Open and click metrics are zero when those tracking modes are off. |
| `GET /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/schedule` | Read `{timezone, schedule}`. |
| `PUT /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/schedule` | Replace the schedule. Body `{timezone (required), schedule (required)}`, both required. Per day `{enabled, from, to}` with hours 0-23 and `to` greater than `from`. |
| `GET /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/settings` | Read all settings fields. |
| `PATCH /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/settings` | Partial update. Send only the fields you change. |
| `GET /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/branches` | List branches. Query `page`, `limit`. Returns `branches[]` of `{id, name, description, fromNodeId, toNodeId, analytics {count, percentage}}`. |
| `GET /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/sender-profiles` | List profiles assigned to this sequence, paged. |
| `POST /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/sender-profiles` | Assign profiles. Body `{"senderProfileIds": [int]}`, at least 1. Returns `{senderProfileIds[], counts {senderProfiles, uniqueMailboxes, linkedinAccounts}}`. |
| `POST /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/sender-profiles/remove` | Unassign profiles. Body `{"senderProfileIds": [int]}`, 1-50 IDs. Same response shape. |

Settings fields (all optional on PATCH): `openTrackingEnabled`, `clickTrackingEnabled`, `plainTextEmailsEnabled`, `ccAndBccEnabled`, `cc`, `bcc`, `optOutTextEnabled`, `optOutText`, `optOutLinkEnabled`, `optOutLinkText`, `localizedOptOutEnabled`, `pauseOnOpen`, `pauseOnClick`, `trackOpportunitiesEnabled`, `opportunitiesValue`, `companyOutreachLimitEnabled`, `companyOutreachLimitCount`, `sequentialCompanySendingEnabled`, `taskPriorityPolicy`.

Sequence analytics object (on list, detail, launch, status): `emails {sent, contacted, opened, clicked, replied, bounced, optOuted, *Percent, conversion}`, `linkedinMessages {sent, contacted, replied, conversion}`, `connectionRequests {sent, accepted, conversion}`, `contacts {total, inProgress, completed, failed}`, `positiveReplies {email, linkedin, conversion}`, `uniqueContacted`, `uniqueReplied`, `replyRate`, `progressPercentage`, `actionCounts` (map name to count), `goalsAchievedCount`, `opportunitiesCount`, `totalOpportunitiesValue`, `computedAt`.

### Nodes

| Endpoint | Purpose |
| --- | --- |
| `GET /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/nodes` | List nodes. Query `type` (`action`\|`condition`\|`root`\|`terminal`), `channel` (`email`\|`linkedin`\|`inmail`), `name`, `page`, `limit`. |
| `GET /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/nodes/{nodeID}` | Read one node with its branches and variants. |
| `POST /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/nodes/actions` | Create an action node on a branch. Body `requests.CreateActionNodeRequest`. 201 with the node. |
| `PATCH /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/nodes/actions/{nodeID}` | Update an action node. Body `{distributionStrategy, variants[], wait_in_minutes}`. Note the snake_case wait field. |
| `POST /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/nodes/conditions` | Create a condition node on a branch. Body `requests.CreateConditionNodeRequest`. 201 with the node and its `yes`/`no` branches. |
| `DELETE /multichannel/workspaces/{workspaceID}/sequences/{sequenceID}/nodes/{nodeID}` | Delete a node. 204. |

Create action node body:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `branchId` | integer | yes | Branch to attach to. Its `toNodeId` becomes the new node. |
| `actionId` | integer | yes | From `GET /multichannel/actions`. |
| `waitDays` | integer, min 0 | no | Days to wait before running this action. |
| `distributionStrategy` | `equal`\|`custom` | no | How variant traffic splits. |
| `variants` | array | no | See variant shape below. |

Create condition node body:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `branchId` | integer | yes | Branch to attach to. |
| `conditionId` | integer | yes | From `GET /multichannel/conditions`. |
| `minutesToWait` | integer | no | Evaluation window in minutes, not days. |
| `distributionStrategy` | `equal`\|`custom` | no | |
| `metadata` | object | no | `{allowedValidationStatuses: [string]}`, camelCase here. |

Variant shape (`requests.UpdateNodeVariantRequest`, used on both create and update):

```json
{
  "id": 0,
  "isEnabled": true,
  "exposureInPercentage": 100,
  "metadata": {
    "name": "Variant A",
    "subject": "Quick intro for {{company}}",
    "message": "Hi {{first_name}} ...",
    "allowed_validation_statuses": ["safe", "catch_all"]
  }
}
```

`exposureInPercentage` is 0-100. Omit `id` when creating, send it to update an existing variant. Request metadata uses `allowed_validation_statuses` (snake_case); the response returns `allowedValidationStatuses` (camelCase) plus `contentSource` (`api`\|`tiptap`\|`agent`). Set `subject` to `""` for LinkedIn actions.

Node response: `{id, sequenceId, type, actionId, conditionId, distributionStrategy, waitInMinutes, waitType, branches[], variants[], analytics {active, completed, failed, endValue}}`.

### Enrollments

| Endpoint | Purpose |
| --- | --- |
| `POST /.../sequences/{sequenceID}/enrollments` | **Deprecated.** Enrolls matching contacts immediately with no conflict review. Replacement: the preflight then confirm pair below. Body `{filters, limit}`. 201 with `{leadIds[], skippedLeads: {leadId: reason}}`. |
| `POST /.../sequences/{sequenceID}/enrollments/preflight` | Analyze candidates and create a preflight that expires after 15 minutes. Body `{filters, limit, selectionScope}`. 200 with the preflight. |
| `POST /.../sequences/{sequenceID}/enrollments/preflight/{preflightID}/move-preview` | Project a move without changing anything. Body `{moveSourceSequenceIds[], skipReplied (required)}`. 200 with `{summary, skipBreakdown {repliedCount, unselectedSourceCount}}`. |
| `POST /.../sequences/{sequenceID}/enrollments/preflight/{preflightID}/confirm` | Apply the decision. Body `{action (required), moveSourceSequenceIds[], skipReplied}`. 200 with `{enrolledLeadIds[], summary}`. |
| `POST /.../sequences/{sequenceID}/enrollments/remove` | Remove matching contacts from the sequence. Body `{filters, limit}`. 204. No preflight needed. |

Preflight response: `{preflightId, expiresAt, summary {candidateCount, decisionRequiredCount, automaticEnrollmentCount, alreadyInTargetCount}, moveGroups: [{sequenceId, sequenceName, sequenceStatus, selectedContactCount}], repliedDecision {contactCount}}`.

Confirm/preview summary: `{enrolledCount, skippedCount, sourceCleanupCount, alreadyInTargetCount}`.

Contact filters (`filters`, shared by preflight, add, and remove):

`leadIds[]`, `notInLeadIds[]`, `tagIds[]`, `notInTagIds[]`, `esps[]`, `notInESPs[]`, `customVars[]`, `notInCustomVars[]`, `customVarIds[]`, `notInCustomVarIds[]`, `searchQuery`, `validationStatuses[]`, `validationRunId`, `excludeContacted`, `hasValidLinkedIn`, `hasEmail`. Supply at least one filter or a `limit` above zero. `leadIds` is intersected with `validationRunId` when both are present.

### Subsequences

| Endpoint | Purpose |
| --- | --- |
| `POST /.../sequences/{sequenceID}/subsequence-assignments` | Attach a subsequence to this parent sequence. Body `{childSequenceId (required, int), priority (int)}`. 201 with `{id, parentSequenceId, childSequenceId, priority}`. |
| `GET /multichannel/workspaces/{workspaceID}/subsequences/{subsequenceID}/parents` | Every active parent assignment. Returns `parents[]` of `{id, parentSequenceId, childSequenceId, priority, parentSequence {id, name, status, kind}}`. |
| `GET /multichannel/workspaces/{workspaceID}/subsequences/{subsequenceID}/triggers` | List triggers. Returns `triggers[]` of `{id, childSequenceId, labelId, priority, triggerType}`. |
| `POST /multichannel/workspaces/{workspaceID}/subsequences/{subsequenceID}/triggers` | Create a trigger. Body `{labelId (required, string), priority (int)}`. The label is a Primebox thread label such as Positive, Meeting Booked, Out of Office. |
| `GET /multichannel/workspaces/{workspaceID}/subsequences/{subsequenceID}/members` | Current members with handoff data. Query `leadId` (check one contact without changing state), `page`, `limit` (default 100, max 100). Returns `members[]` of `{leadId, sequenceLeadId, parentSequenceId, status, enrolledAt, handoffId, handoffState, childOutreachStartedAt}`. |

### Validation runs

| Endpoint | Purpose |
| --- | --- |
| `POST /multichannel/workspaces/{workspaceID}/validations` | Start email validation for the contacts the filters resolve to. Body `{filters (required), limit, strict}`. 201 with `{validationJobID, started, matched, selected, skipped {duplicate}, message}`. 402 on insufficient credits. |
| `GET /multichannel/workspaces/{workspaceID}/validations/{runID}/results` | Results. Returns `{totals {totalSelected, totalValidated, byStatus {...}}, summary}` where `summary` maps each ESP name to the same per-status count object. |

Validation filters (`requests.ValidationFiltersRequest`, a superset of enrollment filters minus the validation-run keys): `leadIds[]`, `notInLeadIds[]`, `tagIds[]`, `notInTagIds[]`, `esps[]`, `notInESPs[]`, `customVars[]`, `notInCustomVars[]`, `customVarIds[]`, `notInCustomVarIds[]`, `searchQuery`, `validationStatuses[]`, `excludeContacted`, `hasValidLinkedIn`, `hasEmail`, `withEmailOnly`, `deleted`, `selectionScope`, `numberOfContactsToAdd`.

`strict` defaults to true, which fails with 400 `validation-all-contacts-excluded` when filters match contacts but every one is excluded before validation. Send `"strict": false` to get a 201 with an already completed empty run (`started: false`, `selected: 0`, `message` explaining why). A scope that resolves to no contact with an email address returns 400 `validation-scope-empty` either way.

## Node graph model

- Every sequence is a DAG with exactly one `root` node, created automatically when you create the sequence. You never create it.
- **Nodes** carry the work: `root`, `action`, `condition`, `terminal`.
- **Branches** are the edges: `{id, name, description, fromNodeId, toNodeId}`. A branch with `toNodeId` empty is an open slot, and leaving it empty ends that path (a terminal end state).
- You never pass a parent node ID. You pass a `branchId`, and the API wires that branch's `toNodeId` to the node it creates, then creates the new node's own outgoing branches.
- An action node emits one outgoing branch. A condition node emits two, named `yes` and `no`. Read the names off `GET .../branches` or off the create response's `branches[]`; do not assume ordering.
- Build order: create sequence, `GET .../branches` to find the root branch (the one whose `fromNodeId` is the root node and whose `toNodeId` is empty), create a node on it, re-list branches, create the next node on one of the new branches, repeat.
- Wait and delay semantics:
  - Action node create: `waitDays`, integer, minimum 0, days to wait before running the action.
  - Action node update: `wait_in_minutes`, integer, minutes. Different field, different unit, snake_case.
  - Condition node create: `minutesToWait`, integer, the evaluation window.
  - All nodes report `waitInMinutes` and `waitType` in responses.
  - Waits are consumed inside the sequence schedule windows and timezone, so a 1-day wait does not fire outside the configured hours.
- `distributionStrategy` controls variant traffic. `equal` splits evenly across enabled variants; `custom` honors each variant's `exposureInPercentage`, which you should make sum to 100.

### Action types

Resolve every ID from `GET /multichannel/actions?channel=...`. Names confirmed by the docs:

- Email: `send_email`.
- LinkedIn: `li_connection_request`, `li_send_message`, `li_send_inmail`, `li_view_profile`, `li_withdraw_connection_request`, `li_like_latest_post`, `li_follow_profile`.

Config per action lives in `variants[].metadata`: `name` (label for the step), `subject` (email only; send `""` for LinkedIn), `message` (body, supports `{{first_name}}`, `{{company}}`, and custom vars such as `{{segment}}`), `allowed_validation_statuses` (gate the step on the contact's email validation status). Profile-only actions such as `li_view_profile` and `li_follow_profile` need no message content.

### Condition types

Resolve every ID from `GET /multichannel/conditions`. Names confirmed by the docs:

- `has_linkedin_url`, `has_email_address`, `li_is_already_connected`, `li_contact_replied_within_days`, `request_accepted_within_days`, `check_email_validation_status`.

Config: `minutesToWait` sets the window for the time-bounded conditions (`*_within_days`, `request_accepted_within_days`), and `metadata.allowedValidationStatuses` sets the passing set for `check_email_validation_status`. The catalog's `branchingType` tells you how many branches a condition produces; the two-way ones produce `yes` and `no`.

### Worked example: email plus LinkedIn tree

Goal: route contacts by LinkedIn availability, send a LinkedIn message to those who have a profile, and an email one day later to those who do not.

```bash
BASE=https://multichannel-api.salesforge.ai/public/multichannel
H=(-H "Authorization: $SALESFORGE_API_KEY" -H "Content-Type: application/json")

# 1. Resolve catalog IDs.
curl -sS "${H[@]}" "$BASE/actions?channel=linkedin&name=li_send_message"   # -> actions[0].id = 31
curl -sS "${H[@]}" "$BASE/actions?channel=email&name=send_email"           # -> actions[0].id = 14
curl -sS "${H[@]}" "$BASE/conditions?name=has_linkedin_url"                # -> conditions[0].id = 12

# 2. Create the sequence. The root node comes with it.
curl -sS -X POST "${H[@]}" "$BASE/workspaces/$WORKSPACE_ID/sequences" \
  -d '{"name":"LinkedIn then email","description":"Route by channel availability","timezone":"America/New_York","kind":"primary"}'
# -> {"id": 900, "status": "draft", ...}

# 3. Find the open root branch.
curl -sS "${H[@]}" "$BASE/workspaces/$WORKSPACE_ID/sequences/900/branches"
# -> branches[0] = {"id": 1001, "fromNodeId": 5000, "toNodeId": null, "name": "next"}
```

Create the condition node on branch 1001:

```json
{
  "branchId": 1001,
  "conditionId": 12,
  "minutesToWait": 0,
  "distributionStrategy": "equal"
}
```

Re-list branches. The condition node now owns two: `yes` (id 2001) and `no` (id 2002). Create the LinkedIn action on `yes`:

```json
{
  "branchId": 2001,
  "actionId": 31,
  "waitDays": 0,
  "distributionStrategy": "equal",
  "variants": [
    {
      "isEnabled": true,
      "exposureInPercentage": 100,
      "metadata": {
        "name": "LinkedIn intro",
        "subject": "",
        "message": "Hi {{first_name}}, I work with {{segment}} teams on multichannel outbound. Open to a short conversation?"
      }
    }
  ]
}
```

Create the email action on `no`:

```json
{
  "branchId": 2002,
  "actionId": 14,
  "waitDays": 1,
  "distributionStrategy": "equal",
  "variants": [
    {
      "isEnabled": true,
      "exposureInPercentage": 100,
      "metadata": {
        "name": "Email follow-up",
        "subject": "Quick intro for {{company}}",
        "message": "Hi {{first_name}}, here is a simple way {{segment}} teams run multichannel workflows in one system.",
        "allowed_validation_statuses": ["safe", "catch_all"]
      }
    }
  ]
}
```

Leave the two new downstream branches unwired to end both paths, or extend them with further nodes.

## Enumerations

- Channel (`actions`, `conditions` query): `email`, `linkedin`.
- Channel (`nodes` query): `email`, `linkedin`, `inmail`.
- Node type: `action`, `condition`, `root`, `terminal`.
- Sequence status (query and `status` field): `draft`, `active`, `completed`, `paused`.
- Sequence status update body: `active`, `paused` only. Reach `active` the first time through launch, not through this endpoint.
- Sequence kind: `primary`, `subsequence`.
- Sender profile status: `draft`, `active`.
- LinkedIn connection state (caller-facing): `connected`, `awaiting_otp`, `pending`, `failed`. The docs name these Connected, Awaiting OTP, Pending, Failed; the raw `status` field carries a wider internal set, so branch on `state`, `isConnected`, and `requires2fa`.
- Distribution strategy: `equal`, `custom`.
- Content source (response only): `api`, `tiptap`, `agent`.
- Email validation status (filters and `allowed_validation_statuses`): `safe`, `invalid`, `disabled`, `disposable`, `inbox_full`, `catch_all`, `role_account`, `spamtrap`, `unknown`, `unvalidated`, `linkedin_only`.
- Validation results `byStatus` keys use `spam_trap` with an underscore while the filter enum uses `spamtrap`. Map between them.
- Preflight selection scope: `all` (default), `in_sequence`, `not_in_sequence`.
  - `in_sequence`: contacts with any draft-sequence enrollment, or an enrollment whose status is `active`, `paused`, `out_of_office`, `failed`, `company_limit_reached`, or `replied`.
  - `not_in_sequence`: everyone else, including contacts whose only enrollments are `completed`, `dnc`, `unsubscribed`, or `bounced`, unless one of those belongs to a draft sequence.
- Preflight confirm action: `skip`, `move`.
- Validation run status (409 `data.status`): `pending`, `in_progress`, `failed`.
- Contact lifecycle outcomes (docs, reported on enrollments): `active`, `paused`, `completed`, `failed`, `replied`, `out_of_office`, `unsubscribed`, `dnc`, `bounced`, `bounce_shield`. Only `active` and `paused` are in progress; the rest are terminal.

## Workflows

### Connect a LinkedIn account with credentials

1. `POST /multichannel/workspaces/{workspaceID}/linkedin/accounts` with `email`, `password`, and a `proxy` when you have one. Add `"skipSenderProfile": true` if you plan to attach the account to an existing profile instead of getting an auto-created draft one.
2. Read the 201 body. When `requires2fa` is false and `isConnected` is true, you are done.
3. When `requires2fa` is true, read `checkpoint.type` and collect the code from the account owner.
4. `POST /.../linkedin/accounts/{linkedinAccountID}/otp` with `{"code": "123456"}`.
5. Poll `GET /.../linkedin/accounts/{linkedinAccountID}` until `state` is `connected` or `failed`. Keep polling while it is `pending` or `awaiting_otp`.
6. On a later expiry, call `POST /.../reconnect` with the new password, then complete any returned checkpoint through the same OTP endpoint from step 4.

### Connect a LinkedIn account with a magic link

1. `POST /multichannel/workspaces/{workspaceID}/linkedin-magic-links`. This replaces any active link.
2. Share the returned `url` with the account owner. It is valid for 7 days.
3. `POST /.../linkedin-magic-links/{token}/extend` to add another 7 days, or `DELETE /.../linkedin-magic-links/{token}` to revoke.
4. `GET /multichannel/workspaces/{workspaceID}/sender-profiles` to pick up the profile that appears once the owner finishes.

### Create sender profiles

1. Confirm the mailboxes exist in the workspace (Salesforge core: `GET /workspaces/{workspaceID}/mailboxes`).
2. Connect the LinkedIn account first if the profile needs one, because `linkedinAccountId` must reference an already-connected account.
3. `POST /multichannel/workspaces/{workspaceID}/sender-profiles` with `name`, `mailboxIds`, `linkedinAccountId`. Use `/sender-profiles/bulk` for up to 100 at once and read per-entry `results[]`.
4. `PATCH /multichannel/workspaces/{workspaceID}/sender-profiles/{senderProfileID}` later to rename, swap mailboxes, or attach a LinkedIn account to a profile that has none.

### Build and launch a multichannel sequence

1. `GET /multichannel/actions` and `GET /multichannel/conditions`. Resolve IDs by `name`.
2. `POST /multichannel/workspaces/{workspaceID}/sequences`. Store the `id`.
3. `PUT /.../sequences/{sequenceID}/schedule` with an explicit `timezone` and per-day windows.
4. `PATCH /.../sequences/{sequenceID}/settings` for tracking, opt-out, CC/BCC, and opportunity fields.
5. `POST /.../sequences/{sequenceID}/sender-profiles` with `{"senderProfileIds": [...]}`.
6. `GET /.../sequences/{sequenceID}/branches` to get the open root branch.
7. `POST /.../nodes/conditions` or `POST /.../nodes/actions` on that branch.
8. `GET /.../branches` again, then repeat step 7 on the new branch IDs until the tree is complete.
9. `GET /.../sequences/{sequenceID}` and verify `status` is `draft`, `senderProfiles` is right, and nodes and branches are wired as intended.
10. Enroll contacts (next workflow).
11. `PATCH /.../sequences/{sequenceID}/launch`. Confirm `status` is `active`.
12. Operate with `PATCH /.../status` to pause or resume, `POST /.../enrollments/remove` to drop contacts, `GET /.../analytics` for metrics.

### Enroll contacts through validation, preflight, and confirm

1. Optional. `POST /multichannel/workspaces/{workspaceID}/validations` with `{filters, limit, strict}`. Validation is email only, so keep LinkedIn-only contacts out of the run and bring them in through a separate enrollment filter. Store `validationJobID`.
2. Poll `GET /multichannel/workspaces/{workspaceID}/validations/{runID}/results` until the run is complete. You cannot use a pending, in-progress, or failed run.
3. `POST /.../sequences/{sequenceID}/enrollments/preflight` with `{filters: {leadIds: [...]} or {validationRunId: "..."}, limit, selectionScope}`. Store `preflightId` and `expiresAt`.
4. Read `summary`. When `decisionRequiredCount` is 0, jump to the skip confirm in step 7.
5. When contacts need a decision, choose:
   - **Skip**: enroll only the contacts that need no decision and leave the rest in their current sequences.
   - **Move**: enroll eligible contacts here and clean their source enrollments. Select every `moveGroups[].sequenceId` that a contact belongs to; a contact in an unselected required group is skipped.
6. Optional. `POST /.../enrollments/preflight/{preflightID}/move-preview` with `{moveSourceSequenceIds, skipReplied}` to see projected counts without changing anything.
7. `POST /.../enrollments/preflight/{preflightID}/confirm` with `{"action": "skip"}`, or `{"action": "move", "moveSourceSequenceIds": [42], "skipReplied": true}`. `skipReplied` is required for `move` and ignored for `skip`.
8. Handle the failure modes: 409 `preflight_stale` hands you a fresh preflight in `data`, so review it and retry with `data.preflightId`. 404 means the preflight expired past its 15 minute window, so create a new one with the same selection. 409 `validation_run_not_completed` means wait, 409 `validation_run_failed` means start another run, 400 `validation_run_selection_empty` means change the selection. 422 means the account contact limit would be exceeded. 423 `enrollment_confirmation_busy` means another confirmation is running, so retry after it finishes.
9. On move, each selected source enrollment in a draft sequence is deleted and every other selected source enrollment is set to `completed` with its pending steps canceled.

### Set up a subsequence

1. `POST /multichannel/workspaces/{workspaceID}/sequences` with `"kind": "subsequence"`. Build its graph exactly like a primary sequence.
2. `POST /.../sequences/{parentSequenceID}/subsequence-assignments` with `{"childSequenceId": <subsequence id>, "priority": 1}`.
3. `POST /multichannel/workspaces/{workspaceID}/subsequences/{subsequenceID}/triggers` with `{"labelId": "<primebox label id>", "priority": 1}`. The trigger fires when a thread gets that label.
4. `GET /.../subsequences/{subsequenceID}/parents` and `/triggers` to verify wiring.
5. `GET /.../subsequences/{subsequenceID}/members` to watch handoffs. Pass `leadId` to check one contact without changing state.

## Gotchas

1. **Launch locks the graph.** After launch you cannot create nodes, delete nodes, or rewire branches. Schedule updates, settings and metadata updates, sender-profile assignment, and new enrollments all stay available. Build the whole tree before you launch.
2. **The create-sequence body in the tutorial does not match the spec.** The tutorial posts a `settings` object inside `POST /sequences`, but `requests.CreateSequenceRequest` only defines `name`, `description`, `timezone`, and `kind`. Create the sequence, then `PATCH /.../settings`.
3. **Wait fields disagree across verbs.** Create an action node with `waitDays` (days, camelCase). Update the same node with `wait_in_minutes` (minutes, snake_case). Read it back as `waitInMinutes`. Condition nodes use `minutesToWait` on create.
4. **Variant metadata casing flips between request and response.** Send `allowed_validation_statuses`; read `allowedValidationStatuses`. Condition node metadata uses camelCase `allowedValidationStatuses` on the request too.
5. **`enrolledCount` is not the contactable count.** Contacts suppressed elsewhere by do-not-contact, unsubscribe, or bounce shield are enrolled carrying that status, are never contacted, and still appear in `enrolledLeadIds` and `enrolledCount` with no field distinguishing them.
6. **Preflights expire in 15 minutes and go stale on any enrollment change.** A stale preflight returns 409 with a replacement in `data`, and an expired one returns 404. Do not cache a `preflightId` across a long workflow.
7. **`moveGroups[].selectedContactCount` overlaps across groups.** A contact can appear in several groups, so never sum the field. Select every group a contact belongs to or that contact gets skipped.
8. **Branch names are data, not positions.** Read `yes` and `no` off the branch list rather than assuming index order, and re-list branches after every node creation because new branch IDs only exist after the API creates them.
9. **`espMatchingEnabled` is in the public settings model per the docs but is absent from `requests.UpdateSequenceSettingsRequest`, and it can be plan-gated.** Leave it out unless you know the workspace supports it.
10. **Validation is email only.** LinkedIn-only contacts cannot go through a validation run. Enroll them with a separate filter such as `hasValidLinkedIn`.
11. **`strict` defaults to true on validation start,** which turns a fully-excluded selection into a 400. Send `"strict": false` when you want a completed empty run instead.
12. **Ordering constraints before launch:** connect the LinkedIn account before creating the sender profile that references it; create the sender profile before assigning it to the sequence; create the sequence before reading its root branch; create each node before its downstream branch exists; enroll before launch if you want contacts moving at launch time.
13. **A LinkedIn account attaches to exactly one sender profile.** Reusing it returns 409, and replacing a profile's existing account also returns 409. Repeating the same account ID on the same profile is fine.
14. **Sequence IDs are integers, contact and workspace IDs are strings.** `senderProfileIds` and `moveSourceSequenceIds` are integer arrays; `leadIds` and `mailboxIds` are string arrays. Sending the wrong type gives a 400 with a generic message.
15. **`PATCH /.../status` accepts only `active` and `paused`.** Use `PATCH /.../launch` for the first activation.
16. **`POST /.../enrollments` is deprecated.** Use the preflight and confirm pair. The deprecated endpoint still returns 409 when a supplied `validationRunId` is not ready.
