---
name: codex-computer-use
description: Use the OpenAI Codex CLI for browser, GUI, and visual verification work — driving a browser through a Playwright MCP server and analyzing screenshots passed with `-i`. Use when work needs computer use to complete or verify (checking a rendered page, inspecting a simulator or desktop screenshot, driving a local web app), when the user asks Codex/gpt-5.5 to look at a UI, or when a workflow shells out visual verification to Codex. Covers what the CLI actually offers vs what needs MCP wiring, Playwright MCP setup, macOS screenshot capture recipes, and sandbox/network implications.
---

# Codex Computer Use

The Codex CLI has **no built-in browser or desktop control** — no `--browser`, no `--screenshot` flag. Computer use is assembled from two primitives: an **MCP server** (Playwright) for driving a browser, and **image input** (`-i`) for verifying screenshots captured by external tools. The Codex *app* has an in-app browser and a Computer Use plugin, but those are app features, not CLI automation.

*Command surface verified against codex-cli 0.142.5; on flag errors, recheck `codex --help` and `codex exec --help` — placement and availability shift between versions.*

## When to use

- Verify a change visually: rendered page, iOS simulator, desktop app screenshot
- Drive a local web app through a browser (click, navigate, read console) via Codex
- Compare before/after screenshots for regressions

## Preflight

```bash
codex --version # confirm CLI present; stop and report if missing
```

## Capability reality check

| Capability | CLI status | Pattern |
|------------|-----------|---------|
| Browser control | not built in | Playwright MCP server |
| Screenshots | not built in | `screencapture`, `xcrun simctl`, `npx playwright screenshot` → pass with `-i` |
| Image analysis | built in | `codex exec -i shot.png "…"` (repeatable) |
| Desktop control | CLI: no; Codex app: Computer Use plugin | prefer screenshot-verify loops from the CLI |
| MCP | built in | `codex mcp` manages STDIO and streamable-HTTP servers |

## Wire Playwright MCP (one-time setup)

```bash
codex mcp add playwright -- npx -y @playwright/mcp@latest
codex mcp list --json          # confirm registered
```

Equivalent `~/.codex/config.toml`:

```toml
[mcp_servers.playwright]
command = "npx"
args = ["-y", "@playwright/mcp@latest"]
startup_timeout_sec = 20
tool_timeout_sec = 120
```

Do the `npx` package download during setup (network-enabled shell) — a sandboxed Codex run may not be allowed to download it mid-task.

## Drive the browser

```bash
codex -a never exec \
  -m gpt-5.5 \
  -s workspace-write \
  -c model_reasoning_effort='"medium"' \
  "Use the Playwright MCP server to open http://127.0.0.1:3000, exercise the signup flow, check the console for errors, and report only reproducible UI defects with selectors or routes." \
  </dev/null 2>/dev/null
```

- `-s read-only` suffices for observe-only browsing; use `workspace-write` when Codex should also edit source after what it sees.
- Global flags (`-a`, `--search`) go before `exec`; always end with `</dev/null` (stdin gotcha — open-but-empty stdin hangs the CLI).
- Final message → stdout; progress/thinking → stderr.

## Verify by screenshot (macOS recipes)

Capture outside Codex, analyze with `-i`:

```bash
# Whole screen (terminal app needs Screen Recording permission)
screencapture -x /tmp/screen.png

# iOS simulator
xcrun simctl io booted screenshot /tmp/sim.png

# A URL, headless
npx playwright screenshot http://127.0.0.1:3000 /tmp/page.png
```

```bash
codex exec \
  -i /tmp/sim.png \
  "Inspect this iOS simulator screenshot. Identify layout overlap, clipped text, and visible error states. For each defect, name the likely source file to inspect." \
  </dev/null 2>/dev/null
```

Before/after comparison — pass both:

```bash
codex exec -i /tmp/before.png -i /tmp/after.png \
  "Compare these screenshots and identify visible regressions. Only report differences supported by the images." \
  </dev/null 2>/dev/null
```

## The verify loop

For "make it look right" tasks, iterate:

1. Capture screenshot.
2. `codex exec -i … resume --last` with the new capture.
3. Apply or let Codex apply fixes.
4. Recapture.

Resume keeps prior context:

```bash
codex exec resume --last -i /tmp/after-fix.png \
  "Here is the page after your fix. Confirm the overlap is gone; list anything still broken." \
  </dev/null 2>/dev/null
```

## Sandbox and network

| Mode | Enough for |
|------|-----------|
| `read-only` | screenshot inspection; MCP browsing when server + deps already installed |
| `workspace-write` | editing source after visual verification; shell network still bounded |
| `-c sandbox_workspace_write.network_access=true` | shell network inside workspace-write — prefer scoped MCP over broad access |
| `danger-full-access` | only inside disposable VMs/containers |

MCP server traffic is the server's own process — the Playwright browser reaches the network regardless of the Codex command sandbox. The sandbox bounds what *shell commands* Codex runs.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| MCP tools unavailable in run | server not registered / failed to start | `codex mcp list --json`, `codex mcp get playwright --json`, raise `startup_timeout_sec`, preinstall deps |
| Blank/black screenshot | missing Screen Recording permission | System Settings → Privacy & Security → Screen Recording for the terminal app |
| Hangs before doing work | stdin open-but-empty | append `</dev/null` |
| Playwright download blocked mid-run | sandbox bounds shell network | run `npx -y @playwright/mcp@latest` once during setup |
| Codex "can't see" the image | wrong path or flag | `-i` per image, absolute paths, PNG/JPEG |
