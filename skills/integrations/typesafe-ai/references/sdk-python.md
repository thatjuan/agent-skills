# TypeSafe AI Python SDK (`typesafe-sdk`)

Reference for `typesafe_sdk` v0.6.0: install, clients, question and answer types, retries, exceptions, config, forward compatibility.

## Install

Python >= 3.10.

```bash
pip install typesafe-sdk
```

```bash
uv add typesafe-sdk
```

Set `TYPESAFE_API_KEY` in the environment. HTTP layer is `httpx2`; structs are `msgspec`.

## Quickstart (verbatim)

Async:

```python
from typesafe_sdk import AsyncTypeSafeClient, Choice, Noul, Score


async def main() -> None:
    async with AsyncTypeSafeClient() as client:
        response = await client.system_one(
            state={"document": "I was charged twice. Please fix this ASAP."},
            questions={
                "billing": Noul(instructions="Is this ticket about billing?"),
                "tone": Choice(
                    instructions="What is the customer's tone?",
                    criteria={"calm": None, "frustrated": None, "angry": None},
                ),
                "urgency": Score(
                    instructions="How urgent is this ticket?",
                    criteria=["can wait", "this week", "today"],
                ),
            },
        )

    print(response.nouls["billing"].noul)
    print(response.choices["tone"].choice)
    print(response.scores["urgency"].score)
```

Sync:

```python
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

with TypeSafeClient() as client:
    response = client.system_one(
        state={"document": "I was charged twice. Please fix this ASAP."},
        questions={
            "billing": Noul(instructions="Is this ticket about billing?"),
            "tone": Choice(
                instructions="What is the customer's tone?",
                criteria={"calm": None, "frustrated": None, "angry": None},
            ),
            "urgency": Score(
                instructions="How urgent is this ticket?",
                criteria=["can wait", "this week", "today"],
            ),
        },
    )

print(response.nouls["billing"].noul)
print(response.choices["tone"].choice)
print(response.scores["urgency"].score)
```

## Client construction

`TypeSafeClient(...)` and `AsyncTypeSafeClient(...)` take the same keyword-only parameters. Explicit options beat environment variables; empty or whitespace-only env values are ignored. Use as a context manager (`with` / `async with`) or call `close()` / `await aclose()`, which also closes a supplied `http_client` or `transport`.

| Param | Type | Default | Meaning |
|---|---|---|---|
| `api_key` | `str \| None` | `None` | Required; falls back to `TYPESAFE_API_KEY`. |
| `model` | `str \| None` | `None` | Falls back to `TYPESAFE_DEFAULT_MODEL`, then `jev-latest`. |
| `retry` | `RetryPolicy \| None` | `None` | Retry policy; `None` = `RetryPolicy()` defaults. `RetryPolicy(max_retries=0)` disables retries. |
| `timeout` | `float \| httpx2.Timeout \| None` | `None` | Per HTTP operation, seconds. Inherits `http_client.timeout` when supplied, otherwise `DEFAULT_TIMEOUT = 10.0`. |
| `headers` | `Mapping[str, str] \| None` | `None` | Extra headers on every request. |
| `transport` | `httpx2.BaseTransport \| None` (async: `AsyncBaseTransport`) | `None` | Custom transport; closed with the client. Mutually exclusive with `http_client`. |
| `http_client` | `httpx2.Client \| None` (async: `AsyncClient`) | `None` | Supplied client; closed with the SDK client. |
| `base_url` | `str \| None` | `None` | Falls back to `TYPESAFE_BASE_URL`, then `https://api.typesafe.ai`. |

Raises `TypeSafeError` (missing key, invalid timeout) or `ValueError` (both `transport` and `http_client`).

`client.models` is a cached property; `client.models.list(*, retry=None, timeout=None, extra_headers=None) -> ListModelsResponse` (awaited on the async client).

## `system_one`

```python
system_one(
    state: JSONContent,
    questions: Mapping[str, Question],
    *,
    model: str | None = None,
    retry: RetryPolicy | None = None,
    timeout: float | httpx2.Timeout | None = None,
    extra_headers: Mapping[str, str] | None = None,
    extra_body: Mapping[str, JSONValue | None] | None = None,
) -> SystemOneResponse
```

Async: `await client.system_one(...)`, same signature. `state` and `questions` may be passed positionally.

| Param | Meaning |
|---|---|
| `state` | `str`, mapping, or sequence. Cannot be `None`; nested values may be. |
| `questions` | Non-empty mapping of id to `Noul`/`Choice`/`Score` or raw dict (`NoulModel`/`ChoiceModel`/`ScoreModel`). Mixing is allowed. |
| `model` | Per-call override; `None` inherits the client default. |
| `retry`, `timeout`, `extra_headers` | Per-call overrides of the client values. |
| `extra_body` | Extra top-level body fields, shallow-merged last-write-wins over `state`, `model`, `questions`; object values replaced, not deep-merged. |

Raises `TypeSafeError` (empty questions, empty Score criteria), `TypeSafeAPIError` (non-2xx after retries), `TypeSafeAPIConnectionError` (cannot connect or timed out after retries).

## Question types

Type aliases: `JSONValue = str | int | float | bool | Sequence[JSONValue | None] | Mapping[str, JSONValue | None]`; `JSONContent = str | Mapping[str, JSONValue | None] | Sequence[JSONValue | None]`.

| Constructor | Fields | Notes |
|---|---|---|
| `Noul(instructions=None, criteria=None)` | `instructions: JSONContent \| None`; `criteria: NoulCriteria \| None` | |
| `NoulCriteria(true=..., false=...)` | `TypedDict`; `true: JSONContent \| None`, `false: JSONContent \| None` | `None` leaves that outcome undescribed. |
| `Choice(instructions=None, criteria=...)` | `criteria: Mapping[str, JSONContent \| None]` (required) | `None` value = undescribed label. |
| `Score(instructions=None, criteria=...)` | `criteria: Sequence[JSONContent]` (required, non-empty; API needs >= 2) | Index = level number from 0. Sequence, not dict, since 0.6.0. |

Raw dicts: `{"type": "noul" | "choice" | "score", "instructions": ..., "criteria": ...}`; extra JSON keys are allowed and forwarded. `Question = Noul | Choice | Score | QuestionModel`; `Questions = Mapping[str, Question]`.

## Response types

`SystemOneResponse`:

| Accessor | Type | Meaning |
|---|---|---|
| `answers` | `dict[str, Answer]` | All answers by question id; `Answer = NoulAnswer \| ChoiceAnswer \| ScoreAnswer`. |
| `nouls` | `dict[str, NoulAnswer]` | Cached property, Noul answers only. |
| `choices` | `dict[str, ChoiceAnswer]` | Cached property. |
| `scores` | `dict[str, ScoreAnswer]` | Cached property. |
| `model` | `str` | Versioned model that answered. |
| `usage` | `Usage` | `input_tokens: int \| None`, `output_tokens: int \| None` (None when not reported). |
| `request_id` | `str` | `x-typesafe-request-id` header. |
| `raw_http_response` | `httpx2.Response` | Status, headers, body. |

Answer classes:

| Class | Fields |
|---|---|
| `NoulAnswer` | `noul: float` |
| `ChoiceAnswer` | `choice: str`; `confidence: float`; `probabilities: dict[str, float]` |
| `ScoreAnswer` | `score: float`; `confidence: float`; `legend: dict[int, str \| dict \| list]`; `probabilities: dict[int, float]` |

Score `legend` and `probabilities` are keyed by `int` level (`probabilities[1]`), unlike the wire format and the JS SDK, which use string keys.

`ListModelsResponse`: `models: tuple[ModelMetadata, ...]` with `name`, `description`, `release_date` (all `str`), plus `request_id` and `raw_http_response`.

## `RetryPolicy`

```python
from typesafe_sdk import RetryPolicy, TypeSafeClient

client = TypeSafeClient(retry=RetryPolicy(max_retries=3, backoff_max=0.2, timeout=1.0))
client.system_one(state, questions, retry=RetryPolicy(max_retries=3, backoff_max=0.2, timeout=1.0))
```

| Field | Default | Meaning |
|---|---|---|
| `max_retries` | `2` | Retries after the first attempt; `0` disables. |
| `backoff_initial` | `0.5` | First delay in seconds, doubled per attempt; `0` disables backoff. |
| `backoff_max` | `5.0` | Cap on delay in seconds. |
| `backoff_jitter` | `0.25` | Fraction of each delay randomly subtracted, 0 to 1. |
| `http_statuses` | `{408, 429, *range(500, 600)}` | Statuses retried (covers 529). |
| `respect_retry_after` | `True` | Honor `Retry-After` and `retry-after-ms`. |
| `api_connection_error` | `True` | Retry `TypeSafeAPIConnectionError`. |
| `api_timeout_error` | `True` | Retry `TypeSafeAPITimeoutError`. |
| `exceptions` | `set()` | Extra exception types that trigger a retry. |
| `predicate` | `None` | `Callable[[BaseException], bool]`; `True` triggers a retry. |
| `timeout` | `30.0` | Total budget in seconds per SDK call, including the first attempt and delays; `None` = unlimited. Stops before a retry whose delay would reach the budget and re-raises the last error. |

Two different timeouts: `RetryPolicy.timeout` (30 s) bounds the whole call across retries; the client/call `timeout` (`DEFAULT_TIMEOUT = 10.0` s) bounds each HTTP operation. Invalid `RetryPolicy` values are rejected since 0.6.0.

## Exceptions

All importable from `typesafe_sdk`.

| Exception | Base | When |
|---|---|---|
| `TypeSafeError` | `Exception` | Base for all SDK failures; also client-side validation (missing key, empty questions). |
| `TypeSafeAPIError` | `TypeSafeError` | Non-2xx after retries. Attrs: `status`, `body` (JSON, text, or `None`), `headers`, `endpoint`, `request_id`. |
| `TypeSafeBadRequestError` | `TypeSafeAPIError` | 400 |
| `TypeSafeAuthenticationError` | `TypeSafeAPIError` | 401 |
| `TypeSafePermissionDeniedError` | `TypeSafeAPIError` | 403 |
| `TypeSafeNotFoundError` | `TypeSafeAPIError` | 404 |
| `TypeSafeUnprocessableEntityError` | `TypeSafeAPIError` | 422 |
| `TypeSafeRateLimitError` | `TypeSafeAPIError` | 429; adds `retry_after_ms: int \| None`. |
| `TypeSafeInternalServerError` | `TypeSafeAPIError` | 5xx (includes 529) |
| `TypeSafeAPIResponseValidationError` | `TypeSafeAPIError` | 2xx with missing or invalid required data; adds `field_path` such as `answers.tone.confidence`. |
| `TypeSafeAPIConnectionError` | `TypeSafeError`, `ConnectionError` | No HTTP response (DNS, TLS, closed connection). |
| `TypeSafeAPITimeoutError` | `TypeSafeAPIConnectionError`, `TimeoutError` | Exceeded the per-operation timeout; adds `timeout`. |

```python
from typesafe_sdk import TypeSafeAPIError

try:
    client.system_one(state, questions)
except TypeSafeAPIError as error:
    print(error.status, error.request_id)
```

## Logging

Logger name `typesafe_sdk`. `info` logs one summary line per request; `debug` adds request and response headers and bodies. Authorization, API key, cookie, and any header containing `token` or `secret` are redacted; bodies are not, so `debug` logs your state.

```python
import logging

logging.getLogger("typesafe_sdk").setLevel(logging.DEBUG)
```

Or set `TYPESAFE_LOG_LEVEL` to `debug`, `info`, `warning`, `error`, or `off` before import (applied once at import time).

## Environment variables and constants

| Variable | Constant (`typesafe_sdk.constants`) | Default constant |
|---|---|---|
| `TYPESAFE_API_KEY` | `API_KEY_ENV` | none, required |
| `TYPESAFE_BASE_URL` | `BASE_URL_ENV` | `DEFAULT_BASE_URL = 'https://api.typesafe.ai'` |
| `TYPESAFE_DEFAULT_MODEL` | `DEFAULT_MODEL_ENV` | `DEFAULT_MODEL = 'jev-latest'` |
| `TYPESAFE_LOG_LEVEL` | `LOG_LEVEL_ENV` | unset |
| | `DEFAULT_TIMEOUT` | `10.0` seconds per HTTP operation |

The usage page's `TypeSafeClient(model="jev")` is not a listed model name; use `jev-latest` or a pinned `jev-1.13.0`.

## Forward compatibility

`beam_width` and `weight` below are the docs' placeholder illustrations of passthrough; neither is a documented API field. Do not use them as real features.

```python
from typesafe_sdk import Noul, TypeSafeClient

with TypeSafeClient() as client:
    client.system_one(
        "I was charged twice.",
        {"billing": Noul(instructions="About billing?")},
        extra_body={"beam_width": 4},
    )
```

```python
from typesafe_sdk import TypeSafeClient

with TypeSafeClient() as client:
    client.system_one(
        "I was charged twice.",
        {"billing": {"type": "noul", "instructions": "About billing?", "weight": 2}},
    )
```

Unknown answer kinds are skipped with a warning; read them from `result.raw_http_response.json()["answers"]`. Unknown extra fields on recognized responses are ignored.

## Changelog

| Version | Date | Changes |
|---|---|---|
| 0.6.0 | 2026-09-15 | Breaking: `Score.criteria` is an ordered sequence, not a dict keyed by int. Inputs accept `Mapping`/`Sequence`; error messages include HTTP details; invalid `RetryPolicy` values handled; exceptions and responses picklable. |
| 0.5.7 | 2026-09-14 | Initial public release. |
