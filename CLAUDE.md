Skills are organized into bucket folders under `skills/`:

- `engineering/` — orchestration and delivery-workflow skills: how work gets planned, delegated, implemented, reviewed, and committed.
- `integrations/` — API, SDK, and tool domain expertise that triggers off code context (an import, an endpoint, an auth header).
- `creative/` — brand, design, and storytelling skills that produce creative deliverables.

All three buckets are **promoted** today. Every skill in a promoted bucket must have a reference in the top-level `README.md`, an entry in its bucket `README.md`, and an entry in `.claude-plugin/plugin.json`. If a non-promoted bucket is added later (e.g. `in-progress/` or `deprecated/`), skills in it must not appear in any of those three.

Every skill is model-invoked — none sets `disable-model-invocation` to remove itself from automatic invocation — so the READMEs use flat lists, not a user-invoked / model-invoked split.

Each skill entry in the top-level `README.md` and in a bucket `README.md` must link the skill name to its `SKILL.md`.

Per-skill human docs live in each skill folder's own `README.md` — every skill folder ships one. There is no separate `docs/` pages tree; the skill folder's `README.md` is the human-facing documentation for that skill.

The `engineering/` skills form a delivery pipeline: `ship` (entrypoint and coordinator) → `design-doc` (design gate) → `implement-issue` → `team-executor` → `software-engineer`, with the `codex-*` skills as the delegation lanes to the OpenAI Codex CLI (gpt-5.5) and `commitpush` closing out the change. Read `ship/SKILL.md` for the authoritative shape before changing how these compose. `ship` defers model routing to the user's global `~/.claude/CLAUDE.md` table when present.

Before every commit, validate the YAML frontmatter of any `SKILL.md` you touched: the skills CLI silently drops a skill whose frontmatter is malformed (for example, an unquoted `description` containing a colon-space, `: `, which YAML parses as a mapping). Quote any description that contains `: `, or the skill disappears without an error.

To (re)link every skill into the local harness skill directories (`~/.claude/skills`, `~/.agents/skills`), run `scripts/link-skills.sh`; `scripts/list-skills.sh` lists what is installed. Each entry is a symlink into this repo, so a `git pull` keeps installed skills current — re-run the script after adding, removing, or renaming a skill.
