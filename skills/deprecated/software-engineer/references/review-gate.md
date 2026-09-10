# Review Gate

The Reviewer lens, run against your own diff as a definition-of-done. The same standard a great reviewer applies to a finished diff — applied here by the author, to their own work, before declaring a step complete. Code that works but would not survive this gate is not done.

## Table of Contents

- [Output Prioritization](#output-prioritization)
- [The Approval Bar: Presumptive Blockers](#the-approval-bar-presumptive-blockers)
- [Definition Of Done](#definition-of-done)
- [Production-Readiness Checklist](#production-readiness-checklist)
- [Self-Review Prompts](#self-review-prompts)

---

## Output Prioritization

When reviewing a diff (including your own), surface findings in this priority order — highest-leverage first. Prefer a few high-conviction findings over a flood of nits; a long list of trivia buries the one structural problem that matters.

1. **Structural regressions** — the change makes the local architecture worse.
2. **Missed dramatic-simplification / code-judo opportunities** — a reframing would delete whole categories of complexity.
3. **Spaghetti / branching increases** — new ad-hoc conditionals tangled into existing flows.
4. **Boundary, abstraction, and type-contract problems** — leaked logic, weak or cast-heavy contracts, unnecessary abstractions.
5. **File-size and decomposition** — files crossing ~1000 lines, missing extractions.
6. **Modularity and abstraction** — cohesion lost, coupling gained.
7. **Legibility and maintainability** — the lowest tier; real, but never ahead of the above.

## The Approval Bar: Presumptive Blockers

Your code **is not done** if any of these is true. Each is a presumptive blocker — the bar is "fix it or have a genuinely strong, stated reason."

- It **preserves incidental complexity** that a plausible code-judo move would delete.
- It **pushes a file from under ~1000 lines to over** without a strong reason.
- It **adds ad-hoc branching that tangles an existing flow** instead of reaching for a dedicated abstraction.
- It **scatters feature checks across shared code** rather than keeping feature logic in its own scope.
- It **adds an unnecessary abstraction, wrapper, or cast-heavy contract** that doesn't earn its keep.
- It **duplicates an existing helper, or misplaces logic, when a clear canonical home exists.**

## Definition Of Done

Before declaring a step complete, confirm:

- [ ] None of the presumptive blockers above apply (or each that does has a strong, stated reason).
- [ ] The change reuses existing patterns, helpers, and components rather than near-duplicating them.
- [ ] Logic lives in its canonical layer; nothing leaked into a shared path or across an API boundary.
- [ ] Contracts are explicit and typed; no `any`/`unknown`, casts, or needless optionals were added to dodge the type system.
- [ ] No placeholders, TODOs, or stubs remain — every path is complete.
- [ ] The change matches existing project conventions (style, structure, naming, error handling).
- [ ] The relevant domain standards (`domain-standards.md`) for this layer are satisfied.
- [ ] The production-readiness checklist below passes.
- [ ] The code was actually run and verified, not just written.

## Production-Readiness Checklist

- [ ] **Error handling** — every failure path is considered; errors carry enough context to diagnose without a repro.
- [ ] **Structured logging** — appropriate levels, no secrets or PII leaked.
- [ ] **Observability** — the metrics/logs/traces needed to answer "is it healthy?" and "why did that fail?" exist.
- [ ] **Graceful degradation** — a slow or down dependency degrades the experience rather than taking the system down.
- [ ] **Input validation** at every external boundary; nothing from outside is trusted.
- [ ] **Atomicity** — related updates apply together or not at all; no half-applied state.
- [ ] **Security baseline** — authz checked on protected actions, secrets out of code/logs, dependencies pinned (see the Security Standards section of `domain-standards.md`).

## Self-Review Prompts

Phrase the review to yourself in the first person. These are the questions a demanding reviewer would ask — asked here by the author, of their own diff.

- "Is there a structural move that makes this dramatically simpler — can I reframe so a whole branch, mode, or layer disappears?"
- "Does this push the file past ~1000 lines — can I decompose first, then add my change to the focused home?"
- "Did I just bolt another `if` onto an existing flow — does a helper, state machine, or dispatcher belong here instead?"
- "Did this make a cohesive module more coupled, more stateful, or harder to scan?"
- "Is this abstraction earning its keep, or is it a thin wrapper that only adds a hop? Should I delete it?"
- "Does every name I introduced say honestly what it does or holds — and if I can't find an honest name, what's murky about the design?"
- "Did I reach for `any`, a cast, or an optional to quiet the compiler instead of modeling the real contract?"
- "Is a primitive standing in for a domain concept, or are the same fields travelling together — should a type be born here?"
- "Am I papering over an unclear invariant with a silent fallback — should the boundary be explicit and loud?"
- "Is this logic in the right layer and package, or did I add it to the first file I happened to open?"
- "Does a canonical helper already do this — am I about to author a near-duplicate?"
- "Did feature-specific logic leak into a shared module, or implementation details leak through an API?"
- "Is this work serialized when the pieces are independent — should it run in parallel?"
- "Are these related updates structured to apply atomically, or could they leave a half-applied state?"
- "If a great reviewer saw only this diff, what is the one thing they would block on — and have I already fixed it?"
