# Agent Skills

A collection of agent skills (slash commands and behaviors) loaded by Claude Code and compatible agents, organized into buckets and installed per-repo or symlinked into the local harness skill directories.

## Language

**Skill**:
A single unit of agent capability — a folder under a bucket containing a `SKILL.md` and a `README.md`. The `SKILL.md` holds the machine-facing definition (YAML frontmatter with `name` and `description`, then the instructions the agent follows); the `README.md` holds the human-facing documentation for that same skill. Every promoted skill is model-invoked.
_Avoid_: command, plugin (a plugin is the packaged set of all promoted skills, not one skill)

**Bucket**:
A top-level grouping folder under `skills/` — `engineering/`, `integrations/`, `creative/`, or `deprecated/`. A skill lives in exactly one bucket, chosen by what it does: engineering = the issue-driven delivery loop, integrations = API/SDK/tool expertise, creative = brand and design deliverables, deprecated = retired.
_Avoid_: category, group, folder

**Promoted**:
A property of a **Bucket**. A promoted bucket's skills are surfaced everywhere — the top-level `README.md`, the bucket `README.md`, and `.claude-plugin/plugin.json` — and are linked by `scripts/link-skills.sh`. `engineering/`, `integrations/`, and `creative/` are promoted; `deprecated/` is not.

**Deprecated**:
A skill that has been retired but kept in the repo for reference, living in the non-promoted `deprecated/` bucket. It is not part of the plugin and is not linked locally. Git history holds its prior location.
_Avoid_: archived (same thing, but use one word), removed (it is still in the tree)

**SKILL.md vs README.md**:
Within a skill folder, `SKILL.md` is what the agent reads to perform the skill; `README.md` is what a person reads to understand it. They are distinct roles, both required — the README is not generated from the SKILL.

**Delivery loop**:
The composed flow of the `engineering/` skills: `capture-issues` → `batch-implement` → `commitpush`. Issues are the handoff between capture and implementation; each implemented issue is committed with `commitpush`.

## Relationships

- A **Bucket** holds many **Skills**
- A **Skill** belongs to exactly one **Bucket**
- A **Bucket** is either **Promoted** or not; promotion decides whether its **Skills** appear in the top-level README and `.claude-plugin/plugin.json` and get linked locally
- A **Deprecated** skill is any **Skill** in the `deprecated/` bucket
- The **Delivery loop** is an ordering over the **Skills** in the `engineering/` bucket, not a bucket of its own
