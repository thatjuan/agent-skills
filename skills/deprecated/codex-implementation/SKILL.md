---
name: codex-implementation
description: Delegate code implementation to the OpenAI Codex CLI (gpt-5.6) via non-interactive `codex exec`. Use when handing bulk, mechanical, or clear-spec implementation work to Codex, when the user asks to have Codex implement, build, refactor, or fix something, or when a model-routing workflow assigns implementation to gpt-5.6. Covers command anatomy, sandbox modes, the implementation prompt contract, structured output, session resume, and verifying the resulting diff.
---

# Codex Implementation

Drive the OpenAI Codex CLI as a code-changing agent from scripts or an agent harness. The contract: explicit scope, explicit acceptance criteria, explicit verification, explicit output format — then verify the diff yourself.

*Command surface verified against codex-cli 0.142.5; on flag errors, recheck `codex --help` and `codex exec --help` — placement and availability shift between versions.*

## When to use

- Bulk or mechanical implementation with a clear spec (migrations, refactors, well-defined features)
- Work explicitly routed to gpt-5.6 / Codex by the user or a model-routing policy
- Parallel implementation lanes where Codex handles one branch of work

Not for: tasks needing your own conversation context Codex can't see (write a self-contained prompt instead), or taste-critical UI/copy work unless the routing policy sends it there.

## Preflight

```bash
codex --version                 # confirm CLI present; stop and report if missing
git status --short              # know the starting state
git switch -c codex/<task-slug> # work on a branch when the change is nontrivial
```

## Canonical invocation

```bash
codex \
  -a never \
  exec \
  -m gpt-5.6-sol \
  -c model_reasoning_effort='"high"' \
  -s workspace-write \
  -C "$PWD" \
  --output-last-message /tmp/codex-final.txt \
  "<implementation prompt — see contract below>" \
  </dev/null 2>/tmp/codex-progress.log
```

Key mechanics:

- **Flag placement matters.** `-a` (approval policy) and `--search` are **global** flags — they go **before** `exec`. `codex exec -a never` is rejected by 0.142.5. Equivalent post-`exec` forms: `-c approval_policy='"never"'`, `-c web_search='"live"'`. `-s` is accepted both globally and on `exec`, but subcommands like `exec review` only get it globally.
- **stdin gotcha.** `codex exec` reads stdin and can hang forever if stdin is open-but-empty (zero output, zero CPU). Always append `</dev/null` unless intentionally piping data.
- **stdout vs stderr.** Final agent message → stdout. Progress/thinking/tool activity → stderr. Suppress with `2>/dev/null` or capture to a log.
- **`--full-auto` is deprecated** (hidden in 0.142.5 help). Spell out `-s workspace-write` plus `-a never` instead.
- **Git check.** Codex refuses to run outside a git repo. `--skip-git-repo-check` only for disposable scratch dirs.

## Flag reference

| Need | Form | Notes |
|------|------|-------|
| Model | `-m gpt-5.6-sol` | `codex debug models` lists the catalog. Plain `gpt-5.6` is invalid; variants: `-sol` (frontier, default), `-terra` (balanced), `-luna` (fast/cheap) |
| Reasoning effort | `-c model_reasoning_effort='"low\|medium\|high\|xhigh"'` | quote the TOML string |
| Sandbox | `-s read-only` / `-s workspace-write` / `-s danger-full-access` | workspace-write for implementation |
| Approvals off | `codex -a never exec …` | global flag, before `exec` |
| Working dir | `-C /path/to/repo` | sets agent root |
| Extra writable dir | `--add-dir /path` | alongside the workspace |
| Web search | `codex --search exec …` or `-c web_search='"live"'` | global flag, before `exec` |
| Image input | `-i /tmp/shot.png` | repeatable |
| Final message to file | `-o file` / `--output-last-message file` | deterministic capture |
| Schema-constrained output | `--output-schema schema.json` | JSON Schema for the final response |
| JSONL event stream | `--json` | lifecycle events on stdout instead of formatted output |
| No session persistence | `--ephemeral` | disables later resume |
| Profile | `-p <name>` | loads `$CODEX_HOME/<name>.config.toml` |
| Outside git | `--skip-git-repo-check` | scratch dirs only |

## Sandbox modes

| Mode | Permits | Use |
|------|---------|-----|
| `read-only` | inspect only | dry runs, analysis |
| `workspace-write` | edit workspace, run local commands; network still bounded | default for implementation |
| `danger-full-access` | no filesystem/network limits | only inside disposable VMs/containers |

Network inside workspace-write: `-c sandbox_workspace_write.network_access=true`, or preinstall dependencies before the run.

## Effort selection and timeout budgets

| Effort | Use for | Harness timeout budget |
|--------|---------|------------------------|
| `low` | mechanical edits, known fixes | 3–15 min |
| `medium` | routine implementation | 5–30 min |
| `high` | multi-file work, concurrency, migrations | 10–60 min |
| `xhigh` | hard debugging, architecture, high-risk changes | 20–120 min |

Codex produces **no intermediate stdout** — killed early means silently empty output. Run in background with a generous timeout, or wrap: `/usr/bin/perl -e 'alarm shift; exec @ARGV' 3600 codex …`.

## Prompt contract

GPT-5-class Codex models respond to operational specificity. Every implementation prompt states four things:

```text
Implement <task, or "the change described in ./task.md">.

Scope:
- Edit only <paths/globs>. Do not touch <exclusions>.
- Do not change <public APIs / schemas / generated files>.

Acceptance criteria:
- <observable behavior 1>
- <observable behavior 2>

Verification:
- Run <exact test command>.
- If tests cannot run, state the exact blocker.

Final message:
- Bullet list only — changed files, tests run, residual risks.
```

Bad: `Fix the auth bug.` — no symptom, scope, tests, or output contract.

For machine-parseable results, add `--output-schema` and demand "final response must match the schema", then parse the `--output-last-message` file.

## Passing context in

- **Point at paths**, don't paste files: "Read ./docs/api.md and ./src/server. Implement the described behavior."
- **Pipe a snapshot** when immutability matters: `git diff | codex exec "…" ` (stdin appended as a `<stdin>` block).
- **Whole prompt from file**: `codex exec - < task.txt`.
- **Images**: `-i mockup.png` (repeatable).
- **AGENTS.md** is auto-discovered: `~/.codex/AGENTS.md` (global), then project root down to cwd; `AGENTS.override.md` wins at each level.

## Session resume

```bash
codex exec resume --last "fix the race conditions you found" </dev/null
codex exec resume <SESSION_ID> "continue; run the narrowest relevant tests" </dev/null
```

`--last` picks the newest session for the cwd (`--all` for any dir). Conversation context and prior tool observations carry over; shell state and env changes do not — restate critical constraints. Don't add config flags on resume; the session keeps its model/effort/sandbox.

## After the run — always verify

1. Check exit code; nonzero → inspect the stderr log before trusting anything.
2. `git diff --stat && git diff` — read the change, confirm scope was respected.
3. Run the tests yourself; don't take Codex's word for it.
4. Report faithfully: separate what you verified from what Codex claimed.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Hangs, zero output, zero CPU | stdin open-but-empty | append `</dev/null` |
| Empty stdout after completion | output went to `--output-last-message`, or run failed | check exit code + stderr log |
| `unexpected argument '-a'` / `'--search'` | global flags placed after `exec` | move before `exec`, or use `-c` equivalents |
| Sandbox denial on npm/network | workspace-write bounds network | preinstall deps, or `-c sandbox_workspace_write.network_access=true` |
| Refuses to run | not a git repo | `git init` or `--skip-git-repo-check` (scratch only) |
| Model/effort rejected | catalog mismatch | `codex debug models` |
