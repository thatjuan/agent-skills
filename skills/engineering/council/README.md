# council

> Adversarially improves anything (a design, a piece of writing, code, a plan) with a council of Orca agents on the models you name, revising until every member scores it at least 9 out of 10.

## What it does

`council` runs a critique-and-revise loop. Your agent is the author; a council of [Orca](https://www.onorca.dev/docs) workers, one per model you name, are the critics. Each round, every member scores the current version against a fixed rubric and writes a verdict with ranked, concrete changes. The author triages every critique (accept, reject with a reason, or escalate to you), revises, and convenes the next round. It ends when every member scores the same version at or above the bar.

The loop is built to resist the usual ways review councils go soft:

- **A fixed rubric.** The criteria and score anchors are written before round 1 and never move, so the goalposts stay put.
- **Blind verdicts.** Members score independently each round and see each other's points only through the author's change log, so nobody anchors on the first score.
- **A hidden bar.** Members know the rubric and the anchors (9 means it would ship to a demanding expert audience with nothing worth changing) but not the pass mark or the round cap, so they score the work rather than toward an exit.
- **Earned scores.** A member who raises or lowers a score names the change that moved it.
- **Pinned versions.** Each round reviews a pinned copy (screenshots, text, or diff), and the pass requires every member to clear the bar on the same version.
- **One author.** Members only critique; the author makes every change, so the artifact stays coherent and each change traces to a critique.

When the council stalls (the round cap, or no progress for two rounds), it stops and hands you the dispute instead of grinding on.

## When to use it

- *"Council this landing page with opus and gpt-5.5 until it's a 9."*
- *"Get a council to tear apart this blog post and keep revising until they all agree it's great."*
- *"Run the onboarding flow past a council of three models and improve it."*
- *"Have a council review this API design doc."*

If you name no models, it asks which ones to seat before starting.

**Not the right skill if** you want a single review with no revision (ask for a review), or a batch of GitHub issues implemented (→ [`orca-implement`](../orca-implement/)).

## Example walkthrough

**Prompt**

> Council the pricing page with opus and gpt-5.5. It's for developers comparing us to two competitors.

**What the skill does**

1. **Seats the council**: an `opus` member on `claude` and a `gpt-5-5` member on `codex`.
2. **Writes the rubric**: clarity of the plan differences, honesty of the comparison, visual hierarchy, mobile layout, call to action, each with what a 10 looks like.
3. **Round 1**: screenshots the page at phone and desktop widths, light and dark, into `.council/pricing-page/round-1/`. Both members score it (6 and 7) and list changes.
4. **Triage and revise**: accepts eleven changes, rejects one ("drop the free tier" conflicts with the goal), rebuilds, re-screenshots.
5. **Rounds 2–3**: scores climb to 8 and 8, then 9 and 9 with no blocking items.
6. **Reports**: final scores, the changes that moved them most, the contested rejection, and where the record lives.

A verdict excerpt:

```markdown
**Score**: 8 overall. Hierarchy 9, comparison 7 (the competitor table omits seat limits, which is where we win), mobile 8.
**Changes**
1. Comparison table, row 3: add per-seat limits for all three plans; it's the strongest argument and it's missing.
2. Hero, phone width: the annual/monthly toggle wraps under the price; move it above the cards.
**Weakest point**: the "Enterprise" card still reads as an afterthought.
```

## Installation

```bash
npx skills add thatjuan/agent-skills --skill council
```

Requires the Orca app with orchestration enabled (Settings → Experimental) and the `orchestration` skill that ships with Orca.

## Bundled resources

| File       | Purpose                                                       |
| ---------- | ------------------------------------------------------------- |
| `SKILL.md` | The council loop: seating, rubric, evidence, rounds, finish. |

## Tips

- Seat models from different providers; two models from one family tend to share blind spots.
- Two or three members is the sweet spot. More members make every round slower without adding many new points.
- Say who the audience is. The rubric, and how hard the members judge, comes from it.
- Set a different bar ("until it's a 10") or round cap in the prompt if the default 9 and six rounds don't fit.
- For designs, say which screens and states are in scope, or the council judges only what the author screenshots.

## Related skills

- [`orca-implement`](../orca-implement/): Orca workers implementing a batch of GitHub issues.
- [`clean-writing`](../../creative/clean-writing/): the prose standard to revise writing against.
