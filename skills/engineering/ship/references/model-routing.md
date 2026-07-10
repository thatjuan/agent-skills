# Model Routing — Traits, Invocation, Prompting

The coordinator assigns an explicit model to every delegated agent. This file is the routing brain: what each model is good at, how to actually invoke it, and how to prompt it — because prompting techniques that work on one family actively hurt on another.

**Precedence**: if the user's global `~/.claude/CLAUDE.md` (or project CLAUDE.md) carries its own model rankings/routing section, that section is the source of truth — it reflects the user's actual subscription economics and current model versions. The tables below are portable defaults for when no such section exists.

## Glossary

- **Intelligence** — how hard a problem the model can handle unsupervised.
- **Taste** — UI/UX, code quality, API design, and copy. Whether the output is the code/text you'd *want*, not just code that works.
- **Cost** — effective cost to the user, accounting for subscription economics (Codex sub usage is extremely generous — treat GPT-5.5 as near-free; coordinator tokens are the most expensive thing in the system).

## Traits (1–10, higher = better; cost 10 = cheapest)

| Model | Cost | Intelligence | Taste | Notes |
|---|---|---|---|---|
| Fable (coordinator) | 2 | 9 | 9 | Best in class on both axes. Reserve for planning, hard problems, review, merge judgment, taste-critical glue. |
| Opus | 4 | 7 | 8 | Meaningfully cheaper than the coordinator, high taste. Often cheaper than Sonnet in practice because Sonnet is token-hungry. |
| GPT-5.5 via Codex CLI | 9 | 8 | 5 | Handles hard problems from a clear spec; writes TypeScript like a Python dev and Rust like a paranoid C++ dev. Also the only computer-use option that actually works (Xcode, simulators, full desktop). |
| Sonnet | 5 | 5 | 7 | Wrapper duty (e.g., hosting a codex call inside a workflow), mechanical checks, light user-facing polish when Opus is overkill. |
| Haiku | 10 | 2 | 2 | Never use. With GPT-5.5 near-free there is no task where Haiku is the right answer. |

Threshold: anything user-facing (UI, copy, API design) needs **taste ≥ 7**.

**Priority for anything that ships: intelligence ≥ taste > cost.** Cost breaks ties and gates exploration, never final quality. Standing permission to redo cheap-model output with a smarter model without asking.

## Routing Quick Reference

| Work | Route to |
|---|---|
| Bulk mechanical work — clear-spec implementation, migrations, codemods, data analysis | GPT-5.5 (codex) |
| Digging through logs, giant PDFs/specs, anything token-devouring | GPT-5.5 (codex) — burn its tokens, not yours |
| Computer use — browser flows, simulators, Xcode, screenshots, runtime verification | GPT-5.5 (codex computer-use) |
| User-facing code — public API, SDK surface, UI, copy (taste ≥ 7 needed) | Opus, coordinator reviews |
| Moderate-complexity in-repo implementation with conventions to follow | Opus (with `software-engineer` skill attached) |
| Independent second review of a plan or PR | Opus or coordinator; add Codex as an extra independent perspective (strongest on Claude-written code) |
| Plan review, architecture calls, contested decisions | Coordinator |

## Invocation Mechanics

### Claude models — Agent tool / team-executor

Pass `model: "opus"` / `model: "sonnet"` on the Agent call, or specify the model per role when overlaying `team-executor`. Attach `software-engineer` (prefer-when-present) to any agent that writes or reviews code. Reasoning effort: high at most — never xhigh/max (per-step overthinking, bloated diffs, absurd cost; effort does not extend runway, only thought-per-step).

### GPT-5.5 — codex CLI (only path to it)

Prefer dedicated codex skills when installed — `codex-implementation`, `codex-review`, `codex-computer-use`, or the `codex` skill from the skill-codex plugin — their command references govern. For work they don't cover (investigation, data analysis), run `codex exec -s read-only` directly with a self-contained prompt. Core shape:

```bash
# read-only analysis/review
codex exec --skip-git-repo-check -m gpt-5.5 \
  --config model_reasoning_effort="high" \
  --sandbox read-only "PROMPT" </dev/null 2>/dev/null

# implementation (edits allowed) — run inside the target worktree with -C
codex exec --skip-git-repo-check -m gpt-5.5 \
  --config model_reasoning_effort="high" \
  --sandbox workspace-write --full-auto -C <WORKTREE> "PROMPT" </dev/null 2>/dev/null

# continue a session
echo "FOLLOW-UP" | codex exec --skip-git-repo-check resume --last 2>/dev/null
```

Hard-won gotchas:
- **Always `</dev/null`** when stdin isn't a closed TTY — codex reads stdin and hangs forever otherwise (symptom: zero output, zero CPU).
- **`2>/dev/null`** suppresses thinking tokens on stderr.
- **No intermediate output** — result appears only at completion. Prefer synchronous runs; if backgrounded, budget timeouts by effort (low 150s / medium 300s / high 600s).
- Give codex implementation work in an **isolated worktree** so a bad run costs nothing.

### GPT-5.5 inside Workflows

Workflow `agent()` calls can only spawn Claude models. To use codex in a workflow stage: spawn a **Sonnet agent on low effort** whose entire job is to shell out to `codex exec`, wait, and report the results back verbatim. Prefix its label `codex:` so runs are attributable in progress views. Account for codex's runtime in the wrapper's expectations.

## Prompting Techniques Per Model

The single most common failure: prompting Codex as if it were Claude. The families need opposite treatment.

### Prompting GPT-5.5 / Codex

- **Simple, literal, self-contained.** It has zero conversation context — include the repo path, the target files, the spec, and nothing else. One task per invocation.
- **No personas, no motivation, no "you are an expert".** Codex does what's asked and doesn't do what isn't — skip the "do not edit unrelated files" defensive lists that Claude models need.
- **Specify the output format explicitly** ("return a markdown list of file:line findings").
- **Tell it to report the empty case**: "If you find nothing, say that clearly and name what you inspected." Without this, empty results confuse the parent agent into wasteful re-runs.
- Point it at concrete inputs (paths, PR numbers, log files), not abstractions.
- **UI design tasks**: tell it to "use imagegen to imagine the design and implement that" — it renders a target before coding toward it.
- **Embed the engineering bar.** Codex can't carry the `software-engineer` skill, so paste this digest into every code-writing prompt:

  > Engineering bar: prefer the reframing that deletes complexity over adding branches. No new conditionals bolted into existing flows — extract a helper/abstraction instead. Reuse existing helpers and patterns; never near-duplicate one. Explicit typed contracts — no `any`, casts, or silent fallbacks; give domain concepts their own types. Keep logic in the module that owns the concept. Don't push a file past ~1000 lines — split first. Honest names. No TODOs, stubs, or placeholders. Match the project's existing conventions.

**Relaying Codex results**: before passing a Codex finding to the user or acting on it, inspect the cited code/diff enough to decide whether it's real. Separate confirmed issues from unverified Codex suggestions in any report. If `codex` is not installed or the command fails, report the error and do the work directly instead.

### Prompting Opus

- Give fuller context: conventions, pointers to exemplar files in the repo ("match the pattern in `src/api/users.ts`"), the issue text, acceptance criteria.
- Attach `software-engineer` for any code-writing/review role; name the definition of done (tests pass, self-review gate run).
- It benefits from explicit structure (numbered requirements, non-goals) more than Fable does, and needs guardrails against scope drift ("only touch X; if Y seems needed, stop and report").

### Prompting Fable-class subagents

- State the **goal, constraints, and verification bar**; do not enumerate steps — it decomposes work better than a hand-written procedure and will invent the right subagent archetypes for the task itself.
- Grant explicit authority up front ("you may create worktrees, rebase, open PRs") so it doesn't stall at permission boundaries.
- Keep effort at high. Trust-but-verify: it goes furthest end-to-end, so the checkpoints you set (CI, reviewers, merge gates) are the real control surface, not prompt-level restrictions.

## Maintenance

When a dispatch misroutes or a prompt-shape failure recurs, fix it *here* — append the lesson to this file (or the relevant skill) instead of re-litigating per session. This file is expected to evolve; model traits change with every release, and the table reflects judgment as of the last edit, not ground truth.
