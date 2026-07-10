# Agent Skills

A collection of agent skills (slash commands and behaviors) for Claude Code and compatible coding agents. They fall into three buckets: an **engineering** delivery pipeline that plans, delegates, implements, reviews, and commits work; **integration** skills that carry deep API/SDK/tool expertise and trigger off your code; and **creative** skills that produce brand, design, and storytelling deliverables.

Every skill here is model-invoked — the agent can reach for one automatically when the task fits, and you can invoke any of them by name.

## Quickstart

Install a single skill:

```bash
npx skills add thatjuan/agent-skills --skill ship
```

Install everything:

```bash
npx skills add thatjuan/agent-skills --all
```

Maintaining a clone? `scripts/link-skills.sh` symlinks every skill into `~/.claude/skills` and `~/.agents/skills` (a `git pull` then keeps them current), and `scripts/list-skills.sh` lists what is installed.

## Reference

### Engineering

Orchestration and delivery-workflow skills — how work gets planned, delegated, implemented, reviewed, and committed. They compose into a pipeline: [ship](./skills/engineering/ship/SKILL.md) is the entrypoint and coordinator; it opens a [design-doc](./skills/engineering/design-doc/SKILL.md) when the design gate fires, cuts GitHub issues, then routes each issue through [implement-issue](./skills/engineering/implement-issue/SKILL.md) → [team-executor](./skills/engineering/team-executor/SKILL.md) → [software-engineer](./skills/engineering/software-engineer/SKILL.md), with the `codex-*` skills as the lanes for delegating work to the OpenAI Codex CLI (gpt-5.6), and [commitpush](./skills/engineering/commitpush/SKILL.md) closing out the change.

- **[ship](./skills/engineering/ship/SKILL.md)** — Task entrypoint and delivery orchestrator: triage a raw task, decide whether it needs a design doc and GitHub issues, then assemble agent teams that route each job to the right model.
- **[design-doc](./skills/engineering/design-doc/SKILL.md)** — Author or review a right-sized software design doc (tech spec, RFC, architecture proposal), grounded in the "Write an Effective Design Doc" practices from Refactoring English.
- **[implement-issue](./skills/engineering/implement-issue/SKILL.md)** — Take a GitHub issue from number to pull request: branch, plan with a stack-specialized team, confirm the approach, build via team-executor, and open the PR.
- **[team-executor](./skills/engineering/team-executor/SKILL.md)** — Turn a braindump into executed results: assemble an expert planning team, produce an execution plan, then deploy a fresh execution team for autonomous delivery.
- **[software-engineer](./skills/engineering/software-engineer/SKILL.md)** — The architect/developer/reviewer engineering SME and base layer for any agent that writes or reviews code, holding the work to the Three Lenses and Eight Standards.
- **[codex-implementation](./skills/engineering/codex-implementation/SKILL.md)** — Delegate bulk, mechanical, or clear-spec implementation to the OpenAI Codex CLI (gpt-5.6) via non-interactive `codex exec`.
- **[codex-review](./skills/engineering/codex-review/SKILL.md)** — Run an independent code review through the Codex CLI over uncommitted changes, a branch diff, a commit range, or a GitHub PR.
- **[codex-computer-use](./skills/engineering/codex-computer-use/SKILL.md)** — Drive browser, GUI, and visual-verification work through Codex — a Playwright MCP browser and screenshot analysis.
- **[commitpush](./skills/engineering/commitpush/SKILL.md)** — Safe commit-and-push workflow with secrets detection, sensitive-file screening, and submodule-aware prompting.

### Integrations

API, SDK, and tool domain expertise that fires off your code context — an import, an endpoint, an auth header, or a direct question about the service. Each one packs the surface, idioms, and gotchas of a specific platform so the agent works it correctly without guessing.

- **[atlassian-cli](./skills/integrations/atlassian-cli/SKILL.md)** — Atlassian CLI (`acli`) for Jira Cloud and org admin from the terminal — JQL automation, bulk operations, work items, boards, sprints, and filters.
- **[browserbase-sdk](./skills/integrations/browserbase-sdk/SKILL.md)** — Browserbase cloud-headless-browser SDK for TypeScript/Node — sessions, contexts, proxies, stealth, and Stagehand act/extract/observe primitives over CDP.
- **[camofox-browser](./skills/integrations/camofox-browser/SKILL.md)** — Deploy and drive camofox-browser, the Camoufox-engine anti-detection browser server (REST API on port 9377) for AI agents.
- **[cloudbeds-api](./skills/integrations/cloudbeds-api/SKILL.md)** — Cloudbeds hospitality API for property-management, booking, payments, accounting, and channel integrations.
- **[drizzle-orm](./skills/integrations/drizzle-orm/SKILL.md)** — Type-safe SQL ORM for TypeScript with zero runtime overhead — schema design, queries, relations, and migrations, PostgreSQL-focused.
- **[grok-imagine-api](./skills/integrations/grok-imagine-api/SKILL.md)** — xAI Grok Imagine API for generating, editing, and refining images through REST, `xai_sdk`, OpenAI-compatible SDKs, and the Vercel AI SDK.
- **[heroui](./skills/integrations/heroui/SKILL.md)** — HeroUI v3 component library for React (web) and React Native (mobile) — components, theming, and migration from NextUI/HeroUI v2.
- **[openrouter-api](./skills/integrations/openrouter-api/SKILL.md)** — OpenRouter unified LLM API — one endpoint across hundreds of models with provider routing, fallbacks, caching, tool calling, and multimodal inputs.
- **[openwa](./skills/integrations/openwa/SKILL.md)** — OpenWA self-hosted WhatsApp API gateway — deployment, sessions, REST API, webhooks, real-time events, SDKs, and plugins.
- **[temporal](./skills/integrations/temporal/SKILL.md)** — Temporal.io durable-execution and workflow orchestration for Python and TypeScript — activities, workers, signals, queries, and reliable distributed systems.
- **[unifi-operator](./skills/integrations/unifi-operator/SKILL.md)** — Operate UniFi Network and Protect through their local APIs on a UDM/Cloud Key/self-hosted console — gateways, switches, APs, firewall, cameras, and events.

### Creative

Brand, design, and storytelling skills that produce richly described creative deliverables — concepts, identities, and scripts — rather than code.

- **[creative-director](./skills/creative/creative-director/SKILL.md)** — World-class creative direction for branding, web design, and UI concepts — detailed creative concepts and visual strategy, not implementations.
- **[logo-studio](./skills/creative/logo-studio/SKILL.md)** — Logo design studio producing 9+ SVG concepts through brand discovery, then a full app-asset package and an optional brand-guidelines document.
- **[video-storyboard](./skills/creative/video-storyboard/SKILL.md)** — World-class all-text video storyboards for ads, brand films, and social spots — shot-by-shot with action, on-screen text, voiceover, sound, and timing.

## Creating skills

See [CLAUDE.md](./CLAUDE.md) for the repo conventions: which bucket a skill belongs in, the invariant that every skill appears in this README, its bucket README, and `.claude-plugin/plugin.json`, the per-skill `README.md` each folder ships, and the frontmatter validation step required before every commit. [CONTEXT.md](./CONTEXT.md) defines the shared vocabulary (skill, bucket, promoted, the delivery pipeline).
