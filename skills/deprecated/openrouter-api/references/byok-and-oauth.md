# BYOK, OAuth PKCE, app attribution

## Contents

- [App attribution headers](#app-attribution-headers)
- [BYOK — bring your own provider keys](#byok--bring-your-own-provider-keys)
- [OAuth PKCE — let users connect their own OpenRouter account](#oauth-pkce--let-users-connect-their-own-openrouter-account)
- [Key safety](#key-safety)

## App attribution headers

Used for OpenRouter rankings, marketplace category placement, and analytics.

| Header | Required | Purpose |
|--------|----------|---------|
| `HTTP-Referer` | yes (for attribution) | Your app URL — primary identifier |
| `X-OpenRouter-Title` | no (recommended) | Display name; `X-Title` accepted for backwards compatibility |
| `X-OpenRouter-Categories` | no | Comma-separated marketplace categories |

Without `HTTP-Referer`, no app page is created. Apps using `localhost` must also set `X-OpenRouter-Title`.

### Recognized categories

| Group | Slugs |
|-------|-------|
| Coding | `cli-agent`, `ide-extension`, `cloud-agent`, `programming-app`, `native-app-builder` |
| Creative | `creative-writing`, `video-gen`, `image-gen` |
| Productivity | `writing-assistant`, `general-chat`, `personal-agent` |
| Entertainment | `roleplay`, `game` |

Lowercase, hyphen-separated, ≤30 chars each. Up to a few categories per request, capped per app overall. Unrecognized values silently dropped.

```typescript
const client = new OpenRouter({
  apiKey: process.env.OPENROUTER_API_KEY,
  defaultHeaders: {
    'HTTP-Referer': 'https://myapp.com',
    'X-OpenRouter-Title': 'My AI Assistant',
    'X-OpenRouter-Categories': 'cli-agent,cloud-agent',
  },
});
```

## BYOK — bring your own provider keys

OpenRouter sends requests through the user's own provider account (OpenAI, Azure, AWS Bedrock, Vertex AI, Anthropic, etc.). The user controls rate limits and billing on the provider side. OpenRouter charges a small fee deducted from credits (waived for ~first 1000 BYOK requests/month).

Manage at <https://openrouter.ai/settings/integrations>.

### Key priority and fallback

By default: BYOK key → fallback to OpenRouter shared capacity if BYOK key fails or is rate-limited. Per-key option **"Always use this key"** disables the fallback (errors instead of falling through).

### BYOK + provider ordering

BYOK endpoints are **always tried first**, regardless of `provider.order`. After BYOK exhausts, OpenRouter shared capacity is tried in `order`.

Example with BYOK keys for Bedrock, Vertex, Anthropic plus `order: ["amazon-bedrock", "google-vertex", "anthropic"]`:

1. Bedrock (BYOK)
2. Vertex (BYOK)
3. Anthropic (BYOK)
4. Bedrock (shared)
5. Vertex (shared)
6. Anthropic (shared)

Partial BYOK works the same way: any BYOK provider in the order is prioritized over any non-BYOK in the order.

### Provider-specific key formats

| Provider | Format |
|----------|--------|
| OpenAI / Anthropic / DeepSeek / etc. | Bare API key string |
| Azure AI Services | JSON object or array (multi-deployment): `{model_slug, endpoint_url, api_key, model_id}` |
| AWS Bedrock | Bedrock API key string (region-locked), OR `{accessKeyId, secretAccessKey, region}` JSON |
| Google Vertex AI | Service-account JSON (`type: service_account`, `project_id`, `private_key`, `client_email`, …) + optional `region` |

#### Azure example

```json
[
  {
    "model_slug": "openai/gpt-5.2",
    "endpoint_url": "https://example.openai.azure.com/openai/deployments/gpt-5.2/chat/completions?api-version=2024-08-01-preview",
    "api_key": "your-azure-api-key",
    "model_id": "gpt-5.2"
  }
]
```

URL must end with `/chat/completions` and include `api-version`.

#### AWS Bedrock IAM minimum

`bedrock:InvokeModel` and `bedrock:InvokeModelWithResponseStream`. Tied to a region — use AWS-credentials JSON to switch regions.

### Multiple BYOK keys for the same provider

All used; ordering between same-provider keys not guaranteed. For deterministic key selection, use separate provider accounts.

### `is_byok` in usage

```json
"usage": { "is_byok": true, "cost_details": { "upstream_inference_cost": ... } }
```

## OAuth PKCE — let users connect their own OpenRouter account

End users connect their OpenRouter account in one click and your app receives a user-controlled API key. Useful for client-side apps where the user pays.

### Step 1 — redirect to `/auth`

```
https://openrouter.ai/auth?callback_url=<YOUR_SITE_URL>
                          &code_challenge=<CHALLENGE>
                          &code_challenge_method=S256
```

`code_challenge` is optional but recommended. `S256` (base64-url SHA-256 of `code_verifier`) preferred over `plain`.

```typescript
import { Buffer } from 'buffer';

async function createSHA256CodeChallenge(input: string) {
  const data = new TextEncoder().encode(input);
  const hash = await crypto.subtle.digest('SHA-256', data);
  return Buffer.from(hash).toString('base64url');
}

const codeVerifier = crypto.randomUUID();
const codeChallenge = await createSHA256CodeChallenge(codeVerifier);
```

For local apps without a public URL, use `http://localhost:3000` for callback + `HTTP-Referer`. Move to a real URL or public GitHub repo for production.

### Step 2 — exchange code for API key

User is redirected back with `?code=...`. POST it to `/api/v1/auth/keys`:

```typescript
const response = await fetch('https://openrouter.ai/api/v1/auth/keys', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    code: '<CODE_FROM_QUERY_PARAM>',
    code_verifier: '<CODE_VERIFIER>',           // if S256/plain used
    code_challenge_method: 'S256',              // must match step 1
  }),
});

const { key } = await response.json();
```

### Step 3 — use the key

Store securely on client (or your own DB) and pass as `Authorization: Bearer <key>`.

### PKCE error codes

- `400 Invalid code_challenge_method` — methods don't match between steps.
- `403 Invalid code or code_verifier` — user not logged in, or verifier wrong, or method mismatch.
- `405 Method Not Allowed` — must `POST` with HTTPS.

## Key safety

- OpenRouter is a GitHub secret-scanning partner. Leaked keys trigger an email alert.
- Revoke at <https://openrouter.ai/settings/keys>.
- Use environment variables. Don't commit keys.
- Per-key credit limits are configurable when creating the key.
