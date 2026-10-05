# orca-implement

`orca-implement` is the [Orca](https://www.onorca.dev/docs) version of `batch-implement`. It works through every issue in a batch or GitHub milestone, giving each issue its own Orca worktree and a supervised Orca worker instead of an in-session subagent. The coordinator drives the batch through Orca's orchestration layer (one Run for the batch, one Task per issue) and owns every commit, push, and pull request.

How it works:

- **Waves.** The coordinator reads every issue and the code it touches, then decides which issues can run in parallel and which must wait. Issues that need another issue's code, or that would edit the same files, run after it. It shows the wave plan, then starts. At most four workers run at once unless you set another limit.
- **One worktree per issue.** Every issue gets a worktree linked to its GitHub issue, created up front. Each worktree's board status tracks the issue: `todo` while it waits, `in-progress` while a worker runs, `in-review` once it is committed and its PR is open, and `completed` once the PR merges. Worktree comments carry the PR link or the blocker.
- **Agents.** Workers run the same agent as the coordinator by default. You can name another agent, assign agents per issue or per kind of work, or ask for a mix.
- **Worker specs.** Each worker gets a self-contained spec: the issue verbatim, the worktree and branch, repository conventions and commands, what it builds on and what runs alongside it, the target files, constraints, and a checkable acceptance list. Workers leave changes uncommitted and report once through Orca's `worker_done`.

Before work starts, the skill asks how to deliver the work:

- One feature branch and one pull request for the whole batch. Each finished issue merges into a batch integration worktree, and one PR opens at the end.
- One feature branch and one pull request per issue. An issue that depends on another stacks its branch and PR on that issue's branch.

It requires the Orca app with orchestration enabled (Settings → Experimental) and the `orchestration` skill that ships with Orca. Worktrees stay in place after the batch so you can review them in Orca and clean them up once the pull requests merge.

## Install

```bash
npx skills add thatjuan/agent-skills --skill orca-implement
```
