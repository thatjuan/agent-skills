# Deprecated

Skills that are no longer maintained. They stay here for reference and can be installed by path if you still want one, but they are not promoted: they do not appear in the top-level `README.md` or `.claude-plugin/plugin.json`, and `scripts/link-skills.sh` skips them.

Archived on 2026-09-09 when the repo was narrowed to the issue-driven delivery loop (`capture-issues` → `batch-implement` → `commitpush`) plus a handful of integration and creative skills.

- `ship`, `design-doc`, `implement-issue`, `team-executor`, `software-engineer` — the old multi-stage delivery pipeline, superseded by `capture-issues` + `batch-implement`.
- `codex-implementation`, `codex-review`, `codex-computer-use` — delegation lanes to the OpenAI Codex CLI.
- `agentmail`, `atlassian-cli`, `browserbase-sdk`, `camofox-browser`, `drizzle-orm`, `grok-imagine-api`, `heroui`, `openrouter-api`, `openwa`, `temporal` — integration skills.
- `video-storyboard` — creative skill.

To revive one, move its folder back into the right bucket and add it to the top-level `README.md`, the bucket `README.md`, and `.claude-plugin/plugin.json`.
