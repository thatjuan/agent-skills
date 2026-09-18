# typesafe-ai

> Expertise for TypeSafe AI's Jev decision model: send a state plus typed Choice, Score, and Noul questions, get calibrated probabilities back, and keep control flow in code.

## What it does

`typesafe-ai` makes your agent fluent in the System One API and both SDKs, and, more importantly, in the design process that decides what to ask. Jev is a decision model, not a text generator: one request carries a `state` and a map of typed questions, every question is answered in parallel against that state in roughly 100 ms, and every answer is a calibrated probability distribution. The skill covers:

- **The three primitives**: `choice` (one of up to 255 unordered options), `score` (a 2 to 10 level ordered rubric, answered as a fractional probability-weighted mean), and `noul` (probability a yes/no statement is true).
- **The design process**: split the feature into judgments and computation, make each judgment atomic, pick the primitive, write criteria as situations rather than degrees, shape the state, fan out, compose in code, gate with confidence.
- **Question design**: instructions, Choice and Score and Noul criteria, structured (object or array) criteria, taxonomy walking, state design, and confidence bands.
- **Patterns and cookbooks**: speculative fan-out, confidence-gated routing, composite scoring, intent routing, plus recipes for verifier batteries, search and rerank, pre-parsed extraction, function calling, entity alignment, and hierarchical classification.
- **Model jaggedness**: the jev-1.13 failure modes with workarounds, covering literal reading, math and counting, dates, double negatives, irrelevant state, adversarial content, and text generation.
- **Both SDKs**: `typesafe-sdk` for Python and `@typesafe-ai/sdk` for TypeScript, including inferred answer types, retry and timeout defaults, and the differences between them.
- **Limits and versioning**: context budget, rate limits, pricing, and the `jev-latest` to pinned-version workflow.

It triggers when code imports `typesafe_sdk` or `@typesafe-ai/sdk`, calls `api.typesafe.ai`, or reads `TYPESAFE_API_KEY`; when the user mentions TypeSafe, Jev, System One, or Noul; or when a feature needs classification, triage, routing, scoring, ranking, verification, guardrails, or extraction checks over text with a confidence signal.

## When to use it

Invoke this skill when you hear:

- *"Route these support tickets to the right queue and escalate the angry ones."*
- *"Check whether this LLM answer is actually supported by the cited passages."*
- *"Rank these candidates against the job description on several criteria."*
- *"Should this be a Score or several Nouls?"*
- *"Pull the delivery date out of this email without the model inventing one."*
- *"Add a guardrail that screens user input before we act on it."*

## Example walkthrough

Asked to build ticket triage, the skill first splits the feature: order age and refund windows are date math, so they stay in code, and only the reading-comprehension parts go to Jev. It writes atomic questions (a `department` Choice whose option descriptions separate neighbours, a `frustration` Score whose levels each describe a recognisable situation, an `is_urgent` Noul) and fans every one of them, including the branch-specific ones, into a single request with the premise stated in the question. Code then branches on `choice`, normalises `score / (len(criteria) - 1)` before weighting, and applies three confidence bands: act, confirm, escalate to a human. Questions and thresholds live in one reviewable module, presented for review before it is wired into control flow, so retuning a threshold reruns no inference.

## Installation

```bash
npx skills add thatjuan/agent-skills --skill typesafe-ai
```

## Bundled resources

| File | Purpose |
|------|---------|
| `SKILL.md` | Request shape, the three primitives, the eight-step design process, hard rules for jev-1.13, SDK quick start, limits and versioning |
| `references/api.md` | HTTP schemas, request/response example, error codes, models, pricing, limits, env vars |
| `references/sdk-python.md` | Client, question and answer classes, `RetryPolicy`, exceptions, logging, changelog |
| `references/sdk-javascript.md` | Client config, helpers, inferred types, `APIPromise`, errors, changelog, full three-primitive example |
| `references/question-design.md` | Choosing primitives, writing instructions and criteria, structured criteria, taxonomy walking, state design, confidence bands, house-style triage example |
| `references/patterns-and-cookbooks.md` | The four patterns, every cookbook as problem shape plus recipe plus thresholds, when a second request is justified, use-case map |
| `references/model-jaggedness.md` | jev-1.13 failure modes with workarounds |

## Tips

- **Question ids are never sent to the model.** They exist for your code, so all the meaning has to live in `instructions` and `criteria`.
- **A Noul of 0.5 means "equally likely yes or no", never "medium".** Anything on a spectrum is a Score; a yes/no fact is a Noul; several labels that may all apply are one Noul each.
- **Fan out every question you might need into one request.** Questions run in parallel and add no latency, so state the premise inside the speculative ones and let code ignore the answers that do not apply. A second request is justified only when its state or options depend on the first answer.
- **Math, counting, date ordering, and exact magnitudes stay in code.** Jev gets only the judgments that need reading comprehension; everything exact is computed.
- **Score `probabilities` are int-keyed in Python and string-keyed in JavaScript** (`probabilities[1]` vs `probabilities["1"]`), so ported code silently misses.
- **Develop on `jev-latest`, then pin `jev-1.13.0` once thresholds are tuned**, and log `response.model` so drift is visible. Thresholds do not transfer between primitives or across versions.

## Related skills

- None in this repo yet. Pair with any classification, triage, or guardrail work.
