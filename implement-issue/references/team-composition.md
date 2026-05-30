# Team Composition

How to pick planning + execution agents and assign skills for the `implement-issue` workflow.

## Table of Contents

1. [Stack detection](#stack-detection)
2. [Skill inventory scan](#skill-inventory-scan)
3. [Agent picks by stack](#agent-picks-by-stack)
4. [Skill-to-agent mapping](#skill-to-agent-mapping)
5. [Issue-type adjustments](#issue-type-adjustments)
6. [The software-engineer Reviewer-Lens review gate](#the-software-engineer-reviewer-lens-review-gate)

## Stack detection

Run before assembling any team:

| Signal | Stack inference |
|--------|-----------------|
| `package.json` with `react`, `next`, `vite` | Frontend (React) |
| `package.json` with `@heroui/*` | HeroUI in use → assign `heroui` skill |
| `package.json` with `drizzle-orm` | Drizzle in use → assign `drizzle-orm` skill |
| `package.json` with `temporalio` or `@temporalio/*` | Temporal in use → assign `temporal` skill |
| `package.json` with `@browserbasehq/sdk` | Browserbase → assign `browserbase-sdk` skill |
| `pyproject.toml` / `requirements.txt` / `*.py` | Python |
| `Cargo.toml` | Rust |
| `go.mod` | Go |
| `*.sol` / `hardhat.config.*` / `foundry.toml` | Solidity |
| `Dockerfile` / `docker-compose.yml` / `.github/workflows/*.yml` | DevOps surface present |
| `migrations/` / `prisma/` / `schema.sql` | Database changes likely needed |
| `src/components/` + design system files (`.stitch/`, `tokens.*`) | Design-system project → consider `stitch-design` |
| `tests/`, `__tests__/`, `*.test.*`, `*.spec.*` | Test infra exists; QA agent needed |

Capture this inference into `docs/plans/issue-<N>/stack.md` and pass it into every agent prompt.

## Skill inventory scan

Per `team-executor` Step 2, scan:

- `~/.claude/skills/`
- `.claude/skills/` (project root)
- `/mnt/skills/`
- `skills-lock.json` (project root)

Read each `SKILL.md` frontmatter. Build a name → description map. The `description` field's trigger phrases are what to match against the issue's needs.

## Agent picks by stack

The team-executor "sweet spot" is 3–5 planning agents. Always include a Project Lead. Pull from these by relevance to the issue:

| Stack / surface | Agents to consider |
|-----------------|--------------------|
| Frontend feature | Frontend architect, UI/component engineer, accessibility specialist, design-system steward |
| Backend feature | API/service architect, backend engineer, data modeler, security engineer |
| Full-stack feature | Architect (cross-cutting), backend engineer, frontend engineer, QA/testing strategist |
| Bug fix | Root-cause investigator (R&D), domain owner of the affected area, QA/regression-test author |
| Refactor / migration | Architect, migration-safety specialist (data integrity, rollback), test-coverage analyst |
| Infrastructure / CI | DevOps engineer, security engineer (secrets, perms), platform reliability engineer |
| Database / schema | Data modeler, migration-safety specialist, performance analyst |
| Performance | Profiler/observability specialist, domain owner, infrastructure engineer |
| Security-flagged issue | Security engineer (lead), backend engineer, threat modeler |
| Library / SDK / API integration | Integration engineer (with the matching SDK skill), error-handling specialist |
| Documentation | Technical writer, domain expert, DX reviewer |

Prefer **opinionated personas** over job titles. "Distributed-systems engineer who insists on idempotent operations and circuit breakers" beats "backend engineer."

## Skill-to-agent mapping

Skills available in this repo (`agent-skills/`) and when to attach them:

| Skill | Attach to | When |
|-------|-----------|------|
| `software-engineer` | Every architect, coding, and review agent | Always, for any agent that writes/updates/reviews code — it is the base engineering layer. Stack/SDK skills below overlay on top of it. |
| `team-executor` | Orchestrator (this skill drives it) | Always — this skill *is* the consumer |
| `heroui` | Frontend agents | Repo uses `@heroui/*` |
| `drizzle-orm` | Backend / data agents | Repo uses `drizzle-orm` |
| `temporal` | Backend / workflow agents | Repo uses `temporalio` / `@temporalio/*` |
| `browserbase-sdk` | Automation / scraping agents | Repo uses `@browserbasehq/sdk` |
| `camofox-browser` | Same as browserbase | Anti-detection browsing needed |
| `openrouter-api` | LLM-integration agents | Code targets `openrouter.ai` |
| `grok-imagine-api` | Image-gen agents | Code targets `api.x.ai` images |
| `stitch-design` | Design-system agents | `.stitch/` present or design-system work |
| `creative-director` | Creative concept agents | Pre-implementation brand/UI thinking needed |
| `logo-studio` | Brand asset agents | Logo / app icon work |
| `video-storyboard` | Video content agents | Video storyboard work |
| `cloudbeds-api` | Backend integration agents | Code targets Cloudbeds APIs |
| `atlassian-cli` | Ops / integration agents | Jira / Atlassian work |
| `commitpush` | Execution agents at commit time | Repo benefits from secrets-aware commits (default: yes) |
| `web-typography` | Frontend / design agents | Typography decisions in scope |
| `react-components` | Frontend agents | Stitch → React conversion in scope |
| `claude-api` / `claude-code-guide` | LLM-integration agents | Code uses the Anthropic SDK |
| `docling` | Document-processing agents | PDF / DOCX / OCR / RAG ingestion |

Only attach a skill when it genuinely matches the agent's mandate. Over-assigning skills bloats agent context and dilutes focus.

**Skill stacking.** A coding agent carries `software-engineer` (the base) *plus* optionally **one** stack/SDK skill from the rows above (`heroui`, `drizzle-orm`, `temporal`, etc.). This is the one sanctioned exception to one-skill-per-agent: `software-engineer` defines *how* to engineer (the Three Lenses, the Eight Standards); the stack skill supplies the specific library/API. Never stack two stack/SDK skills on the same agent.

## Issue-type adjustments

Tune the team by issue type:

**Bug**
- Add an R&D agent first: reproduce, identify root cause, document in `research/root-cause.md`.
- Planning team gets the root-cause analysis as input.
- Always include a regression-test author.

**Feature**
- Standard team-executor composition.
- Include an integration agent if the feature touches >1 module.

**Refactor / migration**
- Add a migration-safety specialist (rollback plan, data-integrity checks, feature-flag plan).
- Include a test-coverage analyst to flag thin spots before the refactor lands.

**Security**
- Security engineer leads.
- Add a threat-modeler.
- The `software-engineer` Reviewer-Lens gate explicitly checks for OWASP-class issues.

**Performance**
- R&D agent first to profile and quantify.
- Avoid speculative optimizations — every change must be backed by a measurement.

**Documentation-only**
- Smaller team: technical writer + domain expert + DX reviewer.
- Skip the `software-engineer` Reviewer-Lens gate (or make it a docs-quality gate instead).

## The software-engineer Reviewer-Lens review gate

Per `team-executor` Step 7, run a review gate on the draft plan before finalizing. That gate is performed by an agent assigned the [`software-engineer`](../../software-engineer/) skill, applying its Reviewer Lens via [`../../software-engineer/references/review-gate.md`](../../software-engineer/references/review-gate.md). For this skill's purposes, that reviewer's mandate emphasizes the following — all of which align with, and are covered by, `software-engineer`'s review gate:

- **Convention consistency** — does this plan match existing patterns in the repo, or does it introduce a parallel pattern?
- **Existing-tooling reuse** — does the plan reach for an installed library/component when one fits, instead of inventing or pulling a new dep?
- **Failure surface** — what happens at every boundary if the input is malformed, the network fails, the upstream service is down?
- **Test coverage** — does the plan specify *which* tests to add (unit, integration, e2e), not just "add tests"?
- **Reversibility** — is the change behind a flag if it's risky? Is there a rollback path?
- **Blast radius** — is the change scoped to what the issue actually asks, or has it grown into a "while we're here" refactor?

Feed the reviewer's findings back into the plan before posting the issue comment.
