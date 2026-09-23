# list-issues

> List every open GitHub issue in the current repo, grouped by category, newest number first, one line each.

## What it does

Pulls the open issues with `gh issue list`, groups them by label (or by an inferred category when the repo has no labels), and prints one line per issue: number, date opened (in the machine's local time zone), and a one-sentence description.

## When to use it

- *"What issues are open?"*
- *"List the unresolved issues."*
- *"What's outstanding in this repo?"*

## Example output

```
### Bug
- #42 2026-09-18 Login fails when the email contains a plus sign.
- #37 2026-09-02 CSV export drops the header row.

### Feature
- #40 2026-09-10 Add dark mode to the settings page.
```

## Installation

```bash
npx skills add thatjuan/agent-skills --skill list-issues
```

## Bundled resources

| File | Purpose |
|------|---------|
| `SKILL.md` | Fetch, grouping rules, and output format |

## Related skills

- [`capture-issues`](../capture-issues/README.md): writes the issues this skill lists.
- [`batch-implement`](../batch-implement/README.md): works through them.
