# Agent Skills

A small, curated set of agent skills (slash commands and behaviors) for Claude Code and compatible coding agents. They fall into three buckets: **engineering** skills that capture work as GitHub issues, implement them, and commit the result; **integration** skills that carry deep API/tool expertise and trigger off your code; and **creative** skills that produce brand and design deliverables, up to generated assets and the sites built around them.

Every skill here is model-invoked — the agent can reach for one automatically when the task fits, and you can invoke any of them by name.

## Quickstart

Install a single skill:

```bash
npx skills add thatjuan/agent-skills --skill capture-issues
```

Install everything:

```bash
npx skills add thatjuan/agent-skills --all
```

Maintaining a clone? `scripts/link-skills.sh` symlinks every promoted skill into `~/.claude/skills` and `~/.agents/skills` (a `git pull` then keeps them current), and `scripts/list-skills.sh` lists what is installed.

## Reference

### Engineering

The issue-driven delivery loop: [capture-issues](./skills/engineering/capture-issues/SKILL.md) turns a braindump into detailed GitHub issues, [batch-implement](./skills/engineering/batch-implement/SKILL.md) works through them one subagent at a time (or [orca-implement](./skills/engineering/orca-implement/SKILL.md) through Orca workers and worktrees), and [commitpush](./skills/engineering/commitpush/SKILL.md) lands each change safely.

- **[capture-issues](./skills/engineering/capture-issues/SKILL.md)** — Turn a braindump, doc, or conversation into a small set of highly detailed GitHub issues, grouped under milestones where appropriate.
- **[batch-implement](./skills/engineering/batch-implement/SKILL.md)** — Implement a batch or milestone sequentially with a fresh subagent per issue and configurable branch and pull request delivery.
- **[orca-implement](./skills/engineering/orca-implement/SKILL.md)** — Implement a batch or milestone through supervised Orca workers, one Orca worktree per issue, in parallel waves where dependencies allow, with one combined pull request or one per issue.
- **[commitpush](./skills/engineering/commitpush/SKILL.md)** — Safe commit-and-push workflow with secrets detection, sensitive-file screening, and submodule-aware prompting.
- **[list-issues](./skills/engineering/list-issues/SKILL.md)**: List every open GitHub issue in the current repo, grouped by category, newest number first, with the date opened and a one-line description.

### Integrations

API, SDK, and tool domain expertise that fires off your code context — an import, an endpoint, an auth header, or a direct question about the service. Each one packs the surface, idioms, and gotchas of a specific platform so the agent works it correctly without guessing.

- **[cloudbeds-api](./skills/integrations/cloudbeds-api/SKILL.md)** — Cloudbeds hospitality API for property-management, booking, payments, accounting, and channel integrations.
- **[forge-suite](./skills/integrations/forge-suite/SKILL.md)**: Operate Salesforge, Warmforge, and Mailforge through their REST APIs. Domains and mailboxes, warmup and placement, email + LinkedIn sequences, replies, and webhooks.
- **[typesafe-ai](./skills/integrations/typesafe-ai/SKILL.md)** — Build application logic on TypeSafe AI's Jev decision model: typed Choice, Score, and Noul questions over a state, calibrated answers, control flow in code.
- **[unifi-operator](./skills/integrations/unifi-operator/SKILL.md)** — Operate UniFi Network and Protect through their local APIs on a UDM/Cloud Key/self-hosted console — gateways, switches, APs, firewall, cameras, and events.

### Creative

Brand, design, and storytelling skills that produce creative deliverables — concepts, identities, and the generated assets and sites built around them.

- **[clean-writing](./skills/creative/clean-writing/SKILL.md)**: Clear, economical prose: Strunk and White's composition principles plus a revision pass against ten AI-writing reflexes, from template structure and corrective framing to phantom authority, each with a target and a before/after example.
- **[creative-director](./skills/creative/creative-director/SKILL.md)** — World-class creative direction for branding, web design, and UI concepts — detailed creative concepts and visual strategy, not implementations.
- **[fal-studio](./skills/creative/fal-studio/SKILL.md)** — Build a site or a generative app on fal.ai — build-time art direction, generated still kits and scroll-scrub film, or a runtime generation app behind a server-proxied queue.
- **[logo-studio](./skills/creative/logo-studio/SKILL.md)** — Designs an iconic logo with full creative freedom, then a full app-asset package and an optional brand-guidelines document.
- **[video-script](./skills/creative/video-script/SKILL.md)**: Production-ready video scripts for ads, brand films, and creator videos, built on a five-line story spine (situation, desire, conflict, change, result) and written out as shot-by-shot frames a crew can shoot from.
- **[video-production](./skills/creative/video-production/SKILL.md)**: Turn a script into a finished video: a look bible of characters and locations, keyframes from image models, shots animated on Runway, voice, effects, and music from ElevenLabs, cut and mixed with ffmpeg.

## Deprecated skills

Skills that are no longer maintained live in [`skills/deprecated/`](./skills/deprecated/README.md). They are kept for reference, are not part of the plugin, and are not linked by `scripts/link-skills.sh`.

## Creating skills

See [CLAUDE.md](./CLAUDE.md) for the repo conventions: which bucket a skill belongs in, the invariant that every promoted skill appears in this README, its bucket README, and `.claude-plugin/plugin.json`, the per-skill `README.md` each folder ships, and the frontmatter validation step required before every commit. [CONTEXT.md](./CONTEXT.md) defines the shared vocabulary (skill, bucket, promoted, deprecated).
