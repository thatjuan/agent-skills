# Patterns and cookbooks

Match the problem in front of you to a row, then read that section. Every recipe keeps thresholds and weights in code beside the raw answers, so a policy change reruns no inference.

Harness note: `cooksafe` (`JsonCache` replay cache, `make_playground_link`) and the throwaway `uid` key some cookbooks add to `state` are cookbook harness conventions, not API features.

## Pick a pattern

| Problem shape | Pattern | Recipe |
|---|---|---|
| Several judgments, some only relevant for some inputs | [Fan-out](#speculative-fan-out) | Ask everything in one request; code ignores the rest |
| Clear answer, acting has stakes | [Confidence routing](#confidence-gated-routing) | Confidence floor, then per-action thresholds by consequence |
| Rank on several criteria | [Composite scoring](#composite-scoring) | One Score per dimension, normalise, weight in code |
| Requests need different handlers | [Intent routing](#intent-routing) | Choice for intent plus Score for complexity; code, LLM, or human |
| Classify, then trust the label or not | `classification_using_confidence` | Coarser parent label when confidence is low |
| Deep taxonomy | `hierarchical_classification` | One Choice per node, beam search over path probabilities |
| Verify an LLM's output | `citation_check`, `sde_cascade`, `llm_guardrails` | Nouls with `true` = wrong, aggregate with `max` |
| Find, gate, or rank passages | `semantic_find`, `rerank_typesafe`, `classifying_rag_passages` | Choice over ids to rank, Noul for "answer exists", Noul per pair to rerank |
| Exact value out of text | `pre_parsed_value_extraction`, `date_extraction` | Code finds candidates, Choice picks, code normalises |
| Sentence to a typed function call | `function_calling` | Choice per `Literal` arg plus a `stated` Noul |
| Two records, same thing? | `entity_alignment` | One 3-level Score rounded to nearest level |
| Free text into ML features | `autoresearch_feature_discovery` | LLM proposes Score/Noul questions, Jev answers per row |
| Repeatable decisions near a threshold | `consistency_choice`, `consistency_noul` | Explicit `uncertain` band sent to a human |
| One document, N questions | `parallel_questions` | One request; same answers, lower cost |
| Pick a skill or tool from a large roster | `skill_suggestion` | Wide Choice plus gate Nouls, then rerank top 3 with full text |

## Speculative fan-out

Source: `patterns/fan-out.md`. A decision tree whose later branches need judgments that only matter for some inputs. Parallel evaluation means extra questions add no latency.

1. List every judgment on every branch.
2. Send them all in one request, premise stated inside speculative questions.
3. Branch on the primary answer; read only what that branch needs.
4. Read cross-cutting answers (frustration, urgency) on every branch.

Questions on the page: `category` (Choice), `bug_severity` and `frustration` (3-level Scores), `has_reproducible_steps` and `refund_requested` (Nouls).

```python
category = response.answers["category"]
bug_severity = response.answers["bug_severity"]
bug_repro = response.answers["has_reproducible_steps"]
refund = response.answers["refund_requested"]
frustration = response.answers["frustration"]

if category.choice == "bug_report":
    if bug_severity.score > 1.5 and bug_repro.noul > 0.6:
        escalate_to_engineering(ticket_id, severity="high")
    else:
        add_to_bug_backlog(ticket_id)

elif category.choice == "billing":
    if refund.noul > 0.7:
        route_to_billing_with_flag(ticket_id, refund_likely=True)
    else:
        route_to_billing(ticket_id)

elif category.choice == "feature_request":
    log_feature_request(ticket_id)

# Frustration is useful regardless of category
if frustration.score > 1.5:
    flag_for_priority_response(ticket_id)
```

Thresholds: severity `> 1.5` on 0..2, repro `> 0.6`, refund `> 0.7`, frustration `> 1.5`.

## Confidence-gated routing

Source: `patterns/confidence-routing.md`. The answer says what; confidence says whether to act.

1. Ask intent as a Choice with an `other` option.
2. Set a floor below which nothing is automated.
3. Give each action its own threshold by stakes.
4. Between the floor and a high-stakes bar, confirm with the user.

```python
action = response.answers["intent"]

# Below 0.6 confidence on any action, route to a human
if action.confidence < 0.6:
    route_to_support_agent(account_id)

elif action.choice == "check_balance":
    # Low stakes. 0.6 confidence is sufficient.
    show_balance(account_id)

elif action.choice == "approve_transfer":
    if action.confidence > 0.85:
        approve_transfer(account_id)
    else:
        ask_user_to_confirm("Just to confirm: you would like to approve this transfer, is that correct?")

else:
    route_to_support_agent(account_id)
```

Thresholds: floor `0.6`; low stakes act at `0.6`; high stakes act `> 0.85`, otherwise confirm.

## Composite scoring

Source: `patterns/composite-scoring.md`. Ranking on several criteria where you want to see and adjust how the number is built.

1. One 5-level Score per independent dimension, levels written as situations.
2. Normalise by the top level index.
3. Weight in code, one weight set per role.
4. Retune weights when the top of the ranking looks wrong.

```python
py      = response.answers["python_depth"].score / 4
lead    = response.answers["team_leadership"].score / 4
arch    = response.answers["system_design"].score / 4
general = response.answers["generalist"].score / 4

# Senior IC
ic_score = (0.40 * py) + (0.10 * lead) + (0.40 * arch) + (0.10 * general)

# Engineering Manager
em_score = (0.15 * py) + (0.40 * lead) + (0.20 * arch) + (0.25 * general)
```

Weights: IC `0.40 / 0.10 / 0.40 / 0.10`; EM `0.15 / 0.40 / 0.20 / 0.25`.

## Intent routing

Source: `patterns/intent-routing.md`. A cheap classifier in front of handlers of different cost: code, a specialist LLM, or a human.

1. Ask `intent` (Choice) and `complexity` (3-level Score) in one request.
2. Below an intent confidence floor, go to a human.
3. Map each intent to a handler; use complexity to split one intent between LLM and human.
4. Treat low confidence on complexity as its own reason to escalate.

```python
def route_ticket(ticket_id, response):
    intent = response.answers["intent"]
    complexity = response.answers["complexity"]

    if intent.confidence < 0.5:
        return route_to_human_agent(ticket_id)

    if intent.choice == "order_status":
        handle_order_status(ticket_id)
    elif intent.choice == "product_question":
        handle_with_llm(ticket_id, PRODUCT_SPECIALIST)
    elif intent.choice == "return_exchange":
        handle_with_llm(ticket_id, RETURNS_SPECIALIST)
    elif intent.choice == "complaint":
        low_confidence = complexity.confidence < 0.5
        if complexity.score > 1 or low_confidence:
            route_to_human_agent(ticket_id)
        else:
            handle_with_llm(ticket_id, COMPLAINT_RESOLUTION)
```

Thresholds: intent confidence `< 0.5` to human; complaint escalates when complexity `score > 1` on 0..2 or complexity confidence `< 0.5`.

## Cookbook index

Sources: `cookbooks/*.md` (`cookbooks.md` duplicates `consistency_noul_cookbook.md`). Model is `jev-1.12` unless noted; the consistency cookbooks use `jev-latest` (resolved `jev-1.13.0`). One request per item unless noted.

| Cookbook | Problem | Question design | Composition rule | Thresholds / models | Result |
|---|---|---|---|---|---|
| `autoformat` | Rebuild Markdown from stripped text | Pass 1: Noul per adjacent line pair, "picks up mid-sentence". Pass 2 per block: Choice type (6 kinds) plus companion level, step, callout questions read only when relevant | `merge if join >= (0.5 if prev ends in punctuation else 0.2)`; `ordered = mean(step) >= 0.5` | 0.2 / 0.5 / 0.5 | 2 requests, 0.8 s; "same paragraph" wording collapsed lists |
| `autoresearch_feature_discovery` | Text into features for CatBoost | LLM proposes questions: `intensity` is a 5-level Score (mean, spread columns), `presence` a Noul; Jev answers per row | Keep an add unless flat (`spread < 0.05`); keep a revise or drop only if dev CV RMSE falls | `claude-sonnet-5` proposer; Score max 10 levels | RMSE 3.09 to 1.87 (one proposal) to 1.77 (5 rounds) |
| `citation_check` | Catch wrong LLM citations | Code string-matches the quote (missing = `fabricated`); one Choice `supports`, `contradicts`, `says_nothing` over `{claim, section}` | `verdict = MAP[choice]; auto = confidence >= 0.8` | 0.8 | 4 accurate at 0.93+; all 4 planted failures caught |
| `classification_using_confidence` | Many labels, trust the pick or not | One Choice over 75 SIC groups, options described by member industries | `group if confidence >= 0.9 else division(group)` | 0.9; Choice reliable to about 240 options | Confident half 90% right; unsure half 40% as group, 70% as division |
| `classifying_rag_passages` | Gate retrieved passages | 4 Nouls per `{query, passage}`: relevant, usable, contradicts premise, injection | First match: `injection > .70 exclude; contradicts > .70 conflict; relevant < .45 exclude; evidence > .55 include; else exclude` | .70 / .70 / .45 / .55, "a starting point, not defaults" | Injection ranked 1st by cosine, dropped at 0.99 |
| `consistency_choice_cookbook` | Repeatable moderation labels | 8 Choices over a JSON post, 15 repeats vs LLMs | `label if max(probabilities) >= 0.60 else "uncertain"` | 0.60 | Agreement 90.8% to 99.2%, 74.2% automatic; 114 ms per call |
| `consistency_noul_cookbook` | Repeatable claim probabilities | 14 Nouls over a JSON claim, 15 repeats vs LLMs | `no if p < .30; yes if p > .70; else uncertain` | .30 / .70 | Mean std dev 0.0102, below every LLM; 111 ms |
| `date_extraction_cookbook` | Dates without model arithmetic | 7 Choices: `mode` (absolute, relative, none), month, day, year (1900..2050 plus `none`, `out_of_range`), day_anchor, weekday, week_offset | Code assembles only the parts `mode` needs; `confidence = min(parts used)`; review if `< 0.60` or unassemblable | 0.60 | 6/6; the unstated date came back empty at 0.46, flagged |
| `entity_alignment` | Same entity or not | One 3-level Score (different, related, same) plus Nouls same name, brewery, style for the curator; ABV compared in code | `OUTCOME[round(score)]`: unlink, curator, merge; no threshold constant | Cut points 0.5 and 1.5 follow from level wording | 450 pairs: 40 merge, 50 curator, 360 unlinked |
| `function_calling` | Sentence to typed call | `__tool__` Choice over functions; per `Literal` arg a Choice plus a `stated` Noul (omit when false); `list[Literal]` gets a Noul per member; ints and free text get no question | Read the chosen function's answers only; `confidence = min`, not product | 54 questions per command | 14/14 correct, confidence 0.53 to 1.00 |
| `hierarchical_classification` | Leaf in a deep taxonomy | One Choice per node over direct children, one request per node per frontier | Beam K=3 by `product(p) ** (1/decisions)`; `exp(mean(log p))` past ~10 levels | K 3, depth 12 | Beam 4/4 leaves, greedy 2/4 |
| `llm_guardrails` | Screen LLM inputs and outputs | 4 Nouls per side (jailbreak or broke_policy, harmful_request, medical_advice, self_harm) plus a 4-level `severity` Score | `p >= action -> HAZARD_ACTION; p >= review -> review; severity >= 2.0 upgrades review to block; precedence support > block > review > pass` | strict .35 / .70, permissive .35 / .85 | Self-harm to support, fiction passes, DAN blocked |
| `parallel_questions` | N questions, one document | 8 Nouls, 2 Choices, 3 Scores over a 54k-char article, batched vs single | None; answers are independent of batching | 5 repeats | Identical answers; 12.2x cheaper, 10.0x faster |
| `pre_parsed_value_extraction_cookbook` | Copy an exact span | Regex over-finds; Choice over spans plus `none`; Choice for currency or country; Noul "is this a credit" | Code copies the pick verbatim and normalises | Past 255 candidates: section first, then span | Receipt 0.98, mobile 1.00, credit 0.99 vs charge 0.01 |
| `rerank_typesafe` | Reorder a fast-search shortlist | One Noul per `{query, candidate}`, "could this be the cited precedent" | `sorted(shortlist, key=noul, reverse=True)` | BM25 top 30, 1,200 calls, $0.0645 | Top-1 5% to 18%, top-10 38% to 62% |
| `sde_cascade` | Cheap extraction, escalate the wrong ones | Per-field Nouls with `true` = wrong (7 heads per filled field, `absence_wrong` per empty one); an `__overall__` judge shown but not gated on | `escalate = any(p > 0.7)` over per-field heads, a max gate | 0.7; `gpt-5.4-mini` extract, Jev verify, `gpt-5.5` escalate | Fabricated field caught at 0.95; cascade frontier beats every single model |
| `semantic_find` | Which line answers a query | Lines tagged `L000\|`; Choice over 218 line ids (criteria `None`) plus Noul "does any line answer", same request | Rank by Choice probabilities; `exists >= .7 answered; < .35 absent; else partial` | .7 / .35 | Absent answer: top line 0.86 but `exists` 0.14 |
| `skill_suggestion` | One skill from 182 per agent turn | Request 1: Choice over 182 names plus 3 Nouls on whether an action is wanted (`prose_suffices` inverted). Request 2: Choice over top 3 with full text plus a `fits` Noul per candidate | `none if mean(gate) < .30; none if max(fits) < .30; else winner` | .30 / .30, shortlist 3; agent `claude-haiku-4-5` | Wrong loads 16.8% to 7.3%, needless 9.8% to 4.0% |

Choice beyond 255 options, stated in `semantic_find` and `pre_parsed_value_extraction`: pick a window or section with one Choice, then rank inside it with a second. `skill_suggestion` says the same for rosters much larger than 182: chunk, rank each chunk, rerank the winners.

## When a second request is justified

Source: `primitives.md`, "When one question depends on another". Questions in one request are independent. A second request is justified only when code cannot build it until it has the first answer: to fetch more state, decide what the state is made of, or pick the next options. Otherwise fold it into the first request and let code ignore the extra answers.

- `hierarchical_classification`: each Choice answer decides which children the next request offers.
- `skill_suggestion`: rank 182 on one-line descriptions, then rejudge the top 3 with full text.
- `autoformat`: the stitch answers create the blocks the classify request is about.
- `semantic_find`, `pre_parsed_value_extraction`: past 255 options, pick a window, then the item inside it.
- `sde_cascade`: Jev between two LLM rungs; the second LLM call runs only when a flag fires. A chain across models, not two Jev requests.
- `rerank_typesafe` is not a chain: one request per pair; the page says a real app would fan several questions per pair into it.

## Use-case map

Source: `concepts/use-case-map.md`. Decision shapes for spotting a Jev-shaped feature request.

| Shape | Reach for it when | Examples |
|---|---|---|
| Classification | One known category should win | Intent, topic, department, entity type |
| Detection | Probability that one property is present | Spam, fraud, urgency, jailbreaks, sensitive data |
| Scoring | The answer sits on an ordered rubric | Severity, relevance, quality, frustration |
| Routing | A category selects the next code path | Tool use, escalation, model routing, queues |
| Search | Find items matching a natural-language query | Semantic search, candidate generation |
| Retrieval | A workflow needs the most relevant context | RAG context, evidence lookup |
| Ranking | Order items by relevance or quality | Search results, recommendations, prioritisation |
| Verification | Check an artifact for specific failure modes | Citations, policy violations, tool-call errors |
| ML feature extraction | A classical model needs semantic signals | Purchase intent, churn signals |
| Structured data extraction | Known fields from unstructured input | Candidate attributes, order fields |

Framing: unattended automation, real-time (about 150 ms), map-reduce over big data, verifying other AIs, harness engineering.

Domains:

- Search and retrieval: relevance scoring, reranking, context selection.
- Scientific discovery: paper screening, transcript labelling, citation checks, missing methods.
- Model routing: intent, domain, difficulty, risk; escalate to a costlier model.
- LLM guardrails: jailbreaks, policy violations, sensitive data, tool-call errors.
- Semantic code linting: team conventions as checks in CI.
- Feature extraction: probabilistic features from text for models with ground truth.
- Recruiting: competency evidence, role match, escalation.
- Lead generation: ICP fit, maturity, purchase intent.
- Customer support: ticket classification, urgency and churn, routing, reply verification.
- Insurance claims: FNOL classification, complexity, missing info, fraud indicators.
- Financial crime: transaction narratives, entity matching, alert prioritisation.
- Legal and compliance: contract classification, missing clauses, prohibited claims.
- E-commerce: listing normalisation, attribute extraction, counterfeit detection.
- Moderation: company-specific criteria; severity plus confidence to allow, warn, review, block.
- Advertising: brand safety, audience suitability, ad-to-landing-page alignment.
- Gaming: chat moderation, player reports, churn signals.
- Risk assessment: reports into probabilistic indicators for underwriting.
- Demand forecasting: intent, urgency, supply concerns as time-series features.
- Knowledge graphs: relationship and entity typing, contradictions, hierarchical traversal.
