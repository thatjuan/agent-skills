# Salesforge core public API (v2)

Spec: `https://api.salesforge.ai/public/v2/swagger/doc.json` (OpenAPI 3.1, title "Salesforge API", version 2.0).
Docs: `https://developer.salesforge.ai` (append `.md` to any page path for markdown).

## Header

- Base URL: `https://api.salesforge.ai/public/v2`
- Auth header: `Authorization: <RAW_API_KEY>`. Send the raw key. Do **not** add a `Bearer ` prefix. Docs: "Send the raw API key in the `Authorization` header. Do not add a `Bearer ` prefix." and "Bearer authentication and API key authentication are different. Adding `Bearer ` changes the header value and causes Salesforge requests to fail."
- The multichannel API accepts both the raw key and `Bearer <key>`. Use the raw key so one value works against both.
- Content type: `application/json` on every request with a body. Two download endpoints return `application/zip` and `application/octet-stream`.
- Key creation: Salesforge app at `https://app.salesforge.ai` -> Settings page -> API tab. Every Forge product issues its own key from its own app (Warmforge at `app.warmforge.ai`, Mailforge at `app.mailforge.ai`, and so on). A Salesforge key does not authenticate Warmforge or Mailforge.
- Key validation endpoint: `GET /me`. Returns `{accountId, apiKeyName}` on 200, 401 on an invalid key.

```bash
curl -sS "https://api.salesforge.ai/public/v2/me" -H "Authorization: $SALESFORGE_API_KEY"
```

## Conventions

- **Pagination**: query params `limit` and `offset`. `offset` defaults to 0. `limit` defaults to 10 on most list endpoints, and to 100 on `GET /workspaces/{id}/dnc` and `GET /workspaces/{id}/sending-data`. `GET /workspaces/{id}/tags` caps `limit` at 100.
- **List envelope**: `{"data": [...], "limit": <int>, "offset": <int>, "total": <int>}`. Read `total` to drive paging.
- **Single-resource responses** return the object at the top level, with no `data` wrapper.
- **Error body**: `{"message": "<string>", "data": <any>}`. `data` is usually absent or null.
- **Status codes**: 200 read/update, 201 create, 202 async accepted (validation start), 204 no body (deletes, assignments, status changes, replies), 400 validation, 401 missing or invalid key, 402 out of credits, 403 key valid but out of scope for the resource, 404 not found, 409 conflict (mailbox address already connecting), 422 insufficient active contact capacity, 500 server error.
- **ID formats**: opaque prefixed strings. Observed prefixes: `lead_` (contact), `prod_` (product), `seq_` (sequence), `ltg_` (tag), `wh_config_` (webhook), `wh_` (webhook event), `whsec_` (webhook signing secret). Do not parse them, and do not assume UUIDs.
- **Dates**: analytics `from_date` / `to_date` and the `days` map keys use `YYYY-MM-DD`. Response timestamps (`createdAt`, `date`, `labelAppliedAt`) are plain strings; the spec does not pin a format, so treat them as RFC 3339 and parse defensively.
- **Array query params** use repeated bracketed keys, for example `?tag_ids[]=ltg_1&tag_ids[]=ltg_2`.
- **Rate limits**: not documented. No rate-limit headers or 429 responses appear in the spec or the docs. Add your own backoff.
- **Workspace scope**: every resource except `/me` and `/workspaces` is nested under `/workspaces/{workspaceID}`. Resolve the workspace before any write.

## Endpoint catalog

61 operations. Path prefix `/workspaces/{workspaceID}` is written as `{ws}`.

### Auth

- `GET /me` - validate the API key. 200 -> `{accountId, apiKeyName}`. 401 -> invalid key.

### Workspaces

- `GET /workspaces` - list workspaces on the account. Query: `limit`, `offset`. Items: `{id, accountId, name, slug}`.
- `POST /workspaces` - create a workspace. Body: `name` (string, required, 1-100 chars). 201 -> `{id, accountId, name, slug}`.
- `GET /workspaces/{workspaceID}` - one workspace. 200 -> `{id, accountId, name, slug}`.

### Contacts (leads)

Leads and contacts are the same record. The internal model is "lead"; the public API says "contact".

- `GET {ws}/contacts` - list contacts. Query: `limit`, `offset`, `tag_ids[]` (alias `tagIds`), `not_in_sequence_id` (alias `notInSequenceId`), `validation_statuses[]` (aliases `validationStatus`, `validationStatuses`). Validation values: `safe`, `valid`, `invalid`, `disabled`, `disposable`, `inbox_full`, `catch_all`, `role_account`, `spamtrap`, `unknown`, `unvalidated` (`valid` is accepted as an alias of `safe`). **Unknown query params return 400.** Items: `ContactResponse`.
- `POST {ws}/contacts` - create one contact. Body `CreateSimpleLeadRequest`: `firstName` (string, required), `email` (string), `linkedinUrl` (string), `lastName`, `company` (min length 1), `position`, `customVars` (map of string to string), `tags` (array of tag names), `tagIds` (array of tag IDs). Supply at least one of `email` or `linkedinUrl`. With no tag supplied, a default date-based tag is applied. 201 -> `ContactResponse`.
- `POST {ws}/contacts/bulk` - create up to 100 contacts. Body: `{contacts: [CreateSimpleLeadRequest]}`, 1 to 100 items. Each entry additionally requires at least one tag via `tags` or `tagIds`. **All or nothing: one invalid entry fails the whole request.** 201 -> `{contacts: [ContactResponse]}`.
- `POST {ws}/contacts/bulk-delete` - delete up to 1000 contacts. Body: `{contactIds: [string]}`, 1 to 1000 items, required. IDs outside the workspace are ignored, not rejected. 204.
- `GET {ws}/contacts/{contactID}` - one contact including tags and sequence enrollment. 200 -> `ContactResponse`.
- `DELETE {ws}/contacts/{contactID}` - delete one contact. 204.

`ContactResponse`: `{id, firstName, lastName, email, linkedinUrl, company, position, customVars (map), tags ([string]), sequences: [{id, name, status: SequenceLeadStatus}]}`.

### Tags

- `GET {ws}/tags` - list non-hidden workspace tags, ordered by name. Query: `limit` (max 100), `offset`, `search` (substring match on name), `caseSensitive` (boolean; true matches exactly instead of ignoring case). Items: `{id, name}`. Use these IDs for the `tag_ids[]` contact filter and for `tagIds` on contact creation.

### Custom variables

- `GET {ws}/custom-vars` - list custom variables. Query: `limit`, `offset`. Items: `{id, name}`. Reference them in step content as `{{var_name}}`. A variable used in a step but missing on an enrolled contact fails that send.

### DNC (do not contact)

- `GET {ws}/dnc` - paginated DNC entries, `limit` default 100. Items: `{value, type: email|domain|linkedin, createdAt}`.
- `POST {ws}/dnc/bulk` - add entries. Body: `{dncs: [string]}`, 1 to 1000 items, required. Values are raw emails, domains, or LinkedIn URLs; the type is inferred. 201 -> `{created: <int>}`.
- `POST {ws}/dnc/bulk/remove` - remove entries by value. Body: `{dncs: [string]}`, 1 to 1000 items, required. 204.

### Webhooks

- `GET {ws}/integrations/webhooks` - list webhooks. Query: `limit`, `offset`. Items: `WebhookResponse`.
- `POST {ws}/integrations/webhooks` - create a webhook. Body: `name` (string, required), `type` (WebhookType enum, required), `url` (string, required, publicly reachable, must answer 2xx; a failed delivery is **not** retried), `sequenceIds` ([string]; omit or leave empty to receive events from every sequence), `sequenceID` (string, **deprecated**, ignored when `sequenceIds` is non-empty; use `sequenceIds`). 201 -> `{id, name, url, type, sequenceId, sequenceIds, sentCount, signingSecret}`. **`signingSecret` is returned exactly once. Store it immediately.**
- `GET {ws}/integrations/webhooks/{webhookID}` - one webhook. 200 -> `WebhookResponse` `{id, name, url, type, sequenceId, sequenceIds, sentCount}`. No `signingSecret`.
- `DELETE {ws}/integrations/webhooks/{webhookID}` - delete a webhook. 204. Secrets cannot be rotated or retrieved, so delete and recreate to replace a leaked secret.

### Mailboxes

- `GET {ws}/mailboxes` - list mailboxes. Query: `limit`, `offset`, `statuses[]` (`active`, `access_lost`, `pending`), `mailbox_ids[]`, `excluded_mailbox_ids[]`, `search`, `tag_ids[]`, `not_tag_ids[]`, `addresses[]`, `status_criteria` (single: `all`, `active`, `warm`, `pending`, `suspended`, `disconnected`, `recommendations`), `statuses_criteria` (array of the same values). Items: `MailboxResponse`.
- `POST {ws}/mailboxes` - connect an SMTP/IMAP mailbox. Body: `address` (required; must not already be connected to another workspace), `firstName` (required), `lastName` (required), `smtp` (required), `imap` (required), `dailyEmailLimit` (integer, min 1, defaults to 30; values above the workspace cap are rejected), `signature` (HTML; scored for spam potential without blocking), `trackingDomain` (domain with a CNAME already pointing at Salesforge). `smtp` and `imap` each take `{host, port, username, password}`, all required, port 1-65535. Port selects encryption: 993 (IMAP) and 465 (SMTP) use implicit TLS, 587 (SMTP) uses STARTTLS, any other port tries TLS then retries without strict certificate verification. Both legs are verified against the provider before anything is stored, so a bad host, port, or password returns 400 and creates nothing. 201 -> `MailboxResponse` with `status: "pending"`; registration flips it to `active` or `access_lost` moments later, so poll `GET {ws}/mailboxes/{mailboxID}`. Idempotent by address: a second request for an address already mid-connect returns 409. Use `/mailboxes/oauth-link` for Google and Outlook instead.
- `POST {ws}/mailboxes/oauth-link` - get a Google or Outlook OAuth URL. Body: `provider` (`google` or `outlook`, required), `redirectUrl` (absolute https URL, required, must be pre-registered with Salesforge support, may carry a path and query but no fragment or credentials), `email` (address to pre-select; the user can still pick another, so trust the address on the redirect). 200 -> `{url}`. Salesforge appends `mailboxId` and `address` on success, or `connection_status=failed` plus an error code on failure, preserving existing query params. The mailbox is auto-provisioned in Warmforge under the matching workspace.
- `GET {ws}/mailboxes/{mailboxID}` - one mailbox. 200 -> `MailboxResponse`.
- `PATCH {ws}/mailboxes/{mailboxID}` - update operational settings. Body (all optional): `firstName`, `lastName`, `signature`, `trackingDomain`, `dailyEmailLimit` (integer, **1 to 100**). 200 -> `MailboxResponse`.
- `PATCH {ws}/mailboxes/{mailboxID}/connection-settings` - replace SMTP and/or IMAP credentials without reconnecting. Body: `smtp` and/or `imap`, each `{host, port, username, password}` with all four required when the leg is supplied. Omitted legs and mailbox metadata stay unchanged. Supplied legs are verified before saving. OAuth mailboxes require provider reauthorization instead. 204.
- `DELETE {ws}/mailboxes/{mailboxID}` - disconnect and mark deleted in Salesforge. Does not delete the account at the provider. 204.

`MailboxResponse`: `{id, address, firstName, lastName, mailboxProvider, status, disconnectReason, dailyEmailLimit, signature, resolvedSignature, trackingDomain, trackingDomainStatus}`.

### Email and attachments

- `GET {ws}/mailboxes/{mailboxID}/emails/{emailID}/attachments` - download every attachment of a thread email as a ZIP (`application/zip`). 204 when the email has no attachments. 400 when attachments are unavailable.
- `GET {ws}/mailboxes/{mailboxID}/emails/{emailID}/attachments/{contentID}` - stream one attachment (`application/octet-stream`). `contentID` comes from the `contentId` field in thread email attachment metadata.
- `POST {ws}/mailboxes/{mailboxID}/emails/{emailID}/reply` - send a reply on the thread that owns the email. Body: `content` (HTML or text body), `ccs` ([string]), `bccs` ([string]), `includeHistory` (boolean, quotes the prior thread), `attachments` ([{filename, contentType, contentBase64}]). 204 with no body, so read the thread afterward to confirm.

### Threads and Primebox labels

- `GET {ws}/threads` - list workspace threads. Query: `limit`, `offset`, `mailbox_ids[]`, `agent_ids[]`, `sequence_ids[]`, `positive` (boolean sentiment filter), `filter` (string criteria such as `all`, `unread`, `archived`), `labels[]` (label IDs), `exclude_labels[]`, `q` (search). Items: `PrimeboxThreadResponse` `{id, mailboxId, agentId, agentReply, agentStatus, contactFirstName, contactLastName, contactEmail, subject, content, date, isUnread, isPositive, labelId, labelAppliedAt, labelAppliedBy, replyType, profilePictureUrl}`.
- `GET {ws}/threads/{threadID}` - one thread, email or LinkedIn-only. 200 -> `ThreadResponse` `{contact: {id, firstName, lastName, email, company, linkedinUrl}, emails: [ThreadEmailResponse], linkedinMessages: [ThreadLinkedinMessageResponse], sequence: {id, name, status, product}}`. `ThreadEmailResponse`: `{id, emailId, subject, content, date, type, fromAddress, toAddress, tos, ccs, bccs, attachments: [{id, contentId, contentType, filename, size, inline, embedded}]}`.
- `PUT {ws}/threads/{threadID}/label` - set the thread label. Body: `{labelId}` (required, a Primebox label ID). 204.
- `GET {ws}/mailboxes/{mailboxID}/threads/{threadID}` - **DEPRECATED.** Use `GET {ws}/threads/{threadID}`, which also handles mailbox-less LinkedIn-only threads. Same `ThreadResponse`.
- `PUT {ws}/mailboxes/{mailboxID}/threads/{threadID}/label` - **DEPRECATED.** Use `PUT {ws}/threads/{threadID}/label`. Body `{labelId}`. 204.
- `GET {ws}/primebox-labels` - list Primebox labels. Query: `limit`, `offset`. Envelope `{data, limit, offset, total}` with items `{id, name, isBuiltIn, specialLabel}`.

### LinkedIn threads (present in this spec, multichannel-adjacent)

- `GET {ws}/threads/{threadID}/linkedin/messages/{messageID}/attachments` - ZIP of all attachments on a LinkedIn message. 204 when there are none.
- `GET {ws}/threads/{threadID}/linkedin/messages/{messageID}/attachments/{attachmentID}` - stream one LinkedIn attachment.
- `POST {ws}/threads/{threadID}/linkedin/reply` - send a LinkedIn reply to the thread's contact. Body: `accountId` (**integer**, required, the LinkedIn account ID), `message` (string), `attachments` ([{filename, contentType, contentBase64}]). 200 -> `ThreadLinkedinMessageResponse` `{id, accountId, direction, message, subject, date, firstName, lastName, linkedinUrl, profilePictureUrl, attachments}`.

### Products

A product describes what a sequence sells and supplies the AI generation context.

- `GET {ws}/products` - list products. Query: `limit`, `offset`. Items: `ProductResponse`.
- `POST {ws}/products` - create a product. Body: `{product: ProductRequest, translation: [ProductRequest]}`. `ProductRequest`: `{internalName, name, language (Language enum), industry, idealCustomerProfile, pain, solution, proofPoints, costOfInaction}`, all optional in the spec. 201 -> `ProductResponse`.
- `GET {ws}/products/{productID}` - one product. 200 -> `ProductResponse` `{id, internalName, translations: [{language, name, industry, idealCustomerProfile, pain, solution, proofPoints, costOfInaction}]}`.

### Sequences (V1, email)

- `GET {ws}/sequences` - list every sequence in the workspace. Query: `limit`, `offset`, `statuses[]` (`active`, `paused`, `draft`, `completed`), `product_id`, `sequence_ids[]`, `type` (`legacy` or `multichannel`). Multichannel sequences are listed first, then legacy sequences fill the page. Items: `SequenceResponse` for legacy entries.
- `POST {ws}/sequences` - create a V1 sequence. Body: `name` (required), `productId` (required), `language` (Language enum, required), `timezone` (required, IANA name such as `America/New_York`). 201 -> `SequenceResponse` in `draft`.
- `GET {ws}/sequences/{sequenceID}` - one sequence with steps, mailboxes, and counters. 200 -> `SequenceResponse`.
- `PUT {ws}/sequences/{sequenceID}` - update sequence settings. Body (`models.UpdateSequenceRequest`, all optional): `name`, `productId`, `language`, `timezone`, `status` (SequenceStatus), `cc`, `bcc`, `openTrackingEnabled`, `clickTrackingEnabled`, `trackingDomainEnabled` (**string**, not boolean), `plainTextEmailsEnabled`, `listUnsubscribeEnabled`, `unsubscribeLinkEnabled`, `unsubscribeLinkText`, `localizedOptOutEnabled`, `optOutText`, `finishOnOpen`, `finishOnClick`, `bounceProtectorEnabled`, `espMatchingEnabled`, `stopOnDomainReplyEnabled`, `sequentialCompanySendingEnabled`, `companyOutreachLimitEnabled`, `companyOutreachLimitCount`, `trackOpportunitiesEnabled`, `opportunitiesValue`, `subsequencePrimeboxLabelId`. 200 -> `SequenceResponse`.
- `DELETE {ws}/sequences/{sequenceID}` - delete a sequence. 204.
- `PUT {ws}/sequences/{sequenceID}/status` - activate or pause. Body: `{status}` required, **only `active` or `paused`** on this endpoint. 204.
- `PUT {ws}/sequences/{sequenceID}/steps` - replace the sequence steps. Body: `{steps: [UpsertStepRequest]}`, at least 1 step. `UpsertStepRequest`: `id` (string, **required** even for a new step), `name`, `order` (integer >= 0), `waitDays` (integer >= 0), `distributionStrategy` (`equal` or `custom`), `variants` (at least 1). Variant: `label` (**required**), `id` (min length 1), `order` (>= 0), `emailSubject`, `emailContent`, `status` (`active`, `paused`, `deleted`), `distributionWeight` (number 0-100), `tonality` (AIGenerationTonality), `contactInformationSource` (`linkedin`, `website`, `all`), `dynamicLanguageEnabled`, `overdriveEnabled`, `isGenerated`. 200 -> `{steps: [SequenceStepResponse]}`.
- `PUT {ws}/sequences/{sequenceID}/schedules` - replace the sending windows. Body: `{schedules: [{weekday, fromHour, toHour}]}`, at least 1. `weekday` 0-6, `fromHour` 0-23, `toHour` 1-24. 200 -> `{schedules: [{id, weekday, fromHour, toHour}]}`.
- `PUT {ws}/sequences/{sequenceID}/mailboxes` - set the sending mailboxes. Body: `{mailboxIds: [string]}` required. Replaces the current assignment. 204.
- `PUT {ws}/sequences/{sequenceID}/contacts` - enroll existing contacts. Body: `{contactIds: [string]}`, at least 1, required. 204. 402 when contact credits run out, 422 when active contact capacity is insufficient.
- `PUT {ws}/sequences/{sequenceID}/import-lead` - create a contact and enroll it in one call. Body: `CreateSimpleLeadRequest` (same shape as `POST {ws}/contacts`). Supply at least one of `email` or `linkedinUrl`. 204. 422 when active contact capacity is insufficient.
- `GET {ws}/sequences/{sequenceID}/contacts/count` - count enrolled contacts. Query: `statuses[]` (`ooo`, `bounced`, `replied`, `failed`, `active`, `paused`, `finished`, `dnc`, `deleted`, `unsubscribed`). 200 -> `{count}`.
- `GET {ws}/sequences/{sequenceID}/analytics` - daily and aggregate analytics. Query: `from_date` (**required**, `YYYY-MM-DD`), `to_date` (**required**), `timezone` (IANA name, optional). 200 -> `{days: {"YYYY-MM-DD": {sent, replied, totalOpened, uniqueOpened, totalClicked, uniqueClicked}}, stats: {contacted, opened, openedPercent, clicked, clickedPercent, replied, repliedPercent, repliedPositive, repliedPositivePercent}}`. 400 when the sequence does not exist.

### Sequence contact validation

- `POST {ws}/sequences/{sequenceID}/contacts/validation/start` - start validation asynchronously. No body. 202 with an empty object. 400 when there is nothing to validate, 402 when validation credits run out.
- `GET {ws}/sequences/{sequenceID}/contacts/validation/result` - poll progress. 200 -> `{status: in_progress|completed, progress: <int 0-100>, result: {"<ESP name>": {safe, invalid, disabled, disposable, inbox_full, catch_all, role_account, spam_trap, unknown, unvalidated}}}`. 400 when no validation is running.
- `POST {ws}/sequences/{sequenceID}/contacts/validation/confirm` - keep only the contacts matching the chosen buckets. Body: `esps` ([LeadESP], at least 1, **required**), `statuses` ([ReonEmailStatus], at least 1, optional). 204.
- `POST {ws}/sequences/{sequenceID}/contacts/validation/skip` - dismiss the results and proceed without filtering. No body. 204.
- `POST {ws}/sequences/{sequenceID}/contacts/validation/validate` - **DEPRECATED.** Synchronous validation that can time out with 408. Use `validation/start` plus `validation/result`. 200 -> `{processedPercentage, result}`.

### Workspace-level sequence reporting

- `GET {ws}/sequence-metrics` - aggregate metrics across sequences. Query: `product_id`, `sequence_ids[]`. No pagination. 200 -> `{contacted, opened, openedPercent, clicked, clickedPercent, replied, repliedPercent, repliedPositive, repliedPositivePercent, bounced, bouncedPercent}`.
- `GET {ws}/sending-data` - per-contact sending data across sequences. Query: `limit` (default 100), `offset`, `sequence_ids[]`. Items: `{sequenceId, contactId, email, scheduled, sent, opened, clicked}` (timestamp-like fields are strings).

`SequenceResponse`: `{id, workspaceId, name, productId, agentId, status, leadCount, contactedCount, openedCount, openedPercent, clickedCount, clickedPercent, repliedCount, repliedPercent, repliedPositiveCount, repliedPositivePercent, bouncedCount, bouncedPercent, completedCount, completedPercent, optOutedCount, optOutedPercent, openTrackingEnabled, clickTrackingEnabled, localizedOptOutEnabled, sequentialCompanySendingEnabled, companyOutreachLimitEnabled, companyOutreachLimitCount, mailboxes: [{id, address, firstName, lastName}], steps: [SequenceStepResponse]}`.

## Enumerations

- **SequenceStatus**: `active`, `draft`, `paused`, `deleted`, `completed`, `video_pending`. `PUT .../status` accepts only `active` and `paused`. The `statuses[]` list filter accepts only `active`, `paused`, `draft`, `completed`.
- **SequenceLeadStatus** (contact status inside a sequence): `none`, `ooo`, `bounced`, `bounce-protect`, `replied`, `failed`, `active`, `paused`, `finished`, `dnc`, `deleted`, `unsubscribed`, `contacted`, `multi-threading`. The `contacts/count` filter accepts the subset `ooo`, `bounced`, `replied`, `failed`, `active`, `paused`, `finished`, `dnc`, `deleted`, `unsubscribed`.
- **SequenceStepVariantStatus**: `active`, `paused`, `deleted`.
- **ABTestDistributionStrategy**: `equal`, `custom`.
- **ContactInformationSource**: `linkedin`, `website`, `all`.
- **AIGenerationTonality**: `playful`, `hilarious`, `formal`, `curious`, `urgent`, `appreciative`, `polite`, `enthusiastic`, `warm`, `empathetic`, `direct`, `persuasive`, `confident`, `respectful`, `helpful`, `sincere`, `encouraging`, `informal`, `caring`, `diplomatic`, `assertive`, `reassuring`, `authoritative`.
- **Language**: `russian`, `ukrainian`, `finnish`, `american_english`, `british_english`, `french`, `spanish`, `polish`, `romanian`, `german`, `lithuanian`, `dutch`, `latvian`, `italian`, `czech`, `hungarian`, `japanese`, `brazilian_portugese` (note the spelling), `swedish`, `danish`, `norwegian`, `estonian`.
- **MailboxProvider**: `gmail`, `outlook`, `smtp`.
- **MailboxStatus**: `active`, `frozen`, `access_lost`, `deleted`, `inactive`, `pending`, `suspended`. The `statuses[]` filter accepts only `active`, `access_lost`, `pending`.
- **Mailbox status_criteria / statuses_criteria**: `all`, `active`, `warm`, `pending`, `suspended`, `disconnected`, `recommendations`.
- **OAuth link provider**: `google`, `outlook`.
- **TrackingDomainStatus**: `active`, `pending`.
- **DncType**: `email`, `domain`, `linkedin`.
- **ValidationStatus** (validation job): `in_progress`, `completed`.
- **ReonEmailStatus** (per-contact validation): `safe`, `invalid`, `disabled`, `disposable`, `inbox_full`, `catch_all`, `role_account`, `spamtrap`, `unknown`, `unvalidated`. The contacts list filter also accepts `valid` as an alias of `safe`. The validation result map uses the key `spam_trap` with an underscore while the enum value is `spamtrap`.
- **LeadESP**: `empty`, `gmail`, `gsuite`, `icloud`, `outlook`, `ms365`, `yandex`, `yahoo`, `unknown`, `mailcom`, `proofpoint`, `antispamsoftware`.
- **SpecialLabel** (built-in Primebox labels): `all`, `none`, `positive`, `negative`, `ooo`, `meeting_booked`, `meeting_completed`, `closed`, `wrong_contact`.
- **LabelAppliedBy**: `system`, `heuristics`, `llm`, `user`.
- **ThreadAgentStatus**: `replied`, `action_required`, `human_review_required`, `action_dismissed`.
- **ReplyType**: `ooo`, `bounced`, `lead_replied`.
- **MultichannelLinkedinMessageDirection**: `inbound`, `outbound`.
- **WebhookType**: `email_sent`, `email_opened`, `link_clicked`, `email_replied`, `linkedin_replied`, `contact_unsubscribed`, `email_bounced`, `positive_reply`, `negative_reply`, `label_changed`, `dnc_added`, `meeting_booked`, `meeting_completed`, `linkedin_message_sent`, `linkedin_inmail_sent`, `linkedin_connection_request_sent`, `linkedin_connection_request_accepted`, `linkedin_connection_request_withdrawn`, `linkedin_profile_viewed`, `linkedin_post_liked`, `linkedin_contact_followed`.

## Webhooks

One webhook registration carries one `type`. Register one webhook per event you want.

**Delivery**: `POST` to your `url` with a JSON body. A delivery that does not get a 2xx is **not retried**. The documented body shape is `{"webhookInfo": {"type": "<WebhookType>"}}` plus event payload; the spec does not define the full payload schema, so treat fields beyond `webhookInfo.type` as event-specific and parse defensively.

**Headers on every signed delivery**:

| Header | Example | Use |
| --- | --- | --- |
| `X-SalesforgeAI-Webhook-Event-ID` | `wh_0123456789abcdef` | First field of the signed content, and your dedupe key |
| `X-SalesforgeAI-Webhook-Signature` | `t=1754563200,v1=d35d4326...` | `t` is the signed Unix timestamp, `v1` is the lowercase hex HMAC-SHA256 digest |
| `User-Agent` | `SalesforgeAI/salesforge-webhook-service-1.1` | Identification only. Never authenticate on it |

**Verification algorithm**:

1. Read the raw body as bytes before any JSON middleware touches it.
2. Split the signature header on `,`, then each part on its first `=`, to get `t` and `v1`.
3. Reject when `t` is more than 300 seconds from now.
4. Build the signed content as `event_id + "." + t + "." + raw_body`, reusing `t` verbatim as a string.
5. Compute HMAC-SHA256 with the full secret **including the `whsec_` prefix** as the key, and compare to `v1` with a constant-time comparison.
6. Reject any delivery with no signature header.

```python
import hashlib, hmac, time

def verify_webhook(secret, event_id, header, raw_body, tolerance_seconds=300):
    """raw_body must be the exact, unparsed request body (bytes)."""
    if not (secret and event_id and header):
        return False
    fields = {}
    for part in header.split(","):
        key, sep, value = part.partition("=")
        if sep:
            fields[key] = value
    timestamp, signature = fields.get("t"), fields.get("v1")
    if not timestamp or not signature or not timestamp.isdigit():
        return False
    if abs(int(time.time()) - int(timestamp)) > tolerance_seconds:
        return False
    signed = f"{event_id}.{timestamp}.".encode() + raw_body
    expected = hmac.new(secret.encode(), signed, hashlib.sha256).digest()
    try:
        received = bytes.fromhex(signature)
    except ValueError:
        return False
    return hmac.compare_digest(expected, received)
```

**Known-good test vector** (disable the timestamp check to run it; it must return true, and flipping one byte of the secret, event ID, or body must return false):

```
secret   = "whsec_" + base64(bytes 0x00..0x1f) with the "=" padding stripped
           python: "whsec_" + base64.b64encode(bytes(range(32))).decode().rstrip("=")
event_id = wh_0123456789abcdef
header   = t=1754563200,v1=d35d432699cc9e59eb73da4396b9a3a96003ba6a9ae259256d270ff3c8f24207
raw_body = {"webhookInfo":{"type":"email_sent"}}
```

Only webhooks created through the public API are signed. Webhooks created in the app UI, Zapier, or Make are unsigned today.

## Workflows

### Create and launch a V1 email sequence end to end

A V1 sequence needs all four of these before it can run: at least one step with at least one variant, at least one enrolled contact, at least one assigned mailbox, and at least one schedule window.

1. `GET /me` to confirm the key, then `GET /workspaces` to resolve `workspaceID`.
2. `GET {ws}/products` or `POST {ws}/products` to get a `productId`.
3. `GET {ws}/mailboxes?statuses[]=active` to pick sending mailboxes, or connect one with `POST {ws}/mailboxes` (SMTP/IMAP) or `POST {ws}/mailboxes/oauth-link` (Google, Outlook) and poll `GET {ws}/mailboxes/{mailboxID}` until `status` is `active`.
4. `GET {ws}/tags` to resolve tag IDs, then `POST {ws}/contacts/bulk` (max 100 per call, each entry needs `firstName`, one of `email` or `linkedinUrl`, and at least one tag).
5. `POST {ws}/sequences` with `name`, `productId`, `language`, `timezone`. The sequence starts in `draft`.
6. `PUT {ws}/sequences/{sequenceID}/steps` with at least one step and one variant per step.
7. `PUT {ws}/sequences/{sequenceID}/schedules` with at least one `{weekday, fromHour, toHour}` window.
8. `PUT {ws}/sequences/{sequenceID}/mailboxes` with `mailboxIds`.
9. `PUT {ws}/sequences/{sequenceID}/contacts` with `contactIds`, or `PUT {ws}/sequences/{sequenceID}/import-lead` to create and enroll in one step. Confirm with `GET {ws}/sequences/{sequenceID}/contacts/count`.
10. `POST {ws}/sequences/{sequenceID}/contacts/validation/start`, poll `GET .../validation/result` until `status` is `completed`, then either `POST .../validation/confirm` with the ESP and status buckets you accept, or `POST .../validation/skip`.
11. `PUT {ws}/sequences/{sequenceID}/status` with `{"status":"active"}`.
12. Monitor with `GET {ws}/sequences/{sequenceID}/analytics?from_date=...&to_date=...` and `GET {ws}/sequence-metrics`.

### Reply to a thread and label it

1. `GET {ws}/threads?filter=unread` (or filter by `labels[]`, `sequence_ids[]`, `positive`) to find the thread. Keep `id` and `mailboxId`.
2. `GET {ws}/threads/{threadID}` to read the conversation. Pick the email to reply to from `emails[].id`.
3. Download attachments if needed: `GET {ws}/mailboxes/{mailboxID}/emails/{emailID}/attachments` for a ZIP, or `.../attachments/{contentID}` for one file.
4. `POST {ws}/mailboxes/{mailboxID}/emails/{emailID}/reply` with `content`, optional `ccs`, `bccs`, `includeHistory`, `attachments`.
5. `GET {ws}/primebox-labels` to resolve a `labelId`, then `PUT {ws}/threads/{threadID}/label` with `{"labelId": "..."}`.

For a LinkedIn-only thread, skip steps 3 and 4 and use `POST {ws}/threads/{threadID}/linkedin/reply` with the integer `accountId`.

### Sync the DNC list

1. `GET {ws}/dnc?limit=100&offset=0`, then page on `offset` until `offset + len(data) >= total`.
2. Diff against your system.
3. `POST {ws}/dnc/bulk` with `{"dncs": [...]}` for additions, in chunks of 1000.
4. `POST {ws}/dnc/bulk/remove` with `{"dncs": [...]}` for removals, in chunks of 1000.
5. Subscribe to the `dnc_added` webhook to stay current instead of re-polling.

## Gotchas

1. **No `Bearer` prefix.** The raw key goes in `Authorization`. Adding `Bearer ` fails on Salesforge endpoints even though the multichannel endpoints tolerate it.
2. **The generated spec lies about list item types.** Every paginated `200` schema declares its `data` items as `api.DNCResponse`. That is a swaggo generic-erasure artifact. The real item type matches the resource (contacts return `ContactResponse`, mailboxes return `MailboxResponse`, and so on). Do not code-generate list responses straight from the spec.
3. **Unknown query params return 400 on `GET {ws}/contacts`.** A typo or a leftover param fails the request rather than being ignored. Expect the same defensive behavior elsewhere.
4. **Bulk contact create is all or nothing.** One invalid entry in a 100-item batch fails the whole call and creates nothing. Bulk delete behaves differently and silently ignores IDs outside the workspace.
5. **`dailyEmailLimit` caps differ by endpoint.** Connect (`POST {ws}/mailboxes`) allows any value at or below the workspace cap and defaults to 30; update (`PATCH {ws}/mailboxes/{mailboxID}`) constrains it to 1-100.
6. **`UpsertStepRequest.id` is required even for a brand-new step**, and every variant requires `label`. `PUT .../steps` and `PUT .../schedules` replace the full collection, so send the complete desired state, not a delta.
7. **`webhook.signingSecret` appears exactly once, in the create response.** There is no rotation or retrieval endpoint. Losing it means deleting and recreating the webhook. Webhook deliveries are never retried, so return 2xx fast and process asynchronously.
8. **`trackingDomainEnabled` on `PUT {ws}/sequences/{sequenceID}` is typed `string`, not boolean**, unlike every neighboring `*Enabled` field. Send a string.
9. Mailbox connect returns `status: "pending"` and 201 even though registration is still finishing. Poll the mailbox until `active` before assigning it to a sequence. A repeat connect for an address already mid-connect returns 409.
10. `POST {ws}/mailboxes/oauth-link` requires `redirectUrl` to be pre-registered with Salesforge support. An unregistered URL fails with 400.
11. The deprecated mailbox-scoped thread endpoints (`GET`/`PUT .../mailboxes/{mailboxID}/threads/{threadID}...`) cannot see LinkedIn-only threads. Use the workspace-scoped pair.
12. `sequenceID` (singular) on `CreateWebhookRequest` is deprecated and ignored whenever `sequenceIds` is non-empty.
13. `POST .../validation/validate` is deprecated and can return 408 on large lists. Use `validation/start` plus polling `validation/result`.
14. Enrollment can fail on quota rather than on data: 402 for contact or validation credits, 422 for insufficient active contact capacity. Handle both.
15. `GET {ws}/sequences` mixes multichannel and legacy sequences in one page, multichannel first, so a page of results may hold two different object shapes. Pass `type=legacy` when you only want V1 sequences.
16. `POST {ws}/dnc/bulk/remove` is documented as 204 yet declares a `string` response body in the spec. Treat it as no content.
17. Custom variables referenced in step content must exist on every enrolled contact. A missing variable fails that contact's send at delivery time, not at validation time.
18. Rate limits are undocumented. Assume they exist, keep bulk calls within the stated item caps, and back off on 5xx.
