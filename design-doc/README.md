# design-doc

> Expert author and reviewer of software design documents — the written artifact an engineer produces *before* building, to think through the decisions that are expensive to get wrong. Grounded in "Write an Effective Design Doc" from *Refactoring English* by Michael Lynch.

## What it does

`design-doc` writes and reviews **technical design documents** (a.k.a. tech specs, engineering design proposals, internal RFCs, architecture decision docs). It treats a design doc as two things at once — a **decision-forcing tool** that surfaces costly choices before code exists, and a **communication tool** that lets teammates pressure-test the plan — and it optimizes for the thing most docs get wrong: knowing **what to leave out**.

It carries the judgment for three questions:

- **Should this project have a doc at all?** A six-question checklist (coordination, duration, lifespan, cross-team, ambiguity, catastrophic risk). Sometimes the right answer is *no doc* — and the skill will say so.
- **What belongs in it?** One filter governs every inclusion and every cut: **"What's the penalty for being wrong?"** Irreversible decisions (language, storage, interfaces, trust boundaries) go in; reversible afternoon-to-change details stay out.
- **How do you write it so it works?** The doc must **stand on its own** for a reader who never spoke to you — plain-language objective, outcome-shaped goals, measurable-not-vague SLOs, inline definitions over glossaries, editable source-linked diagrams.

It guards against the two ways design docs fail: **under-writing** (skipping the irreversible decisions and painting yourself into a corner) and **over-writing** (specifying every detail until you've written the implementation in prose).

## When to use it

Invoke this skill when the user wants a design doc **written, scoped, or reviewed**:

- *"Write a design doc for adding a caching layer in front of our Postgres database."*
- *"Draft an RFC for migrating our auth service to a new identity provider."*
- *"Does this project even need a design doc? It's a 2-week internal tool."*
- *"Review my tech spec — is it missing anything, and is it over-specified?"*
- *"Help me scope this — what sections do I actually need for a multi-year platform that handles PII?"*
- *"Turn this braindump of architecture decisions into a structured design doc."*

**Not the right skill if** the user wants a *creative/visual/brand* design spec (→ [`creative-director`](../creative-director/) for brand and UI concepts, [`logo-studio`](../logo-studio/) for logo and asset systems), or wants the code itself written (→ [`software-engineer`](../software-engineer/)). This skill produces the upstream *thinking-and-deciding* document those build on.

## Example walkthrough

**Prompt**

> Write a design doc for a caching layer between our Trogdor web app and its Postgres database. Pages used to load in 100ms, now they're at 600ms, and 95% of lookups hit the same 3% of rows.

**What the skill does**

1. **Decides a doc is warranted** — runs the checklist: multi-year production code, real performance risk, an interface other code depends on. Clears the bar.
2. **Decides what belongs** via penalty-for-being-wrong — language and the system-of-record (Postgres stays authoritative) are high-penalty and go in; the eviction algorithm and key encoding are reversible and are deliberately *left to code*.
3. **Drafts the right subset** — Objective (one plain sentence), a quantified Background (100ms → 600ms, 95%/3%) that makes the solution feel inevitable, outcome Goals, fenced Non-goals ("not a general-purpose cache"), a `Store`-interface seam, measurable SLOs (p50 ≤ 200ms), monitoring alerts, an honest Open Issues list (cross-replica invalidation), and brief Alternatives (read replicas, Redis-from-day-one).
4. **Makes it stand alone** — runs the writing-craft self-edit so a partner-team engineer who never spoke to the author understands *what* and *why* by the end of page one.

The result is the fully written **RecencyBank** doc in [`references/worked-example.md`](references/worked-example.md) — right-sized, measurable, and reviewable.

## Installation

```bash
npx skills add thatjuan/agent-skills --skill design-doc
```

## Bundled resources

| File | Purpose |
|------|---------|
| `SKILL.md` | The thesis, the two failure modes, and the five-phase workflow (decide whether → decide what belongs → draft → make it stand alone → drive through review) |
| `references/section-catalog.md` | Every section the article defines, grouped into six clusters, each with its purpose, the questions it answers, a good vs bad example, and when to include it |
| `references/writing-craft.md` | The communication layer — the stand-alone test, plain-language objectives, outcome goals, measurable-not-vague, inline-over-glossary, editable diagrams, naming — with before/after rewrites and a self-edit pass |
| `references/worked-example.md` | A complete, right-sized, annotated exemplar (the RecencyBank caching layer) to imitate end to end |
| `references/review-and-lifecycle.md` | The judgment layer — the when-to-write checklist, the penalty-for-being-wrong framework, right-sizing, driving the doc through review, and the open/resolved-issue lifecycle |

## Tips

- **The skill's best answer is sometimes "don't write one."** If the project doesn't clear the when-to-write bar, a doc is ceremony. The checklist protects your time.
- **The hard part is subtraction.** A good design doc is defined by what it leaves out. If a decision costs an afternoon to reverse, it doesn't belong in the doc — it belongs in the code.
- **Lead with Background.** Most docs fail on page one by assuming shared context. Write the Background as if the reader will see it before you ever explain the project — because they will.
- **Replace every soft adjective with a number.** "Fast," "scalable," and "performant on mobile" are unreviewable. "p50 ≤ 200ms" is a promise a metric can check.
- **Pair it with [`software-engineer`](../software-engineer/).** Once the design is agreed, hand it to the engineering layer that builds against it.

## Related skills

- [`software-engineer`](../software-engineer/) — the engineering layer that implements against an agreed design doc.
- [`implement-issue`](../implement-issue/) and [`team-executor`](../team-executor/) — orchestration that can take a design doc into planning and execution.
- [`creative-director`](../creative-director/) / [`logo-studio`](../logo-studio/) — the *creative/visual* design counterparts, for when "design" means brand and UI rather than systems and architecture.
