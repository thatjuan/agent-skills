---
name: orca-implement
description: Implement every issue in a batch or GitHub milestone through supervised Orca workers in Orca worktrees, with either one combined PR or one PR per issue.
---

# Orca implement

You are the Orca coordinator. Work through every requested issue until the batch is complete, giving each issue a fresh supervised Orca worker. You own the Run, the worktrees, the commits, the pushes, and the pull requests. Workers own only the code change for their one issue.

## Load Orca

Invoke the `orchestration` skill, resolve the Orca executable it describes, and load its version-matched guide. That guide is the single source of truth for command syntax, the `check --wait` loop, settlement, release, and recovery; this skill adds only the batch shape on top of it. Running this skill is the user's explicit request for supervision, so you take the Coordinator role. Every worker is an Orca worker started with `worker-start`.

`ORCA status --json` must succeed before anything else. If orchestration commands are rejected as disabled, tell the user to enable it under Orca Settings → Experimental and stop.

## Ask first

Collect these two choices before touching the repository. Treat a choice the user already stated as answered and ask only what is missing, both questions together when the interface supports it.

1. "Which Orca agent should implement each issue?" Offer `Auto` and the agents Orca can launch (`claude`, `codex`, `cursor`, `antigravity`, `muse`, `opencode`, and any others the user has enabled). Accept an optional model for that agent. With a named agent, use it for every issue and pass `--model` only when the user named one. With `Auto`, pick the agent per issue from the work it requires and omit `--model` so the agent's configured default applies.
2. "How should the work be delivered?"
   - One feature branch for the whole batch, followed by one pull request.
   - One feature branch and one pull request per issue.

Wait for both answers.

## Plan the batch

1. Resolve the complete issue list and its order. Use the user's order unless dependencies require another.
2. Read every issue in full: title, body, comments, acceptance criteria, and linked instructions.
3. Record real dependencies: issue B depends on A only when B needs A's code to exist.
4. Create one Run for the batch with `run-create`, objective naming the batch or milestone.
5. Create one Task per issue with `task-create`, `--task-title "#<number> <title>"`, and `--deps` for the dependencies from step 3. Write each spec to the contract under **Worker spec**.

## Place the workers

Placement follows the delivery choice. Each worktree is a real git worktree on its own branch, so read the worktree's path and branch from the `worker-start` or `worktree create` receipt and use them for every git command on that issue (`git -C <path>`).

**One combined branch.** Create one worktree for the batch from the repo's default base with `ORCA worktree create --name <batch-slug> --setup run --json`; its branch is the feature branch. Run the issues sequentially in that worktree: start each issue's worker with `worker-start --task <task_id> --worktree id:<worktree_id> --agent <agent>`, and start the next issue only after the current one is committed. Workers sharing a checkout run one at a time.

**One branch per issue.** Give each issue its own worktree with `worker-start --task <task_id> --worktree new-top-level --name issue-<number>-<slug> --setup run --agent <agent>`. Start every issue whose dependencies are satisfied in one parallel wave before the first wait. An issue with a dependency starts after that dependency is committed, with `--base-branch <dependency branch>`, so its branch and PR stack on the dependency.

## Worker spec

Each Task spec is self-contained, follows the orchestration guide's task-spec contract, and carries:

- The full issue text, including comments and acceptance criteria, plus any repository context the worker needs to execute without guessing.
- The worktree it works in, and the scope: this issue only.
- Implement the issue and run the validation the repository and the issue call for.
- Leave git to the coordinator: the worker stays on its branch and leaves the change uncommitted, unpushed, and without a pull request.
- Blocking questions go through the preamble's `ask` command.
- The `worker_done` message is the worker's only report. Its `--outcome` is `succeeded` or `failed`, its `--files-modified` lists the changed files, and its body holds only short highlights of what was done, the validation results, and notes the coordinator needs. No reasoning, code excerpts, command output, or progress updates.

## Supervise

Run the orchestration guide's wait loop until every Task has settled. Keep the coordinator's context to the inbox: read worker output with `worker-read` only to diagnose a stuck or failed worker. For each delivery:

- **Question:** answer from the issues and the repository; ask the user only when the decision is theirs.
- **Succeeded:** validate the `worker_done` against the expected Dispatch, check the worktree's diff matches the issue, and commit it in that worktree with a message that references the issue. Release the worker. For one branch per issue, push the branch, open the pull request against its base (the default branch, or the dependency branch for a stacked issue), then start any Tasks this unblocked.
- **Failed or escalation:** if missing context caused it, supply the context and retry with `worker-start --task <task_id> --retry-of <dispatch_id>`, repeating the original placement. Otherwise mark the issue blocked, and hold back every issue that depends on it. In combined delivery the batch pauses there; ask the user how to proceed. In per-issue delivery, independent issues continue.

The batch is supervised to completion when every Task has an outcome and `worker-list --run <run_id> --terminal-state reclaimable --json` returns none.

## Deliver

For one combined branch, push the batch worktree's branch after every issue succeeds and open one pull request covering the whole batch. For one branch per issue, every pull request is already open.

Leave the worktrees in place; the user removes them from Orca after the pull requests merge. Finish with a concise list per issue: outcome, pull request link, and worktree, plus any unresolved blocker.
