# codex-review

> Independent code review through the OpenAI Codex CLI — `codex exec review` for uncommitted work, branch diffs, and commits; piped-diff patterns for commit ranges and GitHub PRs; JSON findings a harness can parse.

## What it does

`codex-review` runs Codex as a second-opinion reviewer, always in a read-only sandbox. It documents the exact review targets codex-cli 0.142.5 supports (`--uncommitted`, `--base`, `--commit` — and what it doesn't: no `--range`, no `--pr`), with `gh pr diff | codex exec` handoffs for the rest.

Two things make its reviews usable in automation: a scope-prompt template (severity taxonomy, mandatory `file:line` citations, no-speculation rule, explicit style exclusions) that kills nitpick noise, and `--output-schema` + `--output-last-message` for findings as validated JSON instead of prose.

The skill also enforces a relaying discipline: every finding gets checked against the cited code before it's reported, and confirmed issues are separated from unverified Codex suggestions.

## When to use it

- *"Have Codex review this branch before I merge."*
- *"Get a gpt-5.6 second opinion on PR #123, security only."*
- Review workflows pairing an OpenAI reviewer with Claude reviewers for independent perspectives
- Pre-release risk sweeps at `high`/`xhigh` effort

**Not the right skill if** you want Codex to fix things (→ [`codex-implementation`](../codex-implementation/)) or to look at rendered UI (→ [`codex-computer-use`](../codex-computer-use/)).

## Example walkthrough

**Prompt**

> Codex-review my branch against main for correctness and data-loss risks.

**What the skill does**

1. `git fetch origin main`, then `codex -a never -s read-only exec review --base origin/main …` with the scope template (correctness/security/data-loss only, `file:line` required, `{"findings":[]}` when clean).
2. Adds `--output-schema` + `--output-last-message /tmp/review-findings.json` so the result parses.
3. Opens each cited `file:line`, confirms or rejects the finding.
4. Reports: 2 confirmed issues (with evidence), 1 unverified suggestion, 1 rejected false positive — clearly separated.

## Installation

```bash
npx skills add thatjuan/agent-skills --skill codex-review
```

## Bundled resources

| File | Purpose |
|------|---------|
| `SKILL.md` | Review targets, piped-diff/PR patterns, scope-prompt template, JSON schema recipe, verification duty, troubleshooting |

## Tips

- **Scope or drown in nits.** The template's exclusion lines ("no formatting/naming comments…") do more for signal than any model choice.
- **Ranges and PRs go through plain `exec`.** `codex exec review` has exactly three targets; pipe `git diff A...B` or `gh pr diff N --patch` for the rest.
- **Don't `</dev/null` when piping.** The diff *is* stdin. Everywhere else, do.
- **Verify before relaying.** A finding you haven't checked is a suggestion, not an issue — label it that way.

## Related skills

- [`codex-implementation`](../codex-implementation/) — have Codex fix what the review found
- [`codex-computer-use`](../codex-computer-use/) — visual regression checks alongside code review
