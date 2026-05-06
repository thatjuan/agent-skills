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
| [atlassian-cli](./atlassian-cli/) | `npx skills add thatjuan/agent-skills --skill atlassian-cli`<br><br>Atlassian CLI (acli) expertise for interacting with Jira Cloud and Atlassian organization admin from the terminal. Use when scripts invoke `acli`, user asks about Atlassian CLI, Jira CLI, JQL-driven automation, bulk Jira operations, or managing Jira work items, projects, boards, sprints, filters, fields, dashboards, Atlassian org admin users, or Rovo Dev authentication. |
| [cloudbeds-api](./cloudbeds-api/) | `npx skills add thatjuan/agent-skills --skill cloudbeds-api`<br><br>Cloudbeds hospitality API expertise for building property-management, booking, payments, accounting, and channel integrations. Use when code calls `api.cloudbeds.com`, `hotels.cloudbeds.com`, `api.payments.cloudbeds.com`, or imports a Cloudbeds SDK; when the user asks about Cloudbeds PMS, reservations, rate plans, webhooks, Pay-By-Link, Payments Vault, Accounting API, Data Insights, Fiscal Documents, or Group Profile APIs; when authenticating with `cbat_`-prefixed API keys or OAuth 2.0 against Cloudbeds; when subscribing to Cloudbeds webhooks or working with `postReservation`, `getAvailableRoomTypes`, `postCharge`, `patchRate`, or similar operations. |
| [camofox-browser](./camofox-browser/) | `npx skills add thatjuan/agent-skills --skill camofox-browser`<br><br>Deploy, configure, and use camofox-browser — the Camoufox-engine anti-detection browser server (REST API on port 9377) for AI agents. Use when code hits the `/tabs`, `/sessions/:userId/cookies`, or `/youtube/transcript` endpoints; when scripts install `@askjo/camofox-browser`, run `npm start` in the `camofox-browser` repo, or call `make up`/`make fetch`; when agents invoke OpenClaw `camofox_*` tools; when the user asks about Camoufox fingerprint spoofing, bypassing Cloudflare/Google bot detection, element refs (`e1`, `e2`), accessibility snapshots, search macros, Netscape cookie import, per-user session isolation, backconnect proxy rotation with GeoIP, VNC/noVNC login, writing plugins with `register(app, ctx)`, `CAMOFOX_*`/`PROXY_*` env vars, or deploying to Docker/Fly.io/Railway. |
| [browserbase-sdk](./browserbase-sdk/) | `npx skills add thatjuan/agent-skills --skill browserbase-sdk`<br><br>Browserbase cloud-headless-browser SDK expertise for TypeScript/Node. Use when code imports `@browserbasehq/sdk`, `@browserbasehq/stagehand`, `playwright-core`, or `puppeteer-core` and connects to Browserbase; when code POSTs to `api.browserbase.com/v1/sessions`, `/v1/contexts`, `/v1/extensions`, or `/v1/projects`; when sending the `x-bb-api-key` header or using `BROWSERBASE_API_KEY`/`BROWSERBASE_PROJECT_ID`; when the user asks about Browserbase sessions, contexts, proxies, downloads, uploads, recordings, live debugger URL, captcha solving, advanced stealth, verified browsers, fingerprinting, BYOS S3 storage, regions (`us-west-2`/`us-east-1`/`eu-central-1`/`ap-southeast-1`), keepAlive, the `connectUrl` CDP WebSocket, `chromium.connectOverCDP`, `puppeteer.connect({browserWSEndpoint})`, the `browser.contexts()[0]` default-context pattern, Stagehand `act`/`extract`/`observe`/`agent` primitives, the Model Gateway, or deploying serverless via Browserbase Functions. |
| [video-storyboard](./video-storyboard/) | `npx skills add thatjuan/agent-skills --skill video-storyboard`<br><br>World-class video storyboard writer for marketing, advertising, brand films, social spots, and product videos. Use when the user asks for a storyboard, video script, ad concept, commercial treatment, video pitch, or shot-by-shot breakdown for any film, ad, social video, explainer, or brand content. Produces an all-text markdown storyboard with richly described visuals (no images, no sketches) — every frame includes shot, action, on-screen text, voiceover, dialogue, sound, and timing. Grounded in the canonical literature on marketing storytelling and ad video production (Donald Miller's StoryBrand, Joseph Campbell / Christopher Vogler's Hero's Journey, Blake Snyder's Save the Cat, Pixar's 22 Rules of Storytelling, Chip & Dan Heath's Made to Stick, Luke Sullivan's Hey Whipple Squeeze This, David Ogilvy's Ogilvy on Advertising, Giuseppe Cristiano's The Storyboard Artist). |
| [openrouter-api](./openrouter-api/) | `npx skills add thatjuan/agent-skills --skill openrouter-api`<br><br>OpenRouter unified-LLM-API expertise. Use when code POSTs to `openrouter.ai/api/v1`, imports `@openrouter/sdk`, `openrouter` (Python), or `@openrouter/agent`; when the OpenAI SDK is pointed at `https://openrouter.ai/api/v1`; when the user asks about routing across hundreds of LLMs (OpenAI, Anthropic, Google, DeepSeek, Meta, xAI, Mistral, etc.) through one endpoint; when working with provider routing, model fallbacks (`models` array), the Auto Router (`openrouter/auto`), `:nitro`/`:floor`/`:online` model suffixes, presets (`@preset/...`), prompt caching with `cache_control`, structured outputs, tool calling, the `openrouter:web_search` server tool, reasoning tokens, multimodal (image/PDF/audio/video) inputs, BYOK provider keys, OAuth PKCE, the `openrouter:` plugins (`web`, `file-parser`, `response-healing`, `context-compression`), or generation/usage accounting via `/api/v1/generation` and `/api/v1/key`. |
| [grok-imagine-api](./grok-imagine-api/) | `npx skills add thatjuan/agent-skills --skill grok-imagine-api`<br><br>xAI Grok Imagine API expertise for generating, editing, and refining images through xAI REST, xai_sdk, OpenAI-compatible SDKs, and Vercel AI SDK. Use when code calls `api.x.ai/v1/images/generations` or `api.x.ai/v1/images/edits`, imports `xai_sdk` or `@ai-sdk/xai`, points an OpenAI SDK at `https://api.x.ai/v1`, or mentions Grok Imagine, `grok-imagine-image`, `grok-imagine-image-quality`, `aspect_ratio`, image editing, image variations, base64 image output, or `sample_batch()`. |

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
