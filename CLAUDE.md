Skills are organized into bucket folders under `skills/`:

- `engineering/` — the issue-driven delivery loop: capture work as GitHub issues, implement them, commit the result.
- `integrations/` — API, SDK, and tool domain expertise that triggers off code context (an import, an endpoint, an auth header).
- `creative/` — brand, design, and storytelling skills that produce creative deliverables.
- `deprecated/` — retired skills kept for reference. **Not promoted.**

`engineering/`, `integrations/`, and `creative/` are **promoted**. Every skill in a promoted bucket must have a reference in the top-level `README.md`, an entry in its bucket `README.md`, and an entry in `.claude-plugin/plugin.json`. Skills in `deprecated/` must not appear in any of those three, and `scripts/link-skills.sh` skips them. To deprecate a skill, `git mv` its folder into `skills/deprecated/`, remove it from the three promoted lists, and add a line to `skills/deprecated/README.md`.

Every promoted skill is model-invoked — none sets `disable-model-invocation` to remove itself from automatic invocation — so the READMEs use flat lists, not a user-invoked / model-invoked split.

Each skill entry in the top-level `README.md` and in a bucket `README.md` must link the skill name to its `SKILL.md`.

Per-skill human docs live in each skill folder's own `README.md` — every skill folder ships one. There is no separate `docs/` pages tree; the skill folder's `README.md` is the human-facing documentation for that skill.

The `engineering/` skills compose as a loop: `capture-issues` writes the issues, `batch-implement` works through a batch or milestone with a fresh subagent per issue, and `commitpush` lands each change. Read `batch-implement/SKILL.md` for the authoritative shape before changing how these compose.

Before every commit, validate the YAML frontmatter of any `SKILL.md` you touched: the skills CLI silently drops a skill whose frontmatter is malformed (for example, an unquoted `description` containing a colon-space, `: `, which YAML parses as a mapping). Quote any description that contains `: `, or the skill disappears without an error.

To (re)link every promoted skill into the local harness skill directories (`~/.claude/skills`, `~/.agents/skills`), run `scripts/link-skills.sh`; `scripts/list-skills.sh` lists what is installed. Each entry is a symlink into this repo, so a `git pull` keeps installed skills current — re-run the script after adding, removing, or renaming a skill.
