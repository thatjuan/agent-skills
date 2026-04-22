# Cloudbeds developer resources

## Table of contents

- [Documentation](#documentation)
- [OpenAPI specs](#openapi-specs)
- [MCP server for AI agents](#mcp-server-for-ai-agents)
- [SDKs](#sdks)
- [Postman collections](#postman-collections)
- [Sandbox access](#sandbox-access)
- [Support](#support)

## Documentation

Root: `https://developers.cloudbeds.com/`.

- Sitemap for LLMs: `https://developers.cloudbeds.com/llms.txt` — lists every guide and API reference page.
- Any doc page has a markdown mirror: append `.md` to the URL. `https://developers.cloudbeds.com/docs/authentication-1.md`, `https://developers.cloudbeds.com/reference/get_getreservation-2.md`, etc. The markdown version strips formatting tokens and is preferred for LLM consumption.
- Changelog: `https://developers.cloudbeds.com/changelog`.
- Use-case blueprints: `https://developers.cloudbeds.com/docs/use-cases-blueprints.md` (Accounting, Booking Engine, BI, Check-in, CRM, Door Locks, Event Management, Fiscal Docs, Gov Police Report, Guest Comm, Insurance, Housekeeping, Upsell, Payment, POS, RMS).

## OpenAPI specs

Repo: `https://github.com/cloudbeds/openapi-specs`. Directory `src/`:

| File | Product |
|---|---|
| `pms-v1.3-openapi.yaml` | PMS Classic v1.3 (current primary) |
| `pms-v1.2-openapi.yaml` | PMS Classic v1.2 |
| `pms-v2.0-openapi.yaml` | PMS v2 (modular REST) |
| `accounting-v1.0-openapi.json` | Accounting |
| `cloudbeds-insights-v1.1-openapi.json` | Data Insights |
| `group-profile-v1.0-openapi.yaml` | Group Profile |
| `fiscal-document-v1.0-openapi.yaml` | Fiscal Documents |
| `pay-by-link-v2.0-openapi.json` | Pay-By-Link |
| `payments-vault-v1.0-openapi.json` | Payments Vault |
| `ota-build-to-us-v5.3-openapi.yaml` / `.json` | OTA Build-To-Us (partners implement) |

Pin a commit when generating clients: `gh api repos/cloudbeds/openapi-specs/commits/main --jq .sha`.

Codegen example (OpenAPI Generator):

```bash
openapi-generator-cli generate \
  -i https://raw.githubusercontent.com/cloudbeds/openapi-specs/<sha>/src/pms-v2.0-openapi.yaml \
  -g typescript-fetch \
  -o ./cloudbeds-pms-v2
```

## MCP server for AI agents

Cloudbeds operates an official Model Context Protocol server at `https://developers.cloudbeds.com/mcp` (HTTP transport). It exposes tools for doc search, API discovery, and integration-code generation against current Cloudbeds APIs.

Add to Claude Code:

```bash
claude mcp add --transport http cloudbeds-developers https://developers.cloudbeds.com/mcp
```

Cursor (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "cloudbeds-developers": { "url": "https://developers.cloudbeds.com/mcp" }
  }
}
```

VS Code (`.vscode/mcp.json`): same `servers` key. Claude Desktop supports it via the "custom connector" UI.

## SDKs

| Language | Status | Source |
|---|---|---|
| Python | Official, auto-generated, tracks PMS v2 | `https://github.com/cloudbeds/cloudbeds-api-python` |
| Browser payment UI | Official web component | `@cloudbeds/payment-element-webcomponent` on GitHub Packages (`https://github.com/orgs/cloudbeds/packages/npm/package/payment-element-webcomponent`). Demo: `https://payment-element.cloudbeds.com/0.5.9/demo/index.html` |
| JavaScript / TypeScript | No official REST SDK | Generate from OpenAPI spec |
| PHP / Ruby / Java / Go / C# | No official REST SDK | Generate from OpenAPI spec |

Python package:

- Package module: `cloudbeds_pms`.
- Requires Python ≥ 3.9.
- Dependencies: `urllib3 ≥ 2.1 < 3`, `python-dateutil ≥ 2.8.2`, `pydantic ≥ 2`, `typing-extensions ≥ 4.7.1`.
- Version 2.13.0 tracks PMS v2. The classic v1.3 RPC-style API is not fully covered; codegen from `pms-v1.3-openapi.yaml` fills gaps.

## Postman collections

Index: `https://developers.cloudbeds.com/docs/postman-api-collection.md`.

- PMS v1.3 — built-in "Run in Postman" button from the API docs.
- Accounting — GitHub hosted.
- Data Insights — GitHub hosted.
- Group Profile — GitHub hosted.
- Pay-By-Link — GitHub hosted.
- Fiscal Documents — GitHub hosted.

Webhook endpoint testing: `https://webhook.site` creates a unique endpoint URL on page load and displays each POST's headers and body in real time.

## Sandbox access

No self-serve sandbox. Access gating:

1. Submit the "Partner with Us" form: `https://www.cloudbeds.com/partner-with-cloudbeds/`.
2. Email `integrations@cloudbeds.com` with company name, website, and integration category (pick from the Use Case Blueprints list).
3. Internal Cloudbeds review before access is granted.

Certification requirements before go-live:

- 5–10 pilot properties connected.
- Automated auth flow (no manual key pasting for marketplace apps).
- HTTPS redirect_uri.
- Demonstrated correct behavior on disconnect / reconnect.

Payment gateway test mode: email `integrations@cloudbeds.com` for a test-gateway account.

## Support

- Email: `integrations@cloudbeds.com` (only official channel).
- Include `X-Request-ID` from the failing response's headers.
- Stack Overflow tag: `cloudbeds`.
- Partner portal: `https://integrations.cloudbeds.com/hc/en-us`.
- Monthly API announcements mailing list: subscribe via the link in the API docs.
