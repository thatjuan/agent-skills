---
name: capture-issues
description: Turn a braindump, doc, spec, or conversation into a small set of highly detailed GitHub issues, grouped under milestones where appropriate. Use when the user asks to capture, file, cut, or write up issues.
---

# Capture issues

Turn whatever the user handed you into GitHub issues in the current repo (`gh repo view`). Ask only if the target repo or project is ambiguous.

## Rules

- **Fewer issues, not more.** One issue per coherent unit of work. Never split what a single implementer would finish in one pass. When the input spans several themes, group the issues under milestones.
- **Write for a weaker agent.** Issues are implemented by coding agents less capable than you, with no access to this conversation. An issue is finished when one of them can implement it without guessing: intended architecture, files and modules to touch, data shapes and signatures, worked examples, edge cases, and acceptance criteria. Drop that depth only when the user explicitly asks for terse issues.
- **Draft with the strongest model available.** Prefer Fable (`model: "fable"`) or GPT Astra through the Codex CLI for writing the issue bodies. Never mention the model in an issue.
- **Create directly.** Create the issues with `gh issue create` (and `gh api` for milestones) without asking for confirmation.

Finish with the created issue numbers, titles, links, and milestones.
