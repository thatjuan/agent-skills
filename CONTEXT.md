# Agent Skills

A collection of agent skills (slash commands and behaviors) loaded by Claude Code and compatible agents, organized into buckets and installed per-repo or symlinked into the local harness skill directories.

## Language

**Skill**:
A single unit of agent capability — a folder under a bucket containing a `SKILL.md` and a `README.md`. The `SKILL.md` holds the machine-facing definition (YAML frontmatter with `name` and `description`, then the instructions the agent follows); the `README.md` holds the human-facing documentation for that same skill. Every skill here is model-invoked.
_Avoid_: command, plugin (a plugin is the packaged set of all skills, not one skill)

**Bucket**:
A top-level grouping folder under `skills/` — `engineering/`, `integrations/`, or `creative/`. A skill lives in exactly one bucket, chosen by what it does: engineering = delivery-workflow orchestration, integrations = API/SDK/tool expertise, creative = brand and storytelling deliverables.
_Avoid_: category, group, folder

**Promoted**:
A property of a **Bucket**. A promoted bucket's skills are surfaced everywhere — the top-level `README.md`, the bucket `README.md`, and `.claude-plugin/plugin.json`. All three current buckets are promoted. A non-promoted bucket (none exist today; `in-progress/` or `deprecated/` may be added later) keeps its skills out of the top-level README and plugin manifest.

**SKILL.md vs README.md**:
Within a skill folder, `SKILL.md` is what the agent reads to perform the skill; `README.md` is what a person reads to understand it. They are distinct roles, both required — the README is not generated from the SKILL.

**Delivery pipeline**:
The composed flow of the `engineering/` skills: `ship` → `design-doc` → `implement-issue` → `team-executor` → `software-engineer`, with the `codex-*` skills as delegation lanes and `commitpush` closing out the change. `ship` is the entrypoint and coordinator; the rest are the stages it dispatches to.

## Relationships

- A **Bucket** holds many **Skills**
- A **Skill** belongs to exactly one **Bucket**
- A **Bucket** is either **Promoted** or not; promotion decides whether its **Skills** appear in the top-level README and `.claude-plugin/plugin.json`
- The **Delivery pipeline** is an ordering over the **Skills** in the `engineering/` bucket, not a bucket of its own
