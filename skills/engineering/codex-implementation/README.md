# codex-implementation

> Delegate code implementation to the OpenAI Codex CLI (gpt-5.6) via non-interactive `codex exec` — with a strict prompt contract, sandboxing, and mandatory diff verification afterward.

## What it does

`codex-implementation` turns Codex into a reliable implementation subcontractor. It encodes the full non-interactive invocation for codex-cli 0.142.5 — global-vs-subcommand flag placement, sandbox modes, reasoning effort, the stdin gotcha that silently hangs harness runs — plus a four-part prompt contract (scope, acceptance criteria, verification, output format) that GPT-5-class models follow far more faithfully than freeform asks.

The skill treats Codex output as a claim, not a result: after every run it reads the diff, re-runs the tests, and reports verified facts separately from Codex's own summary.

## When to use it

- *"Have Codex implement the change described in the issue."*
- *"Ship this migration with gpt-5.6, it's mechanical."*
- Model-routing policies that send bulk/clear-spec implementation to gpt-5.6
- Parallel work lanes where Codex builds one branch while other agents review or plan

**Not the right skill if** the work needs review only (→ [`codex-review`](../codex-review/)) or visual/browser verification (→ [`codex-computer-use`](../codex-computer-use/)).

## Example walkthrough

**Prompt**

> Use Codex to add a `--dry-run` flag to `scripts/release.ts`.

**What the skill does**

1. Preflight — confirms `codex` is installed, snapshots `git status`, creates `codex/dry-run-flag` branch.
2. Builds the invocation: `codex -a never exec -m gpt-5.6-sol -c model_reasoning_effort='"high"' -s workspace-write --output-last-message /tmp/codex-final.txt "…" </dev/null`.
3. The prompt states scope (`scripts/release.ts` and its tests only), acceptance criteria (dry-run prints the plan, mutates nothing, normal mode unchanged), verification (run the test file), and output format (bullet list).
4. After the run: checks exit code, reads `git diff`, runs tests itself, reports confirmed results vs Codex claims.

## Installation

```bash
npx skills add thatjuan/agent-skills --skill codex-implementation
```

## Bundled resources

| File | Purpose |
|------|---------|
| `SKILL.md` | Command anatomy, flag/sandbox/effort tables, prompt contract, resume, verification workflow, troubleshooting |

## Tips

- **The prompt contract is the skill.** Scope + acceptance criteria + verification + output format. Skipping any of the four is how you get out-of-scope diffs.
- **Budget timeouts by effort.** Codex writes nothing to stdout until it finishes — a killed run looks like an empty success. `xhigh` can run 20–120 minutes.
- **`-a never` and `--search` go before `exec`.** Placing them after is the most common 0.142.5 flag error.
- **Never skip the diff read.** Codex's final message says what it thinks it did; `git diff` says what happened.

## Related skills

- [`codex-review`](../codex-review/) — independent Codex review of the resulting diff
- [`codex-computer-use`](../codex-computer-use/) — visual verification of UI-facing changes
