---
name: codex-review
description: Run code reviews through the OpenAI Codex CLI via `codex exec review` and read-only `codex exec`. Use when asking Codex/gpt-5.5 to review uncommitted changes, a branch diff, a commit, a commit range, or a GitHub PR, or when a workflow wants an independent second-opinion review from an OpenAI model. Covers review targets, read-only sandboxing, severity-scoped prompts, machine-parseable JSON findings, and the duty to verify findings before relaying them.
---

# Codex Review

Use Codex as an independent reviewer. Always read-only, always scoped, always machine-parseable when a harness consumes the result — and never relay a finding you haven't checked against the code.

*Command surface verified against codex-cli 0.142.5; on flag errors, recheck `codex --help` and `codex exec --help` — placement and availability shift between versions.*

## When to use

- Independent second-opinion review of a diff, branch, commit, or PR
- Review workflows that route to gpt-5.5 alongside Claude reviewers
- Pre-merge risk sweeps (correctness, security, data loss, concurrency, migrations)

## Preflight

```bash
codex --version       # confirm CLI present; stop and report if missing
git fetch origin main # when reviewing against a base
```

## Review targets (`codex exec review`)

The dedicated subcommand supports exactly three targets in 0.142.5 — no `--range`, no `--pr`:

```bash
# Uncommitted work (staged + unstaged + untracked)
codex -a never -s read-only exec review \
  --uncommitted \
  "<scope prompt>" </dev/null 2>/dev/null

# Branch diff vs base
git fetch origin main
codex -a never -s read-only exec review \
  --base origin/main \
  "<scope prompt>" </dev/null 2>/dev/null

# Single commit (optional --title for context)
codex -a never -s read-only exec review \
  --commit abc1234 --title "auth refresh concurrency fix" \
  "<scope prompt>" </dev/null 2>/dev/null
```

`codex exec review` also accepts `-m`, `-c`, `--json`, `--output-last-message`, `--output-schema`, `--ephemeral`. Global flags (`-a`, `--search`) go **before** `exec`.

The review subcommand accepts no `-s`/`--sandbox` flag of its own (verified via `codex exec review --help`), which is why every example places `-s` globally, before `exec`.

### Commit ranges and PRs — pipe a diff to plain `exec`

```bash
# Commit range
git diff --find-renames origin/main...HEAD \
  | codex -a never -s read-only exec \
      -m gpt-5.5 -c model_reasoning_effort='"high"' \
      "<scope prompt>" \
  > /tmp/range-review.md 2>/dev/null

# GitHub PR — either checkout + --base, or pipe the patch
gh pr checkout 123 && git fetch origin main
codex -a never -s read-only exec review --base origin/main "<scope prompt>" </dev/null 2>/dev/null

gh pr diff 123 --patch --color never \
  | codex -a never -s read-only exec "<scope prompt>" > /tmp/pr-123-review.md 2>/dev/null
```

Piped stdin is appended to the prompt as a `<stdin>` block. When piping, do **not** add `</dev/null`.

## Scope prompt template

Unscoped reviews produce nits. State target, scope, format, and reliability rules:

```text
Review target: branch diff against origin/main.

Scope:
- Correctness, security, data loss, concurrency, and migration risks only.
- No formatting, naming, or preference comments unless they hide a real bug.
- Ignore generated files and snapshots unless they prove a behavioral regression.

Finding format:
- severity: blocker | high | medium | low
- file:line
- title, why this is a bug, minimal fix direction

Reliability rules:
- Every finding must cite a concrete file:line from the diff or surrounding code.
- Do not speculate. If evidence is insufficient, omit the finding.
- If there are no findings, output {"findings":[]}.

Final message must be valid JSON only:
{"findings":[{"severity":"","file":"","line":0,"title":"","rationale":"","fix":""}]}
```

Narrow the scope line to specialize: security-only, migration-only, test-coverage-only.

## Machine-parseable findings

Prompt-only JSON formatting drifts. For strict parsing, combine `--output-schema` with `--output-last-message`:

```bash
schema=$(mktemp /tmp/review-schema.XXXXXX.json)
printf '%s\n' '{
  "type": "object", "additionalProperties": false, "required": ["findings"],
  "properties": { "findings": { "type": "array", "items": {
    "type": "object", "additionalProperties": false,
    "required": ["severity", "file", "line", "title", "rationale", "fix"],
    "properties": {
      "severity": { "enum": ["blocker", "high", "medium", "low"] },
      "file": { "type": "string" }, "line": { "type": "integer", "minimum": 1 },
      "title": { "type": "string" }, "rationale": { "type": "string" }, "fix": { "type": "string" }
    } } } }
}' > "$schema"

codex -a never -s read-only exec review \
  --base origin/main \
  --output-schema "$schema" \
  --output-last-message /tmp/review-findings.json \
  "Review correctness and security only. Final message must match the schema." \
  </dev/null 2>/dev/null
```

Parse `/tmp/review-findings.json`, not stdout.

## Model and effort

Default `-m gpt-5.5`. Effort by stakes: `medium` for routine diffs, `high` for security-sensitive or concurrency-heavy changes, `xhigh` for high-risk pre-release audits. Reviews at `high`/`xhigh` can run 10–60+ minutes with no intermediate output — budget the harness timeout accordingly.

## Relaying findings — verification duty

Before reporting any Codex finding:

1. Open the cited `file:line` and decide whether the finding is real.
2. Separate **confirmed issues** from **unverified Codex suggestions** in the report.
3. If Codex found nothing, say so explicitly and name the review target it inspected.
4. If `codex` is missing or exits nonzero, report the error and offer to review directly instead.

Follow-up on a finding reuses the session:

```bash
codex exec resume --last "Expand on finding 2 — show the exact failure interleaving." </dev/null 2>/dev/null
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Findings full of nits | unscoped prompt | use the scope template; exclude style explicitly |
| JSON unparseable | prompt-only formatting | `--output-schema` + `--output-last-message` |
| `unexpected argument '--pr'` / `'--range'` | targets don't exist in 0.142.5 | pipe `gh pr diff` / `git diff A...B` to plain `exec` |
| Hangs | stdin open-but-empty | `</dev/null` (unless piping a diff) |
| Review of stale code | forgot to fetch | `git fetch origin main` before `--base origin/main` |
