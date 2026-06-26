# Review, Judgment & Lifecycle

The judgment layer of the skill: deciding **whether** to write a doc, **how much** to invest, how to **drive it through review**, and how it **lives** before and after the code. This is where a design doc earns or wastes its cost.

## When to Write One

A design doc is an investment, and like testing there is *"no universal rule that says how long you should spend."* Sometimes the right amount is **zero**. Run the checklist — **any one yes** makes a doc likely worth it; **two or more** and it almost certainly is:

1. Will **multiple people** coordinate work to implement the design?
2. Will the project take **more than three months** of full-time dev work?
3. Will the implementation run **in production for several years**?
4. Does the project involve **cross-team collaboration**?
5. Are the **goals and requirements ambiguous**?
6. Are there **catastrophic risks** you could prevent at design time (e.g. security, legal, irreversible data decisions)?

Recommending *no doc* is a legitimate outcome of this skill. A throwaway script, a spike, or a reversible one-afternoon change usually shouldn't have one — saying so is more valuable than generating ceremony.

## The Penalty-for-Being-Wrong Framework

The single filter for *what goes in the doc* — and for *how much detail*:

> **What's the penalty for being wrong?**

Think of every decision on a reversibility axis:

| Decision | Penalty if wrong | Belongs in the doc? |
|---|---|---|
| Programming language | Choose C++, write 200k lines, then need to switch → unrecoverable rewrite | **Yes — heavily** |
| Storage backend / data model | Migrations, dual-writes, months of pain | **Yes** |
| Public API / interface contract | Every client breaks; coordinated migration | **Yes** |
| Trust boundaries, PII handling | Breach, legal exposure | **Yes** |
| Third-party email provider | *"Replace it in an afternoon"* | No — barely |
| Pagination: all-at-once vs "Load more" | Low cost to change later | No |
| Log field names, button spacing | Trivial to change in code | No |

The same filter cuts **both** failure modes: it tells you the irreversible decision you must *include* (don't under-write), and it tells you the reversible detail you must *exclude* (don't over-write). *"Think deeply about which dependencies will be difficult to change after implementation, and don't worry so much about the ones that swap out easily."*

## Right-Sizing the Investment

There's no fixed length. Scale effort to *"your team's goals, risks, deadlines, and culture."* Practical dials:

- **Risk** — more irreversible/catastrophic decisions → more doc.
- **Coordination** — more people and teams → more doc (it's the shared contract).
- **Lifespan** — multi-year production code → more doc (future maintainers are readers too).
- **Ambiguity** — fuzzier requirements → more doc (writing forces the questions out).

When the dials are low across the board, write less — or nothing. *"Sometimes, the right amount to invest in a design doc is zero."*

## Selecting the Section Subset

The section catalog is a menu. *"You generally don't need every single section for every doc. Choose the subset that makes sense for you."* Two tests per section:

1. **Penalty test** — does it document a costly-to-reverse decision?
2. **Reader-need test** — does a cold reader or reviewer need it to evaluate or build the system?

If a section answers *no* to both, cut it. Front matter, Goals, Non-goals, and Alternatives survive almost always; the operability and compliance clusters scale up with risk and lifespan.

## Driving the Doc Through Review

The doc's whole point is to be **pressure-tested before code is**. The review is not a rubber stamp at the end — it's why you wrote prose instead of code.

- **Write it to stand on its own first.** Reviewers will read it without you in the room; the page-one stand-alone test (see `writing-craft.md`) is a precondition for useful review, not a nicety. A doc that needs you to narrate it can't be reviewed asynchronously.
- **Circulate early, while decisions are still open.** A doc sent after the code is written collects rubber stamps, not feedback. Send it when the open issues are genuinely open.
- **Make feedback easy and specific.** Pose the real questions in **Open issues** so reviewers know exactly where their judgment is wanted, rather than asking for a vague "thoughts?".
- **Use Security's rationale to bait better review.** Documenting your threat reasoning — *even when threats seem unlikely* — *"might prompt reviewers to identify threats you overlooked."* The same applies anywhere you write down *why*: stated reasoning is what reviewers can productively attack.

## The Issue Lifecycle

Design docs are living during the project. Two sections carry that life:

- **Open issues** — every unresolved question, each with: **the problem**, **the options**, and **the immediate next step** (concrete and assignable, e.g. *"Ask our tech lead to weigh in,"* not "TBD"). This is the doc's to-do list and the agenda for review.
- **Resolved issues** — when an open issue closes, **move** it here and **retain the full discussion for posterity**. Months later, someone will ask "why did we decide this?" — the resolved-issue trail is the answer, and it prevents re-litigating settled questions.

## Relationship to the Implementation

The doc precedes and guides the code — written *"before writing any code,"* and you *"adhere to the design as [you] implement."* But the relationship is bounded by the penalty filter:

- **Above the line** (irreversible, high-penalty): the doc decides, and the implementation follows it. Deviating means updating the doc and, usually, re-review.
- **Below the line** (reversible, low-penalty): the doc is silent on purpose. These are settled in code. Writing them into the doc would mean *"you've essentially written the implementation during the design phase"* — the over-writing failure.

The doc is the contract for the expensive decisions, and a deliberate blank for the cheap ones.

## A Compact Reviewer Checklist

When **reviewing** a design doc (yours or someone else's), check:

1. **Stands alone** — does page one tell a cold reader what and why?
2. **Right project to doc** — does it clear the when-to-write bar, or is it ceremony?
3. **Goals are outcomes**, non-goals fence the real assumptions, SLOs are measurable.
4. **The irreversible decisions are present and justified** (language, storage, interfaces, trust boundaries).
5. **No implementation written in prose** — reversible details are absent by design.
6. **Alternatives** show the obvious option was considered, briefly.
7. **Open issues** are honest, each with a concrete next step.
8. **Security/privacy rationale is written down**, even where threats seem unlikely.
