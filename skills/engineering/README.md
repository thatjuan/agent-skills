# Engineering

The issue-driven delivery loop: `capture-issues` turns a braindump into detailed GitHub issues, `batch-implement` works through them one subagent at a time (or `orca-implement` through Orca workers and worktrees), and `commitpush` lands each change safely.

- **[capture-issues](./capture-issues/SKILL.md)** — Turn a braindump, doc, or conversation into a small set of highly detailed GitHub issues, grouped under milestones where appropriate.
- **[batch-implement](./batch-implement/SKILL.md)** — Implement a batch or milestone sequentially with a fresh subagent per issue and configurable branch and pull request delivery.
- **[orca-implement](./orca-implement/SKILL.md)** — Implement a batch or milestone through supervised Orca workers, one Orca worktree per issue, in parallel waves where dependencies allow, with one combined pull request or one per issue.
- **[commitpush](./commitpush/SKILL.md)** — Safe commit-and-push workflow with secrets detection, sensitive-file screening, and submodule-aware prompting.
- **[list-issues](./list-issues/SKILL.md)**: List every open GitHub issue in the current repo, grouped by category, newest number first, with the date opened and a one-line description.
