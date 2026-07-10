# atlassian-cli

> Expertise for Atlassian's official command-line interface (`acli`) — Jira Cloud automation and Atlassian organization admin from the terminal.

## What it does

`atlassian-cli` turns your agent into an `acli` expert. `acli` is the binary Atlassian ships for scripting Jira Cloud and org-admin tasks, and this skill knows its command tree, flag signatures, and the uniform selection pattern that makes bulk operations work. It covers:

- **Authentication** — the two independent auth contexts (`acli jira auth` scoped to a site, `acli admin auth` scoped to an org), web OAuth vs. token-via-stdin, `status`/`switch`/`logout`.
- **Work items** — the feature-dense `jira workitem` group: `create`, `create-bulk`, `search`, `view`, `edit`, `assign`, `transition`, `comment-*`, `link`, `clone`, archive/watcher management.
- **Selection primitives** — the shared `--key` / `--jql` / `--filter` / `--from-json` / `--from-file` selectors that let one command surface act on one item or thousands.
- **Project, board, sprint, filter, field, dashboard** — full lifecycle commands for each.
- **Admin & Rovo Dev** — managed-account lifecycle (`admin user activate|deactivate|delete|cancel-delete`) and Rovo Dev CLI authentication.

It triggers when scripts invoke `acli` or the user asks about the Atlassian CLI, Jira CLI, JQL-driven automation, or bulk Jira operations.

## When to use it

Invoke this skill when you hear:

- *"Bulk-transition every ticket matching this JQL to Done."*
- *"Create 30 subtasks from this list without confirmation prompts."*
- *"Log in to Jira from a CI script without leaking the token into shell history."*
- *"Export a sprint's work items as CSV for a standup report."*
- *"Reassign all of this person's open issues to someone else."*
- *"Deactivate these org accounts, but keep the delete reversible."*

## Installation

```bash
npx skills add thatjuan/agent-skills --skill atlassian-cli
```

## Bundled resources

| File | Purpose |
|------|---------|
| `SKILL.md` | Command tree, dual auth model, work-item core capabilities and selection primitives, project/board/sprint/filter/field/dashboard summary, admin/Rovo Dev, platform limitations |
| `references/workitem.md` | Full `jira workitem` reference — every subcommand, flag, and bulk-operation option |
| `references/jira-other.md` | Concise command reference for project, board, sprint, filter, field, and dashboard |
| `references/admin-rovodev.md` | Org-admin user lifecycle, `admin auth`, and Rovo Dev CLI authentication |
| `references/recipes.md` | Workflow recipes — daily standup report, sprint rollover, bulk reassignment, JQL-driven exports |

## Tips

- **`acli <command> --help` is authoritative.** The `-h` flag on any leaf reveals its exact flag set — reach for it when a signature is uncertain rather than guessing.
- **Pipe tokens through `--token` on stdin.** `echo "$API_TOKEN" | acli jira auth login --site ... --email ... --token` keeps credentials out of shell history.
- **The selectors are uniform.** `--key`, `--jql`, and `--filter` work across `edit`, `assign`, `transition`, `delete`, and `clone` — learn them once, apply everywhere. Pair with `--yes` and `--ignore-errors` for unattended bulk runs.
- **`--generate-json` templates bulk work.** Emit a JSON skeleton, fill it, and feed it back via `--from-json` for repeatable multi-item creates and edits.
- **Jira auth and admin auth are separate.** Being logged into a Jira site does not authenticate org-admin commands, and vice versa.

## Related skills

- None in this repo yet — pair with any workflow that reads or writes tracked work items from the command line.
