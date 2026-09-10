# temporal

> Expert-level knowledge for building durable, reliable distributed systems with Temporal.io. Covers the Python SDK (`temporalio`), TypeScript SDK (`@temporalio/*`), core platform concepts, and AI/LLM orchestration patterns.

## What it does

`temporal` turns your agent into a Temporal expert. It understands:

- **Durable execution model** — workflows as deterministic replay, activities as non-deterministic work
- **The determinism contract** — what's safe inside workflow code vs. what belongs in activities, SDK sandbox replacements for `Date.now()`, `Math.random()`, `uuid`, `sleep`
- **The 7 timeouts** — Workflow Execution, Run, Task, Start-to-Close, Schedule-to-Close, Schedule-to-Start, Heartbeat — and when each one matters
- **Retry policies** — defaults, backoff tuning, non-retryable error types, activity vs. workflow retry behavior
- **Signals, Queries, Updates, Child Workflows, Schedules** — full primitive coverage
- **AI orchestration patterns** — durable agent loops, multi-agent architectures, human-in-the-loop, LLM pipelines, framework integrations (OpenAI Agents, LangChain, DSPy)

It triggers automatically when code imports `temporalio` or `@temporalio/*`, but it's also the right skill for any conversation about durable execution, workflow orchestration, or AI agent reliability.

## When to use it

Invoke this skill when you hear:

- *"Build a workflow that processes orders and calls three external APIs with retries."*
- *"My LLM agent keeps losing state when the process restarts — can Temporal help?"*
- *"Why is my workflow non-deterministic? Temporal keeps erroring on replay."*
- *"Set up a Temporal worker in Python for our pricing job."*
- *"Migrate our cron-based ETL to Temporal schedules."*
- *"Design an AI agent architecture with human approval gates."*

## Example walkthrough

**Prompt**

> I need a TypeScript workflow that calls an LLM to classify a document, then routes it to one of three downstream services. It should retry on LLM failures but not on downstream-service failures (those should page the on-call).

**What the skill produces**

```typescript
// activities.ts
export async function classifyDocument(doc: string): Promise<Category> {
  // Non-deterministic LLM call — lives in an activity
  return await openai.chat.completions.create({ ... });
}

export async function routeToService(category: Category, doc: string) {
  await services[category].ingest(doc);
}

// workflow.ts
import { proxyActivities } from '@temporalio/workflow';

const { classifyDocument } = proxyActivities<typeof activities>({
  startToCloseTimeout: '30 seconds',
  retry: {
    initialInterval: '1s',
    backoffCoefficient: 2,
    maximumAttempts: 5,
  },
});

const { routeToService } = proxyActivities<typeof activities>({
  startToCloseTimeout: '10 seconds',
  retry: {
    maximumAttempts: 1,                            // no retry — page on-call
    nonRetryableErrorTypes: ['DownstreamError'],
  },
});

export async function classifyAndRoute(doc: string) {
  const category = await classifyDocument(doc);
  await routeToService(category, doc);
}
```

The skill also explains **why**: LLM calls are retryable (transient), but downstream routing failures are business-critical and should fail loud. It warns if you tried to put the `openai` call directly in the workflow (determinism violation on replay).

## Installation

```bash
npx skills add thatjuan/agent-skills --skill temporal
```

## Bundled resources

| File | Purpose |
|------|---------|
| `SKILL.md` | Platform overview, SDK quick reference, pattern selection guide, AI orchestration overview |
| `references/core-concepts.md` | Architecture, durable execution model, determinism constraints, timeouts, retry policies, advanced features |
| `references/python-sdk.md` | Python decorators, async patterns, testing, client/worker setup, sandbox configuration |
| `references/typescript-sdk.md` | TypeScript packages, proxyActivities, sandboxing, bundling, interceptors, testing |
| `references/ai-patterns.md` | AI agent loops, multi-agent architectures, human-in-the-loop, LLM pipelines, framework integrations |

## Tips

- **State determinism problems early.** If you say *"my workflow is flaky on replay,"* the skill immediately suspects the determinism contract and walks through common violations (direct network calls, `Date.now()`, `Math.random()`, file I/O, loose iteration order).
- **Ask for the timeout table for your use case.** The 7 timeouts confuse everyone. The skill will produce a specific recommendation for each based on what your activity actually does.
- **Use the AI patterns for agent work.** If you're building an LLM agent, ask for the "durable agent loop" pattern — it's the canonical Temporal approach to state-preserving AI agents.

## Related skills

- [`claude-api`](https://github.com/thatjuan/agent-skills) — for Claude API / Anthropic SDK work inside activities
