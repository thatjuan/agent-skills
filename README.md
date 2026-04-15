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
| [commitpush](./commitpush/) | `npx skills add thatjuan/agent-skills --skill commitpush`<br><br>Safe commit-and-push workflow with secrets detection, sensitive file screening, and submodule-aware prompting. Use when committing and pushing changes to git, especially in repos with submodules or when security-conscious commits are needed. |
| [creative-director](./creative-director/) | `npx skills add thatjuan/agent-skills --skill creative-director`<br><br>World-class creative director for branding, web design, and UI concepts. Use when the user asks for a new design concept, brand identity, website creative direction, UI experience concept, visual identity, or creative strategy for a business, product, or project. Produces detailed, richly described creative concepts — not code or implementations. |
| [team-executor](./team-executor/) | `npx skills add thatjuan/agent-skills --skill team-executor`<br><br>Multi-agent orchestration that transforms braindumps into executed results. Assembles expert planning teams (3-7 agents), produces comprehensive execution plans, then deploys fresh execution teams for autonomous delivery |
| [temporal](./temporal/) | `npx skills add thatjuan/agent-skills --skill temporal`<br><br>Expert Temporal.io workflow orchestration for Python and TypeScript. Use when code imports temporalio/sdk-python or @temporalio/* packages, user asks about durable execution, workflow orchestration, AI agent orchestration with Temporal, or building reliable distributed systems with Temporal |
| [heroui](./heroui/) | `npx skills add thatjuan/agent-skills --skill heroui`<br><br>HeroUI v3 component library expertise for React (web) and React Native (mobile). Use when code imports @heroui/react, @heroui/styles, or heroui-native, user asks to build UI with HeroUI, or references HeroUI components, theming, or migration from NextUI/HeroUI v2 |
| [drizzle-orm](./drizzle-orm/) | `npx skills add thatjuan/agent-skills --skill drizzle-orm`<br><br>Type-safe SQL ORM for TypeScript with zero runtime overhead. Use when code imports drizzle-orm, drizzle-kit, or drizzle-orm/pg-core, user asks about Drizzle schema design, queries, relations, migrations, or database management with Drizzle ORM |
| [logo-studio](./logo-studio/) | `npx skills add thatjuan/agent-skills --skill logo-studio`<br><br>Professional logo design studio that produces 9+ SVG logo concepts through brand discovery, archetype mapping, and iterative refinement, then generates a complete app asset package (iOS, Android, macOS, Windows, favicons, PWA, social) from the final selection and optionally produces a multi-page brand guidelines document (logo, color, typography, layout, UI components, motion, voice, asset management). Use when the user asks for a logo, brand mark, icon, wordmark, app icon, visual identity, or brand guidelines for a business, product, or project. |

Click a skill above for full details, example prompts, and bundled resources.

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
