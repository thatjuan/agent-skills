# Jira Non-Workitem Commands

Reference for `jira project`, `jira board`, `jira sprint`, `jira filter`, `jira field`, `jira dashboard`, and `jira auth`.

## Table of Contents

- [jira auth](#jira-auth)
- [jira project](#jira-project)
- [jira board](#jira-board)
- [jira sprint](#jira-sprint)
- [jira filter](#jira-filter)
- [jira field](#jira-field)
- [jira dashboard](#jira-dashboard)

## jira auth

| Subcommand | Purpose |
|-----------|---------|
| `login` | Authenticate with an Atlassian host |
| `logout` | Remove stored credentials |
| `status` | Show active account |
| `switch` | Change active account when multiple are logged in |

### login flags

| Flag | Description |
|------|-------------|
| `--web`, `-w` | Browser-based OAuth flow |
| `--site`, `-s` | Atlassian site (e.g. `example.atlassian.net`) |
| `--email`, `-e` | Account email — required with token auth |
| `--token` | Read API token from stdin |

## jira project

| Subcommand | Purpose |
|-----------|---------|
| `create` | Create a project |
| `list` | List visible projects |
| `view` | Retrieve project detail |
| `update` | Modify project attributes |
| `archive` | Archive a project |
| `restore` | Restore an archived project |
| `delete` | Delete a project |

### create flags

| Flag | Description |
|------|-------------|
| `--key` | Project key (required) |
| `--name` | Project name (required) |
| `--description` | Description |
| `--url` | Associated URL |
| `--lead-email` | Project lead |
| `--from-project` | Clone configuration from an existing company-managed project |
| `--from-json` | JSON-defined creation |
| `--generate-json` | Emit a creation template |

## jira board

| Subcommand | Purpose |
|-----------|---------|
| `search` | Find boards |
| `list-sprints` | List sprints on a board |

## jira sprint

| Subcommand | Purpose |
|-----------|---------|
| `list-workitems` | List work items within a sprint |

## jira filter

| Subcommand | Purpose |
|-----------|---------|
| `list` | List my/favourite filters |
| `search` | Search filters by criteria |
| `add-favourite` | Mark filter as favourite |
| `change-owner` | Reassign filter ownership |

## jira field

| Subcommand | Purpose |
|-----------|---------|
| `create` | Create a custom field |
| `delete` | Soft-delete (moves to trash) |
| `cancel-delete` | Restore a trashed field |

## jira dashboard

| Subcommand | Purpose |
|-----------|---------|
| `search` | Find dashboards |
