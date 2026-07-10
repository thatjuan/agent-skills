# software-engineer

> The base engineering brain a coding agent wears while it builds — the architect, developer, and reviewer subject-matter expert that carries the engineering quality bar and applies a great reviewer's standard from the first line, not just at review.

## What it does

`software-engineer` is the coding SME in a three-skill pipeline. It is **not** an orchestrator — it spawns no teams, runs no phases, manages no other agents. It is the engineering judgment a single coding agent reads and applies to its own work, so the diff it produces would survive the most demanding review.

It works through three lenses on the same eight standards:

- **Architect lens** (before writing) — frame the change so whole branches, modes, and layers never need to exist; decide module boundaries, the canonical owning layer, and domain-shaped data models; reuse before building; design atomic flows.
- **Developer lens** (while writing) — write the boring, direct version; push logic into dedicated abstractions instead of bolting on conditionals; make typed contracts explicit; no placeholders or stubs.
- **Reviewer lens** (before declaring done) — run the review gate on your own diff as a definition-of-done.

The core thesis: the standards are distilled from a brutal "thermo-nuclear" code-**review** bar, then **inverted** to apply at design and authoring time. The complexity a reviewer would make you delete is complexity you never write. This holds equally for new code and for changes to existing code.

It carries the eight engineering standards (structural simplification, the ~1000-line file boundary, no spaghetti growth, clean-over-working, boring-over-magical, typed boundaries, canonical-layer reuse, atomic/parallel work), per-domain standards (backend, frontend, data, devops/infra, security, testing/QA), and a production-readiness baseline.

## When to use it

Invoke this skill whenever an agent is **engineering production software**:

- Implementing, writing, or refactoring a feature.
- Updating or extending existing code.
- Reviewing a diff against a professional bar.
- Making a design or architecture decision.
- Whenever `team-executor` assigns it to a coding or review agent.

It applies to **both** new code and changes to existing code — an update is held to the same bar as greenfield work.

**It is the base layer, not the whole stack.** `software-engineer` defines *how* to engineer. Library- and SDK-specific skills (`heroui`, `drizzle-orm`, `temporal`) supply the *what* and overlay on top. A coding agent may carry `software-engineer` **plus one stack skill** — the one sanctioned exception to "one skill per agent."

## Example walkthrough

**Scenario**

> `team-executor` spawns an execution agent to add a new "archived" state to projects, and assigns it `software-engineer` plus `drizzle-orm`.

**What the skill does**

1. **Architect lens** — instead of threading `if (status === 'archived')` through a dozen list/query/render paths, the agent reframes: `status` becomes a typed enum on the model, and the existing query layer already filters by status. The new state needs almost no new branches — the complexity is designed out before it is written.
2. **Developer lens** — the migration is written reversible and safe on the live table; the status transition goes through one dedicated function rather than scattered inline checks; the Drizzle schema and query knowledge comes from the overlaid `drizzle-orm` skill, while `software-engineer` governs *where* that logic lives and *how* it is shaped.
3. **Reviewer lens** — before declaring done, the agent runs the review gate on its own diff: no file pushed past ~1000 lines, no feature checks scattered into shared code, the contract is explicitly typed, the migration is atomic, and the change was actually run. Only then is the step complete.

The result is a diff that was born clean — not one that worked and was cleaned up later.

## Installation

```bash
npx skills add thatjuan/agent-skills --skill software-engineer
```

## Bundled resources

| File | Purpose |
|------|---------|
| `SKILL.md` | The pipeline framing, core thesis, base-layer note, the three lenses, and the eight-standard summary |
| `references/engineering-principles.md` | The eight standards in full — each adapted for both authoring and review — plus diagnostic questions, preferred remedies/moves, and anti-patterns |
| `references/domain-standards.md` | Per-domain standards (backend, frontend, data, devops/infra, security, testing/QA) and the production-readiness baseline |
| `references/review-gate.md` | The Reviewer lens: output prioritization, presumptive-blocker approval bar, definition-of-done, production-readiness checklist, and first-person self-review prompts |

## Tips

- **It is a base layer — pair it with one stack skill.** Give a coding agent `software-engineer` plus the one library skill matching its work (`heroui`, `drizzle-orm`, `temporal`). The base layer governs engineering judgment; the stack skill supplies API specifics.
- **The point is authoring-time, not just review-time.** The biggest wins come from the Architect lens — designing complexity *out* before any code is written, not refactoring it away afterward.
- **Run the review gate on your own diff.** `references/review-gate.md` is a definition-of-done. "It works" is the floor; "it would survive review" is the bar.
- **Prefer fewer high-conviction findings.** When self-reviewing, surface the one structural problem, not a flood of nits.

## Related skills

- [`team-executor`](../team-executor/) — the domain-agnostic orchestrator that composes and sequences agent teams and assigns this skill to its coding and review agents.
- [`implement-issue`](../implement-issue/) — drives `team-executor` to deliver a GitHub issue end-to-end; its coding agents wear `software-engineer`.
