---
name: design-doc
description: Expert author and reviewer of software design documents (technical design docs, engineering design proposals, architecture decision docs, internal RFCs). Use when the user asks to write, draft, outline, structure, scope, right-size, or review a design doc, tech spec, RFC, or architecture proposal for a software system, feature, service, migration, or platform change — or asks whether a project even needs one. Produces a decision-forcing, audience-ready document grounded in the practices from "Write an Effective Design Doc" in Refactoring English by Michael Lynch — deciding when to write one, what belongs (judged by the penalty for being wrong), the section-by-section template, the writing craft that makes the doc stand on its own, and how to drive it through review. This is the engineering/technical design document, not a creative, visual, or brand design spec.
---

# Design Doc

Authors and reviews **software design documents** — the written artifact an engineer produces *before* building, to think through the decisions that are expensive to get wrong. This skill is the judgment for three questions the article centers on: **should this project have a doc at all**, **what goes in it**, and **how do you write it so it actually works** on a reader who never spoke to you.

A design doc is not a formality or a status report. Its purpose is leverage:

> A good design doc can save you years of development time. Writing a design doc forces you to think through important decisions before you waste time on the wrong implementation or paint yourself into a corner.

It is two things at once: a **decision-forcing tool** (writing the hard parts down surfaces the choices you'd otherwise discover mid-build, when they're costly to reverse) and a **communication tool** (it lets teammates, partner teams, and reviewers understand and pressure-test the plan before code exists).

## The Two Ways a Design Doc Fails

Hold both failure modes in mind the entire time. Every decision in this skill is about staying between them.

- **Under-writing** — skipping the doc, or omitting the decisions that are hard to reverse. You discover the mistake after 200k lines of C++, when a rewrite is unrecoverable. The cure is the *when-to-write* test and the *penalty-for-being-wrong* filter.
- **Over-writing** — specifying every detail (button spacing, every helper). *"If you specify every possible detail in a design doc, you've essentially written the implementation during the design phase. That would defeat the whole purpose of a design doc."* The cure is the same penalty-for-being-wrong filter, applied to cut.

Good design-doc work is almost entirely about **what to leave out**. Reach for high-cost-of-error decisions; let cheap, reversible choices be discovered in code.

## Phase 1 — Decide Whether to Write One

Not every project earns a doc. *"Sometimes, the right amount to invest in a design doc is zero."* Run the checklist — answer **yes** to any one and a doc is likely worth it; **two or more** and it almost certainly is:

1. Will **multiple people** coordinate work to implement the design?
2. Will the project take **more than three months** of full-time dev work?
3. Will the implementation run **in production for several years**?
4. Does the project involve **cross-team collaboration**?
5. Are the **goals and requirements ambiguous**?
6. Are there **catastrophic risks** (security, legal, data loss) you could prevent at design time?

If it clears the bar, scale the effort to the project's risks and deadlines — there is no universal "right length," just as there's no rule for how much to test. If it doesn't, say so and stop; recommending *no doc* is a valid, useful answer.

## Phase 2 — Decide What Belongs

One question governs every inclusion decision:

> **What's the penalty for being wrong?**

- **High penalty → put it in the doc.** Choices that are hard or impossible to reverse: programming language, storage backend, public interfaces, trust boundaries, data model, anything with multi-year lock-in. *"Think deeply about which dependencies will be difficult to change after implementation, and don't worry so much about the ones that swap out easily."* (Languages and storage backends are agony to change; the third-party email provider you can swap in an afternoon.)
- **Low penalty → leave it out.** Whether 1,000 articles render all at once or behind a "Load more" button costs an afternoon to change later — it does not belong in a design doc.

Then **select the section subset.** The catalog in [references/section-catalog.md](references/section-catalog.md) is a menu, not a mandate: *"You generally don't need every single section for every doc. Choose the subset that makes sense for you."* A small internal service may need only Objective, Background, Goals, Non-goals, Interfaces, and Alternatives. A multi-year platform with PII may need almost all of them.

## Phase 3 — Draft the Doc

Work from [references/section-catalog.md](references/section-catalog.md) — every section the article defines, grouped, each with its purpose, the questions it answers, a good/bad example, and an "include when." The canonical clusters:

| Cluster | Sections | Carries |
|---------|----------|---------|
| **Front matter** | Title · Metadata · Objective · Background · Related documents · Glossary | Orient a cold reader; one-sentence purpose; why this project exists. |
| **Scope (the contract)** | Goals · Non-goals · Constraints | Outcomes after launch, explicit out-of-scope, hard limits. |
| **The design** | Scenarios · Diagrams · Interfaces · Dependencies & infrastructure | How the built system behaves and fits together. |
| **Operability** | SLOs · Monitoring & alerting · Logging · Timeline | How you'll run it, measure it, and ship it in milestones. |
| **Risk & compliance** | Security · Privacy · Legal | Threats, sensitive data, regulatory and licensing obligations. |
| **Living sections** | Open issues · Resolved issues · Alternatives considered | Unresolved questions, their history, and the roads not taken. |

A full, imitable example doc — the **RecencyBank** caching layer, written right-sized and stand-alone end to end — is in [references/worked-example.md](references/worked-example.md). Read it before drafting; it is the target shape.

## Phase 4 — Make It Stand on Its Own

A design doc is a **writing** artifact, and most of them fail as writing, not as engineering. The governing test:

> Imagine what you'd say to a teammate or partner team before they read your design doc. Now realize that **some readers will see the doc before hearing any explanation from you.** Whatever they'd need to understand should be on the first page.

The craft rules that follow from this — write the Objective in plain language any stakeholder grasps; goals as *outcomes* not implementations; be **measurable, not vague** ("p50 latency ≤ 200ms," never "performant on mobile"); prefer recognizable terms and define them **inline** over burying them in a glossary; keep diagrams **editable** (Mermaid, D2, Excalidraw, draw.io — never a whiteboard photo) and link their source — live in [references/writing-craft.md](references/writing-craft.md) with before/after rewrites. Run them as a self-edit pass over every draft.

## Phase 5 — Drive It Through Review

The doc exists to be pressure-tested before code does. Circulate it, gather meaningful feedback, and track what's unresolved in **Open issues** (each with: the problem, the options, the immediate next step) — moving them to **Resolved issues** with the discussion intact for posterity as they close. Write the doc before writing code, and adhere to it as you implement, while accepting that details below the cost-of-error line are settled in code, not prose. Full guidance — the when-to-write rationale, the cost-of-error framework, right-sizing, circulating for feedback, and the issue lifecycle — is in [references/review-and-lifecycle.md](references/review-and-lifecycle.md).

## Bundled Resources

| File | When to Read |
|------|--------------|
| [references/section-catalog.md](references/section-catalog.md) | While drafting — every section the article defines, grouped into six clusters, each with purpose, the questions it answers, a good vs bad example, and when to include it. |
| [references/writing-craft.md](references/writing-craft.md) | During Phase 4 — the communication layer: the stand-alone test, plain-language objectives, outcome-shaped goals, measurable-not-vague, inline-over-glossary, editable diagrams, concision, naming, with before/after rewrites. |
| [references/worked-example.md](references/worked-example.md) | Before drafting — a complete, right-sized exemplar design doc (RecencyBank caching layer) to imitate end to end. |
| [references/review-and-lifecycle.md](references/review-and-lifecycle.md) | During Phases 1, 2, and 5 — the when-to-write checklist and rationale, the penalty-for-being-wrong framework, right-sizing investment, driving the doc through review, gathering feedback, and the open/resolved-issue lifecycle. |

## Scope Note

This skill writes the **engineering/technical** design document — systems, services, features, migrations, architecture. It is not the creative, visual, or brand "design" artifact. For brand identity and UI creative direction use `creative-director`; for logo and asset systems use `logo-studio`.
