<div align="center">

# Agent Skills

**A curated collection of AI agent skills for Claude Code and compatible agents.**

[![Skills CLI](https://img.shields.io/badge/npx-skills-blue?style=flat-square)](https://www.npmjs.com/package/skills)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

[Overview](#overview) • [Skills Catalog](#skills-catalog) • [Getting Started](#getting-started) • [Skill Anatomy](#skill-anatomy) • [Creating Skills](#creating-skills)

</div>

## Overview

Agent Skills are self-contained instruction sets that give AI coding agents specialized capabilities. Each skill defines a complete workflow — from persona construction to execution strategy — that an agent can follow to accomplish complex, multi-step tasks autonomously.

This repository is designed for use with the [`skills` CLI](https://www.npmjs.com/package/skills). Install individual skills or the entire collection into your project, and your AI agent gains new abilities instantly.

## Skills Catalog

| Skill | Description |
|-------|-------------|
| [team-executor](./team-executor/) | Multi-agent orchestration that transforms braindumps into executed results. Assembles expert planning teams (3-7 agents), produces comprehensive execution plans, then deploys fresh execution teams for autonomous delivery |

### team-executor

Multi-agent orchestration that transforms braindumps into executed results through expert planning and autonomous execution. Works across Claude Code, Codex, and any platform supporting agent spawning.

**Phase 1 — Planning**: Organizes raw input, assembles a team of 3-7 expert agents (architect, backend engineer, security engineer, etc.), has each analyze the goal from their domain expertise, and produces a comprehensive execution plan.

**Phase 2 — Execution**: A fresh team of agents autonomously executes the plan to completion with no human intervention required.

Included resources:

| File | Purpose |
|------|---------|
| `SKILL.md` | Core skill definition with the full 12-step workflow |
| `agent-templates.md` | Persona construction framework and ready-to-use templates for R&D, architect, frontend, backend, DevOps, QA, security, data, and project lead agents |
| `orchestration-workflow.md` | Agent spawning (Claude Code Agent tool, Codex subagents, sequential fallback), output collection, conflict resolution, and phase transitions |
| `scan-project.sh` | Gathers project context (directory structure, config files, technologies, available skills) for agent prompts |
| `init-plan-dirs.sh` | Initializes the `docs/plans/` directory structure for agent outputs |

> [!TIP]
> The team-executor skill works best when your project has existing code and documentation — the agents use that context to make informed, convention-consistent decisions.

## Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) >= 18
- An AI agent that supports skills (e.g., [Claude Code](https://docs.anthropic.com/en/docs/claude-code))

### Install a specific skill

```bash
npx skills add thatjuan/agent-skills --skill team-executor
```

### Install all skills

```bash
npx skills add thatjuan/agent-skills --all
```

Once installed, skills are available to your AI agent automatically. Invoke them by describing a task that matches the skill's trigger — for example, pasting a braindump of project ideas will activate the `team-executor` skill.

### Verify installation

After installation, you should see the skill files in your project's skills directory and a `skills-lock.json` tracking installed skills:

```json
{
  "version": 1,
  "skills": {
    "team-executor": {
      "source": "github/thatjuan/agent-skills",
      "sourceType": "github"
    }
  }
}
```

## Skill Anatomy

Each skill follows a consistent structure:

```
skill-name/
  SKILL.md          # Skill definition (required) — YAML frontmatter + instructions
  *.md              # Bundled reference docs (optional)
  *.sh              # Helper scripts (optional)
```

The `SKILL.md` file is the entry point. Its YAML frontmatter defines the skill's `name` and `description` (used for trigger matching), followed by the full instructions the agent will follow.

> [!NOTE]
> Reference files like `agent-templates.md` and `orchestration-workflow.md` are loaded by the agent at runtime — they keep the main `SKILL.md` focused while providing depth on demand.

## Creating Skills

Want to add a new skill to this collection? Each skill should:

1. **Solve a specific, repeatable problem** — skills work best when they encode a well-defined workflow
2. **Be self-contained** — include all instructions, templates, and scripts the agent needs
3. **Use rich frontmatter** — write a descriptive `description` field with trigger phrases so agents know when to activate the skill
4. **Include bundled resources** — break complex workflows into reference docs rather than stuffing everything into `SKILL.md`
5. **Be production-oriented** — skills should produce real, working output — not drafts or placeholders

```yaml
---
name: my-skill
description: Short description of what this skill does and when to use it.
---

# My Skill

Instructions the agent follows...
```
