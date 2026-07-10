# codex-computer-use

> Browser, GUI, and visual verification work through the OpenAI Codex CLI — Playwright MCP for driving a browser, `-i` image input for verifying screenshots captured with macOS tools.

## What it does

`codex-computer-use` is honest about what the Codex CLI actually offers: no built-in browser, no screenshot flag, no desktop control. Computer use is assembled from two real primitives — an MCP server (Playwright) that gives Codex browser tools, and repeatable `-i` image input for analyzing screenshots captured externally (`screencapture`, `xcrun simctl io booted screenshot`, `npx playwright screenshot`).

The skill covers the one-time `codex mcp add playwright` setup, drive-the-browser invocations, before/after screenshot comparison, an iterative verify loop built on `codex exec resume --last -i`, and the sandbox/network subtleties (MCP server traffic bypasses the command sandbox; shell network doesn't).

## When to use it

- *"Check the signup flow on localhost:3000 renders without console errors."*
- *"Look at this simulator screenshot — anything visually broken?"*
- *"Compare before/after screenshots for regressions."*
- Verify-by-screenshot loops after UI changes, from CLI or agent harness

**Not the right skill if** the work is code review (→ [`codex-review`](../codex-review/)) or non-visual implementation (→ [`codex-implementation`](../codex-implementation/)).

## Example walkthrough

**Prompt**

> Verify my fix removed the header overlap in the iOS app.

**What the skill does**

1. Captures: `xcrun simctl io booted screenshot /tmp/after.png`.
2. Runs `codex exec -i /tmp/before.png -i /tmp/after.png "Compare these screenshots…"` — read-only, `</dev/null`, stderr suppressed.
3. Codex confirms overlap gone, flags clipped label at top-right.
4. After the label fix: `codex exec resume --last -i /tmp/after2.png "Confirm nothing remains broken."` — prior context carries over.

## Installation

```bash
npx skills add thatjuan/agent-skills --skill codex-computer-use
```

## Bundled resources

| File | Purpose |
|------|---------|
| `SKILL.md` | Capability reality check, Playwright MCP setup, macOS capture recipes, verify loop, sandbox/network table, troubleshooting |

## Tips

- **Install the MCP server during setup, not mid-task.** A sandboxed run may not be allowed to download `@playwright/mcp` when it first needs it.
- **Screen Recording permission** for your terminal app, or `screencapture` returns black frames.
- **The sandbox bounds shell commands, not MCP servers.** Playwright reaches the network even in `read-only` — pick sandbox mode by whether Codex should edit source, not by browsing needs.
- **Resume keeps the visual context.** Iterating on a fix? `resume --last -i new-shot.png` beats re-explaining.

## Related skills

- [`codex-implementation`](../codex-implementation/) — make the fix the screenshot revealed
- [`codex-review`](../codex-review/) — code-level review to pair with visual checks
