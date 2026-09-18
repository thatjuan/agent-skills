# TypeSafe AI JavaScript SDK (`@typesafe-ai/sdk`)

Reference for `@typesafe-ai/sdk` v0.6.0: install, client config, `systemOne` and type inference, helpers, interfaces, `APIPromise`, retries, errors, constants.

## Install

Node.js 20 or newer. Ships ESM, CommonJS, and TypeScript declarations. Source: `https://github.com/typesafe-ai/typesafe-sdk-js` (tag `v0.6.0`).

```sh
npm install @typesafe-ai/sdk
```

Set `TYPESAFE_API_KEY` in the environment.

## Quickstart (verbatim)

```ts
import { choice, TypeSafeClient } from "@typesafe-ai/sdk";

const client = new TypeSafeClient();
const response = await client.systemOne({
  state: { document: "I was charged twice. Please fix this ASAP." },
  questions: {
    category: choice("What is this ticket about?", {
      billing: null,
      technical: null,
      other: null,
    }),
  },
});

console.log(response.answers.category.choice);
```

## `TypeSafeClientConfig`

`new TypeSafeClient(config?: TypeSafeClientConfig)`. Explicit values beat env vars, which beat SDK defaults; empty or whitespace-only env values are ignored. Throws when the API key is missing, config is invalid, or the runtime is unsupported (a browser without `dangerouslyAllowBrowser`).

| Field | Type | Default | Meaning |
|---|---|---|---|
| `apiKey` | `string` | `TYPESAFE_API_KEY` | Required. |
| `baseURL` | `string` | `TYPESAFE_BASE_URL`, then `https://api.typesafe.ai` | Trailing slashes removed. |
| `defaultModel` | `string` | `TYPESAFE_DEFAULT_MODEL`, then `jev-latest` | Used when a request omits `model`. |
| `timeout` | `number` | `10000` | Per attempt, milliseconds. No total retry budget. |
| `retry` | `Partial<RetryPolicy>` | `RetryPolicy` defaults | Omitted fields use defaults. |
| `logLevel` | `LogLevel` | `TYPESAFE_LOG_LEVEL`, then `warn` | `info` logs request summaries; `debug` adds headers and bodies. Credential headers redacted; bodies not. |
| `logger` | `Logger` | prefixed `console` | `debug/info/warn/error(message, ...args)`. |
| `fetch` | `Fetch` | global `fetch` | `(input: string, init?: RequestInit) => Promise<Response>`. |
| `defaultHeaders` | `Record<string, string>` | none | Per-call `headers` take precedence. |
| `dangerouslyAllowBrowser` | `boolean` | `false` | Allows browser use, exposing the API key to page users. Keep the client server-side. |

Readonly props on the instance: `baseURL`, `defaultHeaders`, `defaultModel`, `fetch`, `logger`, `logLevel`, `models`, `retry` (with overrides applied), `timeout`.

## `systemOne<Q>`

```ts
systemOne<Q extends Questions>(request: SystemOneRequest<Q>, options?: RequestOptions): APIPromise<SystemOneResult<Q>>
```

Throws (rejects) with `TypeSafeError` when questions are empty or Score criteria have fewer than two entries; `APIError` on non-2xx after retries; `APIConnectionError`/`APITimeoutError` when it cannot connect or times out after retries; `APIUserAbortError` on abort.

`SystemOneRequest<Q>`:

| Field | Type | Required | Meaning |
|---|---|---|---|
| `state` | `EntryType` | yes | `string`, JSON object, array, or `null`. |
| `questions` | `Q` | yes | Non-empty, keyed by id. |
| `model` | `string` | no | Overrides `defaultModel`. |

Extra properties on the request object are forwarded to the wire, including `null` values (no documented extra fields exist; do not invent any).

`SystemOneResult<Q>`:

| Field | Type |
|---|---|
| `answers` | `{ readonly [K in keyof Q]: ResultFor<Q[K]> }` |
| `model` | `string` |
| `usage` | `Usage` = `{ input_tokens: number; output_tokens: number }` |

Type inference: `ResultFor<T>` maps each question to its answer type and preserves criteria keys.

```ts
type ResultFor<T> = T extends NoulQuestion ? NoulResponse : T extends ScoreQuestion<infer S> ? ScoreResponse<S> : T extends ChoiceQuestion<infer E> ? ChoiceResponse<E> : never;
```

So `answers.tone.choice` is `keyof typeof criteria & string`, and a Score built from a tuple literal gets `legend` keyed by its indices (`ScoreOf<T>`: fixed-length tuple yields `"0" | "1" | ...`, otherwise `number`). Build questions inline or with the helpers so literal types survive; a `Questions`-typed variable widens everything to `string`.

`client.models.list(options?): APIPromise<ModelCard[]>` where `ModelCard = { name; description; release_date }` (all `string`).

## Question helpers

| Helper | Signature | Notes |
|---|---|---|
| `noul` | `noul(instructions?: EntryType = null, criteria?: { true?: EntryType; false?: EntryType } \| null): NoulQuestion` | |
| `choice` | `choice<T extends ChoiceCriteria>(instructions: EntryType, criteria: T): ChoiceQuestion<T>` | `null` value = undescribed label. |
| `score` | `score<T extends ScoreCriteria>(instructions: EntryType, criteria: T): ScoreQuestion<T>` | At least two entries; entries may be `null`. |

Type aliases: `EntryType = string | { [key: string]: JsonValue } | JsonValue[] | null`; `JsonValue = string | number | boolean | null | JsonValue[] | { [key: string]: JsonValue }`; `ChoiceCriteria = { [label: string]: EntryType }`; `ScoreCriteria = readonly [EntryType, EntryType, ...EntryType[]]`; `Question = NoulQuestion | ScoreQuestion | ChoiceQuestion`; `Questions = { [name: string]: Question }`.

## Question and response interfaces

| Interface | Fields |
|---|---|
| `NoulQuestion` | `type: "noul"`; `instructions?: EntryType`; `criteria?: { true?: EntryType; false?: EntryType } \| null` |
| `ChoiceQuestion<T>` | `type: "choice"`; `instructions?: EntryType`; `criteria: T` |
| `ScoreQuestion<T>` | `type: "score"`; `instructions?: EntryType`; `criteria: T` |
| `NoulResponse` | `type: "noul"`; `noul: number` (P(yes), 0 to 1; no confidence) |
| `ChoiceResponse<T>` | `type: "choice"`; `choice: keyof T & string`; `probabilities: { [label in keyof T]: number }`; `confidence: number` |
| `ScoreResponse<T>` | `type: "score"`; `score: number` (may be fractional); `legend: ScoreLegend<T>`; `probabilities: { [score in number \| \`${number}\`]: number }`; `confidence: number` |

Score `probabilities` and `legend` keys are strings on the wire; indexing with `probabilities[0]` or `probabilities["0"]` both type-check.

## `APIPromise<T>`

Returned by `systemOne` and `models.list`. Extends `Promise<T>`; non-2xx rejects with `APIError`, including through `asResponse()`.

| Method | Returns | Meaning |
|---|---|---|
| `asResponse()` | `Promise<Response>` | Raw `Response`, body unparsed. The body is buffered under the request timeout before handoff; reading it afterwards is caller-owned. Do not also `await` the parsed result on the same promise. |
| `withResponse()` | `Promise<WithResponse<T>>` | `{ data: T; response: Response (body consumed); requestId: string \| undefined }`. |
| `map(fn)` | `APIPromise<U>` | Transform the parsed result, sharing one body parse. |

```ts
const { data, requestId } = await client.systemOne({ state, questions }).withResponse();
```

## `RequestOptions`

| Field | Type | Meaning |
|---|---|---|
| `headers` | `Record<string, string>` | Merged over `defaultHeaders`. |
| `retry` | `Partial<RetryPolicy>` | Per-call overrides; omitted fields inherit the client. |
| `signal` | `AbortSignal` | Cancels the request and pending retries (`APIUserAbortError`). |
| `timeout` | `number` | Per attempt, milliseconds; no total retry budget. |

## `RetryPolicy`

| Field | Default | Meaning |
|---|---|---|
| `maxRetries` | `2` | Retries after the first attempt; `0` disables. |
| `backoffInitialMs` | `500` | First delay, doubled up to `backoffMaxMs`. |
| `backoffMaxMs` | `5000` | Cap on delay. |
| `backoffJitter` | `0.25` | Fraction of each delay randomly subtracted, 0 to 1. |
| `httpStatuses` | `408, 429, 500-599` | `ReadonlySet<number>` of retried statuses (covers 529). |
| `respectRetryAfter` | `true` | Honor `Retry-After` and `retry-after-ms` up to `maxRetryAfterMs`. |
| `maxRetryAfterMs` | `60000` | Server delays above this fall back to backoff. |
| `apiConnectionError` | `true` | Retry `APIConnectionError`, including interrupted bodies. |
| `apiTimeoutError` | `true` | Retry `APITimeoutError`. |

Unlike the Python SDK, there is no total time budget: worst case is `(maxRetries + 1) * timeout` plus delays. Bound it with an `AbortSignal` (`AbortSignal.timeout(ms)`) if that matters.

## Errors

All extend `TypeSafeError extends Error`. `APIError` and subclasses expose `status: number`, `body: unknown` (parsed JSON, text, or `undefined`), `headers: Headers`, `requestId: string | undefined`; `APIError.fromResponse(status, body, headers)` picks the subclass.

| Class | Extends | Status / when |
|---|---|---|
| `BadRequestError` | `APIError` | 400 |
| `AuthenticationError` | `APIError` | 401 |
| `PermissionDeniedError` | `APIError` | 403 |
| `NotFoundError` | `APIError` | 404 |
| `UnprocessableEntityError` | `APIError` | 422 |
| `RateLimitError` | `APIError` | 429; adds `retryAfterMs: number \| undefined` |
| `InternalServerError` | `APIError` | 5xx (includes 529) |
| `APIConnectionError` | `TypeSafeError` | DNS, TLS, connection closed, body interrupted |
| `APITimeoutError` | `APIConnectionError` | Full response not within `timeout`; adds `timeoutMs` |
| `APIUserAbortError` | `TypeSafeError` | Caller aborted via `AbortSignal` |

```ts
import { APIError, RateLimitError } from "@typesafe-ai/sdk";

try {
  await client.systemOne({ state, questions });
} catch (err) {
  if (err instanceof RateLimitError) console.warn(err.retryAfterMs);
  else if (err instanceof APIError) console.error(err.status, err.requestId, err.body);
  else throw err;
}
```

## Constants

| Export | Value |
|---|---|
| `ENV.apiKey` | `"TYPESAFE_API_KEY"` (required) |
| `ENV.baseURL` | `"TYPESAFE_BASE_URL"` (default `https://api.typesafe.ai`) |
| `ENV.defaultModel` | `"TYPESAFE_DEFAULT_MODEL"` (default `jev-latest`) |
| `ENV.logLevel` | `"TYPESAFE_LOG_LEVEL"` (default `warn`) |
| `EnvVar` | `typeof ENV[keyof typeof ENV]` |
| `LOG_LEVELS` | `readonly LogLevel[]`, most to least verbose; `LogLevel = "debug" \| "info" \| "warn" \| "error" \| "off"` |
| `VERSION` | `"0.6.0"` |

## All three types in one request (adapted, not from the docs)

Adapted from the Python triage example in `primitives/choice.md`; the docs have no JS example beyond the quickstart. Comments show inferred types.

```ts
import { choice, noul, score, TypeSafeClient } from "@typesafe-ai/sdk";

const client = new TypeSafeClient();

// Keep questions and thresholds in one reviewable place.
const TRIAGE = {
  department: choice("Which team should handle this ticket?", {
    returns: "Exchanges, refunds, wrong or damaged items",
    shipping: "Delivery status, delays, lost packages",
    billing: "Charges, invoices, payment problems",
  }),
  frustration: score("How frustrated is the customer?", [
    "Calm, just stating facts",
    "Frustrated but civil",
    "Very angry, strong language or threatening to leave",
  ]),
  wants_refund: noul("The customer is asking for money back", {
    true: "Explicitly requests a refund or chargeback",
    false: "Wants an exchange, replacement, or only information",
  }),
};

const REFUND_THRESHOLD = 0.8;
const ROUTE_CONFIDENCE = 0.3;

export async function triage(ticket: string) {
  const { answers, model } = await client.systemOne({
    state: { ticket },
    questions: TRIAGE,
  });

  const dept = answers.department;
  // dept.choice: "returns" | "shipping" | "billing"
  // dept.probabilities: { returns: number; shipping: number; billing: number }
  if (dept.confidence < ROUTE_CONFIDENCE) {
    return { route: "manual" as const, model };
  }

  const frustration = answers.frustration;
  // frustration.score: number (0 to 2, may be fractional)
  // frustration.legend: { "0": string; "1": string; "2": string }
  // frustration.probabilities["2"]: number
  const normalizedFrustration = frustration.score / (TRIAGE.frustration.criteria.length - 1);

  const escalate =
    normalizedFrustration > 0.66 && frustration.confidence > 0.5;

  // answers.wants_refund.noul: number, no confidence field on Noul
  const refundRequested = answers.wants_refund.noul > REFUND_THRESHOLD;

  // Any second team holding real probability mass gets a copy.
  const alsoNotify = (Object.keys(dept.probabilities) as (keyof typeof dept.probabilities)[])
    .filter((team) => team !== dept.choice && dept.probabilities[team] > 0.25);

  return { route: dept.choice, escalate, refundRequested, alsoNotify, model };
}
```

## Changelog

| Version | Date | Changes |
|---|---|---|
| 0.6.0 | 2026-09-15 | Breaking: `Score.criteria` is an ordered sequence (tuple), not a dictionary keyed by integers. |
| 0.5.7 | 2026-09-11 | Initial public release. |
