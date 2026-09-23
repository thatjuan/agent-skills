---
name: list-issues
description: List every open GitHub issue in the current repo, grouped by category and sorted newest-number first, one line each. Use when the user asks what issues are open, unresolved, or outstanding.
---

# List issues

Fetch every open issue in the current repo, converting each creation date to the system's local time zone:

```bash
gh issue list --state open --limit 1000 --json number,title,createdAt,labels,body \
  --jq 'map(.createdAt |= (fromdateiso8601 | strflocaltime("%Y-%m-%d")))'
```

GitHub returns `createdAt` in UTC; `strflocaltime` converts it using the machine's time zone (`TZ` or the OS setting). Use the converted date as is. Do not reformat it from the raw UTC timestamp, or an issue opened late in the evening shows the next day.

## Categories

- Use the repo's labels as categories. An issue with several labels goes under its most specific one, so each issue appears exactly once.
- When the repo does not label its issues, infer a short category (a word or two) from each issue's title and body.
- Put issues that fit no category under **Other**, last.

## Output

A heading per category, then one line per issue, sorted by issue number descending:

```
### Bug
- #42 2026-09-18 Login fails when the email contains a plus sign.
- #37 2026-09-02 CSV export drops the header row.

### Feature
- #40 2026-09-10 Add dark mode to the settings page.
```

- Date is the day the issue was opened in the system's local time zone, `YYYY-MM-DD`.
- The description is one sentence or less, rewritten from the title and body so it says what the issue is about.

The list is done when every open issue appears exactly once. Print the list and nothing else.
