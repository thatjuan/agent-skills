# Recipe Patterns

Concrete invocation patterns for common Atlassian CLI automation tasks. These are examples of correct `acli` invocations — the runtime selects and adapts them to the requested task.

## Table of Contents

- [Authentication](#authentication)
- [Creating Work Items](#creating-work-items)
- [Searching & Exporting](#searching--exporting)
- [Bulk Transitions](#bulk-transitions)
- [Bulk Assignment](#bulk-assignment)
- [Comments & Context](#comments--context)
- [Projects](#projects)
- [Sprint & Board Inspection](#sprint--board-inspection)
- [JSON-Template Workflow](#json-template-workflow)

## Authentication

Browser-based:
```bash
acli jira auth login --web
```

Token via stdin (keeps token out of shell history):
```bash
echo "$JIRA_API_TOKEN" | acli jira auth login \
  --site mysite.atlassian.net \
  --email user@example.com \
  --token
```

Verify:
```bash
acli jira auth status
```

## Creating Work Items

Single task:
```bash
acli jira workitem create \
  --project TEAM \
  --type Task \
  --summary "Upgrade Node to 20 LTS" \
  --assignee @me \
  --label infra,upgrade
```

From JSON template:
```bash
acli jira workitem create --generate-json > item.json
# edit item.json
acli jira workitem create --from-json item.json
```

Bulk create from JSON array:
```bash
acli jira workitem create-bulk --from-json items.json
```

## Searching & Exporting

JQL search, JSON output:
```bash
acli jira workitem search \
  --jql "project = TEAM AND status = 'In Progress' AND assignee = currentUser()" \
  --fields key,summary,status,assignee \
  --json
```

Export matching issues to CSV, paginating through all results:
```bash
acli jira workitem search \
  --jql "project = TEAM AND created >= -30d" \
  --paginate \
  --csv > recent.csv
```

Count only:
```bash
acli jira workitem search --jql "project = TEAM AND status != Done" --count
```

## Bulk Transitions

Move everything in review to done (confirmationless, continue past errors):
```bash
acli jira workitem transition \
  --jql "project = TEAM AND status = 'In Review' AND sprint in openSprints()" \
  --status "Done" \
  --yes \
  --ignore-errors \
  --json
```

Specific keys:
```bash
acli jira workitem transition --key "TEAM-101,TEAM-102" --status "In Progress" --yes
```

## Bulk Assignment

Self-assign a filter's worth of tickets:
```bash
acli jira workitem assign --filter 10042 --assignee @me --yes
```

Clear assignees on stale tickets:
```bash
acli jira workitem assign \
  --jql "project = TEAM AND updated < -90d" \
  --remove-assignee \
  --yes \
  --ignore-errors
```

## Comments & Context

Add a comment:
```bash
acli jira workitem comment-create --key TEAM-123 --description "Rolled out in build 2045"
```

List an issue's comments as JSON for programmatic use:
```bash
acli jira workitem comment-list --key TEAM-123 --json
```

## Projects

Clone an existing project's configuration:
```bash
acli jira project create \
  --from-project SOURCE \
  --key NEW \
  --name "New Team Project" \
  --lead-email lead@example.com
```

List accessible projects as JSON:
```bash
acli jira project list --json
```

## Sprint & Board Inspection

Find a board, list its sprints, then list workitems in a sprint:
```bash
acli jira board search --json
acli jira board list-sprints --board <boardId> --json
acli jira sprint list-workitems --sprint <sprintId> --json
```

## JSON-Template Workflow

For any command supporting `--generate-json` / `--from-json` (`workitem create`, `workitem create-bulk`, `workitem edit`, `project create`):

1. Generate a template: `acli <cmd> --generate-json > payload.json`
2. Populate the fields.
3. Execute: `acli <cmd> --from-json payload.json`

This pattern enables deterministic bulk operations stored alongside code.
