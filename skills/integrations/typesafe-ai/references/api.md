# TypeSafe AI HTTP API

Wire-level reference for `POST /v1/systemone` and `GET /v1/models`: schemas, one full example, errors, models, limits, env vars.

## Endpoints

| Method | URL | Purpose |
|---|---|---|
| `POST` | `https://api.typesafe.ai/v1/systemone` | Evaluate `state` against `questions`, one answer per question |
| `GET` | `https://api.typesafe.ai/v1/models` | List names accepted by the `model` field (currently the aliases only) |

Headers on every call:

```http
Authorization: Bearer <API_KEY>
Content-Type: application/json
```

Every response carries `x-typesafe-request-id`; log it with any error. Retry hints arrive as `Retry-After` or `retry-after-ms`.

## Request body (`POST /v1/systemone`)

| Field | Type | Required | Meaning |
|---|---|---|---|
| `state` | `string \| object \| array` | yes | Content to evaluate. Cannot be `null` at top level; values inside an object may be `null`. Text only. |
| `model` | `string` | yes | Model ID or alias, e.g. `"jev-latest"`. SDKs fill this in; raw HTTP must send it. |
| `questions` | `map<string, Question>` | yes | Non-empty. Keys are yours and are never sent to the model; answers come back under the same keys. |

No other top-level fields are documented. No streaming, batch, or async job endpoints exist.

## Question schemas

All three share `type` and `instructions`; each has its own `criteria`. `instructions` and every criteria value are `EntryType` = `string | object | array | null`. `api.md` types Noul `criteria.true/false` as `string` and Choice values as `string | null`, but the SDK types (`EntryType` in JS, `JSONContent | None` in Python) are authoritative: objects and arrays are accepted everywhere.

### Noul

| Field | Type | Required | Meaning |
|---|---|---|---|
| `type` | `"noul"` | yes | |
| `instructions` | `EntryType` | yes (API); optional in SDK types | The yes/no statement. Phrase so a high value means yes. |
| `criteria` | `object` | no | `{ "true": EntryType, "false": EntryType }`, both optional. `true` = what a value near 1 means; `false` = what a value near 0 means. |

### Choice

| Field | Type | Required | Meaning |
|---|---|---|---|
| `type` | `"choice"` | yes | |
| `instructions` | `EntryType` | yes (API); optional in SDK types | What to decide. |
| `criteria` | `map<string, EntryType>` | yes | Option name to description; `null` when no description is needed. Names and descriptions are both sent to the model. Up to 255 options. |

### Score

| Field | Type | Required | Meaning |
|---|---|---|---|
| `type` | `"score"` | yes | |
| `instructions` | `EntryType` | yes (API); optional in SDK types | What to rate. |
| `criteria` | `array<EntryType>` | yes | Ordered level descriptions, low to high; index = level number. Minimum 2 levels, maximum 10. Each level is judged on its own; the model never sees level numbers or neighbours. |

## Response body

| Field | Type | Required | Meaning |
|---|---|---|---|
| `model` | `string` | yes | Versioned ID that answered (log this; aliases move). |
| `answers` | `map<string, Answer>` | yes | Keyed by the same question ids. |
| `usage.input_tokens` | `integer` | yes | Billed tokens. |
| `usage.output_tokens` | `integer` | yes | Always free. |

## Answer schemas

Every answer carries `type` matching its question.

### Noul answer

| Field | Type | Required | Meaning |
|---|---|---|---|
| `type` | `"noul"` | yes | |
| `noul` | `number` | yes | P(yes), 0 to 1. No `confidence` field on Noul. |

### Choice answer

| Field | Type | Required | Meaning |
|---|---|---|---|
| `type` | `"choice"` | yes | |
| `choice` | `string` | yes | Highest-probability option name. |
| `probabilities` | `map<string, number>` | yes | Every option to its probability; sums to 1. |
| `confidence` | `number` | yes | 0 to 1, derived from `probabilities`; how peaked the distribution is. |

### Score answer

| Field | Type | Required | Meaning |
|---|---|---|---|
| `type` | `"score"` | yes | |
| `score` | `number` | yes | Probability-weighted mean of level indices; may be fractional. Normalize with `score / (len(criteria) - 1)`. |
| `legend` | `map<string, EntryType>` | yes | Level number (string key) to its description. |
| `probabilities` | `map<string, number>` | yes | Level number (string key) to probability; sums to 1. |
| `confidence` | `number` | yes | 0 to 1, derived from `probabilities`. |

Wire keys for Score `legend` and `probabilities` are strings (`"0"`, `"1"`); the Python SDK converts them to `int`, the JS SDK leaves them as string keys typed by tuple index. Different distributions can produce the same `score`; read `probabilities` and `confidence` alongside it.

## Full example (quickstart, verbatim)

Request:

```json
{
  "state": "Hi, I've been trying to connect my Stripe account for 3 days and it keeps failing. I'm losing sales. Please help ASAP.",
  "model": "jev-latest",
  "questions": {
    "department": {
      "type": "choice",
      "instructions": "Which team should handle this",
      "criteria": {
        "billing": "Payment or subscription issues",
        "technical": "Bugs or integration problems",
        "sales": "Pricing or account questions"
      }
    },
    "frustration": {
      "type": "score",
      "instructions": "How frustrated the customer appears",
      "criteria": [
        "Calm, just stating facts",
        "Frustrated but civil",
        "Very angry, strong language"
      ]
    },
    "is_urgent": {
      "type": "noul",
      "instructions": "The message conveys urgency or time-sensitivity"
    }
  }
}
```

Response:

```json
{
  "model": "jev-latest",
  "answers": {
    "department": {
      "type": "choice",
      "choice": "billing",
      "probabilities": {
        "billing": 0.84,
        "technical": 0.159,
        "sales": 0.001
      },
      "confidence": 0.596
    },
    "frustration": {
      "type": "score",
      "score": 1.035,
      "legend": {
        "0": "Calm, just stating facts",
        "1": "Frustrated but civil",
        "2": "Very angry, strong language"
      },
      "confidence": 0.842
    },
    "is_urgent": {
      "type": "noul",
      "noul": 0.999
    }
  },
  "usage": {
    "input_tokens": 312,
    "output_tokens": 48
  }
}
```

The quickstart sample omits `probabilities` on the Score answer; the API reference marks it required and every other example includes it. Expect it to be present.

cURL shape:

```bash
curl -X POST https://api.typesafe.ai/v1/systemone \
  -H "Authorization: Bearer $TYPESAFE_API_KEY" \
  -H "Content-Type: application/json" \
  -d @- <<'EOF'
  { "state": "...", "model": "jev-latest", "questions": { ... } }
EOF
```

## Errors

JSON body describes the failure; for 422 "the body details the offending field". No error body schema is documented.

| Status | Meaning | Retry |
|---|---|---|
| `401 Unauthorized` | Missing or invalid API key; check `Authorization`. | No. Fix the key. |
| `422 Unprocessable Entity` | Body failed validation: missing required field, malformed question, Score with fewer than 2 levels, empty `questions`. | No. Fix the request. |
| `429 Too Many Requests` | Over tokens/s or requests/min limit. | Yes, exponential backoff; honor `Retry-After` / `retry-after-ms`. |
| `529 Overloaded` | Service temporarily overloaded. | Yes, exponential backoff after a short delay. |

Both SDKs retry 408, 429, and 500 to 599 (which covers 529) by default with backoff and `Retry-After` handling, so raw-HTTP callers are the only ones who need to implement this.

## Models

| Model | ID | Price | Rate limits | Context |
|---|---|---|---|---|
| Jev 1.13 | `jev-1.13.0` | $42 / Btok input ($0.042 / Mtok); output free | 250,000 tokens/s and 1,200 requests/min | 64k tokens per request; 32k tokens for `state` plus the longest single question |

| Alias | Points to | Meaning |
|---|---|---|
| `jev-latest` | `jev-1.13.0` | Most recent stable release. SDK default. |
| `jev-preview` | `jev-1.13.0` | Most recent release, preview or not. Currently identical to `jev-latest`; no preview build exists. |

Rules:

- Context: the 64k budget is `state` plus all questions combined; the 32k budget is `state` plus the single longest question. Both apply.
- Rate limits are "adjusting dynamically" and can change without notice; over either limit returns 429.
- Aliases move when a new release ships, so answers behind them can change with no change on your side. `response.model` reports the versioned ID that answered. If confidence thresholds are tuned against a version, pin that version's ID (`jev-1.13.0`) instead of the alias and migrate on your own schedule.
- Versioned IDs are accepted by `model` whether or not `GET /v1/models` lists them.
- Text only, English primary; other languages accepted with lower accuracy. No fine-tuning; not trained on customer data.

`GET /v1/models` response:

| Field | Type | Meaning |
|---|---|---|
| `models[]` | `array` | One entry per model or alias |
| `models[].name` | `string` | ID or alias as accepted by `model` |
| `models[].description` | `string` | What the model is for |
| `models[].release_date` | `string` | Release date |

```bash
curl https://api.typesafe.ai/v1/models \
  -H "Authorization: Bearer $TYPESAFE_API_KEY"
```

## Environment variables

| Variable | Used by | Default |
|---|---|---|
| `TYPESAFE_API_KEY` | both SDKs, cURL examples | required |
| `TYPESAFE_BASE_URL` | both SDKs | `https://api.typesafe.ai` |
| `TYPESAFE_DEFAULT_MODEL` | both SDKs | `jev-latest` |
| `TYPESAFE_LOG_LEVEL` | both SDKs | Python: unset; JS: `warn` |

Keys are created at `https://console.typesafe.ai` (`/settings/keys` or `/keys`).
