# `acli jira workitem` Reference

Complete command surface for Jira work items. Source: https://developer.atlassian.com/cloud/acli/reference/commands/jira-workitem/

## Table of Contents

- [Subcommand Summary](#subcommand-summary)
- [create](#create)
- [create-bulk](#create-bulk)
- [view](#view)
- [search](#search)
- [edit](#edit)
- [transition](#transition)
- [assign](#assign)
- [delete / archive / unarchive](#delete--archive--unarchive)
- [clone](#clone)
- [Comments](#comments)
- [Attachments](#attachments)
- [Links](#links)
- [Watchers](#watchers)
- [Selector Pattern](#selector-pattern)

## Subcommand Summary

| Subcommand | Purpose |
|-----------|---------|
| `archive` | Archive one or more work items |
| `assign` | Assign work items to assignees |
| `attachment-delete` | Remove attachments from a work item |
| `attachment-list` | List attachments on a work item |
| `clone` | Duplicate work items |
| `comment-create` | Add a comment |
| `comment-delete` | Remove a comment |
| `comment-list` | List comments on a work item |
| `comment-update` | Modify an existing comment |
| `comment-visibility` | Set comment visibility (role/group restricted) |
| `create` | Create a single work item |
| `create-bulk` | Create many work items in one call |
| `delete` | Delete work items |
| `edit` | Modify fields on existing work items |
| `link` | Manage issue links (block, relates, duplicates, etc.) |
| `search` | Search via JQL or saved filter |
| `transition` | Move work items to a new status |
| `unarchive` | Restore archived work items |
| `view` | Show details of a work item |
| `watcher-remove` | Remove a watcher from a work item |

## create

Creates one Jira work item.

| Flag | Description |
|------|-------------|
| `--project` | Project key (e.g. `TEAM`) |
| `--type` | Issue type: `Epic`, `Story`, `Task`, `Bug`, subtask types, etc. |
| `--summary` | Title |
| `--description` | Plain text or ADF description |
| `--description-file` | Read description from file |
| `--assignee` | Email, account ID, or `@me` |
| `--label` | Comma-separated labels |
| `--from-file` | Text file providing summary + description |
| `--from-json` | Full JSON definition |
| `--generate-json` | Emit a template JSON to stdout/file |
| `--editor` | Open `$EDITOR` for interactive input |
| `--json` | JSON output of the created item |

Example: `acli jira workitem create --project TEAM --type Task --summary "Rollup build times" --assignee @me --label perf,ci`

## create-bulk

Bulk-creates issues from a JSON payload. Pair with `--generate-json` to produce a template.

## view

Positional argument: work item key.

| Flag | Description |
|------|-------------|
| `--fields` | Comma list, `*all`, `*navigable`, or exclusions with `-` prefix |
| `--json` | JSON output |
| `--web` | Open in browser |

Default field set: `key,issuetype,summary,status,assignee,description`.

## search

Searches via JQL or saved filter.

| Flag | Description |
|------|-------------|
| `--jql` | JQL query string |
| `--filter` | Saved filter ID |
| `--fields` | Fields to include (default: `issue type, key, assignee, priority, status, summary`) |
| `--limit` | Max results |
| `--paginate` | Fetch all matching across pages |
| `--count` | Return only the total match count |
| `--csv` | CSV output |
| `--json` | JSON output |
| `--web` | Open search in browser |

## edit

Modifies summary, description, assignee, type, labels (add/remove) on one or many items.

Accepts any [selector](#selector-pattern) plus:
- `--description-file`
- `--generate-json` / `--from-json`
- `--ignore-errors`
- `--yes`
- `--json`

## transition

Moves items to a target status.

Required: selector + `--status "Done"` (target status name).

Supports `--yes`, `--ignore-errors`, `--json`.

Example: `acli jira workitem transition --jql "project = TEAM AND sprint in openSprints() AND status = 'In Review'" --status "Done" --yes`

## assign

| Flag | Description |
|------|-------------|
| `--key` / `--jql` / `--filter` / `--from-file` | Selectors |
| `--assignee` | Email, account ID, `@me`, or `default` |
| `--remove-assignee` | Clear assignee |
| `--ignore-errors` | Continue on failures |
| `--yes` | Skip confirmation |
| `--json` | JSON output |

## delete / archive / unarchive

Accept the standard selector set. `archive` soft-archives (reversible via `unarchive`); `delete` is terminal.

## clone

Duplicates one or more work items. Accepts the standard selectors.

## Comments

- `comment-create` — add a comment (supports ADF and `--description-file`-style inputs).
- `comment-update` — edit by comment ID.
- `comment-delete` — remove by ID.
- `comment-list` — enumerate comments on an item.
- `comment-visibility` — restrict to role or group.

## Attachments

- `attachment-list KEY-123` — list attachments on a work item.
- `attachment-delete` — delete a named attachment.

## Links

`acli jira workitem link` manages issue links (types include `blocks`, `is blocked by`, `relates to`, `duplicates`, etc.).

## Watchers

`watcher-remove` detaches a user from a work item's watcher list.

## Selector Pattern

Mutating and bulk subcommands share this selector set:

| Selector | Format |
|----------|--------|
| `--key` | `"KEY-1,KEY-2,KEY-3"` |
| `--jql` | Any valid JQL |
| `--filter` | Numeric filter ID |
| `--from-json` | Path to JSON describing items |
| `--from-file` | Path to plain text list (assign only) |

Pairing a selector with `--yes --ignore-errors --json` produces scriptable, idempotent bulk operations.
