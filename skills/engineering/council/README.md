# council

> Adversarially improves anything (a concept, a design, a piece of writing, code, a plan) with a council of Orca agents on the models you name, revising until every member scores it at least 9 out of 10.

## What it does

`council` runs a critique-and-revise loop. Your agent is the author; a council of [Orca](https://www.onorca.dev/docs) workers, one per model you name, are the critics. Each round, every member scores the current version against a fixed rubric and writes a verdict with ranked, concrete changes. The author triages every critique (accept, reject with a reason, or escalate to you), revises, and convenes the next round. It ends when every member scores the same version at or above the bar.

The loop is built to resist the usual ways review councils go soft:

- **A fixed rubric.** The criteria and score anchors are written before round 1, from your priorities plus the ones the council adds to raise the standard, so the goalposts stay put. Only a pivot you take on a concept can change them.
- **Blind verdicts.** Members score independently each round and see each other's points only through the author's change log, so nobody anchors on the first score.
- **A hidden bar.** Members know the rubric and the anchors (9 means it would ship to a demanding expert audience with nothing worth changing) but not the pass mark or the round cap, so they score the work rather than toward an exit.
- **Earned scores.** A member who raises or lowers a score names the change that moved it.
- **Pinned versions.** Each round reviews a pinned copy (screenshots, text, or diff), and the pass requires every member to clear the bar on the same version.
- **One author.** Members only critique; the author makes every change, so the artifact stays coherent and each change traces to a critique.

When the council stalls (the round cap, or no progress for two rounds), it stops and hands you the dispute instead of grinding on.

### Concepts

An idea not yet built (a product, feature, campaign, brand, business, story, or strategy) fails a council in its own ways: critics sand it down to something safe, every revision descends from the first idea, and four models agreeing that people will pay gets mistaken for evidence. So a concept gets its own rules on top of the loop. What one strong model revising alone cannot give you is independently written alternatives, scored without knowing whose they are, with every change to your bet left to you.

- **A spine and a recorded bet.** Idea, audience, insight, and edge, one line each, and a one-line bet in your pitch's terms: who it is for, what it promises, and how it delivers. The author sharpens the spine freely. Anything that changes the bet is a pivot, and pivots are yours to pick.
- **Premortem and breakout.** Each member says why the concept would fail, and what would make it the talk of its category, so critique pushes up as well as down.
- **Scored rivals.** In round 1 every member writes the strongest different concept they can. The strongest, and the strongest that makes a different bet, are fleshed out to the same form and scored unattributed against the current one, setting aside proposers' scores when other members' remain. A pivot that leads comes to you with the scores.
- **A sanding check.** Before every round the author compares the spine with your pitch, or the last pivot you took, and restores an edge revisions have dulled, and members check it too.
- **Honest standing.** Researched alternatives, assumptions marked `untested` until something bears directly on them, and a final report that says *ready to test*, *supported for commitment*, *did not pass*, or *killed*. Market questions get a kill test, not a debate.

You get back a one-page concept beside your original, which stays untouched, plus the pivots you took or declined and the open assumptions with the cheapest test for each, riskiest first.

## When to use it

- *"Council this landing page with opus and gpt-5.5 until it's a 9."*
- *"Get a council to tear apart this blog post and keep revising until they all agree it's great."*
- *"Run the onboarding flow past a council of three models and improve it."*
- *"Have a council review this API design doc."*
- *"Council my app idea with opus, fable, and gpt-6.1-sol until it's something I'd bet a year on."*

If you name no models, it asks which ones to seat before starting. It sets the priorities the work is scored on from your prompt, then raises them toward a better result, adding what a demanding expert would also hold the work to. It asks you one to three questions only when a priority is still unclear.

**Not the right skill if** you want a single review with no revision (ask for a review), or a batch of GitHub issues implemented (→ [`orca-implement`](../orca-implement/)).

## Example walkthrough

**Prompt**

> Council the pricing page with opus and gpt-5.5. It's for developers comparing us to two competitors.

**What the skill does**

1. **Seats the council**: an `opus` member on `claude` and a `gpt-5-5` member on `codex`.
2. **Sets the priorities**: from the prompt, a fair comparison for developers; added by the council, every claim checkable against the competitors' own pages. One stays unclear, so it asks: should the page win on price or on features?
3. **Writes the rubric**: clarity of the plan differences, honesty of the comparison, visual hierarchy, mobile layout, call to action, each with what a 10 looks like.
4. **Round 1**: screenshots the page at phone and desktop widths, light and dark, into `.council/pricing-page/round-1/`. Both members score it (6 and 7) and list changes.
5. **Triage and revise**: accepts eleven changes, rejects one ("drop the free tier" conflicts with the goal), rebuilds, re-screenshots.
6. **Rounds 2–3**: scores climb to 8 and 8, then 9 and 9 with no blocking items.
7. **Reports**: final scores, the changes that moved them most, the contested rejection, and where the record lives.

A verdict excerpt:

```markdown
**Score**: 8 overall. Hierarchy 9, comparison 7 (the competitor table omits seat limits, which is where we win), mobile 8.
**Changes**
1. Comparison table, row 3: add per-seat limits for all three plans; it's the strongest argument and it's missing.
2. Hero, phone width: the annual/monthly toggle wraps under the price; move it above the cards.
**Weakest point**: the "Enterprise" card still reads as an afterthought.
```

### A concept

**Prompt**

> Council my app idea with opus, fable, and gpt-6.1-sol: a habit app that charges you when you miss the gym.

A spine the council might start from and end on, invented for this illustration:

```markdown
Bet: people who want to go to the gym keep going because missing costs them money.

Before
Idea: a habit app that charges you when you miss the gym.
Audience: busy people who want to work out more.
Insight: people follow through when money is at stake. (untested)
Edge (added by the council): the charge is automatic, with no check-ins to fake.

After
Idea: promise a friend you'll show up; miss, and your stake goes to them.
Audience: a lapsed gym-goer in their thirties with one friend who'd hold them to it.
Insight: a lost stake hurts more when a friend collects it. (untested)
Edge: stake apps pay a charity or the company; this puts someone you'd hate to let down on the other side.
```

The friend came from a member's rival. It led the scores, and because missing still costs money, the bet line held and the author took it as a sharpen. A second rival, a gym-buddy matching service, dropped the money, so it would have been your call as a pivot; it lost. A note to cap the stake at $1 was rejected for making the concept duller, and the risk went to a test: *twenty pairs for a month; kill it if more than one in four friends ask out.* The report calls the concept *ready to test*.

## Installation

```bash
npx skills add thatjuan/agent-skills --skill council
```

Requires the Orca app with orchestration enabled (Settings → Experimental) and the `orchestration` skill that ships with Orca.

## Bundled resources

| File                                             | Purpose                                                                |
| ------------------------------------------------ | ---------------------------------------------------------------------- |
| [`SKILL.md`](SKILL.md)                           | The council loop: seating, rubric, evidence, rounds, finish.           |
| [`references/concepts.md`](references/concepts.md) | The spine, evidence form, rubric, verdict fields, rivals, pass gates, and triage for concepts. |

## Tips

- Seat models from different providers; two models from one family tend to share blind spots.
- Two or three members is the sweet spot. More members make every round slower without adding many new points.
- Say who the audience is. The rubric, and how hard the members judge, comes from it.
- Set a different bar ("until it's a 10") or round cap in the prompt if the default 9 and six rounds don't fit.
- For designs, say which screens and states are in scope, or the council judges only what the author screenshots.
- For a concept, paste your pitch as you'd say it; it becomes the baseline the council is held to. Say "I'll commit to this with no test first" if that's the decision: any assumption left untested then blocks the pass. Otherwise the council gets the concept ready to test.

## Related skills

- [`big-idea`](../../creative/big-idea/) and [`creative-director`](../../creative/creative-director/): generate the first concept for the council to improve.
- [`orca-implement`](../orca-implement/): Orca workers implementing a batch of GitHub issues.
- [`clean-writing`](../../creative/clean-writing/): the prose standard to revise writing against.
