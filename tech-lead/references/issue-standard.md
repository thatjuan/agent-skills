# Issue Standard — Junior-Dev-Implementable

Every issue this skill cuts must be implementable **without guesswork** by a junior developer or a mid-tier model with no session context. The issue is the entire context handoff: assume the implementer has never seen the conversation, the design doc discussion, or the coordinator's reasoning. Anything not written down does not exist.

## The Test

Before filing, ask: *could an agent that has only this issue text and the repo produce the PR I want, first try?* Every question it would need to ask is a defect in the issue. Common defects:

- "Improve", "clean up", "make better" — no observable definition of done.
- Naming a goal but not the approach when the approach was actually decided.
- Omitting the files/modules involved, forcing rediscovery of what the coordinator already knows.
- Silent scope boundaries — the implementer can't tell what's deliberately out of scope vs forgotten.

## Template

```markdown
## Context
Why this work exists. Link the design doc / parent issue / inspiring PRs
(if multiple PRs attempted this before, link all of them and state what
happens to each: superseded, partially reused, closed).

## Current behavior
What the code does today. Name the exact files/modules/functions involved
(paths, not descriptions). If a schema/API is involved, show its current shape.

## Desired behavior
What the code must do after this change. Concrete: inputs → outputs,
UI states, API responses. Include the agreed approach when one was decided
at the design gate — the implementer executes it, not re-derives it.

## Implementation notes
- Files expected to change, and roughly how.
- Conventions to follow, with an exemplar: "match the pattern in <path>".
- Known traps, ordering constraints, and decisions already made (with the why,
  so the implementer doesn't "helpfully" reverse them).

## Out of scope
Explicit non-goals. Anything adjacent the implementer might be tempted to fix.

## Acceptance criteria
- [ ] Checkable statements — each verifiable by running something.
- [ ] Tests: which ones must be added/updated, what they must cover.
- [ ] Verification: the command/flow that proves the behavior end to end.

## Dependencies
Blocked by #N / blocks #M. Which issues can proceed in parallel with this one.
```

## Sizing and Decomposition

- **One issue = one bounded PR.** If the desired behavior needs multiple PRs (e.g., dual-write → read-path flip → column drop), cut one issue per PR and chain them with `Blocked by`.
- Decompose along **merge checkpoints**, not along files: each issue should be independently mergeable and leave the system working.
- Issues that can run in parallel must have **disjoint file surfaces** — say so explicitly in Dependencies so the dispatcher can parallelize without merge-conflict roulette.
- Robustness beats speed: implementers are agents, so human effort estimates don't apply. Never shrink scope because it "would take a person too long"; only split for boundedness and reviewability.

## Filing

Use `gh issue create --title "..." --body-file <tmpfile>` (write the body to a temp file — inline `--body` mangles multiline markdown). Apply the repo's labels/milestone conventions if they exist. Title format: imperative, specific — "Add cursor pagination to /v1/events", not "Pagination improvements".
