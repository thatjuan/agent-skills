---
name: orca-implement
description: Implement every issue in a batch or GitHub milestone through supervised Orca workers, one Orca worktree per issue, run in parallel waves where dependencies allow, with either one combined PR or one PR per issue.
---

# Orca implement

You are the Orca coordinator. Plan the batch into waves, give every issue its own Orca worktree and a fresh supervised Orca worker, keep each worktree's board status true to where the issue stands, and clean up every Orca session and worktree as soon as the batch no longer needs it. You own the Run, the worktrees, the board, the sessions, the commits, the pushes, and the pull requests. Workers own only the code change for their one issue.

Every implementation runs in an Orca worker started with `worker-start`. The planning, repository reading, and spec writing are yours, done directly in this session.

## Load Orca

Invoke the `orchestration` skill, resolve the Orca executable it describes, and load its version-matched guide. Also load its `coordinator-loop` and `recovery-and-cleanup` references, since this skill always runs dependency waves and releases workers. That guide is the single source of truth for command syntax, the `check --wait` loop, settlement, release, and recovery; this skill adds the batch shape on top of it. Running this skill is the user's explicit request for supervision, so you take the Coordinator role. Run each Orca command's `--help` when a flag below is rejected.

`ORCA status --json` must succeed before anything else. If orchestration commands are rejected as disabled, tell the user to enable it under Orca Settings → Experimental and stop.

## Choose agents and delivery

**Agents.** By default every worker runs the same agent as you: `claude` when you are Claude Code, `codex` when you are Codex, and so on. Pass `--model` only when the user names a model, and `--effort` only alongside it; otherwise the worker inherits the user's configured default for that agent. The user may name another agent, model, or effort for all issues, assign them per issue or per kind of work ("codex for the API issues, claude on opus for the UI"), or ask for a mix; honor that assignment exactly. Confirm what actually launched from the receipt's `launch.effective`.

**Delivery.** Ask "How should the work be delivered?" unless the user already said:

- One feature branch for the whole batch, followed by one pull request.
- One feature branch and one pull request per issue.

Wait for the answer before touching the repository.

## Plan the waves

1. Resolve the complete issue list. Read every issue in full: title, body, comments, acceptance criteria, and linked instructions.
2. Read the repository's agent instructions (`AGENTS.md`, `CLAUDE.md`, contributing docs) and locate the code each issue touches. This legwork feeds both the plan and the worker specs.
3. Decide each issue's dependencies. Issue B depends on A when B needs A's code, or when both change the same files or the same contract closely enough that parallel work would conflict. Everything else runs in parallel.
4. Group the issues into waves: wave 1 has no dependencies, and each later wave depends only on earlier ones. Run at most four workers at once unless the user sets another limit.
5. Show the user the wave plan, one line per issue with its agent (and model, when set) and its dependencies, then start.

## Set up the board

1. Create one Run for the batch with `run-create`, objective naming the batch or milestone.
2. For combined delivery, create the integration worktree first: `ORCA worktree create --repo path:<repo root> --name <batch-slug> --no-parent --setup skip --json`. Its branch is the batch feature branch.
3. Create one worktree per issue, every one of them now, before any worker starts:

   ```text
   ORCA worktree create --repo path:<repo root> --name issue-<number>-<slug> --reference <issue URL> --comment "wave <n>: waiting" --setup run --json
   ORCA worktree set --worktree id:<worktree_id> --workspace-status todo --json
   ```

   Pass `--parent-worktree id:<parent_id>` to group it under its parent in Orca: the integration worktree in combined delivery, or the worktree of the issue it depends on in per-issue delivery. Pass `--no-parent` otherwise. Record each worktree's full `id`, path, and branch from the receipt.
4. Create one Task per issue with `task-create`, `--task-title "#<number> <title>"`, `--deps` naming the Tasks it depends on, and the spec from **Worker spec**.

## Keep the board true

Each issue worktree moves through the board with `ORCA worktree set --worktree id:<worktree_id> --workspace-status <status>`, and its `--comment` carries the one-line state a human glancing at the board needs (wave, PR, blocker):

| Status        | When                                                                                         |
| ------------- | -------------------------------------------------------------------------------------------- |
| `todo`        | Worktree created; waiting for its wave or its dependencies. Also after a failed attempt, with the blocker in the comment. |
| `in-progress` | Set immediately before its `worker-start`, and on every retry.                                |
| `in-review`   | Its pull request is open and awaits human review.                                             |

If the repository's board uses custom status ids, map onto those. A worktree leaves the board when **Clean up** removes it. In combined delivery that happens to each issue worktree once it merges into the integration branch, so the integration worktree carries the batch: `in-progress` while issues run, with its comment counting merged issues, then `in-review` once the batch PR is open.

Attach every pull request to the worktree that holds it with `ORCA reference add <PR URL> --worktree id:<worktree_id> --json`: the issue's own PR in per-issue delivery, the batch PR on the integration worktree in combined delivery. Add `--unread` to the `worktree set` when a worktree needs a person: a blocker only the user can clear, or a PR ready for review.

## Start a worker

When an issue is ready (every dependency committed, and a worker slot free; `ORCA orchestration task-list --ready --brief --json` lists the candidates):

1. Bring the issue's branch up to date. Its branch has no commits yet, so this is a fast-forward:
   - Combined delivery: `git -C <path> merge --ff-only <integration branch>`.
   - Per-issue delivery with one dependency: `git -C <path> merge --ff-only <dependency branch>`. With several dependencies, merge each dependency branch in, and target the default branch with the PR body naming the dependency PRs.
2. Set the worktree to `in-progress`.
3. `ORCA orchestration worker-start --task <task_id> --worktree id:<worktree_id> --agent <agent> [--model <id> [--effort <level>]] --json`. The worktree already exists, so setup is not rerun.

Start every ready issue of a wave before the first wait. A worker opens as a chat or a terminal per the user's Chat UI setting; drive both the same way, through the orchestration verbs and the Dispatch ID.

## Worker spec

The Task spec is the worker's entire world: it starts fresh in its worktree, knowing nothing of this conversation, the batch, or the other workers. Write it so a capable engineer could finish the issue without asking a single question. Orca prepends the lifecycle preamble (Task and Dispatch IDs, `ask`, `check`, `worker_done` commands); the spec carries everything else. Use this shape and fill every section:

```markdown
# Issue #<number>: <title>

You are implementing one GitHub issue, alone, in the Orca worktree below.

## Workspace
- Worktree: `<path>`, branch `<branch>`, based on `<base>`. Work only inside this path.
- Repository: `<owner>/<repo>`. <stack, conventions, and the build/test/lint commands from the repo's agent instructions and scripts>
- Builds on: <completed issues this one depends on and what they changed, or "nothing in this batch">
- Running alongside: <parallel issues and the areas they own; stay inside your own>

## Issue
<the issue body, verbatim>

<comments that refine or change the scope, verbatim, with author>

## Target
<files, modules, and components in scope, as located during planning>

## Change
<the concrete result to produce, in your words, resolving any ambiguity the issue leaves>

## Constraints
<invariants, compatibility rules, the issue's non-goals, and areas to leave untouched>

## Acceptance
- [ ] <each acceptance criterion as a checkable item>
- [ ] <the validation commands to run, and that they pass>
- [ ] <for UI work: verified in this worktree's Orca browser tab, with the dev server's URL from `<orca executable> ports --json`>

## Git and reporting
- Stay on `<branch>` and leave the change uncommitted. The coordinator reviews, commits, pushes, and opens the pull request.
- Stop any dev server or watcher you started before you finish.
- For a decision the issue does not settle, use the preamble's `ask` command and wait for the answer.
- Finish with the preamble's `worker_done`, once: `--outcome succeeded` or `--outcome failed`, `--files-modified` with every changed file, and a three-sentence body: what changed, the validation results, and what the coordinator still needs to know. That message is your whole report.
```

## Supervise

Run the orchestration guide's wait loop until every Task has settled. Keep your context to the inbox: read worker output with `worker-read` only to diagnose a stuck or failed worker. For each delivery:

- **Question:** answer from the issues and the repository. Ask the user only when the decision is theirs, and pass their answer back with `reply`.
- **Succeeded:** validate the `worker_done` against the expected Dispatch. Review `git -C <path> diff` against the issue's acceptance list. When something is missing, create a follow-up Task naming the gap and start it on the same worker terminal (`worker-show` for its handle, then `worker-start --task <followup_task_id> --terminal <handle> --worktree id:<worktree_id>`). Once the change is complete, commit in the worktree with a message referencing the issue, release the worker, then:
  - Combined delivery: `git -C <integration path> merge --no-ff <issue branch>`. Resolve a mechanical conflict yourself; for a substantive one, start a worker on the integration worktree with a spec describing both sides, and release it once the merge is done. Then remove the issue worktree (**Clean up**).
  - Per-issue delivery: push the branch, open its pull request against its base (the default branch, or the dependency branch for a stacked issue) with `Closes #<number>` in the body, and attach the PR to the worktree. Set the worktree to `in-review` and close its sessions (**Clean up**); the worktree stays while its PR is open.

  Then start every issue this unblocked.
- **Escalation:** the worker is still running. Send the missing context with `send --to dispatch:<dispatch_id>`, asking the user first when the blocker is theirs. When it cannot be unblocked, tell the worker to finish with `--outcome failed`.
- **Failed:** if missing context caused it, set the worktree to `in-progress`, add the context to the spec, and retry with `worker-start --task <task_id> --retry-of <dispatch_id> --worktree id:<worktree_id> --agent <agent>`; the retry releases the failed worker's terminal. Otherwise release the worker, set the worktree to `todo` with the blocker as its comment and `--unread`, close its sessions (**Clean up**), and hold back every issue that depends on it. When Orca circuit-breaks a Task after three failed starts, report it to the user rather than routing around it. Independent issues continue.

## Clean up

Clean up each worktree as soon as its part of the batch ends. Scope cleanup to this batch's worktrees and Run, and leave sessions the user opened or asked you to keep.

**Release first.** Every worker in the worktree is released, or retained because the user asked. Release the worker yourself with `worker-release --dispatch <dispatch_id> --json` rather than waiting for Orca's automatic release; its output stays readable through `worker-read`. Release is the only way to close a worker's session: follow a `release_pending` or `release_unknown` receipt's exact recovery action, never `terminal close`.

**Close sessions** in a worktree that stays: a per-issue worktree whose PR is open, a failed issue parked as `todo`, and the integration worktree once the batch PR is open. List what remains with `ORCA terminal list --worktree id:<worktree_id> --json` (the setup run, default shells, dev servers) and close each session the batch started with `terminal close --terminal <handle> --json`, or all at once with `terminal close --worktree id:<worktree_id> --all --json` when nothing there belongs to the user. Close a configured default tab only after confirming it is an idle shell.

**Remove the worktree** once nothing in the batch needs it:

| Worktree                                      | Remove when                                            |
| --------------------------------------------- | ------------------------------------------------------ |
| Issue worktree, combined delivery             | Its branch is merged into the integration branch.      |
| Issue worktree, per-issue delivery            | Its pull request is merged or closed.                  |
| Integration worktree                          | The batch pull request is merged or closed.            |
| Issue held back behind a failed dependency    | The batch settles: it never started and holds no work. |

Check `git -C <path> status --porcelain` is empty, then `ORCA worktree rm --worktree id:<worktree_id> --json`, adding `--delete-branch` when the work is merged into the default branch (Orca keeps any branch it cannot prove merged). Removal stops the worktree's remaining sessions. A worktree with uncommitted changes stays in place and goes in the final report; removal is never forced.

**Sweep merged PRs** at the end of the batch and whenever the user comes back to it (for status, review fixes, or cleanup): `gh pr view <PR URL> --json state` for every worktree still in place, and remove each one whose PR merged or closed.

Your own coordinator session stays open until the final report.

## Deliver

For combined delivery, push the integration branch once every issue that can land has landed, open one pull request covering the batch with a `Closes #<number>` line per merged issue, attach it, set the integration worktree to `in-review`, and close its sessions. For per-issue delivery, every pull request is already open. Then remove the held-back worktrees and sweep merged PRs (**Clean up**).

The batch has settled when every Task has an outcome, `worker-list --run <run_id> --terminal-state reclaimable --json` returns none, `terminal list` shows no batch-started session left in any batch worktree, and every batch worktree is either removed or still holds an open PR, a parked blocker, or uncommitted changes. Finish with a concise list per issue: status, agent, pull request link, and any unresolved blocker, plus each worktree still in place and what it is waiting on, any worker you retained, and any session you left open and why. Tell the user to ask you to clean up the batch once its PRs merge.
