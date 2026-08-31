# batch-implement

> Hand it a range of GitHub issues and get back stacked branches and PRs, implemented by subagents that keep their thinking to themselves. The coordinator assigns and integrates; it never drowns in agent output.

## What it does

`batch-implement` turns "implement issues 59-61" into finished pull requests without any check-ins along the way. The coordinating agent reads the issues, splits them into sections with explicit file ownership, and dispatches implementation subagents in parallel where the sections allow it.

The defining rule is lean context. Every subagent works through its section privately and reports back once, with a short summary and a verdict. The coordinator's context holds assignments and verdicts, not walls of agent reasoning, so it stays sharp across a whole batch instead of degrading after the first issue.

Delivery defaults:

- Stacked feature branches, one per issue, each cut from the previous issue's branch
- One PR per issue with stacked bases and `Closes #N`
- No deploy
- Build check only, run right before each PR opens. No tests, no other validation, until you ask for them

Implementation subagents run on Opus 5 (high) under a Claude coordinator, or gpt-5.6 sol (xhigh) under a Codex coordinator. A model-routing table in your global `~/.claude/CLAUDE.md` takes precedence.

## When to use it

- *"Implement these issues: 59-61. Stack branches, PR only, don't deploy."*
- *"Do issues 12, 14 and 15, split it up however you see fit."*
- *"Work through the open milestone issues and give me stacked PRs."*

**Not the right skill if** you have one substantial issue that deserves a planning team and an approach sign-off. That's [`implement-issue`](../implement-issue/).

## Example walkthrough

**Prompt**

> Implement these issues: 59-61. Stack branches, PR only, don't deploy.

**What the skill does**

1. Reads issues 59, 60, and 61 including comments.
2. Orders them (61 depends on 60's schema change, so 59 → 60 → 61) and plans three stacked branches.
3. Splits issue 59 into two sections with disjoint file ownership, dispatches both in parallel; 60 and 61 run as single sections.
4. Each subagent returns a short summary. One flags a naming conflict; the coordinator resolves it with a targeted follow-up agent.
5. Confirms the build on each branch, then opens three PRs with stacked bases.
6. Reports back once: three PR URLs and the one issue that was flagged and fixed.

## Installation

```bash
npx skills add thatjuan/agent-skills --skill batch-implement
```

## Bundled resources

| File | Purpose |
|------|---------|
| `SKILL.md` | Coordinator role, defaults, workflow, and the subagent report contract |

## Tips

- **Overrides go in the invocation.** Say "single branch" or "deploy to staging when done" and the skill follows that instead of its defaults.
- **The build gate is deliberate.** The skill will not run your test suite unless you ask. Follow up with a test run once the PRs are up.
- **Watch the stack order.** PRs merge bottom-up; merge the first branch before the second or GitHub will show inflated diffs.

## Related skills

- [`implement-issue`](../implement-issue/) — single-issue delivery with planning ceremony and a confirmation gate
- [`codex-implementation`](../codex-implementation/) — the lane for routing sections to the OpenAI Codex CLI
- [`commitpush`](../commitpush/) — safety-checked commit and push
