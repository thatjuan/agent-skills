---
name: atlassian-cli
description: Atlassian CLI (acli) expertise for interacting with Jira Cloud and Atlassian organization admin from the terminal. Use when scripts invoke `acli`, user asks about Atlassian CLI, Jira CLI, JQL-driven automation, bulk Jira operations, or managing Jira work items, projects, boards, sprints, filters, fields, dashboards, Atlassian org admin users, or Rovo Dev authentication.
---

# Atlassian CLI (acli)

`acli` is Atlassian's official command-line interface for automating tasks and integrating with Atlassian Cloud products. The binary name is `acli`. Official reference: https://developer.atlassian.com/cloud/acli/reference/commands/

## Top-Level Command Tree

```
acli
├── admin              # Organization-admin operations
│   ├── auth           # login | logout | status | switch
│   └── user           # activate | cancel-delete | deactivate | delete
├── feedback           # Submit requests or report issues to Atlassian
├── jira               # Jira Cloud operations
│   ├── auth           # login | logout | status | switch
│   ├── board          # list-sprints | search
│   ├── dashboard      # search
│   ├── field          # cancel-delete | create | delete
│   ├── filter         # add-favourite | change-owner | list | search
│   ├── project        # archive | create | delete | list | restore | update | view
│   ├── sprint         # list-workitems
│   └── workitem       # archive | assign | attachment-delete | attachment-list |
│                      # clone | comment-create | comment-delete | comment-list |
│                      # comment-update | comment-visibility | create | create-bulk |
│                      # delete | edit | link | search | transition | unarchive |
│                      # view | watcher-remove
└── rovodev            # Atlassian's AI coding agent (Beta)
    └── auth           # Authenticate Rovo Dev CLI
```

The `-h` / `--help` flag is available on every command and subcommand and reveals the exact flag set for that leaf. `acli <command> --help` is the authoritative source when a flag signature is uncertain.

## Authentication Model

Two parallel auth contexts exist and are independent:

- `acli jira auth` — scoped to a Jira Cloud site (user token or OAuth).
- `acli admin auth` — scoped to an Atlassian organization admin account.

`acli jira auth login` accepts:

| Flag | Purpose |
|------|---------|
| `--web`, `-w` | Browser-based OAuth flow |
| `--site`, `-s` | Atlassian site (e.g. `mysite.atlassian.net`) |
| `--email`, `-e` | User email (required for token auth) |
| `--token` | Reads API token from stdin (keeps it out of shell history) |

Token-via-stdin example: `echo "$API_TOKEN" | acli jira auth login --site mysite.atlassian.net --email user@example.com --token`. Windows equivalent uses `Get-Content`.

`acli jira auth status` reports the currently authenticated account; `switch` changes the active account when multiple are logged in; `logout` removes credentials.

## Jira Work Item Commands — Core Capabilities

`jira workitem` is the most feature-dense command group. Full reference: [references/workitem.md](references/workitem.md).

### Selection Primitives

Most mutating subcommands (`edit`, `assign`, `transition`, `delete`, `archive`, `unarchive`, `clone`) accept one of these selectors:

- `--key "KEY-1,KEY-2"` — comma-separated work item keys
- `--jql "project = TEAM AND status = 'In Progress'"` — JQL query
- `--filter 10001` — numeric saved filter ID
- `--from-json path.json` — structured definition file
- `--from-file path.txt` — plain text list (for `assign`)

This uniform selection pattern enables bulk operations across the same command surface.

### Common Bulk-Operation Flags

| Flag | Behavior |
|------|----------|
| `--yes` | Skips interactive confirmation |
| `--ignore-errors` | Continues processing remaining items after failures |
| `--json` | Machine-readable output |
| `--generate-json` | Emits a template JSON for `--from-json` consumption |

### Create (`acli jira workitem create`)

Required: `--project`, `--type`, `--summary`. Optional: `--assignee` (`@me` for self), `--description`, `--description-file`, `--label` (comma-separated), parent linkage flags, `--from-file`, `--from-json`, `--editor`, `--generate-json`, `--json`.

### Search (`acli jira workitem search`)

Accepts `--jql` or `--filter`. Output controls: `--fields` (defaults to `issue type, key, assignee, priority, status, summary`), `--csv`, `--json`, `--limit`, `--paginate` (fetch all pages), `--count` (total only), `--web` (open in browser).

### View (`acli jira workitem view KEY-123`)

Positional argument is the work item key. `--fields` accepts:
- `*all` — every field
- `*navigable` — navigable fields
- Comma list: `summary,comment`
- Exclusions: `-description`

Default field set: `key,issuetype,summary,status,assignee,description`.

### Transition (`acli jira workitem transition`)

Requires a selector + `--status "Done"` (target status name). Supports bulk `--key`, `--jql`, `--filter`.

### Assign (`acli jira workitem assign`)

`--assignee` accepts email, account ID, `@me`, or `default` (project default). `--remove-assignee` clears it.

### Edit (`acli jira workitem edit`)

Updates summary, description, assignee, type, labels (add/remove). Supports all selectors plus `--generate-json` for templated bulk updates.

## Jira Project, Board, Sprint, Filter, Field, Dashboard

Concise command reference lives in [references/jira-other.md](references/jira-other.md). Highlights:

- `jira project create` — three input modes: `--from-project` (clone), `--from-json` (template-driven), or direct flags (`--key`, `--name`, `--description`, `--url`, `--lead-email`).
- `jira project list | view | update | archive | restore | delete` — full lifecycle.
- `jira board search` and `jira board list-sprints` — board discovery and sprint enumeration.
- `jira sprint list-workitems` — workitems in a given sprint.
- `jira filter list | search | add-favourite | change-owner` — saved filter management.
- `jira field create | delete | cancel-delete` — custom field lifecycle (soft-delete with restore).
- `jira dashboard search` — dashboard discovery.

## Admin & Rovo Dev

See [references/admin-rovodev.md](references/admin-rovodev.md).

- `admin user activate | deactivate | delete | cancel-delete` — managed-account lifecycle. Soft-delete is reversible via `cancel-delete`.
- `admin auth login | logout | status | switch` — organization-admin auth, separate from Jira auth.
- `rovodev auth` — authentication for Rovo Dev CLI (Atlassian's AI coding agent, Beta).

## Common Workflow Recipes

Recipe snippets for typical automation tasks (daily standup report, sprint rollover, bulk reassignment, JQL-driven exports) are in [references/recipes.md](references/recipes.md).

## Platform & Limitations

- Supported on macOS, Linux, Windows; installable via platform package managers (see Atlassian install guides).
- Atlassian Government Cloud is not supported.
- Shell autocompletion is available via `acli` completion setup.
