---
name: batch-implement
description: "Implement a batch of GitHub issues autonomously via lean-context subagent fan-out: stacked feature branches, one PR per issue, build check only. Use when the user hands over several issue numbers or a range ('implement these issues: 59-61', 'do issues 12, 14 and 15') expecting all of them delivered without check-ins, or asks for stacked PRs across multiple issues."
---

# Batch Implement

You are the coordinator. Subagents implement; you assign, brief, integrate, and open PRs. Work autonomously until every issue in the batch is done. No user check-ins, no confirmation gates. Make the architectural decisions yourself, from your knowledge of the system.

## Inputs

- Issue numbers: a range (`59-61`), a list, or URLs. Bare integers are issues in the current repo.
- Optional overrides in the invocation: branch/PR/deploy strategy ("single branch", "deploy to staging when done"), model choices, test expectations. Overrides beat the defaults below.

## Defaults

- **Stack branches, PR only, don't deploy.** One feature branch and one PR per issue. The first branch comes off the default branch; each subsequent branch is cut from the previous issue's branch, and each PR uses the previous branch as its base.
- **Build gate only.** No tests and no other validation now; the user will ask for tests later. Right before creating each PR, confirm the app builds. That is the only required check.

## Lean context

The rule that makes this skill work: subagent output stays with the subagent.

Instruct every subagent to keep its reasoning, exploration, and intermediate output to itself while it works through the problem. It reports back once, at the end, with a short summary: what it did, a final verdict, and any issues it hit. You do not need to be informed of everything. Your context carries assignments and verdicts, nothing else.

## Model routing

For implementation subagents:

- Coordinator is Claude → Opus 5 on high effort.
- Coordinator is Codex → gpt-5.6 sol on xhigh.

A model-routing table in the user's global `~/.claude/CLAUDE.md` overrides these defaults.

## Engineering bar

Don't cut corners. Execution agents are not bound by human limitations, so the more robust, well-thought-out solution is normally the right choice, even where a human would reach for the shortcut.

## Workflow

1. **Read the batch.** `gh issue view <N> --json number,title,state,body,labels,comments,url` for each issue. Read bodies and comments; prior discussion may already constrain the approach. A closed or missing issue gets skipped and noted in the final report.
2. **Section the work.** Split each issue (or the batch) into sections as you see fit. State file ownership per section up front so parallel agents never touch the same files; sections that share files run sequentially.
3. **Plan the stack.** Order the issues (dependency order if one builds on another, issue order otherwise) and name the branches, e.g. `issue-<N>-<kebab-title>` or the repo's own convention.
4. **Dispatch.** Write each brief as clear instructions for an agent: scope, owned files, approach constraints, and the report contract below. Your job is assignment and instruction, not implementation.
5. **Integrate.** Read the summaries. Resolve cross-section conflicts or reported issues with targeted follow-up agents, on the same contract.
6. **Build gate.** Confirm the app builds on each branch. If it doesn't, dispatch a fix agent; never open a PR on a broken build.
7. **Open PRs.** One per issue, stacked bases, `Closes #<N>` in the body.
8. **Report.** One summary to the user: branches, PR URLs, skipped issues, anything the subagents flagged.

The one exception to autonomy: pre-existing uncommitted changes on the working tree at the start. Those are the user's state, so stop and ask before touching them.

## Subagent report contract

Include in every dispatch, adapted with the section's specifics:

> You own: `<files/scope>`. Implement `<section>` per the instructions below. Work through the problem yourself and keep your reasoning and intermediate output to yourself; do not stream progress back. When finished, reply with a short final summary only: what you did, your verdict, and any issues you found. Don't cut corners: you're not bound by human limitations, so go for the robust, well-thought-out solution. Do not run tests; confirming your change builds is enough.

## Related skills

- [implement-issue](../implement-issue/) — single issue with planning-team ceremony and a confirmation gate; use it when one issue deserves the full treatment.
- [codex-implementation](../codex-implementation/) — the dispatch lane when routing a section to the Codex CLI.
- [commitpush](../commitpush/) — safety-checked commits if the repo warrants it.
