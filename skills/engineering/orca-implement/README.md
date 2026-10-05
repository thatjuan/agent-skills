# orca-implement

`orca-implement` is the [Orca](https://www.onorca.dev/docs) version of `batch-implement`. It works through every issue in a batch or GitHub milestone, but each issue goes to a supervised Orca worker running in an Orca worktree instead of an in-session subagent. The coordinator drives the batch through Orca's orchestration layer (one Run for the batch, one Task per issue) and owns every commit, push, and pull request.

Before work starts, the skill asks which Orca agent (Claude Code, Codex, Cursor, and so on) should implement the issues, or whether the coordinator should choose per issue. It also asks how to deliver the work:

- One feature branch and one pull request for the whole batch. The issues run one after another in a single batch worktree.
- One feature branch and one pull request per issue. Each issue gets its own worktree, independent issues run in parallel, and an issue that depends on another stacks its branch and pull request on that issue's branch.

It requires the Orca app with orchestration enabled (Settings → Experimental) and the `orchestration` skill that ships with Orca. Worktrees stay in place after the batch so you can review them in Orca and clean them up once the pull requests merge.

## Install

```bash
npx skills add thatjuan/agent-skills --skill orca-implement
```
