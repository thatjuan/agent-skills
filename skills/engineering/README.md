# Engineering

Orchestration and delivery-workflow skills — how work gets planned, delegated, implemented, reviewed, and committed. Listed in pipeline order: `ship` coordinates, `design-doc` gates the design, `implement-issue` → `team-executor` → `software-engineer` deliver each issue, the `codex-*` skills are the delegation lanes to the OpenAI Codex CLI, and `commitpush` closes out the change.

- **[ship](./ship/SKILL.md)** — Task entrypoint and delivery orchestrator: triage a raw task, decide whether it needs a design doc and GitHub issues, then assemble agent teams that route each job to the right model.
- **[design-doc](./design-doc/SKILL.md)** — Author or review a right-sized software design doc (tech spec, RFC, architecture proposal), grounded in the "Write an Effective Design Doc" practices from Refactoring English.
- **[implement-issue](./implement-issue/SKILL.md)** — Take a GitHub issue from number to pull request: branch, plan with a stack-specialized team, confirm the approach, build via team-executor, and open the PR.
- **[team-executor](./team-executor/SKILL.md)** — Turn a braindump into executed results: assemble an expert planning team, produce an execution plan, then deploy a fresh execution team for autonomous delivery.
- **[software-engineer](./software-engineer/SKILL.md)** — The architect/developer/reviewer engineering SME and base layer for any agent that writes or reviews code, holding the work to the Three Lenses and Eight Standards.
- **[codex-implementation](./codex-implementation/SKILL.md)** — Delegate bulk, mechanical, or clear-spec implementation to the OpenAI Codex CLI (gpt-5.5) via non-interactive `codex exec`.
- **[codex-review](./codex-review/SKILL.md)** — Run an independent code review through the Codex CLI over uncommitted changes, a branch diff, a commit range, or a GitHub PR.
- **[codex-computer-use](./codex-computer-use/SKILL.md)** — Drive browser, GUI, and visual-verification work through Codex — a Playwright MCP browser and screenshot analysis.
- **[commitpush](./commitpush/SKILL.md)** — Safe commit-and-push workflow with secrets detection, sensitive-file screening, and submodule-aware prompting.
