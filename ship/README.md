# ship

> The task entrypoint for a coordinator-class model (Fable). Routes any substantive ask through three gates — design, issues, dispatch — then delegates implementation to the right models (Codex/GPT-5.5 and Opus do the heavy lifting) while the coordinator plans, reviews, and merges.

## What it does

`ship` turns the most expensive model in your setup into what it should be: a tech lead, not a typist. Given a raw task, feature request, bug cluster, or goal, it:

1. **Triages** — trivial work gets done directly with zero ceremony; substantive work enters the gates.
2. **Gate 1 — Design**: decides whether architecture/design-doc work must happen before code (penalty-for-being-wrong test), delegating to the [`design-doc`](../design-doc/) skill when it fires.
3. **Gate 2 — Issues**: decides whether to cut GitHub issue(s), and writes them to a strict standard — implementable by a junior dev or mid-tier model **without guesswork** (full context, exact files, agreed approach, out-of-scope list, checkable acceptance criteria).
4. **Gate 3 — Dispatch**: assembles agent teams and routes every role to an explicit model — bulk/mechanical/token-heavy work and computer-use verification to GPT-5.5 via the Codex CLI, taste-sensitive code to Opus, planning/review/merge judgment kept by the coordinator. Includes per-model prompting techniques, because prompts that work on Claude actively hurt on Codex.

It composes with the existing pipeline: `ship → design-doc → issues → implement-issue → team-executor → software-engineer`, all prefer-when-present.

## When to use it

- *"Take this on end to end: we need rate limiting on the public API."*
- *"Here's a braindump of what's broken in checkout — handle it."*
- *"Get the notification system from the design discussion actually shipped."*
- Any substantive task where the path — design first? issues? which models implement? — hasn't been decided yet.

**Not the right skill if** you already have a specific issue number (→ [`implement-issue`](../implement-issue/)) or a fully-formed plan ready for a team (→ [`team-executor`](../team-executor/)). `ship` is the layer that decides those things.

## Example walkthrough

**Prompt**

> We need webhook delivery in Lakebed — customers keep asking. Take it from idea to shipped.

**What the skill does**

1. **Triage** — substantive, path unclear → full gates.
2. **Design gate fires** (public API surface + delivery-guarantee semantics are expensive to reverse). Produces a right-sized design doc via `design-doc`; user signs off on at-least-once delivery with signed payloads.
3. **Issue gate** — cuts four issues, each one bounded PR: schema + outbox table, delivery worker, signature verification + docs, admin UI. Dependencies declared; issues 2 and 4 flagged parallel-safe.
4. **Dispatch** — outbox migration and delivery worker go to Codex (clear spec, mechanical); public API surface and docs go to Opus with `software-engineer` attached; coordinator reviews every diff, Codex runs an independent second review of Opus's PRs and drives a computer-use verification of the admin flow. PRs merge as CI and reviewers pass.
5. **Report** — links to merged PRs, gate decisions and why, plus a note that the delivery worker took far longer than its spec suggested — a coupling smell worth a follow-up.

## Installation

```bash
npx skills add thatjuan/agent-skills --skill ship
```

## Bundled resources

| File | Purpose |
|------|---------|
| `SKILL.md` | The three-gate workflow, division of labor, orchestration shapes, verification rules |
| `references/model-routing.md` | Model traits table, invocation mechanics (Agent tool, `codex exec`, workflows), per-model prompting techniques |
| `references/issue-standard.md` | The junior-dev-implementable issue template, sizing/decomposition rules, filing mechanics |

## Tips

- **Effort stays at high, never above.** xhigh/max overthink per step and bloat both diffs and bills; effort doesn't extend how long agents work, only how much they think per tool call.
- **Judge output, not price tag.** The skill has standing permission to redo a cheap model's output with a smarter one — escalating costs less than shipping mediocre work.
- **Watch the clock as a signal.** When a "simple" fix takes an agent an hour, the skill surfaces it — that's your architecture talking.
- **Keep the routing table honest.** Model traits shift with every release; when a dispatch misroutes, append the lesson to `references/model-routing.md` instead of re-explaining per session.

## Related skills

- [`implement-issue`](../implement-issue/) — per-issue delivery this skill dispatches to
- [`team-executor`](../team-executor/) — multi-agent planning/execution engine underneath
- [`software-engineer`](../software-engineer/) — the engineering bar attached to every coding/review agent
- [`design-doc`](../design-doc/) — the design gate's author/reviewer
