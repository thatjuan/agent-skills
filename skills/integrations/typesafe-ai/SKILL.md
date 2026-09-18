---
name: typesafe-ai
description: "Build application logic on TypeSafe AI's Jev decision model: send a state plus typed Choice, Score, and Noul questions, get calibrated answers, and keep control flow in code. Use when code imports `typesafe_sdk` or `@typesafe-ai/sdk`, calls `api.typesafe.ai`, or reads `TYPESAFE_API_KEY`; when the user mentions TypeSafe, Jev, System One, or Noul; or when an app needs classification, triage, routing, scoring, ranking, verification, guardrails, or extraction checks over text with a confidence signal, where prompting a chat LLM for JSON would be the default."
---

# TypeSafe AI

Jev is a **decision model**, not a text generator. One request carries a `state` (string, JSON object, or array of text) and a map of typed questions; every question is answered in parallel against the same state in roughly 100 ms, and every answer comes back as a calibrated probability distribution. It never writes prose, code, or explanations, accepts text only, and is not fine-tunable. **Code owns control flow**: rules, math, dates, counting, and side effects stay in code, and Jev supplies narrow judgments over unstructured text.

## Request shape

```
POST https://api.typesafe.ai/v1/systemone
Authorization: Bearer $TYPESAFE_API_KEY
{ "state": ..., "model": "jev-latest", "questions": { "<id>": {...}, ... } }
```

| Primitive | Asks | `criteria` | Answer fields |
|---|---|---|---|
| `choice` | Pick one of N unordered options | `{ option: description \| null }`, up to 255 | `choice`, `probabilities`, `confidence` |
| `score` | Position on an ordered rubric | array of 2 to 10 level descriptions, low to high | `score` (probability-weighted mean of level indices, fractional), `legend`, `probabilities`, `confidence` |
| `noul` | Probability a yes/no statement is true | optional `{ true: ..., false: ... }` | `noul` in [0, 1], no confidence field |

Question ids are for your code and are never sent to the model. `instructions` and every criteria value accept a string, JSON object, array, or null, so structured descriptions (`what`, `not_for`, `examples`, any names you choose) are allowed anywhere. Full schemas, errors, limits, and model ids: [`references/api.md`](references/api.md).

## Design process

Work through these in order. The process is done when **every judgment the feature needs is either computed in code or is exactly one atomic question, and every answer is consumed by code or dropped on purpose.**

1. **Split the feature into judgments and computation.** Anything exact (arithmetic, date comparison, counting, string matching, lookups) is code. Jev gets only the judgments that need reading comprehension.
2. **Make each judgment atomic.** A broad question hides several judgments behind one answer. "Should we refund?" becomes `wants_refund` (Noul), `order_within_window` (code), `damage_reported` (Noul), `tone` (Choice). Atomic questions can be inspected, thresholded, and weighted separately.
3. **Pick the primitive.** Yes/no fact: Noul. Exactly one of N: Choice. Several labels may apply: one Noul per label. Ordered spectrum: Score. A Noul of 0.5 means "equally likely yes or no", never "medium", so a spectrum is always a Score.
4. **Write criteria as situations, not degrees.** Each Choice description separates its option from its neighbours; each Score level describes a recognisable situation ("workaround exists") because the model judges every level alone and never sees its number or neighbours; add `other` when the options may not cover the input. Noul `true` is the case that triggers action. When the model selects among candidates you found in code (spans, ids, lines), the candidate list must contain the right answer, since the model cannot choose an omitted value. Detail in [`references/question-design.md`](references/question-design.md).
5. **Shape the state.** Prefer an object with descriptive keys, include only what the questions need, and point questions at parts of it with backticked paths (`` `ticket.messages[0].text` ``). Accuracy falls as irrelevant state grows.
6. **Fan out.** Put every question you might need in one request, including ones that only matter for some inputs, with the premise stated in the question ("If the customer wants to return something, why?"), and let code ignore the rest. Questions are cheap and parallel; a second request is justified only when its state or options depend on the first answer.
7. **Compose in code.** Branch on `choice`, normalise `score / (len(criteria) - 1)` before weighting, aggregate verifier Nouls with `max` so one confident red flag escalates, and read `probabilities` when the rule is statistical. Keep raw answers and policy apart so a changed weight or threshold reruns no inference. Recipes: [`references/patterns-and-cookbooks.md`](references/patterns-and-cookbooks.md).
8. **Gate with confidence.** Three bands per action: act, confirm, escalate to a human or fallback. Thresholds scale with stakes and are tuned on your data; picking the best option needs no threshold at all. Confidence describes how peaked the distribution is, not whether the answer is right.

Keep questions and thresholds in one reviewable module. Agents write weak criteria more often than people do, so present the question module to the user for review before wiring it into control flow.

## Hard rules for jev-1.13

- Jev answers the question you wrote, not the one you meant. Literal wording wins.
- Math, counting, date ordering, and exact magnitudes between Score levels live in code.
- Double negatives and multi-hop indirection degrade answers; ask the direct question.
- State is data, not trusted input. Adversarial text can move answers, so screen it with its own Nouls (see the guardrails and RAG cookbooks) before acting.
- Thresholds do not transfer between primitives, and separate questions obey no arithmetic identity. A Choice is relative across options; one Noul per option is absolute and can be low for all.
- Chaining choices to generate text is unsupported and slow.

Full failure-mode catalogue with workarounds: [`references/model-jaggedness.md`](references/model-jaggedness.md).

## SDK quick start

Python (`pip install typesafe-sdk`, 3.10+; client reads `TYPESAFE_API_KEY`):

```python
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

QUESTIONS = {
    "department": Choice(
        instructions="Which team should handle this?",
        criteria={"billing": "Charges, invoices, payment problems", "shipping": "Delivery status, delays, lost packages"},
    ),
    "frustration": Score(
        instructions="How frustrated is the customer?",
        criteria=["Calm, just stating facts", "Frustrated but civil", "Very angry, strong language"],
    ),
    "is_urgent": Noul(instructions="The message conveys urgency or time-sensitivity"),
}

with TypeSafeClient() as client:
    r = client.system_one(state={"ticket": ticket_text}, questions=QUESTIONS)
dept = r.choices["department"]          # .choice, .probabilities, .confidence
frustration = r.scores["frustration"]   # .score, .probabilities[1] (int-keyed), .legend
urgent = r.nouls["is_urgent"].noul
```

TypeScript (`npm install @typesafe-ai/sdk`, Node 20+; answer types are inferred from the question map):

```ts
import { TypeSafeClient, choice, score, noul } from "@typesafe-ai/sdk";

const client = new TypeSafeClient();
const { answers } = await client.systemOne({
  state: { ticket },
  questions: {
    department: choice("Which team should handle this?", { billing: "Charges, invoices, payment problems", shipping: "Delivery status, delays, lost packages" }),
    frustration: score("How frustrated is the customer?", ["Calm, just stating facts", "Frustrated but civil", "Very angry, strong language"]),
    isUrgent: noul("The message conveys urgency or time-sensitivity"),
  },
});
answers.department.choice;        // "billing" | "shipping"
answers.frustration.probabilities; // string-keyed: "0", "1", "2"
answers.isUrgent.noul;
```

Keys stay server-side; the JS client refuses to run in a browser unless `dangerouslyAllowBrowser` is set. Both SDKs retry 408, 429, and 5xx with backoff by default. Python `RetryPolicy.timeout` is a 30 s total budget; JS `timeout` is 10 s per attempt with no total budget. Client, types, errors, and options: [`references/sdk-python.md`](references/sdk-python.md), [`references/sdk-javascript.md`](references/sdk-javascript.md).

## Limits and versioning

| Item | Value |
|---|---|
| Choice options | 255 per question; past that, narrow in two stages |
| Score levels | 2 to 10 |
| Context | 64k tokens per request; 32k for state plus the longest single question |
| Rate limits | 250k tokens/s, 1,200 requests/min, adjusted without notice |
| Price | $0.042 per million input tokens; output free |
| Models | `jev-1.13.0`; aliases `jev-latest` (SDK default) and `jev-preview` both resolve to it |

Develop on `jev-latest`, then pin `jev-1.13.0` once thresholds are tuned, and log `response.model` so drift is visible. Non-English input works with lower accuracy; test on your own content.

## References

| File | Contents |
|---|---|
| [references/api.md](references/api.md) | HTTP schemas, request/response example, error codes, models, pricing, limits, env vars |
| [references/sdk-python.md](references/sdk-python.md) | Client, question and answer classes, `RetryPolicy`, exceptions, logging, changelog |
| [references/sdk-javascript.md](references/sdk-javascript.md) | Client config, helpers, inferred types, `APIPromise`, errors, changelog, full three-primitive example |
| [references/question-design.md](references/question-design.md) | Choosing primitives, writing instructions and criteria, structured criteria, taxonomy walking, state design, confidence bands, house-style triage example |
| [references/patterns-and-cookbooks.md](references/patterns-and-cookbooks.md) | The four patterns, every cookbook as problem shape plus recipe plus thresholds, when a second request is justified, use-case map |
| [references/model-jaggedness.md](references/model-jaggedness.md) | jev-1.13 failure modes with workarounds |

The references are a snapshot of docs.typesafe.ai taken 2026-09-17. For anything they lack, or when a version newer than jev-1.13 or SDK 0.6.0 is in play, fetch `https://docs.typesafe.ai/llms.txt` and read pages as `<path>.md`.
