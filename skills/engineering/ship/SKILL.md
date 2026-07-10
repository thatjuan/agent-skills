---
name: ship
description: 'Task entrypoint and delivery orchestrator for a Fable-class coordinator. Routes a raw task through three gates — design (design-doc), GitHub issues, dispatch to the right models (Codex/Opus implement; coordinator plans, reviews, merges). Use when the user hands over a nontrivial task expecting idea-to-shipped-code — "take this on", "get this done end to end", "handle this" — or when a substantive task''s path (design? issues? which models?) is undecided.'
---

# Ship

The entrypoint for substantive work. The coordinator model running this skill is the scarcest, most expensive resource in the pipeline — so it behaves like a tech lead, not a developer: it **decides, designs, specs, delegates, reviews, and merges**. Implementation heavy lifting goes to cheaper models with high throughput. The coordinator writes code directly only when the change is trivial (faster to do than to delegate) or taste-critical glue no other model should own.

## Position in the Pipeline

```
ship (THIS skill — triage, design gate, issue gate, dispatch, review/merge)
  ├─ design-doc          — when the design gate fires
  ├─ gh / gh-cli          — issue authoring
  ├─ implement-issue      — per-issue delivery (→ team-executor → software-engineer)
  └─ model routing        — every delegated agent gets an explicit model assignment
```

All downstream skills are **prefer-when-present**: check `~/.claude/skills/<name>/`, `.claude/skills/<name>/`, a sibling `../<name>/`, `/mnt/skills/<name>/`, or `skills-lock.json`. When one is missing, inline a trimmed equivalent of its core judgment; never hard-fail.

## Bundled Resources

| File | Purpose |
|------|---------|
| [references/model-routing.md](references/model-routing.md) | Model traits, invocation mechanics (Agent tool, codex exec, workflows), per-model prompting techniques |
| [references/issue-standard.md](references/issue-standard.md) | The junior-dev-implementable issue template and authoring rules |

Read `model-routing.md` before the first dispatch of the session. Read `issue-standard.md` before writing issues.

## Gate 0 — Triage

Classify the incoming task before doing anything else:

- **Trivial** (single bounded change, obvious approach, < ~15 min of agent work) → skip all gates, do it directly or hand one agent one prompt. Do not ceremony-tax small work.
- **Substantive, path unclear** → proceed through Gates 1–3 in order.
- **Already spec'd** (user supplied an issue, a design doc, or an explicit plan) → skip the satisfied gates, enter at the first unsatisfied one.

Time-to-complete is itself a signal worth reporting: if a "simple" fix takes an agent an hour, the architecture is telling you something — surface it to the user rather than silently merging.

## Gate 1 — Design

Ask: **what is the penalty for being wrong?** Fire this gate when any of these hold:

- Multiple viable architectures exist and reversing the choice later is expensive (schema, public API surface, service boundaries, data migrations).
- The task spans systems or teams, or changes behavior other components depend on.
- The user's ask is a goal, not an approach, and the approach materially shapes the work.

When fired: invoke `design-doc` to produce a right-sized doc (it carries the when/what/how judgment — don't duplicate it). Present the doc's TL;DR and open decisions to the user for sign-off **unless** the user said "decide" / "autonomous" — then choose the most robust, convention-consistent option and record why.

When not fired: skip straight to Gate 2. Most tasks do not need a design doc; over-writing is a real failure mode.

## Gate 2 — Issues

Ask: **should this work survive as GitHub issue(s)?** Cut issues when:

- The work decomposes into more than one bounded PR, or
- Work will be delegated to agents that start fresh (no session context), or
- The user wants a paper trail, parallelization, or to review scope before build.

Otherwise (single PR, doing it now, in-session) skip to Gate 3 with an inline spec of the same rigor.

**The bar**: every issue must be implementable by a junior developer — or a mid-tier model — **without guesswork**. Exact standard and template in [references/issue-standard.md](references/issue-standard.md). Decompose so each issue is one bounded PR; declare dependencies between issues explicitly (`Blocked by #N`). Create with `gh issue create` (see `gh-cli` skill for syntax edge cases).

## Gate 3 — Dispatch

### Division of labor

In one line: **Codex (GPT-5.5, near-free)** takes bulk implementation from a clear spec plus computer-use verification; **Opus** takes taste-sensitive code (public APIs, UI, copy); the **coordinator** plans, resolves conflicts, reviews, and merges; **Sonnet** only as a cheap wrapper; **Haiku** never. The full traits table, routing quick-reference, standing rules (escalate without asking when output misses the bar; cost is a tiebreaker only; reasoning effort high at most, never xhigh/max), invocation mechanics, and per-model prompting are in [references/model-routing.md](references/model-routing.md) — already read before first dispatch. User global/project CLAUDE.md rankings override the bundled defaults.

### Orchestration shape

- **One issue, bounded** → invoke `implement-issue` (it opens the branch, plans, executes via `team-executor`, opens the PR). Overlay model routing: tell the executor which model each role gets, per the table above. Any Claude agent that writes or reviews code also gets the `software-engineer` skill (prefer-when-present); Codex can't carry skills, so code-writing codex prompts embed the engineering-bar digest from `model-routing.md` instead.
- **Several independent issues** → parallel worktrees, one delivery stream per issue. Keep disjoint file surfaces in parallel; serialize streams that touch the same code.
- **Checkpoint-driven programs** (each PR needs CI + review + merge before the next rebase) → orchestrate from this session, step by step. Do NOT wrap the umbrella in one giant workflow — workflows are for deterministic fan-out/verify (triage passes, multi-agent review panels), not for programs with human checkpoints or mid-stream product calls.
- **Reviews before merge**: every PR gets at least one independent review pass by a model that didn't write it. Codex is a good independent second perspective on Claude-written code and vice versa. Merge only what passes the project's configured automated reviewers, if any.

### Verification

Delegated code is claimed-done, not done. Before reporting completion: run the tests/CI, and for user-facing behavior have an agent actually drive the flow (Codex computer-use is the strongest option for runtime/UI verification). The coordinator personally reads the diff of anything taste-critical before merge.

## Reporting

Close the loop with the user in one message: what shipped (PRs/issues with links), what was decided at each gate and why, what was escalated between models, and anything the task revealed about the codebase (slow fixes, surprising coupling) worth acting on.
